#!/bin/bash

source ~/.env/bin/activate

cd VPN_by_Prokin
pip install -r requirements.txt

rm -rf ./build
rm -rf ./dist

pyinstaller --paths . \
            --name vpn-bot-develop \
            --onefile main.py

DATE=`date +"%Y-%m-%d_%H:%M:%S"`
cp dist/vpn-bot-develop /builds/develop/vpn-bot-develop-${DATE}
cd ..

### Building API
cd vpn_bot_api

rm -rf ./build
rm -rf ./dist

pyinstaller --paths . \
            --name vpn-bot-api \
            --onefile vpn_bot_api.py

DATE=`date +"%Y-%m-%d_%H:%M:%S"`
cp dist/vpn-bot-api /builds/develop/vpn-bot-api-${DATE}
cd ..

