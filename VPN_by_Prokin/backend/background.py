from datetime import datetime
from calendar import monthrange
from app.commands import dbcon
from app.commands import outline_api_reqests
from app import config
import telebot
import math
import schedule
import time
from app.logs.logger import logger


VERSION = "1.0.5 - 2024.04.16"

PRICE_PER_MOUNTH = 75

API_TOKEN = config.API_KEY
bot = telebot.TeleBot(API_TOKEN)

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
    users_balance = dbcon.select_many_from_db("""select U.telegram_id, U.balance, V.key_id 
                                                    FROM users AS U 
                                                    JOIN users_vpn_keys AS V 
                                                    ON V.user_name = U.telegram_id;""")
    for user in users_balance:
        if float(user[1]) < 10 and float(user[1]) > -5:
            bot.send_message(758952233, f"Пробуем отправить письмо пользователю {user[0]} о низком балансе")
            try:
                bot.send_message(user[0], f"""Уважаемый пользователь, Ваш баланс менее 10 рублей, пожалуйста пополните счет\nНапоминаю что при балансе менее -5 рублей, доступ будет заблокирован""")
                bot.send_message(758952233, f"Успешно отправлено")
            except :
                bot.send_message(758952233, f"Не удалось отправить...")

        elif float(user[1]) < -5:
            id = user[2]
            outline_api_reqests.remove_key(id)
            dbcon.insert_in_db(f"delete from users_vpn_keys where key_id = '{id}';")

            bot.send_message(758952233, f"Удаляю пользователя {user[0]}")
            try:
                bot.send_message(user[0], f"""Доступ заблокирован, для восстановления доступа пополните счет и сгенерируйте новый ключ.""")
                bot.send_message(758952233, f"Пользователь удален {user[0]}")
            except:
                bot.send_message(758952233, f"Ошибка удаления пользователя {user[0]}")
            
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
    bot.send_message(758952233, f"Сервер запущен - {date}\nВерсия - {VERSION}")

    while True:
        schedule.run_pending()
        time.sleep(1)