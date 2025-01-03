import sys

import psycopg2
from contextlib import closing
from datetime import datetime
from calendar import monthrange
import secrets
from vpn_bot.commands import outline_api_reqests as outline
import string
from vpn_bot import config
from vpn_bot.utils.logger import Logger
from vpn_bot.utils.hash_decoder import MD5

DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASS = config.DB_PASS
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT
SALT = config.SALT
API_HOST = config.API_HOST
logger = Logger(__name__)

logger.info(f"Инициализация подключения к БД...")
logger.info(f"{DB_HOST}, {DB_USER}, {DB_NAME}")


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
    with closing(
            psycopg2.connect(
                dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
            )
    ) as conn:
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
        with closing(
                psycopg2.connect(
                    dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
                )
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(req)
                conn.commit()
    except Exception as error:
        print(f"Error inserting data: {error}")


### Работа с пользователями


def add_new_user(message):
    """
    Функция для добавления нового пользователя. Принимает на вход message из telegram
    Args:
        message:

    Returns:

    """
    telegram_id = message.from_user.id
    name = message.from_user.username
    # Если у пользователя нет логина
    if name == None:
        name = message.from_user.first_name

    if len(name) > 20:
        name = "Пользователь"

    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    status = 10

    user_key = gen_crypted_data(message.from_user.id)

    insert_in_db(
        f"INSERT INTO users (telegram_id, name, date_first_enter, status, user_key) VALUES ({telegram_id}, '{name}','{date}', {status}, '{user_key}')"
    )
    insert_in_db(
        f"INSERT INTO operations (summ, type, operation_date, user_id) values (0, 3, '{date}', (SELECT id FROM users WHERE telegram_id = '{telegram_id}'));"
    )


def reg_user_keys(telegram_id, servers_id: list):
    """
    Регистрирует ключи на серверах из списка servers_id
    Args:
        telegram_id:

    Returns:
        True, False
    """
    server_list = get_outline_server_list_by_id(
        only_connection_link=True, servers_id=servers_id
    )

    print(server_list)

    key_list = outline.create_new_keys(telegram_id, server_list)

    logger.info(key_list)

    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")

    try:
        for key in key_list:
            insert_in_db(
                f"""
                INSERT INTO users_vpn_keys
                (
                    key_id,
                    telegram_id,
                    access_url,
                    date_reg,
                    method,
                    server_port,
                    password,
                    server,
                    server_id
                )
                VALUES
                (
                    '{key[0]}',
                    '{telegram_id}',
                    '{key[2]}',
                    '{date}',
                    '{key[5]}',
                    '{key[4]}',
                    '{key[3]}',
                    '{key[6]}',
                    '{key[7]}'
                )
                """
            )
        return True

    except Exception as error:
        logger.info("Ошибка добавление ключей в БД\n" + str(error))
        return False


def get_user_id(telegram_id):
    """
    Получение внутреннего id пользователя
    Args:
        telegram_id:

    Returns:
    id_user
    """
    return execute_query(f"select id from users where telegram_id = '{telegram_id}';")[
        0
    ]


def get_telegram_id_users():
    """
    Возвращает TG id всех зарегистрированных пользователей
    Returns:

    """
    return execute_query("select telegram_id from users;", False)


def check_user_indb(telegram_id):
    id = execute_query(f"select id from users where telegram_id = '{telegram_id}'")

    if id == None:
        return False
    else:
        return True


def set_status(message, status):
    insert_in_db(
        f"UPDATE users SET status = {status} where telegram_id = '{message.from_user.id}'"
    )


def get_status(message):
    return execute_query(
        f"SELECT status from users where telegram_id = '{message.from_user.id}'"
    )[0]


def user_name(message):
    return execute_query(
        f"SELECT user_name FROM users WHERE telegram_id = '{message.from_user.id}'"
    )[0]


def get_user_balance(telegram_id):
    return execute_query(
        f"SELECT balance from users where telegram_id = '{telegram_id}'"
    )[0]


def create_support_task(message):
    telegram_id = message.from_user.id
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    insert_in_db(
        f"INSERT INTO support_tasks (telegram_id, message, date_create) VALUES ('{telegram_id}', '{message.text}', '{date}')"
    )
    list_tasks = execute_query(
        f"SELECT id FROM support_tasks WHERE telegram_id = '{telegram_id}' and state = 1",
        fetch_one=False,
    )
    tasks = str()
    for i in list_tasks:
        tasks = tasks + str(i[0]) + ", "
    return tasks


def calc_balances():
    id_list = execute_query("select id from users", fetch_one=False)
    for id in id_list:
        insert_in_db(
            f"update users set balance = (select SUM(summ) from operations where user_id = {id[0]}) where id = {id[0]};"
        )


def get_operations_user(message, count=10):
    return execute_query(
        f"""select operations.id, operations.summ, operations.operation_date, operation_types.type_name  from operations
                                    join operation_types on operation_types.id = operations.type 
                                    where user_id = (select id from users where telegram_id = '{message.from_user.id}') 
                                    ORDER BY id DESC LIMIT {count}""",
        fetch_one=False,
    )


def get_list_keys(server_id):
    return execute_query(
        """
                SELECT 
                    key_id,
                    telegram_id
                FROM 
                    users_vpn_keys
                WHERE
                    server_id = '{}'
                ORDER BY
                    key_id 
                ASC;""".format(
            server_id
        ),
        fetch_one=False,
    )


def get_user_vpn_key(telegram_id):
    """
    Возвращает динамический ключ пользователя
    Args:
        message:

    Returns:
        user_key: String

    """

    user_token = execute_query(
        f"""SELECT user_key FROM users WHERE telegram_id  = '{telegram_id}'"""
    )[0]
    if user_token == "":
        user_key = gen_crypted_data(telegram_id)
        insert_in_db(
            f"UPDATE users set user_key = '{user_key}' where telegram_id = '{telegram_id}'"
        )
        user_token = execute_query(
            f"""SELECT user_key FROM users WHERE telegram_id  = '{telegram_id}'"""
        )[0]

    user_key = "ssconf://{}/conf/{}".format(API_HOST, user_token)
    return user_key


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
        password = "".join(secrets.choice(alphabet) for i in range(10))

        insert_in_db(
            f"insert into users_auth (user_id, user_name, reg_token) values ('{id}','{name}', '{password}')"
        )
        insert_in_db(
            f"""insert into users_vpn_keys (user_id, user_password, user_name, access_url, port, date_reg)
                           values ({id}, '{password}', '{name}', '{accessUrl}', '{port}', '{date}') """
        )

        insert_in_db(
            f"insert into operations (summ, type, operation_date, user_id) values (0, 3, '{date}', {id});"
        )


def get_all_outline_servers():
    """
    Возвращает id активных серверов
    Returns:
    ID
    """
    list_id = execute_query(
        """SELECT 
                    id
                FROM 
                    outline_servers 
                WHERE standby_status = TRUE;
            """,
        fetch_one=False,
    )
    ids = []
    for id in list_id:
        ids.append((id[0]))

    return ids


def gen_crypted_data(telegram_id: str) -> str:
    crypt = MD5(SALT + str(telegram_id))
    return crypt.encrypt()


########### ADMIN ############


def get_list_users_with_state():
    """
    Получение информации о пользователях
    Returns:
    Возвращает список пользователей и их трафик
    active_users, disabled_users
    """
    active_users = execute_query(
        """select
                    left(name, 7),
                    telegram_id,
                    balance,
                    id,
                    user_state,
                    user_key
                from
                    users
                where
                    user_state = 0
                order by
                    id asc;""",
        fetch_one=False,
    )

    return active_users


def add_money_to_user_from_buffer(message):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    insert_in_db(
        f"""
        insert
            into
            operations (summ,
            type,
            operation_date,
            user_id)
        values ((
        select
            summ
        from
            operation_buffer),
        2,
        '{date}',
        (
        select
            user_id
        from
            operation_buffer))
        """
    )


def add_money_to_user_from_pay_form(telegram_id, summ):
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    insert_in_db(
        f"""
        insert
            into
            operations (summ,
            type,
            operation_date,
            user_id)
        values ({summ},
        6,
        '{date}',
        (
        select
            id
        from
            users
        where
            telegram_id = '{telegram_id}'))
        """
    )


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
            insert_in_db(
                f"update users set user_state = 0 where telegram_id = '{telegram_id}'"
            )
            return True
        except Exception as error:
            logger.info(error)
            return False
    else:
        return False


def get_count_connection_last_day():
    return execute_query(
        """SELECT count(*)
            FROM users_stat
            WHERE date >= (CURRENT_DATE - interval '1 day')
            AND stat_name ='connect'"""
    )[0]


def get_version():
    return execute_query(
        "SELECT version, date FROM bot_version order by id desc limit 1;"
    )


def get_users_stats():
    return execute_query(
        """select
                    ROW_NUMBER() over() as number,
                    u.id,
                    left(u.name, 5),
                    count(us.telegram_id) as user_count,
                    u.traffic                                    
                from
                    users_stat us
                left join users u 
                    on
                    u.telegram_id = us.telegram_id
                where
                    us.date >= (current_date - interval '1 day')
                group by
                    u.id,
                    u.name,
                    u.traffic
                order by
                    number asc;
                """,
        fetch_one=False,
    )


def get_outline_server_list(only_connection_link=False):
    """
    Возвращает массив данных по серверам.
    Returns:

    """
    logger.info("Запрос в базу")

    if only_connection_link:
        try:
            list_servers = execute_query(
                """
                select
                    id,
                    connection_link
                from
                    outline_servers
                where standby_status = True;
                """,
                fetch_one=False,
            )
            for server in list_servers:
                logger.info(server)
            return list_servers
        except Exception as error:
            logger.info(error)
            sys.exit(1)

    try:
        list_servers = execute_query(
            """
             select
                id,
                name,
                comment,
                country,
                speed_in_kbytes,
                connection_link,
                creation_date
            from
                outline_servers
            where standby_status = True;
            """,
            fetch_one=False,
        )
        for server in list_servers:
            logger.info(server)
        return list_servers

    except Exception as error:
        logger.info(error)
        sys.exit(1)


def get_outline_server_list_by_id(only_connection_link=False, servers_id=False):
    """
    Возвращает массив данных по серверам.
    Returns:

    """
    logger.info("Запрос в базу")
    if only_connection_link:
        try:
            links = []
            for id in servers_id:
                server = execute_query(
                    """
                    select
                        id,
                        connection_link
                    from
                        outline_servers
                    where id = '{}';
                    """.format(
                        id
                    )
                )
                links.append(server)
            return links

        except Exception as error:
            logger.info(error)
            sys.exit(1)

    try:
        list_servers = execute_query(
            """
             select
                id,
                name,
                comment,
                country,
                speed_in_kbytes,
                connection_link,
                creation_date
            from
                outline_servers
            where standby_status = True;
            """,
            fetch_one=False,
        )
        for server in list_servers:
            logger.info(server)
        return list_servers

    except Exception as error:
        logger.info(error)
        sys.exit(1)


def get_active_users_without_keys():
    active_users, disabled_users = get_list_users_with_state()
    list_users = []

    for users in active_users:
        list_users.append(users[1])

    created_users = execute_query(
        """
        SELECT DISTINCT
            telegram_id
        FROM
            users_vpn_keys;
        """,
        fetch_one=False,
    )

    if created_users == []:
        created_users.append("NoData")

    return_users = []
    for telegram_id in list_users:
        if str(telegram_id) not in created_users[0]:
            return_users.append(telegram_id)
            reg_user_keys(telegram_id)
            logger.info(
                "Зарегистрированы ключи для пользователя {}".format(telegram_id)
            )
    return return_users


def get_user_state(telegram_id):
    """
    Функция получает статус пользователя
    Args:
        telegram_id
    Returns:
    state 0 or 1
    """
    return execute_query(
        f"""
        SELECT 
            user_state
        FROM
            users
        WHERE 
            telegram_id = '{telegram_id}'
        """,
        fetch_one=True,
    )[0]


def get_user_state_vpn_key(telegram_id):
    """
    Функция получает случайный ключ пользователя из БД
    Args:
        telegram_id:
        {} - IP сервера
        {} - Порт
        {} - Метод шифрования
        {} - Пароль

    Returns:
    key
    """
    return execute_query(
        f"""
            select
                uvk.server server,
                uvk.server_port,
                uvk.method,
                uvk."password" ,
                os.country country
            from
                users_vpn_keys uvk
            inner join outline_servers os
                    on
                uvk.server = os.server_ip
            where
                telegram_id = '{telegram_id}'
            order by
                server desc;
        """, fetch_one=False
    )


def delete_all_users_keys(telegram_id):
    user_keys = []
    try:
        user_keys = execute_query(
            """
            select
                uvk.key_id,
                os.connection_link
            from
                users_vpn_keys uvk
            left join outline_servers os on
                uvk.server_id = os.id
            where
                telegram_id = '{}';
            """.format(
                telegram_id
            ),
            fetch_one=False,
        )
    except Exception as error:
        logger.info("Не удается получить информацию о ключах из БД\n" + str(error))
        return False

    try:
        for data in user_keys:
            key_id = data[0]
            API_KEY = data[1]
            outline.remove_key(key_id, API_KEY)
    except Exception as error:
        logger.info("Ошибка удаления ключей с серверов \n" + str(error))
        return False

    try:
        insert_in_db(
            """
            delete
            from
                users_vpn_keys
            where
                telegram_id = '{}';
            """.format(
                telegram_id
            )
        )
        return True

    except Exception as error:
        logger.info("Не удается удалить ключи из БД \n" + str(error))
        return False


def get_all_user_keys(telegram_id):
    """
    Функция возвращает ID ключей и ID их серверов пользователя
    Args:
        telegram_id:

    Returns:

    """
    user_keys = execute_query(
        """
        SELECT
            key_id,
            server_id
        FROM
            users_vpn_keys
        WHERE
            telegram_id = '{}'
        """.format(
            telegram_id
        ),
        fetch_one=False,
    )

    return user_keys


def get_count_keys_on_servers_for_user(telegram_id):
    keys_count: list = execute_query(
        """
        SELECT
            server_id,
        COUNT(DISTINCT key_id) AS count_keys
        FROM
            users_vpn_keys
        WHERE
            telegram_id = '{}' 
        GROUP BY
            server_id;
        """.format(
            telegram_id
        ),
        fetch_one=False,
    )
    return keys_count


def get_list_user_keys_by_server_id(telegram_id, server_id):
    """
    Возвращает список key_id по одному серверу на основе server_id
    Args:
        telegram_id:
        server_id:

    Returns:
    user_keys_on_server: list
    """
    user_keys_on_server: list = execute_query(
        """
        SELECT
            key_id
        FROM
            users_vpn_keys
        WHERE
            telegram_id = '{}' and server_id = '{}'
        """.format(
            telegram_id, server_id
        ),
        fetch_one=False,
    )
    result = []

    for key in user_keys_on_server:
        result.append(key[0])
    result.sort()

    return result


def get_server_api_key_by_server_id(server_id):
    API_KEY = execute_query(
        """
        SELECT
            connection_link
        FROM
            outline_servers
        WHERE
            id = '{}'
        """.format(
            server_id
        )
    )[0]
    return API_KEY


def delete_key_by_server_id(key_id, server_id):
    """
    Удаляет конкретный ключ на конкретном сервере
    Args:
        key_id:
        server_id:

    Returns:
    Если успех то True, иначе False
    """
    API_KEY = get_server_api_key_by_server_id(server_id)
    try:
        try:
            logger.info("Удаление ключа с сервера - {}".format(server_id))
            outline.remove_key(key_id, API_KEY)
        except Exception as error:
            logger.info("Ошибка удаления ключа с сервера - {}".format(error))

        try:

            insert_in_db(
                """
                DELETE
                FROM
                    users_vpn_keys
                WHERE
                    server_id = '{}' and key_id = '{}'
                """.format(
                    server_id,
                    key_id
                )
            )
            return True
        except Exception as error:
            logger.info("Ошибка удаления ключа из БД".format(error))
            return False
    except Exception as error:
        logger.info(error)
        return False


def get_list_servers_with_users_state(telegram_id):
    return execute_query(
        '''
        SELECT  
            uvk.server server,
            uvk.enabled enabled,
            os.country country
        FROM  
            users_vpn_keys uvk
        INNER JOIN outline_servers os
        ON uvk.server = os.server_ip
        WHERE  
            telegram_id = '{}'
        ORDER BY server DESC;
        '''.format(telegram_id),
        fetch_one=False
    )


def user_change_server_state(telegram_id, server_ip):
    state: bool = execute_query(
        '''
        SELECT 
            enabled
        FROM
            users_vpn_keys
        WHERE
            telegram_id = '{}' AND server = '{}'
        '''.format(telegram_id, server_ip)
    )[0]

    if state == False:
        insert_in_db(
            '''
            UPDATE 
                users_vpn_keys
            SET
                enabled = True
            WHERE
                telegram_id = '{}' AND server = '{}'
            '''.format(telegram_id, server_ip)
        )
    elif state == True:
        insert_in_db(
            '''
            UPDATE 
                users_vpn_keys
            SET
                enabled = False
            WHERE
                telegram_id = '{}' AND server = '{}'
            '''.format(telegram_id, server_ip)
        )


def get_server_state(server_id):
    """
    Возвращает статус сервера
    True | False
    """
    return execute_query(
        '''
        SELECT
            standby_status
        FROM
            outline_servers
        WHERE
            id = '{}'
        '''.format(server_id)
        , fetch_one=True)[0]
