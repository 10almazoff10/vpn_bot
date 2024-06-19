from datetime import datetime, timedelta
from botApp import config
import bz2
import os

LOGS_DIR = config.LOGS_DIR
# Логгер для отладки
def logger(logs):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")
    logFile = f"{LOGS_DIR}/telebot-{date}.log"
    try:
        with open(logFile, "a", encoding='utf-8') as file:
                dt = datetime.now()
                date = dt.strftime("%Y-%m-%d %H:%M:%S")
                logs = f"{date} - {logs}\n"
                file.write(logs)
    except:
        with open(logFile, "w") as file:
            file.write("Developed by Prokin.O\n")

def get_file_log():
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")
    logFile = f"{LOGS_DIR}/telebot-{date}.log"
    return open(logFile, "rb")
    
def log_rotate():
    yesterday = datetime.strftime(datetime.utcnow() - timedelta(days=1), "%Y-%m-%d")
    logFile = f"{LOGS_DIR}/telebot-{yesterday}.log"
    with open(logFile, "rb") as file:
        data = file.read()
        try:
            with open(f"{logFile}.bz2", "wb") as arch:
                arch.write(bz2.compress(data, compresslevel=9))
        except Exception as error:
            print("Ошибка архивации логов")
            print(error)
    os.remove(logFile)
    