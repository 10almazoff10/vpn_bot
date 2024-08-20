import sys

import psycopg2
from contextlib import closing
import config
from logs.logger import logger
from datetime import datetime

DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASS = config.DB_PASS
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT

logger(f"Инициализация подключения к БД...")
logger(f"{DB_HOST}, {DB_USER}, {DB_NAME}")

### Статусы оплаты
# 1	"Списание"
# 2	"Пополнение"
# 3	"Создание счета"
# 4	"Ежедневное списание за пользование VPN"
# 5	"Корректировка счета"
# 6 "Пополнение через форму оплаты"


#### Функции работы с БД ####
def execute_query(req, fetch_one=True):
    """
    Выполняет SQL-запрос к базе данных.

    Args:
        req (str): SQL-запрос.
        fetch_one (bool, optional): Если True, возвращает одну строку результата. Иначе возвращает все строки. Defaults to True.

    Returns:
        tuple or list: Результат выполнения запроса.
    """
    with closing(psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(req)
            return cursor.fetchone() if fetch_one else cursor.fetchall()


def insert_in_db(req):
    """
    Выполняет SQL-запрос на вставку данных в базу данных.

    Args:
        req (str): SQL-запрос на вставку.

    Returns:
        None
    """
    try:
        with closing(psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)) as conn:
            with conn.cursor() as cursor:
                cursor.execute(req)
                conn.commit()
    except Exception as error:
        print(f'Error inserting data: {error}')

def get_user_hashes():
    """
    Возвращает список пользовательских хешей
    Returns:

    """
    return execute_query("select user_key from users where user_key != '';", fetch_one=False)

def get_telegram_id_user_from_hash(hash):
    """
    Возвращает Telegram-id по хешу
    Args:
        hash:

    Returns:

    """
    return execute_query(f"select telegram_id from users where user_key = '{hash}'", fetch_one=True)[0]
def get_telegram_id_users():
    """
    Возвращает TG id всех зарегистрированных пользователей
    Returns:

    """
    return execute_query('select telegram_id from users;', False)

def get_user_balance(telegram_id):
    """
    Возвращает баланс пользователя по его TelegramID
    Args:
        telegram_id:

    Returns:

    """
    return execute_query(f"SELECT balance FROM users WHERE telegram_id = '{telegram_id}'")[0]


def get_outline_server_list():
    """
    Возвращает массив данных по серверам.
    Returns:

    """
    logger("Запрос в базу")
    try:
        list_servers = execute_query("""
                        select
                            id,
                            name,
                            comment,
                            country,
                            speed_in_kbytes,
                            connection_link,
                            creation_date,
                            standby_status
                        from
                            outline_servers
                        where standby_status = True;
                        """, fetch_one=False)
        for server in list_servers:
            logger(server)
        return list_servers

    except Exception as error:
        logger(error)
        sys.exit(0)



def register_user_key(data):  # id, accessUrl, user_password, port, method, telegram_id
    key_id = data[0]
    accessUrl = data[1]
    user_password = data[2]
    client_port=data[3]
    method=data[4]
    telegram_id = data[5]

    insert_in_db("INSERT INTO users_vpn_keys (key_id, telegram_id, accessUrl, user_password, port, method, )")

def write_stat(telegram_id, ip, stat_name="default"):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    insert_in_db(f"insert into users_stat (telegram_id ,stat_name, date, ip) values ('{telegram_id}', '{stat_name}', '{date}', '{ip}')")

def get_random_user_key(telegram_id):
    """
    Функция получает случайный ключ пользователя из БД
    Args:
        telegram_id:

    Returns:
    key
    """
    return execute_query(
        f"""
        SELECT 
            server,
            server_port,
            password,
            method
        FROM
            users_vpn_keys
        WHERE 
            telegram_id = '{telegram_id}'
        ORDER BY random() 
        LIMIT 1;
        """)