pipeline {
    agent{
        node {
            label "node1"
        }
    }

    stages {
        stage('check out') {
            steps {
              git url: 'https://github.com/SaiSrujan-Asara/py-jenk.git/',
              branch: 'main',
              credentialsId: 'github-repo1'
            }
        }
        stage('OSS SCANNER'){
            options {
              timeout(time: 59, unit: 'MINUTES') 
            }
            steps {
              sh(script: '''
                 python3 -m venv .venv
                 .venv/bin/pip install -r requirements.txt
                 python3 oss.py
                 ''', encoding: 'UTF-8')
            }
        }
        stage('SONAR QUBE STAGE'){
            options {
                timeout(time: 15, unit: 'MINUTES')
            }
            steps{
                sh '''
                 export SONARQUBE_URL="http://sonarqube:9000"
                 export PROJECT_KEY="py-app1"
                 export TOKEN="sqp_1cd0b29a20244ee3276817345ff57fce2ee0e5ec"
                 sonar-scanner -Dsonar.host.url=$SONARQUBE_URL -Dsonar.token=$TOKEN
                 echo "Sonar scanner scanned successfullt"
                 sleep 10
                 python3 sonar.py
                 '''
            }
        }
           stage('DOCKER IMAGE BUILD & PUSH') {
             environment {
                REGISTRY = 'nexus-docker-asarasaisrujan-dev.apps.rm1.0a51.p1.openshiftapps.com'
                IMAGE_NAME = 'my-app'
            }
        
            steps {
                withCredentials([usernamePassword(credentialsId: 'nexus',usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) 
                {
                    sh '''
                        set -eu
        
                        export DOCKER_CONFIG="$(mktemp -d)"
                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT
        
                        echo "Building image: ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
        
                        # Authenticate with Nexus
                        printf '%s' "$NEXUS_PASS" | docker --config "$DOCKER_CONFIG" login "$REGISTRY" \
                            --username "$NEXUS_USER" \
                            --password-stdin
        
                        # Build and push using BuildKit
                        buildctl \
                            --addr tcp://buildkitd:1234 \
                            build \
                            --frontend dockerfile.v0 \
                            --local context=. \
                            --local dockerfile=. \
                            --output "type=image,name=${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER},push=true" \
                            --import-cache "type=registry,ref=${REGISTRY}/${IMAGE_NAME}:buildcache-${BUILD_NUMBER}" \
                            --export-cache "type=registry,ref=${REGISTRY}/${IMAGE_NAME}:buildcache-${BUILD_NUMBER},mode=max"
        
                        echo "Image successfully built and pushed."
                    '''
                }
            }

        }
        stage('OPEN SHIFT LOGIN'){
            steps{
                withCredentials([string(credentialsId: 'openshift-k8s',variable: 'OPENSHIFT_TOKEN')]) 
                {
                    sh '''
                        oc login https://api.rm1.0a51.p1.openshiftapps.com:6443 \
                        --token="$OPENSHIFT_TOKEN"

                        oc project
                    '''
                }
            }
        }
    }
}
