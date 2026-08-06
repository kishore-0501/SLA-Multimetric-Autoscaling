pipeline {

    agent {
        kubernetes {

            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: shell
    image: busybox
    command:
    - sleep
    args:
    - 999999
'''

        }
    }


    stages {

        stage('Test') {

            steps {

                sh '''
                echo "Kubernetes Jenkins Agent Working"
                hostname
                '''

            }

        }

    }

}