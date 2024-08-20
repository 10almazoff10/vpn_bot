#!/usr/bin/python

import telebot
import monitoring
from telebot.types import LabeledPrice, ShippingOption
from threading import Thread
from botApp.text import tg_keyboard, messages
from botApp.commands import dbcon
from botApp.logs.logger import logger, get_file_log
from backend import background
from botApp import config

# Run Backend
backend = Thread(target=background.run_backend)
backend.start()

# Loading config

API_TOKEN = config.API_KEY
bot = telebot.TeleBot(API_TOKEN)

# Статусы
# 10 - статус первого входа в бот
# 11 - статус ожидания токена
# 20 - статус главного меню
# 30 - окно сообщения в ТП
# 40 - список последних операций
# 50 - окно управления ключами
# 99 - админ-панель

# Statuses

MAIN_MENU = 20
CREATE_MESSAGE_TO_SUPPORT = 30
GET_OPERATIONS_REQUEST = 40
PROMO_CODE = 60
CHECK_KEYS = 50
ADMIN_MENU = 99

BROADCAST = 94

# Balances

MINIMAL_BALANCE = -5

# Payment data

provider_token = config.PROVIDER_TOKEN

# More about Payments: https://core.telegram.org/bots/payments

prices_1 = [LabeledPrice(label='Доступ на 1 месяц', amount=7500)]
prices_2 = [LabeledPrice(label='Доступ на 3 месяца', amount=22500)]
prices_3 = [LabeledPrice(label='Доступ на 6 месяцев', amount=40500)]
shipping_options = [
    ShippingOption(id='instant', title='WorldWide Teleporter').add_price(LabeledPrice('Teleporter', 1000)),
    ShippingOption(id='pickup', title='Local pickup').add_price(LabeledPrice('Pickup', 300))]

# Admin
ADMIN_ID = config.ADMIN_ID

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call)
    if call.data == "get_state_key":
        bot.answer_callback_query(
            call.id,
            "Получаем ключ...")

        state_key = dbcon.get_user_state_vpn_key(call.from_user.id)

        server = state_key[0]
        server_port = state_key[1]
        method = state_key[2]
        password = state_key[3]

        bot.send_message(
            call.from_user.id,
            messages.SEND_STATE_KEY.format(
                server,
                server_port,
                method,
                password),
            parse_mode="MARKDOWN")

    elif call.data == "cb_no":

        bot.answer_callback_query(
            call.id,
            messages.GO_TO_MAIN)

        bot.send_message(
            call.from_user.id,
            messages.GO_TO_MAIN,
            reply_markup=tg_keyboard.main_keyboard())

@bot.message_handler(commands=['start'])

# Ответ пользователю на команду START
# Так же выполняется проверка, существует ли пользователь

def send_welcome(message):

# Создание переменной со значением TelegramID

    sender_telegram_id = message.from_user.id

    logger(
        messages.REGISTER_NEW_USER.format(
            sender_telegram_id))

# Получение информации из БД о существовании пользователя
# Если пользователь существует, то просто отправляется приветственное сообщение
# Если же нет, то выполняется регистрация пользователя

    if dbcon.check_user_indb(sender_telegram_id):

        bot.send_message(
            message.from_user.id,
            messages.hello_message,
            reply_markup=tg_keyboard.main_keyboard())

        dbcon.set_status(
            message,
            MAIN_MENU)

    else:
        bot.send_message(
            message.from_user.id,
            messages.hello_message,
            reply_markup=tg_keyboard.main_keyboard())

        logger(message)

        bot.send_message(
            ADMIN_ID,
            messages.REGISTER_NEW_USER.format(
                message.from_user.id,
                message.from_user.first_name))

        # Создание пользователя в БД
        dbcon.add_new_user(message)

        # Регистрация пользовательски ключей на доступном в данный момент
        # пуле серверов

        if dbcon.reg_user_keys(sender_telegram_id):
            logger(
                messages.REG_KEYS_TRUE.format(
                    sender_telegram_id))
        else:
            bot.send_message(
                ADMIN_ID,
                messages.REG_KEYS_FALSE.format(
                    sender_telegram_id))

        dbcon.set_status(
            message,
            MAIN_MENU)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.from_user.id,
        messages.help_message,
        parse_mode="MARKDOWN")


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



