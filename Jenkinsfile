pipeline {

    agent {
        kubernetes {

            yaml '''
apiVersion: v1
kind: Pod

spec:

  containers:

  - name: docker
    image: docker:27-dind

    securityContext:
      privileged: true

    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""

    args:
    - "--host=tcp://0.0.0.0:2375"
    - "--host=unix:///var/run/docker.sock"


    volumeMounts:
    - name: docker-storage
      mountPath: /var/lib/docker



  - name: shell
    image: 562460196113.dkr.ecr.eu-west-1.amazonaws.com/sla-jenkins-agent:latest


    command:
    - sleep

    args:
    - 999999


    env:

    - name: DOCKER_HOST
      value: tcp://localhost:2375



  volumes:

  - name: docker-storage
    emptyDir: {}

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



        stage('Check Environment') {

            steps {

                container('shell') {

                    sh '''
                    echo "Waiting for Docker daemon..."

                    sleep 15

                    echo "Docker version"
                    docker version


                    echo "Docker info"
                    docker info


                    echo "AWS version"
                    aws --version


                    echo "Kubectl version"
                    kubectl version --client

                    '''

                }

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

                container('shell') {

                    sh '''

                    aws ecr get-login-password \
                    --region $AWS_REGION | \
                    docker login \
                    --username AWS \
                    --password-stdin $ECR_REGISTRY

                    '''

                }

            }

        }



        stage('Build and Push Image') {

            when {

                expression {
                    env.BUILD_APP == "true"
                }

            }


            steps {

                container('shell') {


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


                kubectl rollout status deployment/sla-gateway \
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

                echo "Pods:"
                kubectl get pods -n sla-demo


                echo "Services:"
                kubectl get svc -n sla-demo

                '''

            }

        }

    }



    post {

        success {

            echo "SLA Multi-Metric Autoscaling CI/CD completed successfully."

        }


        failure {

            echo "Pipeline failed. Check Jenkins logs."

        }

    }

}