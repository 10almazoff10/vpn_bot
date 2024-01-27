#!/usr/bin/python

import telebot
import config, dbcon, tg_keyboard, messages

API_TOKEN = config.API_KEY

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if dbcon.check_user_indb(message):
        print("user find")
        bot.send_message(message.from_user.id, "Это бот для учета баланса VPN сервиса VPN.by_Prokin. \nПожалуйста авторизуйтесь /auth")
        dbcon.set_status(message, 10)
    else:
        print("user not find")
        bot.send_message(message.from_user.id, "Это бот для учета баланса VPN сервиса VPN.by_Prokin. \nПожалуйста авторизуйтесь /auth")
        dbcon.add_new_user(message)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, messages.help_message)
    


@bot.message_handler(commands=['admin'])
def send_message(message):
    if message.from_user.id != 758952233:
        bot.send_message(message.from_user.id, "Отказано в доступе")
    elif message.from_user.id == 758952233:
        bot.send_message(message.from_user.id, "Выполнен вход в админ-панель", reply_markup=tg_keyboard.admin_keyboard())
        dbcon.set_status(message, 99)
    else:
        bot.send_message((message.from_user.id, "Неопознанная ошибка"))

@bot.message_handler(commands=['auth'])
def send_auth(message):
    dbcon.set_status(message, 10)
    bot.send_message(message.from_user.id, "Введите Ваш токен авторизации")
    dbcon.set_status(message, 11) # статус ожидания токена

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
    print(user_status, message.text)
    if user_status == 11:
        telegram_id = dbcon.check_token(message)
        if telegram_id != "":
            dbcon.user_reg(message)
            user_name = dbcon.user_name(message)
            bot.send_message(message.from_user.id, f"Токен принят, авторизация успешна\nПриветствую, {user_name}",reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, 20)

        else:
            bot.send_message(message.from_user.id, """Токена не существует, либо введен некорректно. 
                                                    Попробуйте снова или обратитесь к администратору""")

    elif user_status == 20:
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
            dbcon.set_status(message, 50)
            bot.send_message(message.from_user.id, "Проверяем Ваши ключи...")
            keys = dbcon.get_user_vpn_keys(message)
            if keys == None:
                dbcon.set_status(message, 51)
                bot.send_message(message.from_user.id, "На данный момент ключей не зарегистрировано.\nЖелаете зарегистрировать?",reply_markup=tg_keyboard.yes_or_no_keyboard())
            elif keys != None:
                user_keys = str()
                for key in keys:
                    user_keys = user_keys + f"Дата регистрации: {key[1]} руб.\nСсылка для подключения: `{key[2]}`\n-----------\n"
                
                dbcon.set_status(message, 20)
                bot.send_message(message.from_user.id, user_keys, parse_mode="MARKDOWN",reply_markup=tg_keyboard.main_keyboard())
                bot.send_message(message.from_user.id, "Инструкия по подключению - /help")

            

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
                user_keys = user_keys + f"-----------\nКлюч: {key[0]}\nДата регистрации: {key[1]} руб.\nДата окончания: {key[2]}"
                
            dbcon.set_status(message, 20)
            bot.send_message(message.from_user.id, user_keys,reply_markup=tg_keyboard.main_keyboard())
            bot.send_message(message.from_user.id, "Информацию по активации ключа можно получить в команде /help",reply_markup=tg_keyboard.main_keyboard())

    elif user_status == 99:
        if message.text == "Список пользователей":
            users_list = dbcon.get_list_users()
            users = str()
            for user in users_list:
                users = users + f"{user[3]}, {user[0]},  баланс {user[2]} руб. \nТокен регистрации `{user[4]}`\n---------\n"
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

        else:
            bot.send_message(message.from_user.id, f"Я вас не понял",reply_markup=tg_keyboard.admin_keyboard())

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
            dbcon.set_status(message, 97)
            bot.send_message(message.from_user.id, f"Введите ID клиента и сумму в виде: 24 500")

        elif message.text == "Отмена":
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