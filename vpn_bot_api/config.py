import yaml

with open('../config.yaml', 'r') as file:
    cfg_file = yaml.safe_load(file)

# Параметры БД
database = cfg_file["database"]
DB_NAME = database["base_name"]
DB_USER = database["user"]
DB_PASS = database["pass"]
DB_HOST = database["host"]
DB_PORT = database["port"]

#Параметры API
api = cfg_file["api"]
API_PORT = api["port"]

#Параметры соли
app = cfg_file["app"]
SALT = app["salt"]

#Параметры логов
LOGS_DIR = cfg_file["logs"]["dir"]