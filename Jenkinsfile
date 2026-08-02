pipeline {

    agent {
        label 'mac-agent'
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


        stage('Check Buildx') {
            steps {
                sh '''
                echo "Current user:"
                whoami

                echo "Docker Buildx:"
                docker buildx ls
                '''
            }
        }


        stage('Detect Changes') {
            steps {

                script {

                    def changes = sh(
                        script: "git diff --name-only HEAD~1 HEAD || true",
                        returnStdout: true
                    ).trim()

                    echo "Changed files:"
                    echo changes

                    env.BUILD_APP =
                    changes.contains("sla-gateway/") ? "true" : "false"

                    env.BUILD_K8S =
                    changes.contains("k8s/") ? "true" : "false"

                }
            }
        }


        // your remaining stages here

    }
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
                        script: "git diff --name-only HEAD~1 HEAD || true",
                        returnStdout: true
                    ).trim()


                    echo "Changed files:"
                    echo changes


                    env.BUILD_APP =
                    changes.contains("sla-gateway/") ? "true" : "false"


                    env.BUILD_K8S =
                    changes.contains("k8s/") ? "true" : "false"


                    echo "BUILD_APP=${env.BUILD_APP}"
                    echo "BUILD_K8S=${env.BUILD_K8S}"

                }

            }

        }



        stage('Login to ECR') {

            when {

                expression {

                    env.BUILD_APP == "true"

                }

            }


            steps {

                sh '''

                aws ecr get-login-password \
                --region $AWS_REGION | \
                docker login \
                --username AWS \
                --password-stdin $ECR_REGISTRY

                '''

            }

        }




        stage('Build and Push Docker Image') {

    when {
        expression { env.BUILD_APP == "true" }
    }

    steps {

        dir('sla-gateway') {

            sh '''
            docker buildx build \
              --platform linux/amd64 \
              -t $ECR_REGISTRY/$IMAGE_NAME:$TAG \
              --push .
            '''

        }

    }
}




        stage('Deploy Gateway') {


            when {

                expression {

                    env.BUILD_APP == "true"

                }

            }


            steps {


                sh '''

                kubectl set image deployment/sla-gateway \
                sla-gateway=$ECR_REGISTRY/$IMAGE_NAME:$TAG \
                -n sla-demo


                kubectl rollout status \
                deployment/sla-gateway \
                -n sla-demo

                '''

            }

        }




        stage('Apply Kubernetes Manifests') {


            when {

                expression {

                    env.BUILD_K8S == "true"

                }

            }


            steps {


                sh '''

                kubectl apply -f k8s

                '''

            }

        }

        


        stage('Verify Deployment') {


            steps {


                sh '''

                echo "Current Pods:"
                kubectl get pods -n sla-demo


                echo "Current Services:"
                kubectl get svc -n sla-demo

                '''

            }

        }


    }



    post {


        success {

            echo "SLA Multi-Metric Autoscaling deployment completed successfully."

        }


        failure {

            echo "Pipeline failed. Check logs."

        }

    }

}