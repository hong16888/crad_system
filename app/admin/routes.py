from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.admin import bp
from app.models import Product, Category, Inventory, Order, User
from app.admin.forms import ProductForm, CategoryForm, InventoryForm

@bp.before_request
@login_required
def before_request():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))

@bp.route('/')
def dashboard():
    product_count = Product.query.count()
    order_count = Order.query.count()
    user_count = User.query.count()
    return render_template('admin/dashboard.html',
                         product_count=product_count,
                         order_count=order_count,
                         user_count=user_count)

# 商品管理
@bp.route('/products')
def products():
    products = Product.query.order_by(Product.product_id.desc()).all()
    return render_template('admin/products.html', products=products)

@bp.route('/product/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    form.category_id.choices = [(c.category_id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product.create_product(
            category_id=form.category_id.data,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            is_hot=1 if form.is_hot.data else 0,
            is_recommend=1 if form.is_recommend.data else 0,
            status=1 if form.status.data else 0
        )
        flash('商品添加成功', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/product_form.html', form=form, title='添加商品')

@bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.category_id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product.update_product(
            category_id=form.category_id.data,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            is_hot=1 if form.is_hot.data else 0,
            is_recommend=1 if form.is_recommend.data else 0,
            status=1 if form.status.data else 0
        )
        flash('商品更新成功', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/product_form.html', form=form, title='编辑商品')

@bp.route('/product/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.delete_product()
    flash('商品已下架', 'success')
    return redirect(url_for('admin.products'))

# 分类管理
@bp.route('/categories')
def categories():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)

@bp.route('/category/add', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    form.parent_id.choices = [(0, '顶级分类')] + [(c.category_id, c.name) for c in Category.query.filter_by(parent_id=0).all()]
    
    if form.validate_on_submit():
        category = Category.create_category(
            name=form.name.data,
            parent_id=form.parent_id.data,
            description=form.description.data,
            sort_order=form.sort_order.data
        )
        flash('分类添加成功', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_form.html', form=form, title='添加分类')

@bp.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    form.parent_id.choices = [(0, '顶级分类')] + [(c.category_id, c.name) for c in Category.query.filter_by(parent_id=0).all()]
    
    if form.validate_on_submit():
        category.update_category(
            name=form.name.data,
            parent_id=form.parent_id.data,
            description=form.description.data,
            sort_order=form.sort_order.data
        )
        flash('分类更新成功', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_form.html', form=form, title='编辑分类')

@bp.route('/category/delete/<int:category_id>')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.delete_category()
    flash('分类已禁用', 'success')
    return redirect(url_for('admin.categories'))

# 卡密管理
@bp.route('/inventory/<int:product_id>')
def inventory(product_id):
    product = Product.query.get_or_404(product_id)
    cards = Inventory.query.filter_by(product_id=product_id).order_by(Inventory.status).all()
    return render_template('admin/inventory.html', product=product, cards=cards)

@bp.route('/inventory/add/<int:product_id>', methods=['GET', 'POST'])
def add_inventory(product_id):
    product = Product.query.get_or_404(product_id)
    form = InventoryForm()
    
    if form.validate_on_submit():
        cards_data = []
        for line in form.cards.data.split('\n'):
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 2:
                    cards_data.append({
                        'card_number': parts[0],
                        'card_password': parts[1],
                        'batch_number': form.batch_number.data
                    })
        
        Inventory.add_cards(product_id, cards_data)
        flash(f'成功添加 {len(cards_data)} 张卡密', 'success')
        return redirect(url_for('admin.inventory', product_id=product_id))
    
    return render_template('admin/inventory_form.html', form=form, product=product)

# 订单管理
@bp.route('/orders')
def orders():
    orders = Order.query.order_by(Order.create_time.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@bp.route('/order/<order_id>')
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@bp.route('/order/complete/<order_id>')
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.mark_as_completed()
    flash('订单已完成', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

@bp.route('/order/cancel/<order_id>')
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.mark_as_cancelled()
    
    # 释放卡密
    for order_card in order.cards:
        order_card.card.mark_as_available()
    
    flash('订单已取消', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))