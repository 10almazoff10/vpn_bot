from datetime import datetime
from calendar import monthrange
import dbcon, config, outline_api_reqests
import telebot
import math


import schedule
import time

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
                	id FROM users;
                	""")



def send_give_price():
    users_balance = dbcon.select_many_from_db("""select U.telegram_id, U.balance, V.key_id 
                                                    FROM users AS U 
                                                    JOIN users_vpn_keys AS V 
                                                    ON V.user_name = U.telegram_id;""")
    for user in users_balance:
        if float(user[1]) < 10 and float(user[1]) > -5:
            bot.send_message(758952233, f"Пользователю {user[0]} отправлено сообщение о низком балансе")
            bot.send_message(user[0], f"""Уважаемый пользователь, Ваш баланс менее 10 рублей, пожалуйста пополните счет\nНапоминаю что при балансе менее -5 рублей, доступ будет заблокирован""")
        elif float(user[1]) < -5:
            id = user[2]
            outline_api_reqests.remove_key(id)
            dbcon.insert_in_db(f"delete from users_vpn_keys where key_id = '{id}';")

            bot.send_message(758952233, f"Удален пользователь {user[0]}")
            bot.send_message(user[0], f"""Доступ заблокирован, для восстановления доступа пополните счет и сгенерируйте новый ключ.""")
            
def update_balance():    
    dbcon.calc_balances()
    bot.send_message(758952233, f"Баланс успшно обновлен")



def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def get_key_traffic():
    data = outline_api_reqests.get_stat()["bytesTransferredByUserId"]
    key_id = dbcon.get_list_keys()

    for i in key_id:
        try:
            traffic = convert_size(int(data[f"{i[0]}"]))
            dbcon.insert_in_db(f"update users_vpn_keys set traffic = '{traffic}' where key_id = {i[0]};")
        except:
            pass


schedule.every().day.at("10:40").do(one_day_using)
schedule.every().hour.at(":00").do(update_balance)
schedule.every().hour.at(":00").do(get_key_traffic)

schedule.every().day.at("10:30").do(send_give_price)

if __name__ == "__main__":
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    get_key_traffic()
    bot.send_message(758952233, f"Бэкэнд запущен - {date}\nВыполнено обновление прогрузки трафика")


    while True:
        schedule.run_pending()
        time.sleep(1)