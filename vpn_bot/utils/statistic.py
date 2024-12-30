from prettytable import PrettyTable
import vpn_bot.commands.dbcon as dbcon
from vpn_bot.utils.data_converter import DataConvert

class Users:
    def __init__(self):
        self.active = dbcon.get_list_users_with_state()


    def create_table_active(self):
        tableUsers = PrettyTable()
        # имена полей таблицы
        tableUsers.field_names = ["id", "Логин", "Telegram-ID", "Баланс"]
        # добавление данных по одной строке за раз

        for user in self.active:

            tableUsers.add_row([user[3], user[0], user[1], user[2]])

        return tableUsers

    def create_table_connections(self):
        user_stats = dbcon.get_users_stats()

        tableUsers = PrettyTable()
        # имена полей таблицы
        tableUsers.field_names = ["№", "ID", "Имя", "Запр.", "Трафик"]
        # добавление данных по одной строке за раз

        for user in user_stats:
            tableUsers.add_row([user[0], user[1], user[2], user[3], DataConvert.convert_size(user[4])])

        return tableUsers