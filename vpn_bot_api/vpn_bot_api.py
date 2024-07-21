import sys

from flask import Flask, jsonify, Response, request
import base64
import dbcon
import outline_api_requests
from logs.logger import logger

#962fd229312b115fe5fb7b6d0b343a58
SALT = "ProkinVPN"

app = Flask(__name__)


def check_user_state(telegram_id):
    user_balance = dbcon.get_user_balance(telegram_id)
    if user_balance > -5:
        return True
    elif user_balance <= -5:
        return False


def get_api_key_for_great_server():
    logger("Получение списка серверов...")
    try:
        servers = dbcon.get_outline_server_list()
    except Exception as error:
        logger("Ошибка получения списка серверов\n" + error)
        sys.exit(1)
    count_servers = len(servers)
    logger(f"Доступно серверов: {count_servers}")
    data = []
    for server in servers:
        server_id = server[0]
        server_api_key = server[5]
        try:
            outline_responce = outline_api_requests.get_count_active_keys(server[5])
            count_keys = len(outline_responce['accessKeys'])
            data.append([count_keys, server_id, server_api_key])
        except Exception as error:
            logger(f"Ошибка подключения к серверу {server[0]}\n{error}")


    data.sort()
    great_server_id=data[0][1]
    logger(f"ID оптимального сервера: {great_server_id}")
    api_key_for_great_server=data[0][2]
    logger(api_key_for_great_server)
    return api_key_for_great_server
def get_key_for_user(telegram_id):
    logger("Определение оптимального сервера...")
    api_key_for_great_server = get_api_key_for_great_server()
    logger("Регистрация ключа для авторизации пользователя...")
    try:
        key = outline_api_requests.create_new_key(telegram_id, api_key_for_great_server) # id, accessUrl, user_password, port, method
        key_url = key[0][1]
        logger(f"Ключ получен: {key_url}")
        return key_url
    except Exception as error:
        logger(f"Ошибка получения ключа:\n{error}")
def check_user(md5_hash, ip):
    logger("Проверка авторизации...")
    try:
        hash_list = dbcon.get_user_hashes()
    except Exception as error:
        logger(f"Ошибка получения списка хешей из бд, выход.\n{error}")
        sys.exit(1)

    logger("Перебор авторизационных данных...")
    find_hash = False
    for hash in hash_list:
        if hash[0] == md5_hash:
            find_hash = True
        else:
            pass

    if find_hash:
        telegram_id = dbcon.get_telegram_id_user_from_hash(md5_hash)
        logger(f"Подключается пользователь {telegram_id}")
        dbcon.write_stat(telegram_id, ip, "connect")

        user_state = check_user_state(telegram_id)
        if user_state:
            logger("Пользователь не заблокирован, создание ключа...")
            key_url = get_key_for_user(telegram_id)

            server = key_url.split("@")[1].split(":")[0]
            server_port = key_url.split("@")[1].split(":")[1].split("/")[0]
            decode_data = str(base64.b64decode(key_url.split("@")[0].split("//")[1]))
            password = decode_data.split("'")[1].split(":")[1]
            method = decode_data.split("'")[1].split(":")[0]

            logger("Ключ отправлен...")
            return jsonify({"server": server, "server_port": server_port, "password": password, "method": method})
        elif user_state == False:
            return jsonify({"message": "Ключ заблокирован, пожалуйста пополните баланс"})
    else:
        return Response("Вы не авторизованы!", 401)

@app.route('/conf/<md5_hash>')
def handle_conf(md5_hash):
    logger(request.headers)
    ip = request.remote_addr
    logger(f"Запрос от - {ip}")
    logger(f"Request: {md5_hash}")
    return check_user(md5_hash, ip)



def check_number():
    # Получение данных из POST запроса
    return jsonify({"server": server, "server_port": server_port, "password": password, "method": method})

def run_api():
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    run_api()

# Примечание: Этот код требует установленного Flask и запустит локальный сервер.
# Пользователь может отправить POST запрос с JSON телом {"number": 1} на эндпоинт /check_number,
# чтобы получить ответ {"result": true}.
