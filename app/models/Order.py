from datetime import datetime
from app import db

class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), comment='alipay/wechat/balance')
    order_status = db.Column(db.SmallInteger, default=0, comment='0-待支付 1-已支付 2-已完成 3-已取消')
    create_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    pay_time = db.Column(db.DateTime)
    complete_time = db.Column(db.DateTime)
    ip_address = db.Column(db.String(50))
    contact_info = db.Column(db.String(100))
    
    # 关系
    cards = db.relationship('OrderCard', backref='order', lazy='dynamic')
    payment = db.relationship('Payment', backref='order', uselist=False)
    
    @staticmethod
    def create_order(user_id, product_id, quantity, total_amount, **kwargs):
        order = Order(
            order_id=generate_order_id(),
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_amount=total_amount,
            **kwargs
        )
        db.session.add(order)
        db.session.commit()
        return order
    
    def mark_as_paid(self, payment_method, transaction_id=None):
        self.order_status = 1
        self.payment_method = payment_method
        self.pay_time = datetime.utcnow()
        
        # 创建支付记录
        payment = Payment(
            payment_id=generate_payment_id(),
            order_id=self.order_id,
            amount=self.total_amount,
            payment_method=payment_method,
            payment_status=1,
            pay_time=datetime.utcnow(),
            transaction_id=transaction_id
        )
        db.session.add(payment)
        db.session.commit()
        return self
    
    def mark_as_completed(self):
        self.order_status = 2
        self.complete_time = datetime.utcnow()
        db.session.commit()
        return self
    
    def mark_as_cancelled(self):
        self.order_status = 3
        db.session.commit()
        return self

class OrderCard(db.Model):
    __tablename__ = 'order_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.order_id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('inventory.card_id'), nullable=False)
    
    # 关系
    card = db.relationship('Inventory', backref='order_cards')

class Payment(db.Model):
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.String(50), primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.order_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.SmallInteger, default=0, comment='0-未支付 1-已支付')
    create_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    pay_time = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(100))

def generate_order_id():
    from datetime import datetime
    import random
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    rand_num = random.randint(1000, 9999)
    return f'ORD{timestamp}{rand_num}'

def generate_payment_id():
    from datetime import datetime
    import random
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    rand_num = random.randint(1000, 9999)
    return f'PAY{timestamp}{rand_num}'