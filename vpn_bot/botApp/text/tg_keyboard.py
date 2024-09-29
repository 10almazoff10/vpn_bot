import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton(text="Написать в поддержку")
    button1 = telebot.types.KeyboardButton(text="Баланс")
    button2 = telebot.types.KeyboardButton(text="Последние операции")
    button3 = telebot.types.KeyboardButton(text="Пополнить")
    button4 = telebot.types.KeyboardButton(text="Ключ VPN")
    button5 = telebot.types.KeyboardButton(text="Трафик")
    button6 = telebot.types.KeyboardButton(text="Управление серверами")
    keyboard.add(button_support, button1)
    keyboard.add(button2, button3)
    keyboard.add(button5, button4)
    keyboard.add(button6)
    return keyboard

def admin_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Пользователи")
    button2 = telebot.types.KeyboardButton(text="Пополнить баланс")
    button3 = telebot.types.KeyboardButton(text="Написать сообщение")
    button4 = telebot.types.KeyboardButton(text="Выручка")
    button6 = telebot.types.KeyboardButton(text="Логи")
    button7 = telebot.types.KeyboardButton(text="Рассылка")
    button8 = telebot.types.KeyboardButton(text="Статистика")
    button_exit = telebot.types.KeyboardButton(text="Выход из админки")
    keyboard.add(button1, button2)
    keyboard.add(button4, button6, button7)
    keyboard.add(button3, button8, button_exit)
    return keyboard

def num_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="5")
    button2 = telebot.types.KeyboardButton(text="10")
    button3 = telebot.types.KeyboardButton(text="20")
    button4 = telebot.types.KeyboardButton(text="30")
    keyboard.add(button1, button2)
    keyboard.add(button3, button4)
    return keyboard

def yes_or_no_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Да")
    button2 = telebot.types.KeyboardButton(text="Нет")
    keyboard.add(button1, button2)
    return keyboard

def get_state_key():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Статичный ключ", callback_data="get_state_key")
    )
    return markup


def manage_servers(servers_list):
    markup = InlineKeyboardMarkup()
    for server in servers_list:
        server_ip = server[0]
        state = server[1]
        if state == True:
            state = '✅'
        elif state == False:
            state = '❌'
        button_text = server_ip + ' ' + state

        markup.add(
            InlineKeyboardButton(button_text, callback_data="user_change_server_state_{}".format(server_ip))
        )
    return markup