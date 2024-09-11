import botApp.commands.dbcon as dbcon
from botApp.logs.logger import Logger

logger = Logger(__name__)
class UserKey:
    def __init__(self, telegram_id):
        self.telegram_id = telegram_id
        self.user_state = dbcon.get_user_state(telegram_id)
        self.active_servers = dbcon.get_all_outline_servers()
        self.servers_count: int = len(self.active_servers)
        self.list_user_keys = dbcon.get_all_user_keys(telegram_id)
        self.keys_count: int = len(self.list_user_keys)

    def validate_count_keys(self):
        if self.user_state == 0:
            if self.servers_count != self.keys_count:
                logger.info("У пользователя нарушено количество ключей относительно серверов.")

                if self.servers_count > self.keys_count:
                    logger.info("Серверов больше чем ключей, регистрируем новые ключи для тех серверов, где нет ключей")
                    unregistered_servers = self.get_unregistered_servers()
                    logger.info("У пользователя нет ключа/ей на сервере/ах с id {}, регистрируем".format(unregistered_servers))
                    if dbcon.reg_user_keys(self.telegram_id, unregistered_servers):
                        logger.info("Ключи успешно зарегистрированы")
                    else:
                        logger.info("Ошибка регистрации ключей")

                elif self.servers_count < self.keys_count:
                    logger.info("Ключей больше чем серверов, удаляем лишние.")
                    keys_count: list = dbcon.get_count_keys_on_servers_for_user(self.telegram_id)
                    print(keys_count)
                    for server in keys_count:
                        server_id = server[0]
                        # server[0] - id-server, server[1], count-keys
                        if server[1] > 1:
                            logger.info("На сервере {} больше одного ключа".format(server_id))
                            logger.info("Получаем все ключи пользователя на сервере {}".format(server_id))
                            keys = dbcon.get_list_user_keys_by_server_id(self.telegram_id, server_id)
                            logger.info("Получено {}".format(len(keys)))
                            count = 0
                            for key in keys:
                                if count != 0:
                                    logger.info("Удаляем ключ {} на сервере {}".format(key, server_id))
                                    if dbcon.delete_key_by_server_id(key, server_id):


                                        logger.info("Ключ успешно удален")
                                    else:
                                        logger.info("Ошибка удаления ключа")
                                count += 1
                            logger.info("Удаление выполнено")


            else:
                logger.info("Проблем с ключами нет.")




        elif self.user_state == 1:
            logger.info("Пользователь заблокирован")

        else:
            logger.info("У пользователя некорректный статус")

    def get_unregistered_servers(self):
        """
        Возвращает ID серверов, на которых не зарегистрирован ни один ключ пользователя
        Returns:
        [1,5,8]
        """
        servers = dbcon.get_all_outline_servers()
        unregistered = []
        for id_server in servers:
            print(self.list_user_keys)
            if self.list_user_keys != [] or self.list_user_keys != None:
                for id_key in self.list_user_keys:
                    if id_key[1] != id_server and id_key[1] not in unregistered:
                        unregistered.append(id_server)
            else:
                unregistered.append(id_server)
        return unregistered

    def delete_user_keys(self):
        logger.info("Удаление ключей пользователя {} в количестве {}".format(self.telegram_id, self.keys_count))
        dbcon.delete_all_users_keys(self.telegram_id)

    def get_user_traffic(self):
        logger.info("Получаем трафик пользователя {}".format(self.telegram_id))
        logger.info("У пользователя - {} ключей".format(self.keys_count))

        if self.keys_count == None:
            return 0
        elif self.keys_count == 1:
            return int(dbcon.execute_query(
                """
                SELECT 
                    traffic
                FROM
                    users_vpn_keys
                WHERE
                    telegram_id = '{}'
                """.format(self.telegram_id))[0])

        elif int(self.keys_count) > 1:
            traffic = int(dbcon.execute_query(
                """
                SELECT 
                    sum(traffic)
                FROM
                    users_vpn_keys
                WHERE
                    telegram_id = '{}' 
                """.format(self.telegram_id))[0])

            logger.info("У пользователя {} ключа, трафик - {}".format(
                self.keys_count,
                traffic))

            return traffic

        else:
            return 0