import sys

from flask import Flask, jsonify, Response, request
import base64
import re
import dbcon
import outline_api_requests
from logs.logger import logger
import config

API_PORT = config.API_PORT

#962fd229312b115fe5fb7b6d0b343a58
SALT = config.SALT

app = Flask(__name__)


def check_user_state(telegram_id):
    user_balance = dbcon.get_user_balance(telegram_id)
    if user_balance > -5:
        return True
    elif user_balance <= -5:
        return False

def get_key_for_user(telegram_id):
    logger("Выдаем пользователю случайный ключ")
    try:
        key_data = dbcon.get_random_user_key(telegram_id)
        logger(f"Ключ получен: {key_data}")
        return key_data
    except Exception as error:
        logger("Ошибка получения ключа из БД\n" + str(error))

def extract_data(key_url):
    # Регулярное выражение для извлечения данных из строке
    pattern = r'ss://(.+):(\d+)/?(\?.*)'
    match = re.match(pattern, key_url)

    if match:
        # Извлечение хоста и порта
        host_port = match.group(1).split('@')
        server = host_port[0]
        port = int(host_port[1].split(':')[0])

        # Извлечение decode_data
        decoded_text = str(base64.b64decode(match.group(1).split('ss://')[1]))

        # Извлечение password и method из decode_data
        data_parts = decoded_text.split(':')
        if len(data_parts) >= 2:
            password = data_parts[1]
            method = data_parts[0]

        return {
            'server': server,
            'port': port,
            'decoded_text': decoded_text,
            'password': password,
            'method': method
        }
    else:
        return None

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
        logger(
            "Подключается пользователь {}".format(
                telegram_id))

        dbcon.write_stat(
            telegram_id=telegram_id,
            ip=ip,
            stat_name="connect")

        user_state = check_user_state(
            telegram_id)

        if user_state:
            logger("Пользователь не заблокирован, выдаем ключ...")

            key_data = get_key_for_user(telegram_id)

            logger("Ключ отправлен...")
            return jsonify({
                "server": key_data[0],
                "server_port": key_data[1],
                "password": key_data[2],
                "method": key_data[3]})

        elif user_state == False:
            return jsonify({"error":
                                {"message": "Key is blocked"}})
    else:
        return Response("Вы не авторизованы!", 401)

@app.route('/conf/<md5_hash>')
def handle_conf(md5_hash):
    try:
        ip = request.headers["X-Forwarded-For"]
    except Exception as error:
        logger(error)
        ip = '0.0.0.0'

    logger(f"Запрос от - {ip}")
    logger(f"Request: {md5_hash}")
    return check_user(md5_hash, ip)



def run_api():
    app.run(host="127.0.0.1", port=API_PORT, debug=False)

if __name__ == "__main__":
    run_api()
