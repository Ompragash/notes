pipeline {
    agent any

    stages {
        stage('Clone Git Repo') {
            steps {
                script {
                    // Clone the repository where your file exists
                    git url: 'https://github.com/Ompragash/notes.git', branch: 'main'
                }
            }
        }

        stage('Read Trusted File') {
            steps {
                script {
                    // Read the trusted file (settings.json in this case) from the cloned repository
                    def configFileContent = readTrusted 'settings.json'
                    echo "Contents of settings.json: \n${configFileContent}"
                }
            }
        }

        stage('Run Tasks Based on File') {
            steps {
                script {
                    // Process the data from the settings.json file
                    echo "Processing the data from the trusted settings.json file..."
                    // Perform tasks based on the file content
                }
            }
        }
    }
}
