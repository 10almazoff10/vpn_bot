from botApp import config
import requests
import json
from botApp.logs.logger import Logger
from datetime import datetime

logger = Logger(__name__)
def get_all_api_keys():
    return json.loads(requests.get(f"{API_KEY}/access-keys/", verify=False).text)


def create_new_keys(telegram_id: str, servers_api: list):
    data = []
    for API_KEY in servers_api:
        response = json.loads(requests.post(f"{API_KEY[1]}/access-keys", verify=False).text)
        id = response["id"]
        accessUrl = response["accessUrl"]
        password = response["password"]
        server_port = response["port"]
        method = response["method"]
        ip = accessUrl.split("@")[1].split(":")[0]
        server_id = API_KEY[0]
        data.append([id, telegram_id, accessUrl, password, server_port, method, ip, server_id])
        requests.put(f"{API_KEY[1]}/access-keys/{id}/name", data={'name': f"{telegram_id}"}, verify=False)
    return data


def remove_key(id, API_KEY):
    try:
        logger.info("Удаление ключа {} {}".format(id, API_KEY))
        result = requests.delete(f"{API_KEY}/access-keys/{id}", verify=False, timeout=2).status_code
        logger.info(result)
        if result == 204:
            return True
        elif result == 404:
            logger.info("Ключа нет на сервере, удаляем из БД")
            return True
        else:
            return False
    except Exception as error:
        logger.info("Ошибка удаления с сервера \n" + str(error))
        return False


def remove_all_keys_on_server(API_KEY):
    response = json.loads(requests.get(f"{API_KEY}/access-keys/", verify=False).text)
    count = 0
    for i in response["accessKeys"]:
        count += 1
        id = i["id"]
        try:
            remove_key(id, API_KEY)
        except Exception as error:
            logger.info(f"Ошибка удаления ключа {id}\n{error}")
    return count


def get_stat(API_KEY):
    """
    Получение статистики по ключам с сервера
    Returns:
    Возвращает json ответ по всем ключам сервера
    """
    return json.loads(requests.get(f"{API_KEY}/metrics/transfer", verify=False).text)

#list_data = json.loads(requests.get(f"{API_KEY}/metrics/transfer", verify=False).text)["bytesTransferredByUserId"]
