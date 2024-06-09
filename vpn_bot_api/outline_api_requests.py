import config
import requests
import json
from datetime import datetime


#API_KEY = config.OUTLINE_API_KEY


def get_all_api_keys():
    return json.loads(requests.get(f"{API_KEY}/access-keys/", verify=False).text)


def get_count_active_keys(API_KEY):
    return json.loads(requests.get(f"{API_KEY}/access-keys/", verify=False).text)

def create_new_key(telegram_id:str, API_KEY:str):
    data = []
    response = json.loads(requests.post(f"{API_KEY}/access-keys", verify=False).text)

    id = response["id"]
    accessUrl = response["accessUrl"]
    user_password = response["password"]
    port = response["port"]
    method = response["method"]

    data.append([id, accessUrl, user_password, port, method, telegram_id])

    requests.put(f"{API_KEY}/access-keys/{id}/name", data={'name':f"{telegram_id}"}, verify=False)

    return data

def remove_key(id):
    requests.delete(f"{API_KEY}/access-keys/{id}", verify=False)

def get_stat():
    return json.loads(requests.get(f"{API_KEY}/metrics/transfer", verify=False).text)

#list_data = json.loads(requests.get(f"{API_KEY}/metrics/transfer", verify=False).text)["bytesTransferredByUserId"]
