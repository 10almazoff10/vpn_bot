import telebot

def main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton(text="Написать в поддержку")
    button1 = telebot.types.KeyboardButton(text="Баланс")
    button2 = telebot.types.KeyboardButton(text="Последние операции")
    button3 = telebot.types.KeyboardButton(text="Пополнить")
    button4 = telebot.types.KeyboardButton(text="Ключ VPN")
    button5 = telebot.types.KeyboardButton(text="Трафик")
    keyboard.add(button_support, button1)
    keyboard.add(button2, button3)
    keyboard.add(button4, button5)
    return keyboard

def admin_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Список пользователей")
    button2 = telebot.types.KeyboardButton(text="Пополнить баланс пользователя")
    button3 = telebot.types.KeyboardButton(text="Написать сообщение пользователю")
    button4 = telebot.types.KeyboardButton(text="Выручка")
    button6 = telebot.types.KeyboardButton(text="Логи")
    button_exit = telebot.types.KeyboardButton(text="Выход из админки")
    keyboard.add(button1, button2)
    keyboard.add(button4, button6)
    keyboard.add(button3, button_exit)
    return keyboard

def admin_keyboard_keys():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Список ключей")
    button2 = telebot.types.KeyboardButton(text="Трафик по ключу")
    button3 = telebot.types.KeyboardButton(text="Создать ключ")
    button4 = telebot.types.KeyboardButton(text="Удалить ключ")
    button_exit = telebot.types.KeyboardButton(text="Выход")
    keyboard.add(button1, button2)
    keyboard.add(button3, button4)
    keyboard.add(button_exit)
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

def make_money():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Реферальный код")
    button2 = telebot.types.KeyboardButton(text="Задания")
    button3 = telebot.types.KeyboardButton(text="Колесо фортуны")
    button4 = telebot.types.KeyboardButton(text="Пост в соц.сети")
    button5 = telebot.types.KeyboardButton(text="Вернуться")
    keyboard.add(button1, button2)
    keyboard.add(button3)
    keyboard.add(button4, button5) 
    return keyboard