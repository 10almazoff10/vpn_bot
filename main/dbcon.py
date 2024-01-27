import psycopg2
import config
from datetime import datetime
from calendar import monthrange
import secrets
import outline_api_reqests as outline
import string


DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASS = config.DB_PASS
DB_HOST = config.DB_HOST

def select_from_db(req):
    try:
        # пытаемся подключиться к базе данных
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    except:
        # в случае сбоя подключения будет выведено сообщение в STDOUT
        print('Can`t establish connection to database')
    # получение объекта курсора
    cursor = conn.cursor()
    cursor.execute(req)
    result = cursor.fetchone()
    cursor.close() # закрываем курсор
    conn.close() # закрываем соединение
    return result

def select_many_from_db(req):
    try:
        # пытаемся подключиться к базе данных
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    except:
        # в случае сбоя подключения будет выведено сообщение в STDOUT
        print('Can`t establish connection to database')
    # получение объекта курсора
    cursor = conn.cursor()
    cursor.execute(req)
    result = cursor.fetchall()
    cursor.close() # закрываем курсор
    conn.close() # закрываем соединение
    return result
def insert_in_db(req):
    try:
        # пытаемся подключиться к базе данных
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    except:
        # в случае сбоя подключения будет выведено сообщение в STDOUT
        print('Can`t establish connection to database')
    # получение объекта курсора
    cursor = conn.cursor()
    cursor.execute(req)
    conn.commit()
    cursor.close() # закрываем курсор
    conn.close() # закрываем соединение

def add_new_user(message):
    telegram_id = message.from_user.id
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    status = 10
    insert_in_db(f"INSERT INTO users (telegram_id, date_first_enter, status) VALUES ({telegram_id}, '{date}', {status})")


def check_user_indb(message):
    id = select_from_db(f"select id from users where telegram_id = '{message.from_user.id}'")

    if id == None:
        return False
    else:
        return True

def set_status(message, status):
    insert_in_db(f"UPDATE users SET status = {status} where telegram_id = '{message.from_user.id}'")

def get_status(message):
    return select_from_db(f"SELECT status from users where telegram_id = '{message.from_user.id}'")[0]

def check_token(message):
    try:
        return select_from_db(f"SELECT telegram_id from users_auth where reg_token = '{message.text}'")[0]
    except:
        return ""

def user_reg(message):
    insert_in_db(f"UPDATE users_auth SET telegram_id = '{message.from_user.id}' where reg_token = '{message.text}'")
    insert_in_db(f"UPDATE users SET reg_token = '{message.text}' where telegram_id = '{message.from_user.id}'")
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")

    check_operations = select_many_from_db(f"SELECT id FROM operations WHERE user_id = (SELECT user_id FROM users_auth WHERE reg_token = '{message.text}');")
    if check_operations == "":
        insert_in_db(f"insert into operations (summ, type, operation_date, user_id) values (0, 3, '{date}', (SELECT user_id FROM users_auth WHERE reg_token = '{message.text}'));")

def user_name(message):
    return select_from_db(f"SELECT user_name FROM users_auth WHERE telegram_id = '{message.from_user.id}'")[0]

def get_user_balance(message):
    return  select_from_db(f"SELECT balance from users_auth where telegram_id = '{message.from_user.id}'")[0]

def create_support_task(message):
    telegram_id = message.from_user.id
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    insert_in_db(f"INSERT INTO support_tasks (telegram_id, message, date_create) VALUES ('{telegram_id}', '{message.text}', '{date}')")
    list_tasks = select_many_from_db(f"SELECT id FROM support_tasks WHERE telegram_id = '{telegram_id}' and state = 1")
    tasks = str()
    for i in list_tasks:
        tasks = tasks + str(i[0]) + ", "
    return tasks

def calc_balances():
    id_list = select_many_from_db("select user_id from users_auth")
    for id in id_list:
        insert_in_db(f"update users_auth set balance = (select SUM(summ) from operations where user_id = {id[0]}) where user_id = {id[0]};")

def get_operations_user(message, count=10):
    
    return select_many_from_db(f"""select operations.id, operations.summ, operations.operation_date, operation_types.type_name  from operations
                                    join operation_types on operation_types.id = operations.type 
                                    where user_id = (select user_id from users_auth where telegram_id = '{message.from_user.id}') 
                                    ORDER BY id ASC LIMIT {count}""")

def get_user_vpn_keys(message):
    return select_many_from_db(f"""SELECT user_password, date_reg, acess_url from users_vpn_keys
                               where user_id = (select user_id from users_auth where telegram_id = '{message.from_user.id}')""")


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
        insert_in_db(f"""insert into users_vpn_keys (user_id, user_password, user_name, acess_url, port, date_reg)
                           values ({id}, '{password}', '{name}', '{accessUrl}', '{port}', '{date}') """)
        
        insert_in_db(f"insert into operations (summ, type, operation_date, user_id) values (0, 3, '{date}', {id});")
        



def create_new_key(message):
    name = select_from_db(f"SELECT user_name FROM users_auth where telegram_id = '{message.from_user.id}'")
    key = outline.create_new_key(name)
    pass

########### ADMIN ############

def get_list_users():
    return select_many_from_db(f"select user_name, telegram_id, balance, user_id, reg_token from users_auth")

def create_user_token(message):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(10))
    client_name = message.text
    insert_in_db(f"insert into users_auth (reg_token, user_name) values ('{password}', '{client_name}')")
    return password

def add_money_to_user_from_buffer(message):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    insert_in_db(f"insert into operations (summ, type, operation_date, user_id) values ((select summ from operation_buffer), 2, '{date}', (select user_id from operation_buffer))")
