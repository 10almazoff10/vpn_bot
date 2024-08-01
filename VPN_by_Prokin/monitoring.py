import psutil
import platform
import datetime
import json

class SystemInfo:
    def __init__(self):
        self.system_info = {
            'platform': platform.system(),
            'release': platform.release(),
            'version': platform.version()
        }
        self.cpu_info = {
            'arch': platform.machine(),
            'model': platform.processor(),
            'core_count': psutil.cpu_count(logical=False),
            'frequency': round(psutil.cpu_freq().current, 2)
        }
        self.ram_info = {
            'ram_total': round(psutil.virtual_memory().total / (1024 **3), 2),
            'ram_available': round(psutil.virtual_memory().available / (1024 **3), 2),
            'ram_percent_used': psutil.virtual_memory().percent
        }
        self.uptime_info = {
            'start_time': datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_system_info(self):
        return self.system_info

    def get_cpu_info(self):
        return self.cpu_info

    def get_ram_info(self):
        return self.ram_info

    def get_uptime_info(self):
        return self.uptime_info


    def to_json(self):
        return json.dumps({
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'ram': self.get_ram_info(),
            'uptime': self.get_uptime_info(),
        })