pipeline {
    agent any
    options {
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    stages {
        stage('Umgebung') {
            steps {
                // Der Agent braucht Python 3.10+; die Pakete bleiben im Workspace.
                sh 'python3 -m venv .venv'
                sh '.venv/bin/python -m pip install -r requirements-dev.txt'
                sh 'rm -rf reports/unit reports/acceptance reports/demo'
            }
        }
        stage('Regressionstests') {
            steps {
                sh '.venv/bin/python -m xmlrunner discover -s tests -o reports/unit -v'
            }
            post {
                always { junit 'reports/unit/*.xml' }
            }
        }
        stage('Abnahmetests') {
            steps {
                sh '.venv/bin/python -m behave --junit --junit-directory reports/acceptance'
            }
            post {
                always { junit 'reports/acceptance/*.xml' }
            }
        }
        stage('Demo') {
            steps {
                sh '.venv/bin/python -m vehicle_data_quality demo --output reports/demo'
                sh '.venv/bin/python -m vehicle_data_quality.ai_review --output reports/demo/ai-review --response examples/ai-response.json'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*.xml,reports/demo/**/*.json,reports/demo/**/*.xlsx,reports/demo/**/*.csv', allowEmptyArchive: true
        }
    }
}
