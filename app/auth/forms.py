from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('手机号', validators=[
        DataRequired(message='手机号不能为空'),
        Regexp(
            regex=r'^1[3-9]\d{9}$',  # 中国手机号正则
            message='请输入有效的11位手机号'
        )
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, message='密码至少6个字符')
    ])
    invite_code = StringField('邀请码', validators=[
        DataRequired(message='邀请码不能为空'),
        Length(min=6, max=6, message='邀请码必须为6位字符')
    ])
    submit = SubmitField('注册')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('该手机号已存在')

    def validate_invite_code(self, invite_code):
        if not invite_code.data.isalnum():
            raise ValidationError('邀请码只能包含字母和数字')
        referrer = User.query.filter_by(invite_code=invite_code.data).first()
        if not referrer:
            raise ValidationError('邀请码无效')
        self.referrer_id = referrer.user_id
class LoginForm(FlaskForm):
    username = StringField('手机号',
                      validators=[
                          DataRequired(message='请输入手机号'),
                          Regexp(
                              regex=r'^1[3-9]\d{9}$',  # 中国手机号正则
                              message='请输入有效的11位手机号'
                          )
                      ])
    password = PasswordField('密码',
                           validators=[
                               DataRequired(message='请输入密码')
                           ])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')