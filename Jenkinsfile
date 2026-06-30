pipeline {
    agent any

    environment {
        IMAGE_NAME = "sla-gateway"
        REGISTRY = "kishore0501"
        TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/kishore-0501/SLA-Multimetric-Autoscaling'
            }
        }

        stage('Detect Changes') {
            steps {
                script {

                    def changes = sh(script: "git diff --name-only HEAD~1 HEAD", returnStdout: true).trim()

                    echo "CHANGED FILES:"
                    echo changes

                    env.BUILD_APP = changes.contains("sla-gateway/")
                    env.BUILD_K8S = changes.contains("k8s/")
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { return env.BUILD_APP == "true" }
            }
            steps {
                sh """
                echo "Building Docker image from gateway.py..."
                docker build -t ${IMAGE_NAME}:${TAG} sla-gateway/
                """
            }
        }

        stage('Push Docker Image') {
            when {
                expression { return env.BUILD_APP == "true" }
            }
            steps {
                sh """
                docker tag ${IMAGE_NAME}:${TAG} ${REGISTRY}/${IMAGE_NAME}:${TAG}
                docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}
                """
            }
        }

        stage('Deploy Kubernetes') {
            when {
                expression { return env.BUILD_APP == "true" || env.BUILD_K8S == "true" }
            }
            steps {
                sh """
                echo "Deploying to Kubernetes..."
                kubectl apply -f k8s/
                """
            }
        }
    }
}