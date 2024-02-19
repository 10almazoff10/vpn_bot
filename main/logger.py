from datetime import datetime


LOGS_DIR = "/opt/logs"
# Логгер для отладки
def logger(logs):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")
    logFile = f"{LOGS_DIR}/telebot-{date}.log"
    try:
        with open(logFile, "a") as file:
                dt = datetime.now()
                date = dt.strftime("%Y-%m-%d %H:%M:%S")
                logs = f"{date} - {logs}\n"
                file.write(logs)
    except:
        with open(logFile, "w") as file:
            file.write("Developed by Prokin.O\nSoft-Logic. 2024\n")