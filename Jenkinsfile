pipeline {
    agent any
    
    environment {
        APP_PORT = '5000'
        MONGO_PORT = '27017'
    }
    
    stages {
        stage('Checkout Repo') {
            steps {
                echo 'Checking out code from GitHub...'
                git branch: 'main',
                    credentialsId: 'github-pat',
                    url: 'https://github.com/Ayeshaabbasi21/todo-jenkins.git'
            }
        }
        
        stage('Setup Application') {
            steps {
                script {
                    echo 'Setting up application environment...'
                    
                    // Kill any existing processes on ports
                    sh '''
                        lsof -t -i:5000 | xargs kill -9 || true
                        lsof -t -i:27017 | xargs kill -9 || true
                    '''
                    
                    // Install dependencies
                    sh 'npm install'
                    
                    // Start MongoDB
                    sh 'sudo systemctl start mongod'
                    
                    // Wait for MongoDB
                    sh 'sleep 5'
                    
                    // Start application in background
                    sh '''
                        nohup npm start > app.log 2>&1 &
                        echo $! > app.pid
                        echo "Waiting for app to start on port 5000..."
                    '''
                    
                    // Wait for app to be ready
                    def maxAttempts = 30
                    def attempt = 0
                    def appReady = false
                    
                    while (attempt < maxAttempts && !appReady) {
                        attempt++
                        try {
                            sh 'curl -f http://localhost:5000'
                            appReady = true
                            echo "✅ App started successfully on attempt ${attempt}!"
                        } catch (Exception e) {
                            echo "Attempt ${attempt}/${maxAttempts}: App not ready yet..."
                            sleep(2)
                        }
                    }
                    
                    if (!appReady) {
                        error("Failed to start application after ${maxAttempts} attempts")
                    }
                }
            }
        }
        
        stage('Build Test Container') {
            steps {
                echo 'Building Docker container for Selenium tests...'
                sh 'docker build -t todo-selenium-tests .'
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                echo 'Running Selenium tests in Docker container...'
                sh '''
                    mkdir -p test-results
                    chmod 777 test-results
                    docker run --rm --network=host \
                      -v $(pwd)/test-results:/app/test-results \
                      todo-selenium-tests
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
                lsof -t -i:5000 | xargs kill -9 || true
            '''
            
            // Publish test results
            junit 'test-results/*.xml'
            
            // Archive test results
            archiveArtifacts artifacts: 'test-results/*.xml', fingerprint: true
            
            // Send email to committer
            emailext (
                subject: "Jenkins Build ${currentBuild.currentResult}: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                    <html>
                    <body>
                        <h2>Build ${currentBuild.currentResult}</h2>
                        <p><strong>Project:</strong> ${env.JOB_NAME}</p>
                        <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                        <p><strong>Build Status:</strong> ${currentBuild.currentResult}</p>
                        <p><strong>Build URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                        
                        <h3>Test Results</h3>
                        <p>Total Tests: ${currentBuild.rawBuild.getAction(hudson.tasks.junit.TestResultAction.class)?.totalCount ?: 'N/A'}</p>
                        <p>Passed: ${currentBuild.rawBuild.getAction(hudson.tasks.junit.TestResultAction.class)?.passCount ?: 'N/A'}</p>
                        <p>Failed: ${currentBuild.rawBuild.getAction(hudson.tasks.junit.TestResultAction.class)?.failCount ?: 'N/A'}</p>
                        <p>Skipped: ${currentBuild.rawBuild.getAction(hudson.tasks.junit.TestResultAction.class)?.skipCount ?: 'N/A'}</p>
                        
                        <h3>Recent Changes</h3>
                        <ul>
                        ${env.GIT_COMMIT ? "<li>Commit: ${env.GIT_COMMIT}</li>" : ""}
                        ${env.GIT_AUTHOR_NAME ? "<li>Author: ${env.GIT_AUTHOR_NAME}</li>" : ""}
                        ${env.GIT_AUTHOR_EMAIL ? "<li>Email: ${env.GIT_AUTHOR_EMAIL}</li>" : ""}
                        </ul>
                        
                        <h3>Console Output</h3>
                        <p><a href="${env.BUILD_URL}console">View Full Console Output</a></p>
                        
                        <p><i>This is an automated message from Jenkins CI/CD Pipeline</i></p>
                    </body>
                    </html>
                """,
                to: "${env.GIT_AUTHOR_EMAIL ?: 'ayesha13abbasi@gmail.com'}",
                from: 'jenkins@yourdomain.com',
                replyTo: 'noreply@yourdomain.com',
                mimeType: 'text/html',
                attachmentsPattern: 'test-results/*.xml'
            )
        }
        
        success {
            echo '✅ Build succeeded!'
        }
        
        failure {
            echo '❌ Build failed!'
        }
    }
}