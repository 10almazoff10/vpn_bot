import yaml

with open('./config.yaml', 'r') as file:
    cfg_file = yaml.safe_load(file)


API_KEY = cfg_file["telegram"]["api"]
ADMIN_ID = cfg_file["telegram"]["admin_id"]

#OUTLINE_API_KEY = cfg_file["outline"]["api"]
PROVIDER_TOKEN = cfg_file["providers"]["yookassa"]

database = cfg_file["database"]

DB_NAME = database["base_name"]
DB_USER = database["user"]
DB_PASS = database["pass"]
DB_HOST = database["host"]
DB_PORT = database["port"]

LOGS_DIR = cfg_file["logs"]["dir"]