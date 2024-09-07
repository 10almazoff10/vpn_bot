from datetime import datetime, timedelta
from botApp import config
import bz2
import os

LOGS_DIR = config.LOGS_DIR
# Логгер для отладки

class Logger:
    def __init__(self, className):
        """
        Класс логгера, принимает __name__ для указании места выпаолнения лога
        Args:
            className: __name__
        """
        self.className = className

    def info(self, logs, level="MAIN"):
        dt = datetime.now()
        date = dt.strftime("%Y-%m-%d")

        if level == "MAIN":

            logFile = f"{LOGS_DIR}/telebot-{date}.txt"
            try:
                with open(logFile, "a", encoding='utf-8') as file:
                    dt = datetime.now()
                    date = dt.strftime("%Y-%m-%d %H:%M:%S")
                    logs = f"{date} - [{self.className}] - {logs}\n"
                    file.write(logs)
            except Exception as error:
                print(error)

        elif level == "DEBUG":

            logFile = f"{LOGS_DIR}/debug/debug-{date}.txt"
            try:
                with open(logFile, "a", encoding='utf-8') as file:
                    dt = datetime.now()
                    date = dt.strftime("%Y-%m-%d %H:%M:%S")
                    logs = f"{date} - [{self.className}]  {logs}\n"
                    file.write(logs)
            except Exception as error:
                print(error)


def logger(logs, level="MAIN"):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")

    if level == "MAIN":

        logFile = f"{LOGS_DIR}/telebot-{date}.txt"
        try:
            with open(logFile, "a", encoding='utf-8') as file:
                    dt = datetime.now()
                    date = dt.strftime("%Y-%m-%d %H:%M:%S")
                    logs = f"{date} - {logs}\n"
                    file.write(logs)
        except Exception as error:
            print(error)

    elif level == "DEBUG":

        logFile = f"{LOGS_DIR}/debug/debug-{date}.txt"
        try:
            with open(logFile, "a", encoding='utf-8') as file:
                dt = datetime.now()
                date = dt.strftime("%Y-%m-%d %H:%M:%S")
                logs = f"{date} - {logs}\n"
                file.write(logs)
        except Exception as error:
            print(error)


def get_file_log():
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d")
    logFile = f"{LOGS_DIR}/telebot-{date}.txt"
    return open(logFile, "rb")

    