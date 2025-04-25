from app import db

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
    status = db.Column(db.SmallInteger, default=1, comment='0-下架 1-上架')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    
    # 关系
    category = db.relationship('Category', backref='products')
    inventory = db.relationship('Inventory', backref='product', lazy='dynamic')
    orders = db.relationship('Order', backref='product', lazy='dynamic')
    
    @staticmethod
    def get_all_products():
        return Product.query.filter_by(status=1).order_by(Product.sort_order).all()
    
    @staticmethod
    def get_hot_products(limit=5):
        return Product.query.filter_by(status=1, is_hot=1).order_by(Product.sort_order).limit(limit).all()
    
    @staticmethod
    def get_recommend_products(limit=5):
        return Product.query.filter_by(status=1, is_recommend=1).order_by(Product.sort_order).limit(limit).all()
    
    @staticmethod
    def get_by_category(category_id):
        return Product.query.filter_by(category_id=category_id, status=1).order_by(Product.sort_order).all()
    
    @staticmethod
    def create_product(category_id, name, description, price, **kwargs):
        product = Product(
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            **kwargs
        )
        db.session.add(product)
        db.session.commit()
        return product
    
    def update_product(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self
    
    def delete_product(self):
        self.status = 0
        db.session.commit()
        return self