from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, IntegerField, DecimalField, BooleanField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    category_id = SelectField('分类', coerce=int, validators=[DataRequired()])
    name = StringField('商品名称', validators=[DataRequired()])
    description = TextAreaField('商品描述')
    price = DecimalField('价格', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('库存', validators=[NumberRange(min=0)])
    is_hot = BooleanField('热销商品')
    is_recommend = BooleanField('推荐商品')
    status = BooleanField('上架', default=True)
    submit = SubmitField('提交')

class CategoryForm(FlaskForm):
    parent_id = SelectField('父分类', coerce=int, validators=[DataRequired()])
    name = StringField('分类名称', validators=[DataRequired()])
    description = StringField('分类描述')
    sort_order = IntegerField('排序', default=0)
    submit = SubmitField('提交')

class InventoryForm(FlaskForm):
    cards = TextAreaField('卡密', validators=[DataRequired()], 
                         description='每行一张卡，格式：卡号 密码 可选备注')
    batch_number = StringField('批次号')
    submit = SubmitField('提交')