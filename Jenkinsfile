#!/usr/bin/env groovy
// Jenkinsfile (Declarative Pipeline)
pipeline {
  agent any
  stages {
    stage('Build') {
      steps {

        echo 'Create build archive for project ${env.JOB_BASE_NAME}'
        sh 'chmod +x build.sh'
        sh './build.sh'
        sh 'ssh vpn-bot rm -f /root/${env.JOB_BASE_NAME}/vpn-bot-develop'
        sh 'scp ./VPN_by_Prokin/dist/vpn-bot-develop vpn-bot:/root/${env.JOB_BASE_NAME}/'
        
      }
    }
    stage('Deploy'){
      steps {
        echo 'Send files to server'
        sh 'ssh vpn-bot systemctl restart ${env.JOB_BASE_NAME}'

      }
    }
  }
}
