pipeline {

	agent any
	
	stages {
		stage('deletion_previous_image') {
		
			steps {
				echo 'deleting previous image'
				sh 'docker rm -f uno'
				sh ' docker rmi uno:latest'
				echo 'deletion complete'
			
				}
			}
	
		stage('build') {
		
			steps {
				echo 'building new image'
				sh 'docker build -t uno:latest .'
				echo 'building complete'
				
				}
			}
				
		stage('deploy') {
		
			steps {
				echo 'deploying new image'
				sh 'docker run -dit -name uno uno:latest'
				echo 'deployment complete'
				
				}
			}
		
			}
		}

	

