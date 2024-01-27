import config
import requests
import json
from datetime import datetime

API_KEY = config.OUTLINE_API_URL


def get_all_api_keys():
    return json.loads(requests.get(f"{API_KEY}/access-keys/", verify=False).text)