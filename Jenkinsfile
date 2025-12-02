pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'selenium-todo-tests'
        APP_PORT = '5000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '========== Checking out code from GitHub =========='
                checkout scm
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
                        # Kill any existing process on port 5000
                        kill -9 $(lsof -t -i:5000) || true
                        
                        # Install npm dependencies
                        npm install
                        
                        # Start MongoDB (assuming it's running as service)
                        sudo systemctl start mongod || true
                        
                        # Start application in background
                        nohup npm start > app.log 2>&1 &
                        
                        # Wait for app to be ready
                        echo "Waiting for application to start..."
                        sleep 15
                        
                        # Verify app is running
                        curl -f http://localhost:5000 || (echo "App failed to start" && cat app.log && exit 1)
                        echo "Application is running!"
                    '''
                }
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                echo '========== Running Selenium Tests =========='
                script {
                    docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").inside("--network=host") {
                        sh '''
                            pytest selenium-tests/test_todo_app.py \
                                -v -s --tb=short \
                                --junitxml=test-results.xml
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo '========== Cleanup =========='
            script {
                // Stop the application
                sh 'kill -9 $(lsof -t -i:5000) || true'
                
                // Archive test results
                junit allowEmptyResults: true, testResults: 'test-results.xml'
                
                // Clean up Docker images (keep last 3 builds)
                sh """
                    docker images ${DOCKER_IMAGE} --format "{{.Tag}}" | sort -rn | tail -n +4 | xargs -I {} docker rmi ${DOCKER_IMAGE}:{} || true
                """
            }
        }
        success {
            echo '✅ ========== ALL TESTS PASSED! =========='
        }
        failure {
            echo '❌ ========== TESTS FAILED! =========='
            sh 'cat app.log || true'
        }
    }
}
```

---

### **Step 4: Update Your `.gitignore`**

Add these lines to your `.gitignore`:
```
# Python
__pycache__/
*.pyc
.pytest_cache/

# Test results
test-results.xml

# Logs
app.log
nohup.out

# Environment
.env
node_modules/

# AWS
*.pem