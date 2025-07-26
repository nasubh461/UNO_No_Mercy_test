pipeline {
    agent any

    stages {
        stage('deletion_previous_image') {
            steps {
                echo 'Checking and deleting previous container and image'
                // Remove container if it exists
                sh '''
                    if docker ps -a --format '{{.Names}}' | grep -qw uno; then
                        docker rm -f uno
                    else
                        echo 'Container "uno" does not exist.'
                    fi
                '''
                // Remove image if it exists
                sh '''
                    if docker images --format '{{.Repository}}:{{.Tag}}' | grep -qw 'uno:latest'; then
                        docker rmi uno:latest
                    else
                        echo 'Image "uno:latest" does not exist.'
                    fi
                '''
                echo 'Deletion step complete'
            }
        }

        stage('build') {
            steps {
                echo 'Building new image if Dockerfile exists'
                sh '''
                    if [ -f Dockerfile ]; then
                        docker build -t uno:latest .
                    else
                        echo "Dockerfile not found! Skipping build."
                        exit 1
                    fi
                '''
                echo 'Build step complete'
            }
        }

        stage('deploy') {
            steps {
                echo 'Deploying new image if build succeeded'
                sh '''
                    # Only run container if image exists
                    if docker images --format '{{.Repository}}:{{.Tag}}' | grep -qw 'uno:latest'; then
                        docker run -dit --name uno uno:latest
                    else
                        echo 'Image "uno:latest" not found, skipping deployment.'
                        exit 1
                    fi
                '''
                echo 'Deployment step complete'
            }
        }
    }
}
