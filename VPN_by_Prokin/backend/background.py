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


VERSION = "1.4.0 - 2024.06.09"

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
    users_balance = dbcon.execute_query("""select telegram_id, balance, user_state, id FROM users where balance < 5;""", False)
    for user in users_balance:
        if float(user[1]) > -5:
            bot.send_message(ADMIN_ID, f"Пробуем отправить письмо пользователю {user[3]} о низком балансе")
            try:
                bot.send_message(user[0], f"""Уважаемый пользователь, Ваш баланс менее 5 рублей, пожалуйста пополните счет\nНапоминаю что при балансе менее -5 рублей, доступ будет заблокирован""")
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

def get_key_traffic():
    try: 
        data = outline_api_reqests.get_stat()["bytesTransferredByUserId"]
    except Exception as error:
        logger(error)

    key_id = dbcon.get_list_keys()
    logger("Выполняется загрузка информации о трафике..")

    for i in key_id:
        try:
            traffic = convert_size(int(data[f"{i[0]}"]))

            dbcon.insert_in_db(f"update users_vpn_keys set traffic = '{traffic}' where key_id = {i[0]};")
        except:
            pass
    logger("Загрузка выполнена.")

schedule.every().day.at("10:40").do(one_day_using)
schedule.every().hour.at(":00").do(update_balance)
schedule.every().hour.at(":00").do(get_key_traffic)
schedule.every().day.at("10:30").do(send_give_price)

def run_backend():
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    get_key_traffic()
    logger(f"Старт бота, установлена сумма оплаты в месяц - {PRICE_PER_MOUNTH}")
    bot.send_message(ADMIN_ID, f"Сервер запущен - {date}\nВерсия - {VERSION}")

    while True:
        schedule.run_pending()
        time.sleep(1)
