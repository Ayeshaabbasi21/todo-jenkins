pipeline {
    agent any

    environment {
        APP_PORT = '5000'
        MONGODB_PORT = '27017'
        TODO_REPO = 'https://github.com/Ayeshaabbasi21/todo-jenkins.git'
        DOCKER_IMAGE = 'todo-selenium-tests'
        GITHUB_CREDENTIALS = 'github-pat'
    }

    stages {
        stage('Checkout Repo') {
            steps {
                git branch: 'main',
                    url: "${TODO_REPO}",
                    credentialsId: "${GITHUB_CREDENTIALS}"
            }
        }

        stage('Setup Application') {
            steps {
                sh '''
                    # Kill old processes
                    kill -9 $(lsof -t -i:${APP_PORT}) 2>/dev/null || true
                    kill -9 $(lsof -t -i:${MONGODB_PORT}) 2>/dev/null || true

                    # Install dependencies
                    npm install

                    # Start MongoDB
                    sudo systemctl start mongod || mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log
                    sleep 5

                    # Start app in background
                    nohup npm start > app.log 2>&1 &
                    echo $! > app.pid

                    # Wait for app to start (up to 60 seconds)
                    echo "Waiting for app to start on port ${APP_PORT}..."
                    for i in {1..30}; do
                        if curl -f http://localhost:${APP_PORT} 2>/dev/null; then
                            echo "✅ App started successfully!"
                            exit 0
                        fi
                        echo "Attempt $i/30: App not ready yet..."
                        sleep 2
                    done
                    
                    echo "❌ App failed to start. Check app.log"
                    cat app.log
                    exit 1
                '''
            }
        }

        stage('Build Test Container') {
            steps {
                sh '''
                    # Build Docker image from Dockerfile
                    docker build -t ${DOCKER_IMAGE} .
                '''
            }
        }

        stage('Run Selenium Tests') {
            steps {
                sh '''
                    # Create test results directory
                    mkdir -p test-results

                    # Run Selenium tests using custom image
                    docker run --rm \
                        --network=host \
                        -v $(pwd)/test-results:/app/test-results \
                        ${DOCKER_IMAGE}
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up app...'
            sh '''
                if [ -f app.pid ]; then
                    kill -9 $(cat app.pid) 2>/dev/null || true
                    rm -f app.pid
                fi
                kill -9 $(lsof -t -i:${APP_PORT}) 2>/dev/null || true
            '''

            // Publish JUnit results
            junit allowEmptyResults: true, testResults: 'test-results/**/*.xml'

            // Archive logs and artifacts
            archiveArtifacts artifacts: 'app.log,test-results/**/*', allowEmptyArchive: true

            // Email notifications
            emailext (
                subject: "Jenkins Build ${currentBuild.currentResult}: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                    <html>
                    <body>
                        <h2>Build ${currentBuild.currentResult}</h2>
                        <p><b>Job:</b> ${env.JOB_NAME}</p>
                        <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                        <p><b>Build URL:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                        <p><b>Status:</b> ${currentBuild.currentResult}</p>
                        
                        <h3>Test Results</h3>
                        <p>Check Jenkins for detailed results: <a href="${env.BUILD_URL}testReport/">Test Report</a></p>
                        
                        <h3>Console Output</h3>
                        <p><a href="${env.BUILD_URL}console">View Full Console Output</a></p>
                    </body>
                    </html>
                """,
                mimeType: 'text/html',
                to: 'ayesha13abbasi@gmail.com',
                replyTo: 'ayesha13abbasi@gmail.com',
                from: 'ayesha13abbasi@gmail.com'
            )
        }

        success {
            echo '✅ All tests passed!'
        }

        unstable {
            echo '⚠️ Some tests failed!'
        }

        failure {
            echo '❌ Build failed!'
        }
    }
}