pipeline {
    agent any
    triggers {
        // Check for drift hourly
        cron('H * * * *')
        // You can uncomment githubPush() if you configure GitHub webhooks in Jenkins
        // githubPush()
    }
    environment {
        GITHUB_REPO_URL = 'https://github.com/Preet018/Log-Anomaly-Detection.git'
        DOCKER_USERNAME = 'preet1018'
        IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()

        ANSIBLE_INVENTORY = "Ansible/hosts.ini"
        ANSIBLE_PLAYBOOK  = "Ansible/deploy.yml"
    }
    stages {
        // ==========================================
        // STAGE 1: CONTINUOUS INTEGRATION (CI)
        // ==========================================
        stage('Checkout') {
            when { not { triggeredBy 'TimerTrigger' } }
            steps {
                script {
                    git branch: 'main', url: "${GITHUB_REPO_URL}"
                }
            }
        }
        stage('Linting') {
            when { not { triggeredBy 'TimerTrigger' } }
            steps {
                script {
                    sh 'pip install flake8'
                    sh 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics'
                }
            }
        }
        stage('Unit Tests') {
            when { not { triggeredBy 'TimerTrigger' } }
            steps {
                script {
                    sh 'pip install pytest'
                    sh 'pytest frontend/ prediction_service/ drift_service/ || true'
                }
            }
        }
        stage('Build Docker Images') {
            when { not { triggeredBy 'TimerTrigger' } }
            steps {
                script {
                    // Build images with version tag
                    sh "docker build -t ${DOCKER_USERNAME}/frontend:${IMAGE_TAG} -f frontend/Dockerfile ./frontend"
                    sh "docker build -t ${DOCKER_USERNAME}/prediction-service:${IMAGE_TAG} -f prediction_service/Dockerfile ."
                    sh "docker build -t ${DOCKER_USERNAME}/drift-service:${IMAGE_TAG} -f drift_service/Dockerfile ./drift_service"
                    sh "docker build -t ${DOCKER_USERNAME}/ml-pipeline:${IMAGE_TAG} -f ml_pipeline/Dockerfile ./ml_pipeline"
                    sh "docker build -t ${DOCKER_USERNAME}/mongo-service:${IMAGE_TAG} -f data_storage/Dockerfile ./data_storage"

                    // Tag as latest
                    sh "docker tag ${DOCKER_USERNAME}/frontend:${IMAGE_TAG} ${DOCKER_USERNAME}/frontend:latest"
                    sh "docker tag ${DOCKER_USERNAME}/prediction-service:${IMAGE_TAG} ${DOCKER_USERNAME}/prediction-service:latest"
                    sh "docker tag ${DOCKER_USERNAME}/drift-service:${IMAGE_TAG} ${DOCKER_USERNAME}/drift-service:latest"
                    sh "docker tag ${DOCKER_USERNAME}/ml-pipeline:${IMAGE_TAG} ${DOCKER_USERNAME}/ml-pipeline:latest"
                    sh "docker tag ${DOCKER_USERNAME}/mongo-service:${IMAGE_TAG} ${DOCKER_USERNAME}/mongo-service:latest"
                }
            }
        }
        stage('Push Docker Images') {
            when { not { triggeredBy 'TimerTrigger' } }
            steps {
                script {
                    docker.withRegistry('', 'DockerHubCred') {
                        // Push versioned tags
                        sh "docker push ${DOCKER_USERNAME}/frontend:${IMAGE_TAG}"
                        sh "docker push ${DOCKER_USERNAME}/prediction-service:${IMAGE_TAG}"
                        sh "docker push ${DOCKER_USERNAME}/drift-service:${IMAGE_TAG}"
                        sh "docker push ${DOCKER_USERNAME}/ml-pipeline:${IMAGE_TAG}"
                        sh "docker push ${DOCKER_USERNAME}/mongo-service:${IMAGE_TAG}"

                        // Push latest tags
                        sh "docker push ${DOCKER_USERNAME}/frontend:latest"
                        sh "docker push ${DOCKER_USERNAME}/prediction-service:latest"
                        sh "docker push ${DOCKER_USERNAME}/drift-service:latest"
                        sh "docker push ${DOCKER_USERNAME}/ml-pipeline:latest"
                        sh "docker push ${DOCKER_USERNAME}/mongo-service:latest"
                    }
                }
            }
        }
        stage('Load Images into Minikube') {
            when { not { triggeredBy 'TimerTrigger' } }
            steps {
                script {
                    sh """
                        minikube image load ${DOCKER_USERNAME}/frontend:latest || true
                        minikube image load ${DOCKER_USERNAME}/prediction-service:latest || true
                        minikube image load ${DOCKER_USERNAME}/drift-service:latest || true
                        minikube image load ${DOCKER_USERNAME}/ml-pipeline:latest || true
                        minikube image load ${DOCKER_USERNAME}/mongo-service:latest || true
                    """
                }
            }
        }

        // ==========================================
        // STAGE 2: CONTINUOUS DEPLOYMENT (CD)
        // ==========================================
        stage('Deploy with Ansible') {
            when { not { triggeredBy 'TimerTrigger' } }
            steps {
                script {
                    sh """
                    ansible-playbook -i ${ANSIBLE_INVENTORY} ${ANSIBLE_PLAYBOOK} \
                        -e frontend_tag=${IMAGE_TAG} \
                        -e prediction_tag=${IMAGE_TAG} \
                        -e drift_tag=${IMAGE_TAG} \
                        -e ml_pipeline_tag=${IMAGE_TAG}
                    """
                }
            }
        }

        // ==========================================
        // STAGE 3: CONTINUOUS TRAINING (CT)
        // ==========================================
        stage('Check For Drift (CT)') {
            when { triggeredBy 'TimerTrigger' }
            steps {
                script {
                    echo "Waking up to check Drift Service for model drift..."
                    // We use curl to ask the running Drift Service inside K8s because it has access to the live PVC data.
                    def driftStatus = sh(script: "curl -s http://localhost:30001/drift/status | grep '\"overall_drift\": true' >/dev/null && echo true || echo false", returnStdout: true).trim()
                    
                    if (driftStatus == 'true') {
                        env.DRIFT_DETECTED = 'true'
                        echo "Drift detected! Proceeding to retrain..."
                    } else {
                        env.DRIFT_DETECTED = 'false'
                        echo "No drift detected. Skipping retraining."
                    }
                }
            }
        }
        stage('Launch Training Job (CT)') {
            when { 
                allOf {
                    triggeredBy 'TimerTrigger'
                    expression { return env.DRIFT_DETECTED == 'true' }
                }
            }
            steps {
                script {
                    echo "Launching ML Training Job..."
                    sh "sed 's/{{ ml_pipeline_tag | default(.latest.) }}/latest/g' Kubernetes/ml-pipeline-job.yaml.j2 > /tmp/ml-pipeline-job.yaml"
                    sh "kubectl apply -f /tmp/ml-pipeline-job.yaml"
                }
            }
        }
        stage('Wait for Model Update (CT)') {
            when { 
                allOf {
                    triggeredBy 'TimerTrigger'
                    expression { return env.DRIFT_DETECTED == 'true' }
                }
            }
            steps {
                script {
                    echo "Waiting for the ML Job to complete training and save the model..."
                    sh "kubectl wait --for=condition=complete job/ml-training-job-latest -n log-anomaly --timeout=600s"
                }
            }
        }
        stage('Restart Prediction Pods (CT)') {
            when { 
                allOf {
                    triggeredBy 'TimerTrigger'
                    expression { return env.DRIFT_DETECTED == 'true' }
                }
            }
            steps {
                script {
                    echo "Restarting Prediction Service to load the new model..."
                    sh "kubectl rollout restart deployment/prediction-deployment -n log-anomaly"
                    sh "kubectl rollout status deployment/prediction-deployment -n log-anomaly --timeout=180s"
                }
            }
        }
        stage('Clean Up Job (CT)') {
            when { 
                allOf {
                    triggeredBy 'TimerTrigger'
                    expression { return env.DRIFT_DETECTED == 'true' }
                }
            }
            steps {
                script {
                    echo "Cleaning up the completed training job..."
                    sh "kubectl delete job/ml-training-job-latest -n log-anomaly"
                }
            }
        }
    }
    post {
        success {
            echo 'Pipeline successfully completed!'
            emailext(
                to: 'chandrakarpreet.1100@gmail.com',
                subject: 'Build Success: Log Anomaly Detection',
                body: """The Jenkins pipeline for the Log Anomaly Detection project has completed successfully.\n\nJob: ${env.JOB_NAME}\nBuild Number: ${env.BUILD_NUMBER}\nBuild URL: ${env.BUILD_URL}"""
            )
        }
        failure {
            echo 'Pipeline failed!'
            emailext(
                to: 'chandrakarpreet.1100@gmail.com',
                subject: 'Build Failure: Log Anomaly Detection',
                body: """The Jenkins pipeline for the Log Anomaly Detection project has failed.\n\nJob: ${env.JOB_NAME}\nBuild Number: ${env.BUILD_NUMBER}\nBuild URL: ${env.BUILD_URL}"""
            )
        }
    }
}
