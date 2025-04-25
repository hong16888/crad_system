from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    register_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger, default=1, comment='0-禁用 1-正常')
    api_token = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    
    # Flask-Login 需要的属性
    def get_id(self):
        return str(self.user_id)
    
    # 密码处理
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # 关系
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def create_user(username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user