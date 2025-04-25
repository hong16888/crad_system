import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:admin@localhost/card_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # 可以查看生成的SQL语句，通常调试时开启
    DEBUG = True  # 开发时使用 True，生产时使用 False
    # SERVER_NAME = None  # 避免覆盖 host
    # PORT = None         # 避免覆盖 port
