import yaml

with open('./config.yaml', 'r') as file:
    cfg_file = yaml.safe_load(file)

PRICE_PER_MOUNTH = cfg_file["price"]

API_KEY = cfg_file["telegram"]["api"]
ADMIN_ID = cfg_file["telegram"]["admin_id"]

PROVIDER_TOKEN = cfg_file["providers"]["yookassa"]

database = cfg_file["database"]

DB_NAME = database["base_name"]
DB_USER = database["user"]
DB_PASS = database["pass"]
DB_HOST = database["host"]
DB_PORT = database["port"]

#Параметры соли
app = cfg_file["app"]
SALT = app["salt"]
API_HOST = app["api_host"]

LOGS_DIR = cfg_file["logs"]["dir"]