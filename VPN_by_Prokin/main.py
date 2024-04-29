#!/usr/bin/python

import telebot
from threading import Thread
from app.text import tg_keyboard, messages
from app.commands import dbcon
from app.logs import logger
from app import config
from backend import background

# Run Backend
backend = Thread(target=background.run_backend)
backend.start()

API_TOKEN = config.API_KEY

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.logger(f"Авторизация нового пользователя, id - {message.from_user.id}")
    if dbcon.check_user_indb(message):
        print("user find")
        bot.send_message(message.from_user.id, "Это бот для учета баланса VPN сервиса VPN_by_Prokin.",
                         reply_markup=tg_keyboard.main_keyboard())
        dbcon.set_status(message, 20)
    else:
        print("Зарегистрирован новый пользователь!")
        bot.send_message(message.from_user.id, "Это бот для учета баланса VPN сервиса VPN_by_Prokin.",
                         reply_markup=tg_keyboard.main_keyboard())
        dbcon.add_new_user(message)
        dbcon.set_status(message, 20)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, messages.help_message, parse_mode="MARKDOWN")


@bot.message_handler(commands=['admin'])
def send_message(message):
    if message.from_user.id != 758952233:
        bot.send_message(message.from_user.id, "Отказано в доступе")
    elif message.from_user.id == 758952233:
        bot.send_message(message.from_user.id, "Выполнен вход в админ-панель",
                         reply_markup=tg_keyboard.admin_keyboard())
        dbcon.set_status(message, 99)
    else:
        bot.send_message(message.from_user.id, "Неопознанная ошибка")


#@bot.message_handler(commands=['auth_'])
#def send_auth(message):
#    dbcon.set_status(message, 10)
#    bot.send_message(message.from_user.id, "Введите Ваш токен авторизации")
#   dbcon.set_status(message, 11) # статус ожидания токена

# Статусы
# 10 - статус первого входа в бот
# 11 - статус ожидания токена
# 20 - статус главного меню
# 30 - окно сообщения в ТП
# 40 - список последних операций
# 50 - окно управления ключами
# 99 - админ-панель
# 
#
#
#


