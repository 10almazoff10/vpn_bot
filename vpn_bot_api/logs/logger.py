from datetime import datetime
import config

LOGS_DIR = config.LOGS_DIR
# Логгер для отладки
def logger(logs):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")
    logFile = f"{LOGS_DIR}/api/bot-api-{date}.log"
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
    logFile = f"{LOGS_DIR}/api/bot-api-{date}.log"
    return open(logFile, "rb")