@bot.message_handler(func=lambda message: True)
def status(message):
    sender_telegram_id = message.from_user.id
    logger(message, level="DEBUG")
    logger(f"Пользователь {sender_telegram_id} написал - {message.text}")
    user_status = dbcon.get_status(message)

    if user_status == MAIN_MENU:

        if message.text == "Баланс":
            dbcon.calc_balances()
            balance = dbcon.get_user_balance(sender_telegram_id)
            bot.send_message(sender_telegram_id, f"Ваш баланс {balance} руб.",
                             reply_markup=tg_keyboard.main_keyboard())

        elif message.text == "Написать в поддержку":
            dbcon.set_status(message, CREATE_MESSAGE_TO_SUPPORT)
            bot.send_message(sender_telegram_id,
                             "Напишите Ваше сообщение\nМаксимальная длина одного сообщения 100 символов",
                             reply_markup=telebot.types.ReplyKeyboardRemove())

        elif message.text == "Пополнить":
            logger(f"Пользователь {sender_telegram_id} запросил варианты оплаты")

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

        elif message.text == "Последние операции":
            dbcon.set_status(message, GET_OPERATIONS_REQUEST)
            bot.send_message(sender_telegram_id, "Введите количество операций:",
                             reply_markup=tg_keyboard.num_keyboard())

        elif message.text == "Ключ VPN":

            if dbcon.get_user_balance(sender_telegram_id) > MINIMAL_BALANCE:

                dbcon.set_status(
                    message,
                    CHECK_KEYS)

                bot.send_message(
                    sender_telegram_id,
                    "Проверяем Ваш ключ...")

                key = dbcon.get_user_vpn_key(
                    sender_telegram_id)

                user_key = messages.USER_KEY_MESSAGE.format(key)

                dbcon.set_status(
                    message,
                    MAIN_MENU)

                bot.send_message(
                    sender_telegram_id,
                    user_key,
                    parse_mode="MARKDOWN",
                    reply_markup=tg_keyboard.main_keyboard())

                bot.send_message(
                    sender_telegram_id,
                    "Инструкция по подключению - /help")

                bot.send_message(
                    sender_telegram_id,
                    messages.GET_STATE_KEY,
                    parse_mode="MARKDOWN",
                    reply_markup=tg_keyboard.get_state_key())

            else:
                bot.send_message(sender_telegram_id,
                                 messages.LOW_BALANCE_MESSAGE.format(MINIMAL_BALANCE),
                                 parse_mode="MARKDOWN", reply_markup=tg_keyboard.main_keyboard())

        else:
            bot.send_message(sender_telegram_id,
                             messages.DONT_UNDERSTAND,
                             reply_markup=tg_keyboard.main_keyboard())

    elif user_status == CREATE_MESSAGE_TO_SUPPORT:
        if len(message.text) < 100:
            task_id = dbcon.create_support_task(message)
            id_user = dbcon.get_user_id(sender_telegram_id)
            bot.send_message(ADMIN_ID, f"Пользователь {id_user} оставил сообщение:\n{message.text}")
            dbcon.set_status(message, MAIN_MENU)
            bot.send_message(sender_telegram_id, f"Ваше обращение № {task_id} зарегистрировано.",
                             reply_markup=tg_keyboard.main_keyboard())
        else:
            bot.send_message(sender_telegram_id, "Максимальная длина сообщения 100 символов.")
            dbcon.set_status(message, MAIN_MENU)

    elif user_status == GET_OPERATIONS_REQUEST:
        operations_count = 0
        try:
            if len(message.text) < 5:
                operations_count = int(message.text)
                if operations_count > 30:
                    operations_count = 31
            else:
                bot.send_message(ADMIN_ID,
                                 f"")
                bot.send_message(sender_telegram_id, "Введено неверное количество операций",
                                 reply_markup=tg_keyboard.num_keyboard())
        except Exception as error:
            bot.send_message(ADMIN_ID,
                             messages.BAD_OPERATIONS_COUNT.format(sender_telegram_id, message.text))

            bot.send_message(sender_telegram_id,
                             "Введено неверное количество операций",
                             reply_markup=tg_keyboard.num_keyboard())

        if int(operations_count) <= 30 and int(operations_count) > 0:
            operations_list = dbcon.get_operations_user(message, message.text)
            operations = str()
            for operation in operations_list:
                operations = operations + messages.LIST_OPERATIONS.format(
                    operation[0],
                    operation[1],
                    operation[2],
                    operation[3]
                )

            bot.send_message(
                sender_telegram_id,
                operations,
                parse_mode='MARKDOWN',
                reply_markup=tg_keyboard.main_keyboard())

            dbcon.set_status(message, MAIN_MENU)

        elif int(operations_count) > 30 or int(operations_count) < 0:
            bot.send_message(sender_telegram_id, messages.maxOperations,
                             reply_markup=tg_keyboard.main_keyboard())
            dbcon.set_status(message, MAIN_MENU)

        else:
            bot.send_message(
                sender_telegram_id,
                messages.notUnderstand,
                reply_markup=tg_keyboard.main_keyboard())

            dbcon.set_status(
                message,
                MAIN_MENU)

    elif user_status == ADMIN_MENU:

        if message.text == "Пользователи":
            active_users, disabled_users = dbcon.get_list_users_with_state()
            active = str()
            active_count = 0

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

            active = active.replace("_", "\\_")

            message_with_users = messages.LIST_USERS.format(
                active_count,
                active,
                disabled_users)

            try:
                bot.send_message(
                    sender_telegram_id,
                    message_with_users,
                    parse_mode="MARKDOWN")

            except Exception as error:
                logger(
                    message_with_users,
                    level="DEBUG")

                bot.send_message(
                    sender_telegram_id,
                    str(error),
                    parse_mode="MARKDOWN")

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
            file = get_file_log()
            bot.send_document(sender_telegram_id, file)

        elif message.text == "Выручка":
            money_all = dbcon.execute_query("select sum(summ) from operations where  type in (2,6)")[0]
            money_last_mounth = dbcon.execute_query(
                "select sum(summ) from operations where type in (2,6) and operation_date > (SELECT (NOW() - interval '1 months'))")[
                0]
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
            user_stats = dbcon.get_users_stats()
            message = "```txt\n"
            for user in user_stats:
                message += str(user[0]) + " " + str(user[1]) + " " + str(user[2]) + "\n"
            message += "\n```"
            bot.send_message(sender_telegram_id, f"За последние сутки обработано {connection_count} коннектов")
            bot.send_message(sender_telegram_id, message, parse_mode="MARKDOWN")


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
                bot.send_message(telegram_id,
                                 f"Ваш баланс пополнен на {moneyInCome} руб.\nБлагодарим за сотрудничество!")
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
                logger(f"Ошибка отправки сообщения пользователю\n{error}")

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

        payer = dbcon.get_user_id(telegram_id)
        bot.send_message(ADMIN_ID,
                         'Успешная оплата пользователя `{}` в размере `{} {}`'.format(
                             payer,
                             message.successful_payment.total_amount / 100,
                             message.successful_payment.currency),
                         parse_mode='Markdown')

    except Exception as error:
        logger(f"Ошибка при оплате\n{error}")
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


logger("Запуск приложения бота")
logger(monitoring.SystemInfo().to_json())

if __name__ == "__main__":
    bot.infinity_polling()
