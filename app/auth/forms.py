from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('用户名',
                         validators=[
                             DataRequired(message='用户名不能为空'),
                             Length(min=4, max=20, message='用户名长度4-20个字符')
                         ])
    email = StringField('邮箱',
                      validators=[
                          DataRequired(message='邮箱不能为空'),
                          Email(message='无效的邮箱地址')
                      ])
    password = PasswordField('密码',
                           validators=[
                               DataRequired(message='密码不能为空'),
                               Length(min=6, message='密码至少6个字符')
                           ])
    confirm_password = PasswordField('确认密码',
                                   validators=[
                                       DataRequired(message='请确认密码'),
                                       EqualTo('password', message='两次密码不一致')
                                   ])
    submit = SubmitField('注册')

    # 自定义验证：用户名是否已存在
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用')

    # 自定义验证：邮箱是否已注册
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已注册')

class LoginForm(FlaskForm):
    email = StringField('邮箱',
                      validators=[
                          DataRequired(message='请输入邮箱'),
                          Email(message='无效的邮箱格式')
                      ])
    password = PasswordField('密码',
                           validators=[
                               DataRequired(message='请输入密码')
                           ])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')