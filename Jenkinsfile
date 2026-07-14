pipeline {
    agent any

    environment {
        DOCKER_IMAGE       = "flask-app"
        DOCKER_TAG         = "${BUILD_NUMBER}"
        NEXUS_URL          = "nexus:8082"                      // docker-hosted repo (container name, not localhost)
        NEXUS_REPO         = "docker-hosted"
        NEXUS_PYPI_URL     = "http://nexus:8081/repository/pypi-hosted/"
        SONARQUBE_ENV      = "SonarQubeServer"                 // must match name configured in Manage Jenkins > System
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/yourusername/flask-app-pipeline.git',
                    credentialsId: 'github-creds'
            }
        }

        stage('Setup Python Env & Install Deps') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest --junitxml=report.xml
                '''
            }
            post {
                always {
                    junit 'report.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    sh '''
                        . venv/bin/activate
                        pip install pysonar-scanner || true
                        sonar-scanner \
                          -Dsonar.projectKey=flask-app \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=$SONAR_HOST_URL \
                          -Dsonar.login=$SONAR_AUTH_TOKEN
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Artifact') {
            steps {
                sh '''
                    . venv/bin/activate
                    python setup.py sdist bdist_wheel
                '''
            }
        }

        stage('Push Artifact to Nexus') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'nexus-creds',
                                 usernameVariable: 'NEXUS_USER',
                                 passwordVariable: 'NEXUS_PASS')]) {
                    sh '''
                        . venv/bin/activate
                        pip install twine
                        twine upload --repository-url $NEXUS_PYPI_URL \
                          -u $NEXUS_USER -p $NEXUS_PASS dist/*
                    '''
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
            }
        }

        stage('Push Docker Image to Nexus') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'nexus-creds',
                                 usernameVariable: 'NEXUS_USER',
                                 passwordVariable: 'NEXUS_PASS')]) {
                    sh '''
                        echo $NEXUS_PASS | docker login ${NEXUS_URL} -u $NEXUS_USER --password-stdin
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${NEXUS_URL}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${NEXUS_URL}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    '''
                }
            }
        }

        stage('Deploy with Ansible') {
            steps {
                sh '''
                    ansible-playbook -i ansible/inventory.ini ansible/deploy.yml \
                      --extra-vars "image_tag=${DOCKER_TAG} registry=${NEXUS_URL} image_name=${DOCKER_IMAGE}"
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully! Flask app deployed."
        }
        failure {
            echo "Pipeline failed. Check the console output above for the failing stage."
        }
    }
}