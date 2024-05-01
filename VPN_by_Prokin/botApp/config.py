import yaml

with open('./config.yaml', 'r') as file:
    cfg_file = yaml.safe_load(file)


API_KEY = cfg_file["telegram"]["api"]
OUTLINE_API_KEY = cfg_file["outline"]["api"]

database = cfg_file["database"]

DB_NAME = database["base_name"]
DB_USER = database["user"]
DB_PASS = database["pass"]
DB_HOST = database["host"]
DB_PORT = database["port"]

LOGS_DIR = cfg_file["logs"]["dir"]