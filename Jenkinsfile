pipeline {
    agent any

    environment {
        APP_PORT = '5000'
        MONGODB_PORT = '27017'
        APP_REPO = 'https://github.com/YourUsername/mern-app.git'
        TEST_REPO = 'https://github.com/YourUsername/selenium-tests.git'
        DOCKER_IMAGE = 'markhobson/maven-chrome'
        GITHUB_CREDENTIALS = 'github-pat'
    }

    stages {
        stage('Checkout App') {
            steps {
                git url: "${APP_REPO}", credentialsId: "${GITHUB_CREDENTIALS}"
            }
        }

        stage('Checkout Tests') {
            steps {
                dir('selenium-tests') {
                    git url: "${TEST_REPO}", credentialsId: "${GITHUB_CREDENTIALS}"
                }
            }
        }

        stage('Setup Application') {
            steps {
                sh '''
                    # Kill old processes
                    kill -9 $(lsof -t -i:${APP_PORT}) 2>/dev/null || true
                    kill -9 $(lsof -t -i:${MONGODB_PORT}) 2>/dev/null || true

                    # Install npm dependencies
                    npm install

                    # Start MongoDB
                    sudo systemctl start mongod || mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log
                    sleep 5

                    # Start MERN app
                    nohup npm start > app.log 2>&1 &
                    echo $! > app.pid

                    # Wait for app
                    for i in {1..30}; do
                        curl -f http://localhost:${APP_PORT} && exit 0 || echo "Waiting for app..."
                        sleep 2
                    done
                '''
            }
        }

        stage('Run Selenium Tests') {
            steps {
                sh '''
                    mkdir -p test-results
                    docker run --rm \
                        --network=host \
                        -v $(pwd)/selenium-tests:/app \
                        -v $(pwd)/test-results:/app/test-results \
                        ${DOCKER_IMAGE} \
                        mvn -f /app/pom.xml test
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up app...'
            sh '''
                if [ -f app.pid ]; then
                    kill -9 $(cat app.pid) || true
                    rm -f app.pid
                fi
                kill -9 $(lsof -t -i:${APP_PORT}) 2>/dev/null || true
            '''

            // Publish JUnit results
            junit allowEmptyResults: true, testResults: 'selenium-tests/target/surefire-reports/*.xml'

            // Archive logs
            archiveArtifacts artifacts: 'app.log', allowEmptyArchive: true

            // Email committers automatically using configured Jenkins SMTP
            emailext (
                subject: "Jenkins Build ${currentBuild.currentResult}: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                <h2>Build ${currentBuild.currentResult}</h2>
                <p><b>Job:</b> ${env.JOB_NAME}</p>
                <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                <p><b>Build URL:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                <h3>Test Results</h3>
                <p>Check Jenkins Test Report: <a href="${env.BUILD_URL}testReport/">Test Report</a></p>
                """,
                mimeType: 'text/html',
                recipientProviders: [[$class: 'CulpritsRecipientProvider']] // emails the committer(s)
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
