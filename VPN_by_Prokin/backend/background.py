from datetime import datetime
from calendar import monthrange
from botApp.commands import dbcon
from botApp.commands import outline_api_reqests
from botApp import config
import telebot
import math
import schedule
import time
from botApp.logs.logger import logger, log_rotate
import sys


VERSION = dbcon.get_version()[0]

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
            bot.send_message(ADMIN_ID, f"Блокирую пользователя {user[0]}")
            try:
                bot.send_message(user[0], "Доступ заблокирован, для восстановления доступа пополните счет.")
                bot.send_message(ADMIN_ID, f"Пользователь заблокирован {user[0]}")
            except Exception as error:
                bot.send_message(ADMIN_ID, f"Ошибка удаления пользователя {user[0]}\n{error}")
            
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


schedule.every().day.at("10:40").do(one_day_using)
schedule.every().hour.at(":00").do(update_balance)
schedule.every().day.at("10:30").do(send_give_price)
schedule.every().day.at("03:10").do(log_rotate)
schedule.every().day.at("10:30").do(send_day_stat)



def run_backend():
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    logger(f"Старт бота, установлена сумма оплаты в месяц - {PRICE_PER_MOUNTH}")
    try:
        dbcon.execute_query("select 1", fetch_one=True)
    except Exception as error:
        logger("Ошибка подключения к БД, выход...")
        logger(error)
        bot.send_message(ADMIN_ID, f"Ошибка подключения к БД, {error}")

        sys.exit(1)

    bot.send_message(ADMIN_ID, f"Сервер запущен - {date}\nВерсия - {VERSION}")

    while True:
        schedule.run_pending()
        time.sleep(1)
