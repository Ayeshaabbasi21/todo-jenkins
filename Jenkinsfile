pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'selenium-todo-tests'
        APP_PORT = '5000'
        MONGODB_PORT = '27017'
        GITHUB_CREDENTIALS = 'github-pat' // Jenkins credentials ID for GitHub PAT
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '========== Checking out code from GitHub =========='
                script {
                    // Ensure permissions are correct to avoid index.lock errors
                    sh 'sudo chown -R jenkins:jenkins $WORKSPACE || true'
                    sh 'chmod -R u+rwX $WORKSPACE || true'

                    // Checkout using credentials
                    checkout([$class: 'GitSCM',
                        branches: [[name: '*/main']],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        userRemoteConfigs: [[
                            url: 'https://github.com/Ayeshaabbasi21/todo-jenkins.git',
                            credentialsId: "${GITHUB_CREDENTIALS}"
                        ]]
                    ])
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '========== Building Docker test image =========='
                script {
                    docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                }
            }
        }
        
        stage('Setup Application') {
            steps {
                echo '========== Setting up Todo application =========='
                script {
                    sh '''
                        # Kill any existing processes
                        kill -9 $(lsof -t -i:5000) 2>/dev/null || true
                        kill -9 $(lsof -t -i:27017) 2>/dev/null || true
                        
                        # Install npm dependencies
                        npm install
                        
                        # Start MongoDB (assuming installed)
                        sudo systemctl start mongod || mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log
                        
                        # Wait for MongoDB
                        sleep 5
                        
                        # Start app in background
                        nohup npm start > app.log 2>&1 &
                        echo $! > app.pid
                        
                        # Wait for app to be ready
                        for i in {1..30}; do
                            curl -f http://localhost:5000 && exit 0 || echo "Attempt $i: App not ready"
                            sleep 2
                        done
                        echo "ERROR: App failed to start"
                        cat app.log
                        exit 1
                    '''
                }
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                echo '========== Running Selenium Tests =========='
                script {
                    sh """
                        docker run --rm \
                            --network=host \
                            -v \$(pwd)/test-results:/app/test-results \
                            ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                            pytest selenium-tests/test_todo_app.py \
                                -v -s --tb=short \
                                --junitxml=/app/test-results/test-results.xml
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo '========== Cleanup =========='
            script {
                sh '''
                    if [ -f app.pid ]; then
                        kill -9 $(cat app.pid) 2>/dev/null || true
                        rm -f app.pid
                    fi
                    kill -9 $(lsof -t -i:5000) 2>/dev/null || true
                '''
                
                junit allowEmptyResults: true, testResults: 'test-results/test-results.xml'
                archiveArtifacts artifacts: 'app.log', allowEmptyArchive: true
                
                // Clean old Docker images
                sh """
                    docker images ${DOCKER_IMAGE} --format "{{.Tag}}" | \
                    sort -rn | tail -n +4 | \
                    xargs -I {} docker rmi ${DOCKER_IMAGE}:{} 2>/dev/null || true
                """
            }
            
            // Email notification
            emailext (
                subject: "Jenkins Build ${currentBuild.currentResult}: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                    <h2>Build ${currentBuild.currentResult}</h2>
                    <p><b>Job:</b> ${env.JOB_NAME}</p>
                    <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                    <p><b>Build URL:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                    <p><b>Test Results:</b> <a href="${env.BUILD_URL}testReport/">${env.BUILD_URL}testReport/</a></p>
                    
                    <h3>Build Log (Last 50 lines):</h3>
                    <pre>${currentBuild.rawBuild.getLog(50).join('\n')}</pre>
                """,
                mimeType: 'text/html',
                to: '${DEFAULT_RECIPIENTS}',
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        success {
            echo '✅ ========== ALL TESTS PASSED! =========='
        }
        failure {
            echo '❌ ========== TESTS FAILED! =========='
            sh 'cat app.log || echo "No application log available"'
        }
    }
}
