from datetime import datetime
from calendar import monthrange
from botApp.commands import dbcon
from botApp.commands import outline_api_reqests
from botApp import config
import telebot
import math
import schedule
import time
from botApp.logs.logger import logger
import sys
from DataConvert import DataConvert

about_version = dbcon.get_version()
VERSION = about_version[0]
BUILD_DATE = about_version[1]

PRICE_PER_MOUNTH = 75

API_TOKEN = config.API_KEY
bot = telebot.TeleBot(API_TOKEN)

###Admin
ADMIN_ID = config.ADMIN_ID

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
                logger(f"Не удалось отправить...\n{error}")

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
    logger("Просчитываем баланс пользователей...")

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
#    logger("Запущен процесс удаления старых ключей")
#    try:
#        for server in list_servers:
#            logger(f"Сервер - {server[0]}")
#            server_api_key = server[5]
#            print(server_api_key)
#            count = outline_api_reqests.remove_all_keys_on_server(server_api_key)
#            logger(f"Удалено {count} ключей")
#        logger("Очистка успешно выполнена!")
#    except Exception as error:
#        logger(f"Ошибка удаления:\n{error}")


def check_users_keys():
    bot.send_message(ADMIN_ID, "Проверка наличия ключей у пользователей")
    telegram_id_without_keys = dbcon.get_active_users_without_keys()

    if telegram_id_without_keys != []:
        bot.send_message(
            ADMIN_ID,
            "Зарегистрированы ключи для пользователей - \n".format(
                telegram_id_without_keys))
    else:
        bot.send_message(
            ADMIN_ID,
            "У всех пользователей есть ключи")

def get_key_traffic():
    """
    Функция для получения трафика по ключам.
    - Сначала получает список серверов, затем список ключей.
    - Создает запрос на сервер, получает данные со всех ключей
    - парсит полученные данные, вставляет данные по ID ключа
    Returns:
        Ничего не возвращает
    """
    try:
        server_api_keys = dbcon.get_all_outline_servers()
    except Exception as error:
        logger("Ошибка получения данных серверов")
        return 1

    logger("""Получены сервера:\n{}""".format(server_api_keys))

    for API_KEY in server_api_keys:
        server_url_token = API_KEY[0]
        server_ip = API_KEY[1]
        try:
            data = outline_api_reqests.get_stat(server_url_token)["bytesTransferredByUserId"]
        except Exception as error:
            logger(error)
            return 1
        # Получаем список ключей принадлежащих серверу
        key_id = dbcon.get_list_keys(server_ip)
        logger("Выполняется загрузка информации о трафике сервера {}".format(server_ip))

        for key in key_id:
            try:
                # Получаем значение трафика для ключа
                traffic = int(data[str(key[0])])
                traffic_in_human = DataConvert.convert_size(traffic)
                logger("Трафик ключа {} составил {}".format(key[0], traffic_in_human))

                dbcon.insert_in_db(
                    f"""UPDATE
                            users_vpn_keys
                        SET
                            traffic = '{traffic}' 
                        WHERE 
                            key_id = {key[0]} 
                        AND server = '{API_KEY[1]}'""")
            except Exception as error:
                logger("Ошибка обновления трафика для ключа {}, по причине: {}".format(key[0], error))


    # Обновление данных по трафику в таблице users

    active_users, disabled_users = dbcon.get_list_users_with_state()
    for user_data in active_users:
        telegram_id = user_data[1]
        traffic = dbcon.get_traffic_by_user(telegram_id)

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



        logger("Загрузка выполнена.")

schedule.every().day.at("10:40").do(one_day_using)
schedule.every().hour.at(":00").do(update_balance)
schedule.every().hour.at(":00").do(get_key_traffic)
schedule.every().day.at("10:30").do(send_give_price)
schedule.every().day.at("10:30").do(send_day_stat)
#schedule.every().day.at("03:00").do(delete_all_keys_on_all_servers)

def run_backend():
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    logger(f"Запуск бекенда, установлена сумма оплаты в месяц - {PRICE_PER_MOUNTH} руб.")
    try:
        dbcon.execute_query(
            "select 1",
            fetch_one=True)

        logger("Подключение к БД успешно")

    except Exception as error:
        logger("Ошибка подключения к БД, выход...")
        logger(error)
        bot.send_message(ADMIN_ID, f"Ошибка подключения к БД, {error}")
        sys.exit(1)

    bot.send_message(ADMIN_ID, f"Сервер запущен - {date}\nВерсия - {VERSION}\nДата выхода - {BUILD_DATE}")

    get_key_traffic()

    while True:
        schedule.run_pending()
        time.sleep(1)

