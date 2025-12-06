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
                    echo 'Setting up application...'
                    sh '''
                        lsof -t -i:5000 | xargs kill -9 2>/dev/null || true
                        lsof -t -i:27017 | xargs kill -9 2>/dev/null || true
                        npm install
                        sudo systemctl start mongod
                        sleep 5
                        nohup npm start > app.log 2>&1 &
                        echo $! > app.pid
                    '''
                    
                    def maxAttempts = 30
                    def attempt = 0
                    def appReady = false
                    
                    while (attempt < maxAttempts && !appReady) {
                        attempt++
                        try {
                            sh 'curl -f http://localhost:5000 > /dev/null 2>&1'
                            appReady = true
                            echo "App started on attempt ${attempt}"
                        } catch (Exception e) {
                            echo "Attempt ${attempt}/${maxAttempts}..."
                            sleep(2)
                        }
                    }
                    
                    if (!appReady) {
                        error("Failed to start application")
                    }
                }
            }
        }
        
        stage('Build Test Container') {
            steps {
                echo 'Building Docker container...'
                sh 'docker build -t todo-selenium-tests .'
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                echo 'Running tests...'
                sh '''
                    mkdir -p test-results
                    chmod 777 test-results
                    docker run --rm --network=host \
                      -v $(pwd)/test-results:/app/test-results \
                      todo-selenium-tests || echo "Tests completed"
                '''
            }
        }
    }
    
    post {
        always {
            script {
                echo 'Cleaning up...'
                sh '''
                    if [ -f app.pid ]; then
                        kill -9 $(cat app.pid) 2>/dev/null || true
                        rm -f app.pid
                    fi
                    lsof -t -i:5000 | xargs kill -9 2>/dev/null || true
                '''
                
                try {
                    env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.GIT_COMMIT_MSG = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                    env.GIT_AUTHOR_NAME = sh(script: 'git log -1 --pretty=%an', returnStdout: true).trim()
                    env.GIT_AUTHOR_EMAIL = sh(script: 'git log -1 --pretty=%ae', returnStdout: true).trim()
                } catch (Exception e) {
                    env.GIT_AUTHOR_EMAIL = 'ayesha13abbasi@gmail.com'
                }
            }
            
            junit allowEmptyResults: true, testResults: 'test-results/*.xml'
            archiveArtifacts artifacts: 'test-results/*.xml, app.log', allowEmptyArchive: true
            
            emailext (
                subject: "Jenkins Build ${currentBuild.currentResult}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2 style="color: ${currentBuild.currentResult == 'SUCCESS' ? 'green' : 'red'}">
                            Build ${currentBuild.currentResult}
                        </h2>
                        
                        <h3>Build Information</h3>
                        <table border="1" cellpadding="10" style="border-collapse: collapse;">
                            <tr><td><b>Project</b></td><td>${env.JOB_NAME}</td></tr>
                            <tr><td><b>Build Number</b></td><td>#${env.BUILD_NUMBER}</td></tr>
                            <tr><td><b>Status</b></td><td>${currentBuild.currentResult}</td></tr>
                            <tr><td><b>Duration</b></td><td>${currentBuild.durationString}</td></tr>
                        </table>
                        
                        <h3>Commit Details</h3>
                        <table border="1" cellpadding="10" style="border-collapse: collapse;">
                            <tr><td><b>Commit ID</b></td><td>${env.GIT_COMMIT_SHORT}</td></tr>
                            <tr><td><b>Author</b></td><td>${env.GIT_AUTHOR_NAME}</td></tr>
                            <tr><td><b>Email</b></td><td>${env.GIT_AUTHOR_EMAIL}</td></tr>
                            <tr><td><b>Message</b></td><td>${env.GIT_COMMIT_MSG}</td></tr>
                        </table>
                        
                        <h3>Quick Links</h3>
                        <p>
                            <a href="${env.BUILD_URL}">View Build</a> | 
                            <a href="${env.BUILD_URL}console">Console Output</a> | 
                            <a href="${env.BUILD_URL}testReport">Test Report</a>
                        </p>
                        
                        <p style="color: #666; font-size: 12px;">
                            <i>Automated email from Jenkins CI/CD Pipeline</i>
                        </p>
                    </body>
                    </html>
                """,
                to: "${env.GIT_AUTHOR_EMAIL}",
                mimeType: 'text/html'
            )
            
            echo "Email sent to: ${env.GIT_AUTHOR_EMAIL}"
        }
        
        success {
            echo 'Build succeeded!'
        }
        
        failure {
            echo 'Build failed!'
        }
    }
}
