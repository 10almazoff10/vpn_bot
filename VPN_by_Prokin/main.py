#!/usr/bin/python

import telebot
from telebot.types import LabeledPrice, ShippingOption
from threading import Thread
from botApp.text import tg_keyboard, messages
from botApp.commands import dbcon
from botApp.logs import logger
from backend import background
from botApp import config

# Run Backend
backend = Thread(target=background.run_backend)
backend.start()

### Loading config

API_TOKEN = config.API_KEY
bot = telebot.TeleBot(API_TOKEN)

### Payment data

provider_token = config.PROVIDER_TOKEN

# More about Payments: https://core.telegram.org/bots/payments

prices_1 = [LabeledPrice(label='Доступ на 1 месяц', amount=7500)]
prices_2 = [LabeledPrice(label='Доступ на 3 месяца', amount=22500)]
prices_3 = [LabeledPrice(label='Доступ на 6 месяцев', amount=40500)]
shipping_options = [
    ShippingOption(id='instant', title='WorldWide Teleporter').add_price(LabeledPrice('Teleporter', 1000)),
    ShippingOption(id='pickup', title='Local pickup').add_price(LabeledPrice('Pickup', 300))]


###Admin
ADMIN_ID = config.ADMIN_ID


@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.logger(f"Авторизация нового пользователя, id - {message.from_user.id}")
    if dbcon.check_user_indb(message):
        bot.send_message(message.from_user.id,
                         messages.hello_message,
                         reply_markup=tg_keyboard.main_keyboard())
        dbcon.set_status(message, 20)
    else:
        bot.send_message(message.from_user.id,
                         messages.hello_message,
                         reply_markup=tg_keyboard.main_keyboard())
        logger.logger(message)
        bot.send_message(ADMIN_ID, f"""Зарегистрирован новый пользователь
                                            {message.from_user.id}, {message.from_user.first_name}""")
        dbcon.add_new_user(message)
        dbcon.set_status(message, 20)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, messages.help_message, parse_mode="MARKDOWN")


@bot.message_handler(commands=['admin'])
def send_message(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.from_user.id, "Отказано в доступе")
    elif message.from_user.id == ADMIN_ID:
        bot.send_message(message.from_user.id, "Выполнен вход в админ-панель",
                         reply_markup=tg_keyboard.admin_keyboard())
        dbcon.set_status(message, ADMIN_MENU)
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

### Statuses

MAIN_MENU = 20
CREATE_MESSAGE_TO_SUPPORT = 30
GET_OPERATIONS_REQUEST = 40
PROMO_CODE = 60
CHECK_KEYS = 50
DONT_HAVE_KEYS = 51
ADMIN_MENU = 99

BROADCAST = 94

### Balances

MINIMAL_BALANCE = -5


