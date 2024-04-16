#!/usr/bin/env groovy
// Jenkinsfile (Declarative Pipeline)
pipeline {
  agent any
  stages {
    stage('Build') {
      steps {

        echo 'Create build archive'
        sh 'ssh vpn-bot cd vpnbot-test/vpn_bot && git pull'
        
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