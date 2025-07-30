from typing import Optional

import requests
import api.config.AppConfig
from api.utils.sign_utils import generate_sign

class AuthClient:
    def __init__(self, config):
        self.config = config

    def check_quota(self, interface_id: str,thrid_app_key: str) -> dict:
        api_path = "/open-api/v1/check_quota"
        url = f"http://{self.config.auth_ip}:{self.config.auth_port}{api_path}"
        sign = generate_sign(api_path,self.config.apisecret)
        headers = {
            "X-App-Id": self.config.appid,
            "X-App-Key": self.config.apikey,
            "X-Signature": sign,
            "X-Api-type": "1",
            "X-Interface-Id": interface_id,
            "X-Thrid-App-Key": thrid_app_key,
            "sign-check": "1"
        }

        response = requests.get(url, headers=headers)
        return response.json()
