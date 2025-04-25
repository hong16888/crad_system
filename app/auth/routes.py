import secrets
import string
from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from .forms import RegistrationForm, LoginForm
from app.auth import bp as auth_bp



def generate_invite_code(length=6):
    """生成6位唯一邀请码（大小写字母+数字）"""
    alphabet = string.ascii_letters + string.digits  # A-Za-z0-9
    while True:
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        # 确保邀请码在数据库中唯一
        if not User.query.filter_by(api_token=code).first():
            return code
def generate_unique_invite_code(length=6, retries=5):
    for _ in range(retries):
        code = generate_invite_code(length)
        if not User.query.filter_by(invite_code=code).first():
            return code
    raise ValueError("无法生成唯一的邀请码，请重试")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # 获取推荐人用户
            referrer = User.query.filter_by(invite_code=form.invite_code.data).first()
            # 生成自己的邀请码
            invite_code = generate_invite_code()

            user = User(
                username=form.username.data,
                password_hash=generate_password_hash(form.password.data),
                register_time=datetime.utcnow(),
                last_login=None,
                status=1,
                api_token=None,  # 如果不需要 token 可设置为 None
                ip_address=request.remote_addr,
                invite_code=invite_code,
                referrer_id=referrer.user_id if referrer else None
            )

            db.session.add(user)
            db.session.commit()

            flash('注册成功！欢迎加入。', 'success')
            return redirect(url_for('auth.login'))

        except IntegrityError as e:
            print(e)
            db.session.rollback()
            flash('注册失败，用户名可能已存在。', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html', title='注册', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('登录成功！', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('auth/login.html', title='登录', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('main.index'))


# 用户加载器（必须放在auth模块内）
@auth_bp.record_once
def setup_auth(state):
    from app.extensions import login_manager

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))