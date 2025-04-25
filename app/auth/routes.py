from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from .forms import RegistrationForm, LoginForm
from app.auth import bp as auth_bp



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # 创建新用户
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='注册', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            # login_user(user, remember=form.remember.data)  #记住我
            login_user(user, remember=False)  #记住我
            session.permanent = False
            next_page = request.args.get('next')  # 获取重定向页面
            flash('登录成功！', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('邮箱或密码错误', 'danger')

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