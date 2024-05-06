import psycopg2
from contextlib import closing
from datetime import datetime
from calendar import monthrange
import secrets
from botApp.commands import outline_api_reqests as outline
import string
from botApp import config
from botApp.logs.logger import logger

DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASS = config.DB_PASS
DB_HOST = config.DB_HOST

logger(f"{DB_HOST}, {DB_USER}, {DB_PASS}, {DB_NAME}")


def execute_query(req, fetch_one=True):
    """
    Выполняет SQL-запрос к базе данных.

    Args:
        req (str): SQL-запрос.
        fetch_one (bool, optional): Если True, возвращает одну строку результата. Иначе возвращает все строки. Defaults to True.

    Returns:
        tuple or list: Результат выполнения запроса.
    """
    with closing(psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)) as conn:
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


def add_new_user(message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name
    if len(name) < 15 and is_good_string(name):
        pass
    else:
        name = "Пользователь"

    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    status = 10
    insert_in_db(
        f"INSERT INTO users (telegram_id, name, date_first_enter, status) VALUES ({telegram_id}, '{name}','{date}', {status})")
    insert_in_db(
        f"INSERT INTO operations (summ, type, operation_date, user_id) values (0, 3, '{date}', (SELECT id FROM users WHERE telegram_id = '{telegram_id}'));")

def get_user_id(telegram_id):
    """
    Получение внутреннего id пользователя
    Args:
        telegram_id:

    Returns:
    id_user
    """
    return execute_query(f"select id from users where telegram_id = '{telegram_id}';")[0]
def is_good_string(text):
    # Проверяем, что строка состоит только из русских и английских букв, символов и цифр
    allowed_characters = string.ascii_letters + string.digits + "-_., "
    return all(char in allowed_characters for char in text)


def check_user_indb(message):
    id = execute_query(f"select id from users where telegram_id = '{message.from_user.id}'")

    if id == None:
        return False
    else:
        return True


def set_status(message, status):
    insert_in_db(f"UPDATE users SET status = {status} where telegram_id = '{message.from_user.id}'")


def get_status(message):
    return execute_query(f"SELECT status from users where telegram_id = '{message.from_user.id}'")[0]


def user_name(message):
    return execute_query(f"SELECT user_name FROM users WHERE telegram_id = '{message.from_user.id}'")[0]


def get_user_balance(telegram_id):
    return execute_query(f"SELECT balance from users where telegram_id = '{telegram_id}'")[0]


def create_support_task(message):
    telegram_id = message.from_user.id
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    insert_in_db(
        f"INSERT INTO support_tasks (telegram_id, message, date_create) VALUES ('{telegram_id}', '{message.text}', '{date}')")
    list_tasks = execute_query(f"SELECT id FROM support_tasks WHERE telegram_id = '{telegram_id}' and state = 1",
                               fetch_one=False)
    tasks = str()
    for i in list_tasks:
        tasks = tasks + str(i[0]) + ", "
    return tasks


def calc_balances():
    id_list = execute_query("select id from users", fetch_one=False)
    for id in id_list:
        insert_in_db(
            f"update users set balance = (select SUM(summ) from operations where user_id = {id[0]}) where id = {id[0]};")


def get_operations_user(message, count=10):
    return execute_query(f"""select operations.id, operations.summ, operations.operation_date, operation_types.type_name  from operations
                                    join operation_types on operation_types.id = operations.type 
                                    where user_id = (select id from users where telegram_id = '{message.from_user.id}') 
                                    ORDER BY id DESC LIMIT {count}""", fetch_one=False)


def get_user_vpn_keys(message):
    return execute_query(f"""SELECT access_url from users_vpn_keys
                               where user_name = '{message.from_user.id}'""", fetch_one=False)


def get_user_traffic(message):
    return \
    execute_query(f"select traffic from users_vpn_keys where user_name = '{message.from_user.id}'", fetch_one=False)[0]


def get_users_from_outline():
    response = outline.get_all_api_keys()

    for i in response["accessKeys"]:
        id = i["id"]
        name = i["name"]
        accessUrl = i["accessUrl"]
        port = i["port"]
        password = i["password"]
        dt = datetime.now()
        date = dt.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{id} {name} {accessUrl} {port} {password}")
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(10))

        insert_in_db(f"insert into users_auth (user_id, user_name, reg_token) values ('{id}','{name}', '{password}')")
        insert_in_db(f"""insert into users_vpn_keys (user_id, user_password, user_name, access_url, port, date_reg)
                           values ({id}, '{password}', '{name}', '{accessUrl}', '{port}', '{date}') """)

        insert_in_db(f"insert into operations (summ, type, operation_date, user_id) values (0, 3, '{date}', {id});")


def create_new_key(message):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    telegram_id = message.from_user.id
    data = outline.create_new_key(telegram_id)
    key = data[1]
    key_id = data[0]
    insert_in_db(f"""insert into users_vpn_keys (key_id, user_name, access_url, date_reg)
                           values ('{key_id}',{telegram_id}, '{key}', '{date}') """)


########### ADMIN ############

def get_list_users():
    """
    Получение информации о пользователях
    Returns:
    Возвращает список пользователей и их трафик
    """
    return execute_query("""SELECT name,
                                       telegram_id,
                                       balance,
                                       id,
                                       user_state,
                                       keys.traffic
                                FROM   users
                                       left join users_vpn_keys AS keys
                                         ON keys.user_name = users.telegram_id
                                ORDER  BY id ASC;""",
                         fetch_one=False)


def add_money_to_user_from_buffer(message):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    insert_in_db(
        f"insert into operations (summ, type, operation_date, user_id) values ((select summ from operation_buffer), 2, '{date}', (select user_id from operation_buffer))")


def get_list_keys():
    return execute_query(f"select key_id, user_name from users_vpn_keys order by key_id asc;", fetch_one=False)


def get_user_telegram_id(id):
    """
    Функция для получения telegram-id пользователя по его id в БД
    Args:
        id: внутренний id пользователя

    Returns:
        telegram-id
    """
    return execute_query(f"select telegram_id from users where id = {id}")


def unblock_user(telegram_id):
    """
    Функция для разблокировки пользователя по его ТГ id.
    Args:
        telegram_id:

    Returns:
        Если пользователь разблокирован, возвращает True, Если нет то False
    """
    balance = get_user_balance(telegram_id)
    if balance > -5:
        try:
            insert_in_db(f"update users set user_state = 0 where telegram_id = '{telegram_id}'")
            return True
        except Exception as error:
            logger(error)
            return False
    else:
        return False
