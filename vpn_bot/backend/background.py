from datetime import datetime
from calendar import monthrange
from botApp.commands import dbcon
from botApp.commands import outline_api_reqests
from botApp import config
import telebot
import math
import schedule
import time
from botApp.logs.logger import Logger
import sys
from DataConvert import DataConvert
import KeyAdmin

about_version = dbcon.get_version()
VERSION = about_version[0]
BUILD_DATE = about_version[1]

PRICE_PER_MOUNTH = 75

API_TOKEN = config.API_KEY
bot = telebot.TeleBot(API_TOKEN)

###Admin
ADMIN_ID = config.ADMIN_ID

logger = Logger(__name__)
def days_in_mounth():
    current_year = datetime.now().year
    month = datetime.now().month
    return monthrange(current_year, month)[1]

def one_day_using():
    one_day_price = round((PRICE_PER_MOUNTH / int(days_in_mounth()))*-1, 2)
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")

    dbcon.insert_in_db(f"""insert into operations (summ, type, operation_date, user_id)
	                       select
    	                   {one_day_price},
    		               4,
            	           '{date}',
                	       id FROM users where balance > '-5';
                	    """)

def send_give_price():
    users_balance = dbcon.execute_query("""select telegram_id, balance, user_state, id FROM users where balance <= 5 and user_state != 1;""", False)
    for user in users_balance:
        if float(user[1]) > -5:
            bot.send_message(ADMIN_ID, f"Пробуем отправить письмо пользователю {user[3]} о низком балансе")
            try:
                bot.send_message(user[0], f"""Уважаемый пользователь, Ваш баланс менее 5 рублей, пожалуйста, нажмите 'Пополнить' чтобы пополнить счет\nНапоминаю что при балансе менее -5 рублей, доступ будет заблокирован""")
                bot.send_message(ADMIN_ID, f"Успешно отправлено")
            except Exception as error:
                bot.send_message(ADMIN_ID, f"Не удалось отправить...")
                logger.info(f"Не удалось отправить...\n{error}")

        elif float(user[1]) <= float(-5):
            telegram_id = user[0]
            dbcon.insert_in_db(f"update users set user_state = 1 where telegram_id = '{telegram_id}';")
            if dbcon.delete_all_users_keys(telegram_id):
                bot.send_message(
                    ADMIN_ID,
                    "Пользователь {} заблокирован, отправляю сообщение".format(
                        user[0]
                    )
                )
                try:
                    bot.send_message(user[0], "Доступ заблокирован, для восстановления доступа пополните счет.")
                except Exception as error:
                    bot.send_message(
                        ADMIN_ID,
                        f"Ошибка отправки сообщения пользователю {user[0]}\n{error}")
            else:
                bot.send_message(
                    ADMIN_ID,
                    "Ошибка удаления ключей пользователя {}".format(
                        user[3]))
def update_balance():    
    dbcon.calc_balances()
    logger.info("Просчитываем баланс пользователей...")

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def send_day_stat():
    connection_count = dbcon.get_count_connection_last_day()
    bot.send_message(ADMIN_ID, f"За последние сутки обработано {connection_count} коннектов")


#def delete_all_keys_on_all_servers():
#    list_servers = dbcon.get_outline_server_list()
#    logger.info("Запущен процесс удаления старых ключей")
#    try:
#        for server in list_servers:
#            logger.info(f"Сервер - {server[0]}")
#            server_api_key = server[5]
#            print(server_api_key)
#            count = outline_api_reqests.remove_all_keys_on_server(server_api_key)
#            logger.info(f"Удалено {count} ключей")
#        logger.info("Очистка успешно выполнена!")
#    except Exception as error:
#        logger.info(f"Ошибка удаления:\n{error}")


def check_users_keys():
    logger.info("Проверяем актуальность ключей")
    active_users, disabled_users = dbcon.get_list_users_with_state()
    for user_data in active_users:
        # Объявляем класс пользователя
        telegram_id = user_data[1]
        user = KeyAdmin.UserKey(telegram_id)
        # Проверяем актуальность ключей
        user.validate_count_keys()

def get_key_traffic():
    """
    Функция для получения трафика по ключам.
    - Сначала получает список серверов, затем список ключей.
    - Создает запрос на сервер, получает данные со всех ключей
    - парсит полученные данные, вставляет данные по ID ключа
    Returns:
        Ничего не возвращает
    """
    logger.info("Получение информации по трафику ключей")
    servers_api_keys = []
    try:
        servers_id = dbcon.get_all_outline_servers()
        for id in servers_id:
            api_key = dbcon.get_server_api_key_by_server_id(id)
            servers_api_keys.append([api_key, id])

    except Exception as error:
        logger.info("Ошибка получения данных серверов \n{}".format(error))
        return 1

    logger.info("""Получены сервера:\n{}""".format(servers_api_keys))

    for server_creds in servers_api_keys:
        server_url_token = server_creds[0]
        server_id = server_creds[1]
        try:
            data: dict = outline_api_reqests.get_stat(server_url_token)["bytesTransferredByUserId"]
        except Exception as error:
            logger.info(error)
            return 1
        # Получаем список ключей принадлежащих серверу
        key_ids = dbcon.get_list_keys(server_id)
        logger.info("Выполняется загрузка информации о трафике сервера {}".format(server_id))

        for key in key_ids:
            try:
                # Получаем значение трафика для ключа
                try:
                    key = str(key)
                    traffic = data.get(key)
                except Exception as error:
                    traffic = 0
                    logger.info(error)


                dbcon.insert_in_db(
                    f"""UPDATE
                            users_vpn_keys
                        SET
                            traffic = '{traffic}' 
                        WHERE 
                            key_id = {key[0]} 
                        AND server = '{server_creds[1]}'""")
            except Exception as error:
                logger.info("Ошибка обновления трафика для ключа {}, по причине: {}".format(key[0], error))


    # Обновление данных по трафику в таблице users

    active_users, disabled_users = dbcon.get_list_users_with_state()
    for user_data in active_users:
        telegram_id = user_data[1]
        userKey = KeyAdmin.UserKey(telegram_id)
        traffic = userKey.get_user_traffic()

        dbcon.insert_in_db(
            """
            UPDATE
                users
            SET
                traffic = {}
            WHERE
                telegram_id = '{}'
            """.format(
                traffic,
                telegram_id)
        )

        logger.info("Загрузка выполнена.")




schedule.every().day.at("10:40").do(one_day_using)
schedule.every().hour.at(":00").do(update_balance)
schedule.every().hour.at(":00").do(get_key_traffic)
schedule.every().day.at("10:30").do(send_give_price)
schedule.every().day.at("10:30").do(send_day_stat)
schedule.every().day.at("03:00").do(check_users_keys)

#schedule.every().day.at("03:00").do(delete_all_keys_on_all_servers)

def run_backend():
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Запуск бекенда, установлена сумма оплаты в месяц - {PRICE_PER_MOUNTH} руб.")
    try:
        dbcon.execute_query(
            "select 1",
            fetch_one=True)

        logger.info("Подключение к БД успешно")

    except Exception as error:
        logger.info("Ошибка подключения к БД, выход...")
        logger.info(error)
        bot.send_message(ADMIN_ID, f"Ошибка подключения к БД, {error}")
        sys.exit(1)

    bot.send_message(ADMIN_ID, f"Сервер запущен - {date}\nВерсия - {VERSION}\nДата выхода - {BUILD_DATE}")

    get_key_traffic()

    while True:
        schedule.run_pending()
        time.sleep(1)