@bot.message_handler(func=lambda message: True)
def status(message):
    sender_telegram_id = message.from_user.id
    logger.logger(f"Пользователь {sender_telegram_id} написал - {message.text}")
    user_status = dbcon.get_status(message)


    if user_status == MAIN_MENU:

        if message.text == "Баланс":
            dbcon.calc_balances()
            balance = dbcon.get_user_balance(sender_telegram_id)
            bot.send_message(sender_telegram_id, f"Ваш баланс {balance} руб.",
                             reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Написать в поддержку":
            dbcon.set_status(message, CREATE_MESSAGE_TO_SUPPORT)
            bot.send_message(sender_telegram_id, "Напишите Ваше сообщение\nМаксимальная длина одного сообщения 100 символов", reply_markup=telebot.types.ReplyKeyboardRemove())

        elif message.text == "Пополнить":
            user_id = dbcon.get_user_id(sender_telegram_id)
            #bot.send_message(sender_telegram_id, f"СБП `+79635122453` Тинькофф🙂\nВ комментарии к платежу пожалуйста укажите - `{user_id}`", parse_mode="MARKDOWN")
            logger.logger(f"Пользователь {sender_telegram_id} запросил варианты оплаты")

            bot.send_message(message.chat.id,
                             "Переход к форме оплаты...", parse_mode='Markdown')

            bot.send_invoice(message.chat.id,  # chat_id
                'Доступ к VPN на 1 месяц',  # title
                ' Самый быстрый VPN сервер',  # description
                '00001',  # invoice_payload
                provider_token,  # provider_token
                'RUB',  # currency
                prices_1, )

            bot.send_invoice(
                message.chat.id,  # chat_id
                'Доступ к VPN на 3 месяца',  # title
                '3 месяца доступа к лучшему VPN',  # description
                '00001',  # invoice_payload
                provider_token,  # provider_token
                'RUB',  # currency
                prices_2, )

            bot.send_invoice(
                message.chat.id,  # chat_id
                'Доступ к VPN на 6 месяцев',  # title
                ' Скидка 10%',  # description
                '00001',  # invoice_payload
                provider_token,  # provider_token
                'RUB',  # currency
                prices_3, )

        elif message.text == "Трафик":
            traffic = dbcon.get_user_traffic(message)
            bot.send_message(sender_telegram_id, f"За последние 30 дней загружено `{traffic[0]}`", parse_mode="MARKDOWN")

        elif message.text == "Последние операции":
            dbcon.set_status(message, GET_OPERATIONS_REQUEST)
            bot.send_message(sender_telegram_id, "Введите количество операций:",
                             reply_markup=tg_keyboard.num_keyboard())

        elif message.text == "Заработать":
            dbcon.set_status(message, PROMO_CODE)
            bot.send_message(sender_telegram_id, "Переход...", reply_markup=tg_keyboard.make_money())

        elif message.text == "Ключ VPN":

            if dbcon.get_user_balance(sender_telegram_id) > MINIMAL_BALANCE:

                dbcon.set_status(message, CHECK_KEYS)
                bot.send_message(sender_telegram_id, "Проверяем Ваш ключ...")
                key = dbcon.get_user_vpn_key(sender_telegram_id)
                user_key = f"Ключ для подключения:\n`{key}`"
                dbcon.set_status(message, MAIN_MENU)
                bot.send_message(sender_telegram_id, user_key, parse_mode="MARKDOWN",
                                     reply_markup=tg_keyboard.main_keyboard())
                bot.send_message(sender_telegram_id, "Инструкция по подключению - /help")

            else:
                bot.send_message(sender_telegram_id,
                                 f"Ваш баланс менее {MINIMAL_BALANCE} рублей, пожалуйста, пополните баланс для создания нового ключа",
                                 parse_mode="MARKDOWN", reply_markup=tg_keyboard.main_keyboard())

        else:
            bot.send_message(sender_telegram_id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                             reply_markup=tg_keyboard.main_keyboard())

    elif user_status == CREATE_MESSAGE_TO_SUPPORT:
        if len(message.text) < 100:
            task_id = dbcon.create_support_task(message)
            bot.send_message(ADMIN_ID, f"Пользователь {sender_telegram_id} оставил сообщение:\n{message.text}")
            dbcon.set_status(message, MAIN_MENU)
            bot.send_message(sender_telegram_id, f"Ваше обращение № {task_id} зарегистрировано.",
                           reply_markup=tg_keyboard.main_keyboard())
        else:
            bot.send_message(sender_telegram_id, "Максимальная длина сообщения 100 символов.")
            dbcon.set_status(message, MAIN_MENU)

    elif user_status == GET_OPERATIONS_REQUEST:
        try:
            if len(message.text) < 5:
                operationsCount = int(message.text)
                if operationsCount > 30:
                    operationsCount = 31
            else:
                bot.send_message(ADMIN_ID,
                                 f"Пользователь некорректно ввел количество операций\nПользователь: {sender_telegram_id}\nТекст сообщения: {message.text}")
                bot.send_message(sender_telegram_id, "Введено неверное количество операций",
                             reply_markup=tg_keyboard.num_keyboard())
        except Exception as error:
            bot.send_message(ADMIN_ID,
                             f"Пользователь некорректно ввел количество операций\nПользователь: {sender_telegram_id}\nТекст сообщения: {message.text}")
            bot.send_message(sender_telegram_id,
                             "Введено неверное количество операций",
                             reply_markup=tg_keyboard.num_keyboard())

        if int(operationsCount) <= 30 and int(operationsCount) > 0:
            operations_list = dbcon.get_operations_user(message, message.text)
            operations = str()
            for operation in operations_list:
                operations = operations + f"ID операции: `{operation[0]}`\nСумма: {operation[1]} руб.\nДата: {operation[2]}\nТип операции: {operation[3]}\n\n"

            bot.send_message(sender_telegram_id, operations, parse_mode='MARKDOWN', reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, MAIN_MENU)

        elif int(operationsCount) > 30 or int(operationsCount) < 0:
            bot.send_message(sender_telegram_id, messages.maxOperations,
                             reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, MAIN_MENU)

        else:
            bot.send_message(sender_telegram_id, messages.notUnderstand,
                             reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, MAIN_MENU)

    elif user_status == DONT_HAVE_KEYS:
        if message.text == "Да":
            bot.send_message(sender_telegram_id, "Выполняется регистрация ключа...")
            user_key = dbcon.get_user_vpn_key(sender_telegram_id)
            bot.send_message(sender_telegram_id, user_key, parse_mode="MARKDOWN",
                             reply_markup=tg_keyboard.main_keyboard())
            bot.send_message(sender_telegram_id, "Информацию по активации ключа можно получить в команде /help",
                             reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, MAIN_MENU)


        elif message.text == "Нет":
            bot.send_message(sender_telegram_id, "Отмена...", reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, MAIN_MENU)

    elif user_status == PROMO_CODE:
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
            dbcon.set_status(message, MAIN_MENU)

        else:
            dbcon.set_status(message, MAIN_MENU)
            bot.send_message(sender_telegram_id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                             reply_markup=tg_keyboard.main_keyboard())



    elif user_status == ADMIN_MENU:
        if message.text == "Пользователи":
            active_users, disabled_users = dbcon.get_list_users_with_state()
            active = str()
            disabled = str()
            active_count = 0
            disabled_count = 0

            for user in active_users:
                active_count += 1
                try:
                    key = user[5]
                except:
                    key = ""
                if key == "" or key == None:
                    key = "ключа нет"
                else:
                    key = f"{key[:7]}.."
                active = active + f"{user[3]}, {user[0]}, баланс: {user[2]} руб. ключ - {key}\n"

            for user in disabled_users:
                try:
                    key = user[5]
                except:
                    key = ""
                if key == "":
                    key = "ключа нет"
                else:
                    key = f"{key[:5]}.."
                disabled_count += 1
                disabled = disabled + f"{user[3]}, {user[0]}, баланс: {user[2]} руб. ключ - {key}\n"

            message_with_users = f"Активные пользователи: {active_count}\n{active}\nЗаблокированные пользователи: {disabled_count}\n{disabled}"
            bot.send_message(sender_telegram_id, message_with_users, parse_mode="MARKDOWN")

        elif message.text == "Выход из админки":
            dbcon.set_status(message, 20)
            bot.send_message(sender_telegram_id, f"Выход...", reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Пополнить баланс":
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
            money_all = dbcon.execute_query("select sum(summ) from operations where  type in (2,6)")[0]
            money_last_mounth = dbcon.execute_query(
                "select sum(summ) from operations where type in (2,6) and operation_date > (SELECT (NOW() - interval '1 months'))")[0]
            bot.send_message(sender_telegram_id,
                             f"Выручка за последний месяц: {money_last_mounth} руб.\nВыручка за все время: {money_all} руб.")

        elif message.text == "Написать сообщение":
            dbcon.set_status(message, 95)
            bot.send_message(sender_telegram_id, f"Введите ID клиента и cообщение")

        elif message.text == "Рассылка":
            dbcon.set_status(message, BROADCAST)
            bot.send_message(sender_telegram_id, f"Введите текст сообщения")

        elif message.text == "Статистика":
            connection_count = dbcon.get_count_connection_last_day()
            bot.send_message(sender_telegram_id, f"За последние сутки обработано {connection_count} коннектов")


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
                dbcon.set_status(message, ADMIN_MENU)
            except Exception as error:
                bot.send_message(sender_telegram_id, f"Не удалось получить telegram_id пользователя\n`{error}`",
                                 reply_markup=tg_keyboard.admin_keyboard())
                dbcon.set_status(message, ADMIN_MENU)
            dbcon.set_status(message, ADMIN_MENU)

        elif message.text == "Нет":
            dbcon.insert_in_db("delete from operation_buffer")
            dbcon.set_status(message, ADMIN_MENU)
            bot.send_message(sender_telegram_id, "Отмена", reply_markup=tg_keyboard.admin_keyboard())

        else:
            dbcon.insert_in_db("delete from operation_buffer")
            dbcon.set_status(message, ADMIN_MENU)
            bot.send_message(sender_telegram_id, "Не верный ответ", reply_markup=tg_keyboard.admin_keyboard())

    elif user_status == 95:
        id = message.text.split(" ")[0]
        text_message = message.text.split(" ", 1)[1:][0]
        try:
            telegram_id = dbcon.get_user_telegram_id(id)[0]
            bot.send_message(telegram_id, f"{text_message}")
            bot.send_message(sender_telegram_id, "Сообщение успешно отправлено!",
                             reply_markup=tg_keyboard.admin_keyboard())
            dbcon.set_status(message, ADMIN_MENU)
        except Exception as error:
            bot.send_message(sender_telegram_id, f"Не удалось получить telegram_id пользователя\n`{error}`",
                             reply_markup=tg_keyboard.admin_keyboard())
            dbcon.set_status(message, ADMIN_MENU)

    elif user_status == BROADCAST:
        text = message.text
        list_telegram_id = dbcon.get_telegram_id_users()
        counter_done = 0
        counter_error = 0
        for telegram_id in list_telegram_id:
            try:
                bot.send_message(telegram_id[0], text)
                counter_done += 1
            except Exception as error:
                counter_error += 1
                logger.logger(f"Ошибка отправки сообщения пользователю\n{error}")

        bot.send_message(sender_telegram_id, f"Успешно отправлено: {counter_done}\nОшибка отправки: {counter_error}",
                                    reply_markup=tg_keyboard.admin_keyboard())
        dbcon.set_status(message, ADMIN_MENU)


    else:
        bot.send_message(sender_telegram_id, "Не понял Вас, воспользуйтесь /help\nВозвращение в главное меню...",
                         reply_markup=tg_keyboard.main_keyboard())
        dbcon.set_status(message, MAIN_MENU)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])

@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                              error_message='Oh, seems like our Dog couriers are having a lunch right now. Try again later!')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    telegram_id = message.from_user.id
    summ = message.successful_payment.total_amount / 100
    try:
        dbcon.add_money_to_user_from_pay_form(telegram_id, summ)
        bot.send_message(message.chat.id,
                         'Платеж успешно зачислен на ваш счет в размере `{} {}`'.format(
                             message.successful_payment.total_amount / 100, message.successful_payment.currency),
                         parse_mode='Markdown')
    except Exception as error:
        logger.logger(f"Ошибка при оплате\n{error}")
        bot.send_message(ADMIN_ID, f'Не удалось зачислить платеж пользователя {telegram_id} на сумму {summ}')
        bot.send_message(message.chat.id,
                         'Ошибка платежа, информация передана разработчикам, в ближайшее время деньги будут зачислены в размере `{} {}`'.format(
                             message.successful_payment.total_amount / 100, message.successful_payment.currency),
                         parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.from_user.id, "Не понял Вас, воспользуйтесь /help",
                     reply_markup=tg_keyboard.main_keyboard())
    dbcon.set_status(message, 20)


logger.logger("Запуск бота...")
bot.infinity_polling()
