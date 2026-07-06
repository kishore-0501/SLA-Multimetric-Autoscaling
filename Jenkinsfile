pipeline {

    agent {
        label 'windows'
    }

    environment {
        IMAGE_NAME = "sla-gateway"
        REGISTRY   = "kishore0501"
        TAG        = "${BUILD_NUMBER}"
        DOCKER_CREDS = credentials('dockerhub')
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/kishore-0501/SLA-Multimetric-Autoscaling'
            }
        }

        stage('Detect Changes') {
            steps {
                script {

                    def changes = bat(
                        script: '@git diff --name-only HEAD~1 HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Changed files:"
                    echo changes

                    env.BUILD_APP = changes.contains("sla-gateway/") ? "true" : "false"
                    env.BUILD_K8S = changes.contains("k8s/") ? "true" : "false"

                    echo "BUILD_APP = ${env.BUILD_APP}"
                    echo "BUILD_K8S = ${env.BUILD_K8S}"
                }
            }
        }

        stage('Docker Login') {
            when {
                expression { env.BUILD_APP == "true" }
            }
            steps {
                bat """
                docker login -u %DOCKER_CREDS_USR% -p %DOCKER_CREDS_PSW%
                """
            }
        }

        stage('Build Docker Image') {
            when {
                expression { env.BUILD_APP == "true" }
            }
            steps {
                dir('sla-gateway') {
                    bat """
                    docker build -t %REGISTRY%/%IMAGE_NAME%:%TAG% .
                    """
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { env.BUILD_APP == "true" }
            }
            steps {
                bat """
                docker push %REGISTRY%/%IMAGE_NAME%:%TAG%
                """
            }
        }

        stage('Deploy Gateway') {
            when {
                expression { env.BUILD_APP == "true" }
            }
            steps {
                bat """
                kubectl set image deployment/sla-gateway ^
                sla-gateway=%REGISTRY%/%IMAGE_NAME%:%TAG% ^
                -n sla-demo

                kubectl rollout status deployment/sla-gateway -n sla-demo
                """
            }
        }

        stage('Apply Kubernetes Manifests') {
            when {
                expression { env.BUILD_K8S == "true" }
            }
            steps {
                bat """
                kubectl apply -f k8s
                """
            }
        }

    }

    post {
        always {
            bat "docker logout"
        }

        success {
            echo "Pipeline completed successfully!"
        }

        failure {
            echo "Pipeline failed."
        }
    }
}