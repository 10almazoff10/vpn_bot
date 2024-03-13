from datetime import datetime
from VPN_by_Prokin.app import config

LOGS_DIR = config.LOGS_DIR
# Логгер для отладки
def logger(logs):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")
    logFile = f"{LOGS_DIR}/telebot-{date}.txt"
    try:
        with open(logFile, "a") as file:
                dt = datetime.now()
                date = dt.strftime("%Y-%m-%d %H:%M:%S")
                logs = f"{date} - {logs}\n"
                file.write(logs)
    except:
        with open(logFile, "w") as file:
            file.write("Developed by Prokin.O\nSoft-Logic. 2024\n")

def get_file_log():
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")
    logFile = f"{LOGS_DIR}/telebot-{date}.txt"
    return open(logFile, "rb")