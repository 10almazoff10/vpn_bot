from botApp import config
import requests
import json
from botApp.logs.logger import logger
from datetime import datetime


#API_KEY = config.OUTLINE_API_KEY


def get_all_api_keys():
    return json.loads(requests.get(f"{API_KEY}/access-keys/", verify=False).text)

def create_new_keys(telegram_id:str, servers_api:list):
    data = []
    for API_KEY in servers_api:
        response = json.loads(requests.post(f"{API_KEY[0]}/access-keys", verify=False).text)
        id = response["id"]
        accessUrl = response["accessUrl"]
        data.append([id, accessUrl])
        requests.put(f"{API_KEY[0]}/access-keys/{id}/name", data={'name':f"{telegram_id}"}, verify=False)
    return data

def remove_key(id):
    requests.delete(f"{API_KEY}/access-keys/{id}", verify=False)

def remove_all_keys_on_server(API_KEY):
    print(API_KEY)
    response = json.loads(requests.get(f"{API_KEY}/access-keys/", verify=False).text)
    count=0
    for i in response["accessKeys"]:
        count += 1
        id = i["id"]
        try:
            remove_key(id)
        except Exception as error:
            logger(f"Ошибка удаления ключа {id}\n{error}")
    return count
def get_stat():
    return json.loads(requests.get(f"{API_KEY}/metrics/transfer", verify=False).text)

#list_data = json.loads(requests.get(f"{API_KEY}/metrics/transfer", verify=False).text)["bytesTransferredByUserId"]
