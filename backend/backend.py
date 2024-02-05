from datetime import datetime
from calendar import monthrange
import dbcon

import schedule
import time

PRICE_PER_MOUNTH = 50

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
    dbcon.select_many_from_db("select ")

schedule.every().day.at("01:00").do(one_day_using)

while True:
    schedule.run_pending()
    time.sleep(1)