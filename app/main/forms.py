from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class SearchForm(FlaskForm):
    keyword = StringField('关键词', validators=[DataRequired()])
    submit = SubmitField('搜索')