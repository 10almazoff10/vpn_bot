import yaml

with open('../VPN_by_Prokin/config.yaml', 'r') as file:
    cfg_file = yaml.safe_load(file)

database = cfg_file["database"]

DB_NAME = database["base_name"]
DB_USER = database["user"]
DB_PASS = database["pass"]
DB_HOST = database["host"]
DB_PORT = database["port"]

LOGS_DIR = cfg_file["logs"]["dir"]