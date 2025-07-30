import os
from dotenv import load_dotenv

class AppConfig:
    def __init__(self):
        load_dotenv()  # 从 .env 加载环境变量
        self.appid = os.getenv("APPID")
        self.apikey = os.getenv("APIKEY")
        self.apisecret = os.getenv("APISECRET")
        self.auth_ip = os.getenv("AUTH_IP", "127.0.0.1")
        self.auth_port = int(os.getenv("AUTH_PORT", "8080"))


# 全局单例
config = AppConfig()