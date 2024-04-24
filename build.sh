#!/bin/bash
cd VPN_by_Prokin

pyinstaller --paths . \
            --name vpn-bot-develop \
            --onefile main.py

DATE=`date +"%Y-%m-%d_%H:%M:%S"`
cp dist/vpn-bot-develop /builds/develop/vpn-bot-develop-${DATE}
cd ..
