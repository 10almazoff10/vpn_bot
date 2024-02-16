from datetime import datetime
from calendar import monthrange
import dbcon, config, outline_api_reqests
import telebot

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

schedule.every().day.at("10:40").do(one_day_using)
schedule.every().hour.at(":00").do(update_balance)
schedule.every().day.at("10:30").do(send_give_price)

if __name__ == "__main__":
    dt = datetime.now()
    date = dt.strftime("%Y-%m-%d %H:%M:%S")
    bot.send_message(758952233, f"Backend started success - {date}")
    while True:
        schedule.run_pending()
        time.sleep(1)