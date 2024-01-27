#!/usr/bin/python

import telebot
import config, dbcon, tg_keyboard, messages
API_TOKEN = config.API_KEY

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if dbcon.check_user_indb(message):
        print("user find")
        bot.send_message(message.from_user.id, "Это бот для учета баланса VPN сервиса VPN.by_Prokin.",reply_markup=tg_keyboard.main_keyboard())
        dbcon.set_status(message, 20)
    else:
        print("Зарегистрирован новый пользователь!")
        bot.send_message(message.from_user.id, "Это бот для учета баланса VPN сервиса VPN.by_Prokin.",reply_markup=tg_keyboard.main_keyboard())
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
        bot.send_message(message.from_user.id, "Выполнен вход в админ-панель", reply_markup=tg_keyboard.admin_keyboard())
        dbcon.set_status(message, 99)
    else:
        bot.send_message((message.from_user.id, "Неопознанная ошибка"))

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
    user_status = dbcon.get_status(message)
    print(message.from_user.id, user_status, message.text)
    
    if user_status == 20:
        if message.text == "Баланс":
            dbcon.calc_balances()
            balanse = dbcon.get_user_balance(message)
            bot.send_message(message.from_user.id, f"Ваш баланс {balanse} руб.",reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Написать в поддержку":
            dbcon.set_status(message, 30)
            bot.send_message(message.from_user.id, "Напишите Ваше сообщение")
        
        elif message.text == "Пополнить":
            bot.send_message(message.from_user.id, "СБП `+79635122453` Тинькофф🙂", parse_mode="MARKDOWN")
        
        elif message.text == "Последние операции":
            dbcon.set_status(message, 40)
            bot.send_message(message.from_user.id, "Введите количество операций:", reply_markup=tg_keyboard.num_keyboard())
        
        elif message.text == "Получить ключ для VPN":

            if dbcon.get_user_balance(message) > -5:

                dbcon.set_status(message, 50)
                bot.send_message(message.from_user.id, "Проверяем Ваши ключи...")
                keys = dbcon.get_user_vpn_keys(message)
                print(keys)
                if keys == []:
                    dbcon.set_status(message, 51)
                    bot.send_message(message.from_user.id, "На данный момент ключей не зарегистрировано.\nЖелаете зарегистрировать?",reply_markup=tg_keyboard.yes_or_no_keyboard())
                elif keys != []:
                    user_keys = str()
                    for key in keys:
                        user_keys = user_keys + f"Ключ для подключения:\n`{key[0]}`\n-----------\n"
                    
                    dbcon.set_status(message, 20)
                    bot.send_message(message.from_user.id, user_keys, parse_mode="MARKDOWN",reply_markup=tg_keyboard.main_keyboard())
                    bot.send_message(message.from_user.id, "Инструкция по подключению - /help")
            else:
                bot.send_message(message.from_user.id, "Ваш баланс менее -5 рублей, пожалуйста, пополните баланс для создания нового ключа", parse_mode="MARKDOWN",reply_markup=tg_keyboard.main_keyboard())
        
        else:
            bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",reply_markup=tg_keyboard.main_keyboard())            

    elif user_status == 30:
        task_id = dbcon.create_support_task(message)
        dbcon.set_status(message, 20)
        bot.send_message(message.from_user.id, f"Ваше обращение № {task_id} зарегистрировано.",reply_markup=tg_keyboard.main_keyboard())

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
            bot.send_message(message.from_user.id, user_keys, parse_mode="MARKDOWN", reply_markup=tg_keyboard.main_keyboard())
            bot.send_message(message.from_user.id, "Информацию по активации ключа можно получить в команде /help",reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Нет":
            bot.send_message(message.from_user.id, "Отмена...",reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)


    elif user_status == 99:
        if message.text == "Список пользователей":
            users_list = dbcon.get_list_users()
            users = str()
            for user in users_list:
                users = users + f"{user[3]}, {user[0]}, {user[1]}, баланс: {user[2]} руб.\n---------\n"
            bot.send_message(message.from_user.id, users, parse_mode="MARKDOWN")
        
        elif message.text == "Выход из админки":
            dbcon.set_status(message, 20)
            bot.send_message(message.from_user.id, f"Выход...",reply_markup=tg_keyboard.main_keyboard())
        
        elif message.text == "Создать токен пользователя":
            dbcon.set_status(message, 98)
            bot.send_message(message.from_user.id, f"Введите имя клиента")

        elif message.text == "Пополнить баланс пользователя":
            dbcon.set_status(message, 97)
            bot.send_message(message.from_user.id, f"Введите ID клиента и сумму в виде: 24 500")

        elif message.text == "Управление ключами VPN":
            dbcon.set_status(message, 100)
            bot.send_message(message.from_user.id,"Переход в управление ключами",reply_markup=tg_keyboard.admin_keyboard_keys())

        else:
            bot.send_message(message.from_user.id, f"Я вас не понял",reply_markup=tg_keyboard.admin_keyboard())

    elif user_status >= 100 and user_status <= 110:

        if message.text == "Список ключей":
            pass
        elif message.text == "Трафик по ключу":
            pass
        elif message.text == "Создать ключ":
            pass
        elif message.text == "Удалить ключ":
            pass
        
        elif message.text == "Выход":
            dbcon.set_status(message, 99)
            bot.send_message(message.from_user.id, "Переход в админ-панель",reply_markup=tg_keyboard.admin_keyboard())
        else:
            dbcon.set_status(message, 99)
            bot.send_message(message.from_user.id, "Переход в админ-панель",reply_markup=tg_keyboard.admin_keyboard())


    elif user_status == 98:
        dbcon.set_status(message, 99)
        token = dbcon.create_user_token(message)
        bot.send_message(message.from_user.id, "Токен успешно создан")
        bot.send_message(message.from_user.id, token)

    elif user_status == 97:
        dbcon.set_status(message, 96)
        data = message.text.split()
        id = data[0]
        summ = data[1]
        bot.send_message(message.from_user.id, f"Пополнить ID {id} на сумму {summ} руб. Верно?",reply_markup=tg_keyboard.yes_or_no_keyboard())
        dbcon.insert_in_db(f"insert into operation_buffer values ({id}, {summ})")

    elif user_status == 96:
        if message.text == "Да":
            dbcon.add_money_to_user_from_buffer(message)
            dbcon.insert_in_db("delete from operation_buffer")
            bot.send_message(message.from_user.id, f"Баланс успешно пополнен",reply_markup=tg_keyboard.admin_keyboard())
            dbcon.calc_balances()
            dbcon.set_status(message, 99)

        elif message.text == "Нет":
            dbcon.insert_in_db("delete from operation_buffer")
            dbcon.set_status(message, 99)
            bot.send_message(message.from_user.id, "Отмена",reply_markup=tg_keyboard.admin_keyboard())

        else:
            dbcon.insert_in_db("delete from operation_buffer")
            dbcon.set_status(message, 99)
            bot.send_message(message.from_user.id, "Не верный ответ",reply_markup=tg_keyboard.admin_keyboard())

    else:
        bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",reply_markup=tg_keyboard.main_keyboard())
        dbcon.set_status(message, 20)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help",reply_markup=tg_keyboard.main_keyboard())
    dbcon.set_status(message, 20)

bot.infinity_polling()