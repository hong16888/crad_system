import string
from random import random

from sqlalchemy import text

from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

# 辅助函数：生成订单ID和支付ID
def generate_order_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    import random
    rand_num = random.randint(1000, 9999)
    return f'ORD{timestamp}{rand_num}'

def generate_payment_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    import random
    rand_num = random.randint(1000, 9999)
    return f'PAY{timestamp}{rand_num}'

# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    register_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger, default=1)  # 0-禁用 1-正常
    api_token = db.Column(db.String(100), unique=True)
    ip_address = db.Column(db.String(50))
    invite_code = db.Column(db.String(50))
    referrer_id = db.Column(db.String(50))  # 推荐人的 user_id


    # Flask-Login 集成
    def get_id(self):
        return str(self.user_id)

    # 密码管理
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 用户与订单的关系（假设有 Order 表）
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    @property
    def is_admin(self):
        from app.models import Admin  # 防止循环导入
        admin = Admin.query.filter_by(username=self.username).first()
        return admin is not None

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'balance': float(self.balance) if self.balance else 0.00,
            'register_time': self.register_time.isoformat() if self.register_time else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'status': self.status,
            'ip_address': self.ip_address,
            'invite_code': self.invite_code,
            'referrer_id': self.referrer_id

        }

# 商品分类模型
class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), default=0)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    # 新增图片字段
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 自引用关系
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[category_id]), lazy='dynamic')

    @staticmethod
    def get_parent_categories():
        return Category.query.filter_by(parent_id=None).all()

    @staticmethod
    def get_subcategories(parent_id):
        return Category.query.filter_by(parent_id=parent_id).all()

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'parent_id': self.parent_id,
            'name': self.name,
            'description': self.description,
            'sort_order': self.sort_order,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 商品模型
class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)
    is_hot = db.Column(db.SmallInteger, default=0)
    is_recommend = db.Column(db.SmallInteger, default=0)
    status = db.Column(db.SmallInteger, default=1)  # 0-下架 1-上架
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 关系
    category = db.relationship('Category', backref='products')
    inventory = db.relationship('Inventory', backref='product', lazy='dynamic')

    @staticmethod
    def get_hot_products(limit=10):
        return Product.query.filter_by(is_hot=True).limit(limit).all()

    @staticmethod
    def get_recommend_products(limit=10):
        return Product.query.filter_by(is_recommend=True).limit(limit).all()

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.00,
            'stock': self.stock,
            'image_url': self.image_url,
            'sort_order': self.sort_order,
            'is_hot': bool(self.is_hot),
            'is_recommend': bool(self.is_recommend),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 卡密库存模型
class Inventory(db.Model):
    __tablename__ = 'inventory'

    card_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    card_number = db.Column(db.String(100), nullable=False)
    card_password = db.Column(db.String(100), nullable=False)
    status = db.Column(db.SmallInteger, default=0)  # 0-未售 1-已售 2-已锁定
    added_time = db.Column(db.DateTime, default=datetime.utcnow)
    sold_time = db.Column(db.DateTime)
    batch_number = db.Column(db.String(50))

    # 状态管理方法
    def mark_as_sold(self):
        self.status = 1
        self.sold_time = datetime.utcnow()
        return self

    def mark_as_locked(self):
        self.status = 2
        return self

    def mark_as_available(self):
        self.status = 0
        self.sold_time = None
        return self

    def to_dict(self):
        return {
            'card_id': self.card_id,
            'product_id': self.product_id,
            'card_number': self.card_number,
            'status': self.status,
            'added_time': self.added_time.isoformat() if self.added_time else None,
            'sold_time': self.sold_time.isoformat() if self.sold_time else None,
            'batch_number': self.batch_number
        }

    # ✅ 新增：获取指定商品的可用库存卡
    @classmethod
    def get_available_cards(cls, product_id, limit=1):
        return cls.query.filter_by(product_id=product_id, status=0).limit(limit).all()



 # 订单模型
class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.String(50), primary_key=True, default=generate_order_id)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20))  # alipay/wechat/balance
    order_status = db.Column(db.SmallInteger, default=0)  # 0-待支付 1-已支付 2-已完成 3-已取消 4-已删除
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    pay_time = db.Column(db.DateTime)
    complete_time = db.Column(db.DateTime)
    ip_address = db.Column(db.String(50))
    contact_info = db.Column(db.String(100))

    product = db.relationship('Product', backref='orders')
    cards = db.relationship('OrderCard', backref='order', lazy='dynamic')
    payment = db.relationship('Payment', backref='order', uselist=False)

    # ✅ 添加类方法：用于创建订单
    @classmethod
    def create_order(cls, user_id, product_id, quantity, total_amount, ip_address=None, contact_info=None):
        order = cls(
            order_id=generate_order_id(),
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_amount=total_amount,
            ip_address=ip_address,
            contact_info=contact_info
        )
        db.session.add(order)
        return order

    def mark_as_paid(self, payment_method, transaction_id=None):
        self.order_status = 1
        self.payment_method = payment_method
        self.pay_time = datetime.utcnow()
        self.payment = Payment(
            payment_id=generate_payment_id(),
            amount=self.total_amount,
            payment_method=payment_method,
            payment_status=1,
            transaction_id=transaction_id
        )
        return self

    def mark_as_completed(self):
        self.order_status = 2
        self.complete_time = datetime.utcnow()
        return self

    def mark_as_cancelled(self):
        self.order_status = 3
        for card in self.cards:
            card.card.mark_as_available()
        return self

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total_amount': float(self.total_amount) if self.total_amount else 0.00,
            'payment_method': self.payment_method,
            'order_status': self.order_status,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'pay_time': self.pay_time.isoformat() if self.pay_time else None,
            'complete_time': self.complete_time.isoformat() if self.complete_time else None,
            'ip_address': self.ip_address,
            'contact_info': self.contact_info
        }

# 订单卡密关联模型
class OrderCard(db.Model):
    __tablename__ = 'order_cards'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.order_id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('inventory.card_id'), nullable=False)

    # 关系
    card = db.relationship('Inventory')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'card_id': self.card_id,
            'card': self.card.to_dict() if self.card else None
        }

# 支付记录模型
class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.String(50), primary_key=True, default=generate_payment_id)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.order_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.SmallInteger, default=0)  # 0-未支付 1-已支付
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    pay_time = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(100))

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'order_id': self.order_id,
            'amount': float(self.amount) if self.amount else 0.00,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'pay_time': self.pay_time.isoformat() if self.pay_time else None,
            'transaction_id': self.transaction_id
        }

# 系统配置模型
class Setting(db.Model):
    __tablename__ = 'settings'

    setting_id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'setting_id': self.setting_id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 管理员模型
class Admin(db.Model):
    __tablename__ = 'admins'

    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    real_name = db.Column(db.String(50))
    last_login = db.Column(db.DateTime)
    last_ip = db.Column(db.String(50))
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 密码管理
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_ip': self.last_ip,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 管理员操作日志模型
class AdminLog(db.Model):
    __tablename__ = 'admin_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    action = db.Column(db.String(100), nullable=False)
    action_detail = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    admin = db.relationship('Admin', backref='logs')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'admin_id': self.admin_id,
            'action': self.action,
            'action_detail': self.action_detail,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
