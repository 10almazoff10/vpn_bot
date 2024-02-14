#!/bin/bash


timedatectl set-timezone Asia/Barnaul
python /src/backend.py &
python /src/main.py

