import requests
import json

class CheckUserLocation:
    """
    Получение информации об IP Адресе
    """
    def __init__(self, ip):
        self.ip = ip

    def byIP(self):
        """
        Создает запрос на API для получения информации
        Returns:
        Возвращает python Json объект
        """
        url = "http://ip-api.com/json/{}".format(self.ip)
        try:
            req = requests.get(url)
            return json.loads(req.text)

        except Exception as error:
            return error