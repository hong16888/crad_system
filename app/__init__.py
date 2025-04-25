import os
from datetime import timedelta

from flask import Flask
from app.extensions import db, login_manager  # 从 extensions.py 导入


def create_app():
    login_manager.login_view = 'auth.login'

    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(base_dir, '..', 'static')
    template_path = os.path.join(base_dir, '..', 'templates')

    app = Flask(__name__, template_folder=template_path, static_folder=static_path)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app


from sqlalchemy import event
from sqlalchemy.engine import Engine
@event.listens_for(Engine, "before_cursor_execute")
def _print_sql(conn, cursor, statement, parameters, context, executemany):
    print("----- 实际 SQL -----")
    print(statement)
    print("参数:", parameters)
    print("-------------------")
