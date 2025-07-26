pipeline {

	agent any
	
	stages {
		stage('deletion_previous_image') {
		
			steps {
				echo 'deleting previous image'
				sh 'sudo docker rmi uno:latest'
				echo 'deletion complete'
			
				}
			}
	
		stage('build') {
		
			steps {
				echo 'building new image'
				sh 'sudo docker build -t uno:latest .'
				echo 'building complete'
				
				}
			}
				
		stage('deploy') {
		
			steps {
				echo 'deploying new image'
				sh 'sudo docker run -d uno:latest'
				echo 'deployment complete'
				
				}
			}
		
			}
		}

	

