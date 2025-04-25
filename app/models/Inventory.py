from app import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    card_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    card_number = db.Column(db.String(100), nullable=False)
    card_password = db.Column(db.String(100), nullable=False)
    status = db.Column(db.SmallInteger, default=0, comment='0-未售 1-已售 2-已锁定')
    added_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    sold_time = db.Column(db.DateTime)
    batch_number = db.Column(db.String(50))
    
    @staticmethod
    def get_available_cards(product_id, limit=1):
        return Inventory.query.filter_by(product_id=product_id, status=0).limit(limit).all()
    
    @staticmethod
    def add_cards(product_id, cards_data):
        """批量添加卡密
        cards_data: [{'card_number': 'xxx', 'card_password': 'xxx', 'batch_number': 'xxx'}, ...]
        """
        cards = []
        for card_data in cards_data:
            card = Inventory(
                product_id=product_id,
                card_number=card_data['card_number'],
                card_password=card_data['card_password'],
                batch_number=card_data.get('batch_number')
            )
            cards.append(card)
        db.session.add_all(cards)
        db.session.commit()
        return cards
    
    def mark_as_sold(self):
        self.status = 1
        self.sold_time = db.func.current_timestamp()
        db.session.commit()
        return self
    
    def mark_as_locked(self):
        self.status = 2
        db.session.commit()
        return self
    
    def mark_as_available(self):
        self.status = 0
        self.sold_time = None
        db.session.commit()
        return self