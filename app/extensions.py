from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 初始化扩展，但不绑定 app
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'