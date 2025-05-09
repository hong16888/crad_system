from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Product, Category, Order, Inventory
from flask import jsonify
from app.models import OrderCard


@bp.route('/')
@login_required
def index():
    q = request.args.get('q', '')
    category_id = request.args.get('category_id')

    categories = Category.query.order_by(Category.sort_order).all()

    product_query = Product.query.filter_by(status=1)

    if q:
        product_query = product_query.filter(Product.name.ilike(f'%{q}%'))

    if category_id:
        product_query = product_query.filter(Product.category_id == category_id)

    hot_products = product_query.filter_by(is_hot=1).limit(5).all()
    recommended_products = product_query.filter_by(is_recommend=1).limit(5).all()

    return render_template('index.html',
                           categories=categories,
                           hot_products=hot_products,
                           recommended_products=recommended_products)

@bp.route('/orders')
@login_required
def orders():
    return render_template('orders.html')

@bp.route('/online-orders')
@login_required
def online_orders():
    return render_template('online_orders.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@bp.route('/category/<int:category_id>')
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    subcategories = Category.get_subcategories(category_id)
    products = Product.get_by_category(category_id)
    return render_template('category.html',
                          category=category,
                          subcategories=subcategories,
                          products=products)



@bp.route('/buy/<int:product_id>', methods=['POST'])
@login_required
def buy_product2(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':

        quantity = int(request.form.get('quantity', 1))
        # 检查库存
        available_cards = Inventory.get_available_cards(product_id, quantity)
        if len(available_cards) < quantity:
            return redirect(url_for('main.product_detail', product_id=product_id))

        # 创建订单
        total_amount = product.price * quantity
        order = Order.create_order(
            user_id=current_user.user_id,
            product_id=product_id,
            quantity=quantity,
            total_amount=total_amount,
            ip_address=request.remote_addr
        )

        # 关联卡密
        for card in available_cards:
            order_card = OrderCard(order_id=order.order_id, card_id=card.card_id)
            db.session.add(order_card)
            card.mark_as_locked()  # 锁定卡密

        db.session.commit()

        return redirect(url_for('main.order_detail', order_id=order.order_id))

    return render_template('buy_product.html', product=product)

@bp.route('/order/<order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.user_id and not current_user.is_admin:
        abort(403)
    return render_template('order_detail.html', order=order)

@bp.route('/pay/<order_id>', methods=['POST'])
@login_required
def pay_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.user_id:
        abort(403)

    payment_method = request.form.get('payment_method')

    if payment_method == 'balance':
        # 余额支付
        if current_user.balance < order.total_amount:
            flash('余额不足', 'danger')
            return redirect(url_for('main.order_detail', order_id=order_id))

        # 扣款
        current_user.balance -= order.total_amount
        db.session.commit()

        # 标记订单为已支付
        order.mark_as_paid('balance')

        # 标记卡密为已售
        for order_card in order.cards:
            order_card.card.mark_as_sold()

        # 标记订单为已完成
        order.mark_as_completed()

        flash('支付成功', 'success')
    else:
        # 第三方支付（需要集成支付接口）
        order.mark_as_paid(payment_method)
        flash('支付请求已提交', 'success')

    return redirect(url_for('main.order_detail', order_id=order_id))

################################################################################################
@bp.route('/api/index')
@login_required
def index_data():
    # 获取所有分类
    categories = Category.query.filter_by(status=1).order_by(Category.sort_order).all()
    category_data = []
    for c in categories:
        # 获取该分类下的任一商品用于封面图
        product = Product.query.filter_by(category_id=c.category_id, status=1).order_by(Product.sort_order).first()
        category_data.append({
            'category_id': c.category_id,
            'name': c.name,
            'img_url': product.image_url if product and product.image_url else '/static/default.png'
        })

    # 获取所有商品（可加分页/缓存优化）
    all_products = Product.query.filter_by(status=1).order_by(Product.sort_order).all()

    return jsonify({
        'categories': category_data,
        'all_products': [{
            'product_id': p.product_id,
            'name': p.name,
            'price': float(p.price),
            'image_url': p.image_url or '/static/default.png',
            'is_hot': p.is_hot,
            'is_recommend': p.is_recommend,
            'category_id': p.category_id
        } for p in all_products]
    })






################################################################################################


#显示商品详情
@bp.route('/product/<int:product_id>')
@login_required
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

#购买
@bp.route('/buy/<int:product_id>', methods=['POST'])
@login_required
def buy_product(product_id):
    # TODO: 实现购买逻辑
    flash("购买功能暂未实现", "info")
    return redirect(url_for('main.product_detail', product_id=product_id))

################################################################################################orders
@bp.route('/api/orders')
@login_required
def get_orders():
    # 添加过滤条件，排除已删除的订单（status=4）
    orders = Order.query.filter_by(
        user_id=current_user.user_id
    ).filter(
        Order.order_status != 4  # 排除已删除订单
    ).order_by(
        Order.create_time.desc()
    ).all()

    data = []
    for order in orders:
        product = Product.query.get(order.product_id)
        data.append({
            'order_id': order.order_id,
            'product_name': product.name if product else '商品已下架',
            'product_img': product.image_url if product else '/static/default.png',
            'quantity': order.quantity,
            'total_amount': float(order.total_amount),
            'order_status': order.order_status,  # 0-待支付 1-已支付 2-已完成 3-已取消
            'create_time': order.create_time.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify({'orders': data})


@bp.route('/api/orders/<order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(order_id=order_id, user_id=current_user.user_id).first()
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    if order.order_status != 0:
        return jsonify({'error': '只有待支付订单才能取消'}), 400
    order.order_status = 3
    db.session.commit()
    return jsonify({'message': '订单已取消'})

@bp.route('/api/orders/<order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.filter_by(order_id=order_id, user_id=current_user.user_id).first()
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    if order.order_status not in [2, 3]:
        return jsonify({'error': '仅已完成或已取消订单可删除'}), 400
    order.order_status = 4
    db.session.commit()
    return jsonify({'message': '订单已删除'})


################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################