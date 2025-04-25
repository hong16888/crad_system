from datetime import datetime

from app import db


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), default=0)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    # 新增图片字段
    img_url = db.Column(db.String(255))  # 分类图片URL
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
            'img_url': self.img_url,  # 新增        # 新增
            'sort_order': self.sort_order,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }