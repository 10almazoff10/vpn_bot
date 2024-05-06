#!/usr/bin/env groovy
// Jenkinsfile (Declarative Pipeline)
pipeline {
  agent any
  stages {
    stage('Build') {
      steps {

        echo 'Create build archive'
        sh 'chmod +x build.sh'
        sh './build.sh'
        sh 'ssh vpn-bot rm -f /root/vpnbot-test/vpn-bot-develop'
        sh 'scp ./VPN_by_Prokin/dist/vpn-bot-develop vpn-bot:/root/vpnbot-test/'
        
      }
    }
    stage('Deploy'){
      steps {
        echo 'Send files to server'
        sh 'ssh vpn-bot systemctl restart vpn-bot-test'

      }
    }
  }
}
