import requests
import json
import dbcon

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
        try:
            exist_ip = dbcon.get_region_from_base(self.ip)
        except:
            pass

        if exist_ip != None:
            data = json.dumps({"status":"success", 'country':exist_ip[0], 'region':exist_ip[1], 'city':exist_ip[2]})
            return json.loads(data)

        url = "http://ip-api.com/json/{}".format(self.ip)
        try:
            req = requests.get(url)
            return json.loads(req.text)

        except Exception as error:
            return error