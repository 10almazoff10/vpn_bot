#!/usr/bin/python

import telebot
from threading import Thread
from botApp.text import tg_keyboard, messages
from botApp.commands import dbcon
from botApp.logs import logger
from botApp import config
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
    sender_telegram_id = message.from_user.id
    logger.logger(f"Пользователь {sender_telegram_id} написал - {message.text}")
    user_status = dbcon.get_status(message)

    print(sender_telegram_id, user_status, message.text)

    if user_status == 20:

        if message.text == "Баланс":
            dbcon.calc_balances()
            balance = dbcon.get_user_balance(sender_telegram_id)
            bot.send_message(sender_telegram_id, f"Ваш баланс {balance} руб.",
                             reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Написать в поддержку":
            dbcon.set_status(message, 30)
            bot.send_message(sender_telegram_id, "Напишите Ваше сообщение\nМаксимальная длина одного сообщения 100 символов", reply_markup=telebot.types.ReplyKeyboardRemove())

        elif message.text == "Пополнить":
            bot.send_message(sender_telegram_id, "СБП `+79635122453` Тинькофф🙂", parse_mode="MARKDOWN")

        elif message.text == "Трафик":
            traffic = dbcon.get_user_traffic(message)
            bot.send_message(sender_telegram_id, f"За последние 30 дней загружено `{traffic[0]}`", parse_mode="MARKDOWN")

        elif message.text == "Последние операции":
            dbcon.set_status(message, 40)
            bot.send_message(sender_telegram_id, "Введите количество операций:",
                             reply_markup=tg_keyboard.num_keyboard())

        elif message.text == "Заработать":
            dbcon.set_status(message, 60)
            bot.send_message(sender_telegram_id, "Переход...", reply_markup=tg_keyboard.make_money())

        elif message.text == "Ключ VPN":

            if dbcon.get_user_balance(sender_telegram_id) > -5:

                dbcon.set_status(message, 50)
                bot.send_message(sender_telegram_id, "Проверяем Ваши ключи...")
                keys = dbcon.get_user_vpn_keys(message)
                print(keys)
                if keys == []:
                    dbcon.set_status(message, 51)
                    bot.send_message(sender_telegram_id,
                                     "На данный момент ключей не зарегистрировано.\nЖелаете зарегистрировать?",
                                     reply_markup=tg_keyboard.yes_or_no_keyboard())
                elif keys != []:
                    user_keys = str()
                    for key in keys:
                        user_keys = user_keys + f"Ключ для подключения:\n`{key[0]}`\n-----------\n"

                    dbcon.set_status(message, 20)
                    bot.send_message(sender_telegram_id, user_keys, parse_mode="MARKDOWN",
                                     reply_markup=tg_keyboard.main_keyboard())
                    bot.send_message(sender_telegram_id, "Инструкция по подключению - /help")
            else:
                bot.send_message(sender_telegram_id,
                                 "Ваш баланс менее -5 рублей, пожалуйста, пополните баланс для создания нового ключа",
                                 parse_mode="MARKDOWN", reply_markup=tg_keyboard.main_keyboard())

        else:
            bot.send_message(sender_telegram_id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                             reply_markup=tg_keyboard.main_keyboard())

    elif user_status == 30:
        if len(message.text) < 100:
            task_id = dbcon.create_support_task(message)
            bot.send_message(758952233, f"Пользователь {sender_telegram_id} оставил сообщение:\n{message.text}")
            dbcon.set_status(message, 20)
            bot.send_message(sender_telegram_id, f"Ваше обращение № {task_id} зарегистрировано.",
                           reply_markup=tg_keyboard.main_keyboard())
        else:
            bot.send_message(sender_telegram_id, "Максимальная длина сообщения 100 символов.")
            dbcon.set_status(message, 20)

    elif user_status == 40:
        try:
            if len(message.text) < 5:
                operationsCount = int(message.text)
                if operationsCount > 30:
                    operationsCount = 31
            else:
                bot.send_message(758952233,
                                 f"Пользователь некорректно ввел количество операций\nПользователь: {sender_telegram_id}\nТекст сообщения: {message.text}")
                bot.send_message(sender_telegram_id, "Введено неверное количество операций",
                             reply_markup=tg_keyboard.num_keyboard())
        except Exception as error:
            bot.send_message(758952233,
                             f"Пользователь некорректно ввел количество операций\nПользователь: {sender_telegram_id}\nТекст сообщения: {message.text}")
            bot.send_message(sender_telegram_id,
                             "Введено неверное количество операций",
                             reply_markup=tg_keyboard.num_keyboard())

        if int(operationsCount) <= 30 and int(operationsCount) > 0:
            operations_list = dbcon.get_operations_user(message, message.text)
            operations = str()
            for operation in operations_list:
                operations = operations + f"-----------\nID операции: {operation[0]}\nСумма: {operation[1]} руб.\nДата: {operation[2]}\nТип операции: {operation[3]}\n"
            bot.send_message(sender_telegram_id, operations, parse_mode='html', reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)

        elif int(operationsCount) > 30 or int(operationsCount) < 0:
            bot.send_message(sender_telegram_id, messages.maxOperations,
                             reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)

        else:
            bot.send_message(sender_telegram_id, messages.notUnderstand,
                             reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)

    elif user_status == 51:
        if message.text == "Да":
            bot.send_message(sender_telegram_id, "Выполняется регистрация нового ключа...")
            dbcon.create_new_key(message)
            keys = dbcon.get_user_vpn_keys(message)
            user_keys = str()
            for key in keys:
                user_keys = user_keys + f"-----------\nКлюч:\n`{key[0]}`"

            dbcon.set_status(message, 20)
            bot.send_message(sender_telegram_id, user_keys, parse_mode="MARKDOWN",
                             reply_markup=tg_keyboard.main_keyboard())
            bot.send_message(sender_telegram_id, "Информацию по активации ключа можно получить в команде /help",
                             reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Нет":
            bot.send_message(sender_telegram_id, "Отмена...", reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)

    elif user_status == 60:
        if message.text == "Реферальный код":
            bot.send_message(sender_telegram_id, "В разработке", reply_markup=tg_keyboard.make_money())

        elif message.text == "Задания":
            bot.send_message(sender_telegram_id, "В разработке", reply_markup=tg_keyboard.make_money())

        elif message.text == "Колесо фортуны":
            keyboard = telebot.types.InlineKeyboardMarkup()
            url_button = telebot.types.InlineKeyboardButton(text="Крутить колесо", url="http://185.246.118.85")
            keyboard.add(url_button)
            bot.send_message(message.chat.id, "Крутить колесо!", reply_markup=keyboard)

            bot.send_message(sender_telegram_id, "В разработке", reply_markup=tg_keyboard.make_money())

        elif message.text == "Пост в соц.сети":
            bot.send_message(sender_telegram_id, "В разработке", reply_markup=tg_keyboard.make_money())

        elif message.text == "Вернуться":
            bot.send_message(sender_telegram_id, "Переход в главное меню", reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)

        else:
            dbcon.set_status(message, 20)
            bot.send_message(sender_telegram_id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                             reply_markup=tg_keyboard.main_keyboard())



    elif user_status == 99:
        if message.text == "Список пользователей":
            users_list = dbcon.get_list_users()
            active = str()
            disabled_users = str()
            active_count = 0
            disabled_count = 0
            for user in users_list:
                if user[4] == 0:
                    active_count += 1
                    active = active + f"{user[3]}, {user[0]}, {user[1]}, баланс: {user[2]} руб.\n"
                else:
                    disabled_count += 1
                    disabled_users = disabled_users + f"{user[3]}, {user[0]}, {user[1]}, баланс: {user[2]} руб.\n"

            message_with_users = f"""Активные пользователи: {active_count}\n{active}\nЗаблокированные пользователи: {disabled_count}\n{disabled_users}"""
            bot.send_message(sender_telegram_id, message_with_users, parse_mode="MARKDOWN")

        elif message.text == "Выход из админки":
            dbcon.set_status(message, 20)
            bot.send_message(sender_telegram_id, f"Выход...", reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Пополнить баланс пользователя":
            dbcon.set_status(message, 97)
            bot.send_message(sender_telegram_id, f"Введите ID клиента и сумму в виде: 24 500")

        elif message.text == "Управление ключами VPN":
            dbcon.set_status(message, 100)
            bot.send_message(sender_telegram_id, "Переход в управление ключами",
                             reply_markup=tg_keyboard.admin_keyboard_keys())

        elif message.text == "Логи":
            bot.send_message(sender_telegram_id, "Отправляю логи...")
            file = logger.get_file_log()
            bot.send_document(sender_telegram_id, file)

        elif message.text == "Выручка":
            money_all = dbcon.execute_query("select sum(summ) from operations where type = 2")[0]
            money_last_mounth = dbcon.execute_query(
                "select sum(summ) from operations where type = 2 and operation_date > (SELECT (NOW() - interval '1 months'))")[
                0]
            bot.send_message(sender_telegram_id,
                             f"Выручка за последний месяц: {money_last_mounth} руб.\nВыручка за все время: {money_all} руб.")

        elif message.text == "Написать сообщение пользователю":
            dbcon.set_status(message, 95)
            bot.send_message(sender_telegram_id, f"Введите ID клиента и cообщение")


        else:
            bot.send_message(sender_telegram_id, f"Я вас не понял", reply_markup=tg_keyboard.admin_keyboard())

    elif user_status == 97:
        dbcon.set_status(message, 96)
        data = message.text.split()
        id = data[0]
        summ = data[1]
        bot.send_message(sender_telegram_id, f"Пополнить ID {id} на сумму {summ} руб. Верно?",
                         reply_markup=tg_keyboard.yes_or_no_keyboard())
        dbcon.insert_in_db(f"insert into operation_buffer values ({id}, {summ})")

    elif user_status == 96:
        if message.text == "Да":
            dbcon.add_money_to_user_from_buffer(message)
            creds = dbcon.execute_query("select user_id, summ from operation_buffer")
            print(creds)
            dbcon.insert_in_db("delete from operation_buffer")
            bot.send_message(sender_telegram_id, f"Баланс успешно пополнен",
                             reply_markup=tg_keyboard.admin_keyboard())
            dbcon.calc_balances()

            try:
                telegram_id = dbcon.get_user_telegram_id(creds[0])[0]
                moneyInCome = creds[1]
                bot.send_message(telegram_id, f"Ваш баланс пополнен на {moneyInCome} руб.\nБлагодарим за сотрудничество!")
                bot.send_message(sender_telegram_id, "Сообщение успешно отправлено!",
                                 reply_markup=tg_keyboard.admin_keyboard())
                try:
                    bot.send_message(sender_telegram_id, "Пользователь активирован")
                    dbcon.unblock_user(telegram_id)
                except Exception as error:
                    bot.send_message(sender_telegram_id, f"Ошибка при активации пользователя\n{error}")
                dbcon.set_status(message, 99)
            except Exception as error:
                bot.send_message(sender_telegram_id, f"Не удалось получить telegram_id пользователя\n`{error}`",
                                 reply_markup=tg_keyboard.admin_keyboard())
                dbcon.set_status(message, 99)
            dbcon.set_status(message, 99)

        elif message.text == "Нет":
            dbcon.insert_in_db("delete from operation_buffer")
            dbcon.set_status(message, 99)
            bot.send_message(sender_telegram_id, "Отмена", reply_markup=tg_keyboard.admin_keyboard())

        else:
            dbcon.insert_in_db("delete from operation_buffer")
            dbcon.set_status(message, 99)
            bot.send_message(sender_telegram_id, "Не верный ответ", reply_markup=tg_keyboard.admin_keyboard())

    elif user_status == 95:
        id = message.text.split(" ")[0]
        text_message = message.text.split(" ", 1)[1:][0]
        try:
            telegram_id = dbcon.get_user_telegram_id(id)[0]
            bot.send_message(telegram_id, f"{text_message}")
            bot.send_message(sender_telegram_id, "Сообщение успешно отправлено!",
                             reply_markup=tg_keyboard.admin_keyboard())
            dbcon.set_status(message, 99)
        except Exception as error:
            bot.send_message(sender_telegram_id, f"Не удалось получить telegram_id пользователя\n`{error}`",
                             reply_markup=tg_keyboard.admin_keyboard())
            dbcon.set_status(message, 99)

    else:
        bot.send_message(sender_telegram_id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                         reply_markup=tg_keyboard.main_keyboard())
        dbcon.set_status(message, 20)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help",
                     reply_markup=tg_keyboard.main_keyboard())
    dbcon.set_status(message, 20)

logger.logger("Запуск бота...")
bot.infinity_polling()