@bot.message_handler(func=lambda message: True)
def status(message):
    logger.logger(f"Пользователь {message.from_user.id} написал - {message.text}")
    user_status = dbcon.get_status(message)
    print(message.from_user.id, user_status, message.text)

    if user_status == 20:

        if message.text == "Баланс":
            dbcon.calc_balances()
            balance = dbcon.get_user_balance(message)
            bot.send_message(message.from_user.id, f"Ваш баланс {balance} руб.",
                             reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Написать в поддержку":
            dbcon.set_status(message, 30)
            bot.send_message(message.from_user.id, "Напишите Ваше сообщение")

        elif message.text == "Пополнить":
            bot.send_message(message.from_user.id, "СБП `+79635122453` Тинькофф🙂", parse_mode="MARKDOWN")

        elif message.text == "Трафик":
            traffic = dbcon.get_user_traffic(message)
            bot.send_message(message.from_user.id, f"За последние 30 дней загружено {traffic}", parse_mode="MARKDOWN")

        elif message.text == "Последние операции":
            dbcon.set_status(message, 40)
            bot.send_message(message.from_user.id, "Введите количество операций:",
                             reply_markup=tg_keyboard.num_keyboard())

        elif message.text == "Заработать":
            dbcon.set_status(message, 60)
            bot.send_message(message.from_user.id, "Переход...", reply_markup=tg_keyboard.make_money())

        elif message.text == "Ключ VPN":

            if dbcon.get_user_balance(message) > -5:

                dbcon.set_status(message, 50)
                bot.send_message(message.from_user.id, "Проверяем Ваши ключи...")
                keys = dbcon.get_user_vpn_keys(message)
                print(keys)
                if keys == []:
                    dbcon.set_status(message, 51)
                    bot.send_message(message.from_user.id,
                                     "На данный момент ключей не зарегистрировано.\nЖелаете зарегистрировать?",
                                     reply_markup=tg_keyboard.yes_or_no_keyboard())
                elif keys != []:
                    user_keys = str()
                    for key in keys:
                        user_keys = user_keys + f"Ключ для подключения:\n`{key[0]}`\n-----------\n"

                    dbcon.set_status(message, 20)
                    bot.send_message(message.from_user.id, user_keys, parse_mode="MARKDOWN",
                                     reply_markup=tg_keyboard.main_keyboard())
                    bot.send_message(message.from_user.id, "Инструкция по подключению - /help")
            else:
                bot.send_message(message.from_user.id,
                                 "Ваш баланс менее -5 рублей, пожалуйста, пополните баланс для создания нового ключа",
                                 parse_mode="MARKDOWN", reply_markup=tg_keyboard.main_keyboard())

        else:
            bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                             reply_markup=tg_keyboard.main_keyboard())

    elif user_status == 30:
        task_id = dbcon.create_support_task(message)
        bot.send_message(758952233, f"Пользователь {message.from_user.id} оставил сообщение:\n{message.text}")
        dbcon.set_status(message, 20)
        bot.send_message(message.from_user.id, f"Ваше обращение № {task_id} зарегистрировано.",
                         reply_markup=tg_keyboard.main_keyboard())

    elif user_status == 40:
        operations_list = dbcon.get_operations_user(message, message.text)
        operations = str()
        for operation in operations_list:
            operations = operations + f"-----------\nID операции: {operation[0]}\nСумма: {operation[1]} руб.\nДата: {operation[2]}\nТип операции: {operation[3]}\n"
        bot.send_message(message.from_user.id, operations, parse_mode='html', reply_markup=tg_keyboard.main_keyboard())
        dbcon.set_status(message, 20)

    elif user_status == 51:
        if message.text == "Да":
            bot.send_message(message.from_user.id, "Выполняется регистрация нового ключа...")
            dbcon.create_new_key(message)
            keys = dbcon.get_user_vpn_keys(message)
            user_keys = str()
            for key in keys:
                user_keys = user_keys + f"-----------\nКлюч:\n`{key[0]}`"

            dbcon.set_status(message, 20)
            bot.send_message(message.from_user.id, user_keys, parse_mode="MARKDOWN",
                             reply_markup=tg_keyboard.main_keyboard())
            bot.send_message(message.from_user.id, "Информацию по активации ключа можно получить в команде /help",
                             reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Нет":
            bot.send_message(message.from_user.id, "Отмена...", reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)

    elif user_status == 60:
        if message.text == "Реферальный код":
            bot.send_message(message.from_user.id, "В разработке", reply_markup=tg_keyboard.make_money())

        elif message.text == "Задания":
            bot.send_message(message.from_user.id, "В разработке", reply_markup=tg_keyboard.make_money())

        elif message.text == "Колесо фортуны":
            keyboard = telebot.types.InlineKeyboardMarkup()
            url_button = telebot.types.InlineKeyboardButton(text="Крутить колесо", url="http://185.246.118.85")
            keyboard.add(url_button)
            bot.send_message(message.chat.id, "Крутить колесо!", reply_markup=keyboard)

            bot.send_message(message.from_user.id, "В разработке", reply_markup=tg_keyboard.make_money())

        elif message.text == "Пост в соц.сети":
            bot.send_message(message.from_user.id, "В разработке", reply_markup=tg_keyboard.make_money())

        elif message.text == "Вернуться":
            bot.send_message(message.from_user.id, "Переход в главное меню", reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)

        else:
            dbcon.set_status(message, 20)
            bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                             reply_markup=tg_keyboard.main_keyboard())



    elif user_status == 99:
        if message.text == "Список пользователей":
            users_list = dbcon.get_list_users()
            users = str()
            for user in users_list:
                users = users + f"{user[3]}, {user[0]}, {user[1]}, баланс: {user[2]} руб.\n---------\n"
            bot.send_message(message.from_user.id, users, parse_mode="MARKDOWN")

        elif message.text == "Выход из админки":
            dbcon.set_status(message, 20)
            bot.send_message(message.from_user.id, f"Выход...", reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Пополнить баланс пользователя":
            dbcon.set_status(message, 97)
            bot.send_message(message.from_user.id, f"Введите ID клиента и сумму в виде: 24 500")

        elif message.text == "Управление ключами VPN":
            dbcon.set_status(message, 100)
            bot.send_message(message.from_user.id, "Переход в управление ключами",
                             reply_markup=tg_keyboard.admin_keyboard_keys())

        elif message.text == "Логи":
            bot.send_message(message.from_user.id, "Отправляю логи...")
            file = logger.get_file_log()
            bot.send_document(message.from_user.id, file)

        elif message.text == "Выручка":
            money_all = dbcon.execute_query("select sum(summ) from operations where type = 2")[0]
            money_last_mounth = dbcon.execute_query(
                "select sum(summ) from operations where type = 2 and operation_date > (SELECT (NOW() - interval '1 months'))")[
                0]
            bot.send_message(message.from_user.id,
                             f"Выручка за последний месяц: {money_last_mounth} руб.\nВыручка за все время: {money_all} руб.")

        elif message.text == "Написать сообщение пользователю":
            dbcon.set_status(message, 95)
            bot.send_message(message.from_user.id, f"Введите ID клиента и cообщение")


        else:
            bot.send_message(message.from_user.id, f"Я вас не понял", reply_markup=tg_keyboard.admin_keyboard())

    elif user_status == 97:
        dbcon.set_status(message, 96)
        data = message.text.split()
        id = data[0]
        summ = data[1]
        bot.send_message(message.from_user.id, f"Пополнить ID {id} на сумму {summ} руб. Верно?",
                         reply_markup=tg_keyboard.yes_or_no_keyboard())
        dbcon.insert_in_db(f"insert into operation_buffer values ({id}, {summ})")

    elif user_status == 96:
        if message.text == "Да":
            dbcon.add_money_to_user_from_buffer(message)
            dbcon.insert_in_db("delete from operation_buffer")
            bot.send_message(message.from_user.id, f"Баланс успешно пополнен",
                             reply_markup=tg_keyboard.admin_keyboard())
            dbcon.calc_balances()
            creds = dbcon.execute_query("select * from operation_buffer")

            try:
                telegram_id = dbcon.get_user_telegram_id(creds[0])[0]
                bot.send_message(telegram_id, f"Ваш баланс пополнен на {creds[1][0]} руб.\nБлагодарим за сотрудничество!")
                bot.send_message(message.from_user.id, "Сообщение успешно отправлено!",
                                 reply_markup=tg_keyboard.admin_keyboard())
                dbcon.set_status(message, 99)
            except Exception as error:
                bot.send_message(message.from_user.id, f"Не удалось получить telegram_id пользователя\n`{error}`",
                                 reply_markup=tg_keyboard.admin_keyboard())
                dbcon.set_status(message, 99)
            dbcon.set_status(message, 99)

        elif message.text == "Нет":
            dbcon.insert_in_db("delete from operation_buffer")
            dbcon.set_status(message, 99)
            bot.send_message(message.from_user.id, "Отмена", reply_markup=tg_keyboard.admin_keyboard())

        else:
            dbcon.insert_in_db("delete from operation_buffer")
            dbcon.set_status(message, 99)
            bot.send_message(message.from_user.id, "Не верный ответ", reply_markup=tg_keyboard.admin_keyboard())

    elif user_status == 95:
        id = message.text.split(" ")[0]
        text_message = message.text.split(" ", 1)[1:][0]
        try:
            telegram_id = dbcon.get_user_telegram_id(id)[0]
            bot.send_message(telegram_id, f"{text_message}")
            bot.send_message(message.from_user.id, "Сообщение успешно отправлено!",
                             reply_markup=tg_keyboard.admin_keyboard())
            dbcon.set_status(message, 99)
        except Exception as error:
            bot.send_message(message.from_user.id, f"Не удалось получить telegram_id пользователя\n`{error}`",
                             reply_markup=tg_keyboard.admin_keyboard())
            dbcon.set_status(message, 99)

    else:
        bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                         reply_markup=tg_keyboard.main_keyboard())
        dbcon.set_status(message, 20)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help",
                     reply_markup=tg_keyboard.main_keyboard())
    dbcon.set_status(message, 20)


bot.infinity_polling()
