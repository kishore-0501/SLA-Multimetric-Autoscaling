pipeline {

    agent {
        kubernetes {

            defaultContainer 'tools'

            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: tools
    image: amazon/aws-cli:2.30.1
    command:
    - cat
    tty: true

  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
    tty: true

  - name: docker
    image: docker:27-cli
    command:
    - cat
    tty: true
'''
        }
    }

    environment {
        AWS_REGION = "eu-west-1"
        ECR_REGISTRY = "562460196113.dkr.ecr.eu-west-1.amazonaws.com"
        IMAGE_NAME = "gateway"
        TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Detect Changes') {
            steps {
                script {

                    def changes = sh(
                        script: "git diff HEAD~1 HEAD --name-only || true",
                        returnStdout: true
                    ).trim()

                    echo changes

                    env.BUILD_APP = changes.contains("sla-gateway/") ? "true" : "false"
                    env.BUILD_K8S = changes.contains("k8s/") ? "true" : "false"

                    echo "BUILD_APP=${env.BUILD_APP}"
                    echo "BUILD_K8S=${env.BUILD_K8S}"
                }
            }
        }

        stage('Login to ECR') {
            when {
                expression { env.BUILD_APP == "true" }
            }

            steps {

                container('tools') {

                    sh '''
                    aws ecr get-login-password \
                    --region $AWS_REGION
                    '''
                }
            }
        }

        stage('Build Docker Image') {

            when {
                expression { env.BUILD_APP == "true" }
            }

            steps {

                echo "Build Docker Image"

            }
        }

        stage('Push Docker Image') {

            when {
                expression { env.BUILD_APP == "true" }
            }

            steps {

                echo "Push Docker Image to Amazon ECR"

            }
        }

        stage('Deploy Gateway') {

            when {
                expression { env.BUILD_APP == "true" }
            }

            steps {

                container('kubectl') {

                    sh '''
                    kubectl rollout status deployment/sla-gateway -n sla-demo
                    '''
                }
            }
        }

        stage('Apply Kubernetes Manifests') {

            when {
                expression { env.BUILD_K8S == "true" }
            }

            steps {

                container('kubectl') {

                    sh '''
                    kubectl apply -f k8s
                    '''
                }
            }
        }

        stage('Verify') {

            steps {

                container('kubectl') {

                    sh '''
                    kubectl get pods -n sla-demo
                    kubectl get svc -n sla-demo
                    '''
                }
            }
        }

    }

    post {

        success {

            echo "SLA-Multimetric-Autoscaling deployment completed."

        }

        failure {

            echo "Pipeline failed."

        }

        always {

            cleanWs()

        }
    }

}