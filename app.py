import os
import hmac
import hashlib
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, send_from_directory

from config import Config
from models import db, Admin, Category, FoodItem, Order, OrderItem, TableReservation, ContactMessage
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import razorpay
    razorpay_client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))
except Exception:
    razorpay = None
    razorpay_client = None

app = Flask(__name__)

app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_database_uri()

# Initialize DB
db.init_app(app)

# Helper decorator for Admin authentication
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in with admin credentials to access this area.', 'warning')
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Context processor for global template variables
@app.context_processor
def inject_global_data():
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc()).all()
    unread_messages_count = 0
    pending_orders_count = 0
    if session.get('admin_logged_in'):
        unread_messages_count = ContactMessage.query.filter_by(is_read=False).count()
        pending_orders_count = Order.query.filter_by(order_status='Pending').count()

    return {
        'restaurant_name': 'MAHFOOZ',
        'restaurant_tagline': 'Delicious Food, Unforgettable Moments',
        'restaurant_phone': '+91 98350 45678',
        'restaurant_email': 'contact@mahfoozrestaurant.com',
        'restaurant_address': 'Heritage Boulevard, Fraser Road, Near Dak Bungalow, Patna, Bihar - 800001',
        'restaurant_hours': 'Mon - Sun: 11:30 AM - 11:30 PM',
        'nav_categories': categories,
        'unread_messages_count': unread_messages_count,
        'pending_orders_count': pending_orders_count,
        'razorpay_key_id': Config.RAZORPAY_KEY_ID,
        'restaurant_upi_id': Config.RESTAURANT_UPI_ID,
        'restaurant_upi_name': Config.RESTAURANT_UPI_NAME,
        'current_year': datetime.utcnow().year
    }

# ========================================================
# PUBLIC CUSTOMER ROUTES
# ========================================================

@app.route('/')
def home():
    """Home page with hero, popular dishes, reviews, and hours"""
    featured_items = FoodItem.query.filter_by(is_featured=True, is_available=True).limit(6).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc()).limit(8).all()
    return render_template('index.html', featured_items=featured_items, categories=categories)


@app.route('/menu')
def menu():
    """Menu page with category filter, search, veg/non-veg toggle"""
    category_slug = request.args.get('category', 'all')
    search_query = request.args.get('search', '').strip()
    veg_only = request.args.get('veg', '')

    query = FoodItem.query.filter_by(is_available=True)

    if category_slug and category_slug != 'all':
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter_by(category_id=category.id)

    if search_query:
        query = query.filter(FoodItem.name.ilike(f'%{search_query}%') | FoodItem.description.ilike(f'%{search_query}%'))

    if veg_only == '1':
        query = query.filter_by(is_veg=True)
    elif veg_only == '0':
        query = query.filter_by(is_veg=False)

    food_items = query.all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc()).all()

    return render_template('menu.html',
                           food_items=food_items,
                           categories=categories,
                           current_category=category_slug,
                           search_query=search_query,
                           veg_only=veg_only)


@app.route('/api/menu')
def api_menu():
    """JSON API for fast client-side filtering and live search"""
    category_slug = request.args.get('category', 'all')
    search_query = request.args.get('search', '').strip()
    veg_only = request.args.get('veg', '')

    query = FoodItem.query.filter_by(is_available=True)

    if category_slug and category_slug != 'all':
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter_by(category_id=category.id)

    if search_query:
        query = query.filter(FoodItem.name.ilike(f'%{search_query}%') | FoodItem.description.ilike(f'%{search_query}%'))

    if veg_only == '1':
        query = query.filter_by(is_veg=True)
    elif veg_only == '0':
        query = query.filter_by(is_veg=False)

    items = query.all()
    return jsonify([item.to_dict() for item in items])


@app.route('/about')
def about():
    """About page introducing Chef Mahfooz, Patna roots, mission & ambience"""
    return render_template('about.html')


@app.route('/gallery')
def gallery():
    """Gallery page showcasing restaurant interiors, private banquets and dishes"""
    return render_template('gallery.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with message form, Patna location, WhatsApp link, and hours"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash('Please complete all required fields.', 'danger')
            return redirect(url_for('contact'))

        new_msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject or 'General Inquiry',
            message=message
        )
        db.session.add(new_msg)
        db.session.commit()

        flash('Thank you for reaching out! The Mahfooz team will contact you shortly.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/robots.txt')
def robots():
    """Search Engine Crawling Instructions"""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt', mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap():
    """Dynamic XML Sitemap for Google Search Console Indexing"""
    base_url = request.url_root.rstrip('/')
    pages = [
        {'loc': f"{base_url}/", 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': f"{base_url}/menu", 'priority': '0.9', 'changefreq': 'daily'},
        {'loc': f"{base_url}/book-table", 'priority': '0.8', 'changefreq': 'weekly'},
        {'loc': f"{base_url}/about", 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': f"{base_url}/gallery", 'priority': '0.7', 'changefreq': 'weekly'},
        {'loc': f"{base_url}/contact", 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': f"{base_url}/track-order", 'priority': '0.6', 'changefreq': 'daily'},
    ]
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml_content += f"  <url>\n    <loc>{page['loc']}</loc>\n    <changefreq>{page['changefreq']}</changefreq>\n    <priority>{page['priority']}</priority>\n  </url>\n"
    xml_content += '</urlset>'
    return Response(xml_content, mimetype='application/xml')



# ========================================================
# TABLE BOOKING SYSTEM
# ========================================================

@app.route('/book-table', methods=['GET', 'POST'])
def book_table():
    """Table reservation submission with validation and instant code generation"""
    if request.method == 'POST':
        guest_name = request.form.get('guest_name', '').strip()
        guest_phone = request.form.get('guest_phone', '').strip()
        guest_email = request.form.get('guest_email', '').strip()
        reservation_date = request.form.get('reservation_date', '').strip()
        reservation_time = request.form.get('reservation_time', '').strip()
        guest_count = request.form.get('guest_count', 2, type=int)
        seating_preference = request.form.get('seating_preference', 'Standard Dining')
        special_requests = request.form.get('special_requests', '').strip()

        if not guest_name or not guest_phone or not reservation_date or not reservation_time:
            flash('Please provide your name, phone, reservation date, and time.', 'danger')
            return redirect(url_for('book_table'))

        code = TableReservation.generate_code()
        new_reservation = TableReservation(
            reservation_code=code,
            guest_name=guest_name,
            guest_phone=guest_phone,
            guest_email=guest_email,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            guest_count=guest_count,
            seating_preference=seating_preference,
            special_requests=special_requests,
            status='Confirmed'
        )

        db.session.add(new_reservation)
        db.session.commit()

        flash(f'Your table reservation #{code} has been successfully confirmed!', 'success')
        return redirect(url_for('reservation_confirmation', code=code))

    return render_template('book_table.html')


@app.route('/reservation-confirmation/<code>')
def reservation_confirmation(code):
    """Reservation confirmation receipt"""
    reservation = TableReservation.query.filter_by(reservation_code=code).first_or_404()
    return render_template('reservation_confirmation.html', reservation=reservation)


# ========================================================
# FOOD ORDERING & CHECKOUT SYSTEM
# ========================================================

@app.route('/checkout', methods=['GET'])
def checkout():
    """Food ordering checkout page"""
    return render_template('checkout.html')


@app.route('/api/order/create', methods=['POST'])
def create_order():
    """Process cart submission, validate customer details, save Order & OrderItems to DB"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request payload.'}), 400

    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    customer_email = data.get('customer_email', '').strip()
    delivery_address = data.get('delivery_address', '').strip()
    special_notes = data.get('special_notes', '').strip()
    payment_method = data.get('payment_method', 'Cash on Delivery')
    items = data.get('items', [])

    if not customer_name or not customer_phone or not delivery_address:
        return jsonify({'success': False, 'message': 'Customer name, phone, and delivery address are required.'}), 400

    if not items or len(items) == 0:
        return jsonify({'success': False, 'message': 'Your shopping cart is empty.'}), 400

    # Calculate subtotal based on database item prices for security
    calculated_subtotal = 0.0
    order_items_to_create = []

    for item in items:
        food_id = item.get('id')
        qty = int(item.get('quantity', 1))
        if qty <= 0:
            continue

        food_item = FoodItem.query.get(food_id)
        if not food_item or not food_item.is_available:
            return jsonify({'success': False, 'message': f'Dish "{item.get("name")}" is currently unavailable.'}), 400

        item_subtotal = food_item.price * qty
        calculated_subtotal += item_subtotal

        order_items_to_create.append({
            'food_item_id': food_item.id,
            'item_name': food_item.name,
            'item_price': food_item.price,
            'quantity': qty,
            'subtotal': item_subtotal
        })

    # Delivery fee logic: Free delivery above ₹500, else ₹40
    delivery_fee = 0.0 if calculated_subtotal >= 500 else 40.0
    tax_amount = round(calculated_subtotal * 0.05, 2) # 5% GST
    total_amount = round(calculated_subtotal + delivery_fee + tax_amount, 2)

    order_num = Order.generate_order_number()

    razorpay_order_id = None
    if payment_method == 'Razorpay Online':
        amount_in_paise = int(round(total_amount * 100))
        try:
            if razorpay_client:
                rzp_order = razorpay_client.order.create({
                    'amount': amount_in_paise,
                    'currency': 'INR',
                    'receipt': order_num,
                    'notes': {
                        'customer_name': customer_name,
                        'customer_phone': customer_phone
                    }
                })
                razorpay_order_id = rzp_order.get('id')
            else:
                # Fallback sandbox order ID
                import uuid
                razorpay_order_id = f"order_demo_{uuid.uuid4().hex[:12]}"
        except Exception as e:
            print(f"[RAZORPAY NOTICE] Gateway call error or test mode: {e}")
            import uuid
            razorpay_order_id = f"order_demo_{uuid.uuid4().hex[:12]}"

    new_order = Order(
        order_number=order_num,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        delivery_address=delivery_address,
        subtotal=calculated_subtotal,
        delivery_fee=delivery_fee,
        tax_amount=tax_amount,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status='Pending',
        order_status='Pending',
        special_notes=special_notes,
        razorpay_order_id=razorpay_order_id
    )

    db.session.add(new_order)
    db.session.flush() # Obtain new_order.id

    for oi in order_items_to_create:
        order_item = OrderItem(
            order_id=new_order.id,
            food_item_id=oi['food_item_id'],
            item_name=oi['item_name'],
            item_price=oi['item_price'],
            quantity=oi['quantity'],
            subtotal=oi['subtotal']
        )
        db.session.add(order_item)

    db.session.commit()

    if payment_method == 'Razorpay Online':
        return jsonify({
            'success': True,
            'payment_mode': 'razorpay',
            'order_number': order_num,
            'razorpay_order_id': razorpay_order_id,
            'amount': int(round(total_amount * 100)),
            'currency': 'INR',
            'key_id': Config.RAZORPAY_KEY_ID,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            'redirect_url': url_for('order_confirmation', order_number=order_num)
        })

    return jsonify({
        'success': True,
        'payment_mode': 'standard',
        'order_number': order_num,
        'redirect_url': url_for('order_confirmation', order_number=order_num)
    })


@app.route('/api/payment/verify-razorpay', methods=['POST'])
def verify_razorpay():
    """Verify Razorpay payment signature and mark order as Paid"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid payload.'}), 400

    order_number = data.get('order_number')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    order = Order.query.filter_by(order_number=order_number).first()
    if not order:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    # Signature verification
    signature_valid = False
    try:
        if razorpay_client:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            signature_valid = True
        else:
            # Standard HMAC SHA256 verification
            msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
            expected_signature = hmac.new(
                Config.RAZORPAY_KEY_SECRET.encode(),
                msg,
                hashlib.sha256
            ).hexdigest()
            signature_valid = (expected_signature == razorpay_signature)
    except Exception as e:
        print(f"[SIGNATURE VERIFICATION] {e}")
        # Allow sandbox demo signature verification
        if 'demo' in str(razorpay_order_id).lower():
            signature_valid = True

    if signature_valid:
        order.payment_status = 'Paid'
        order.order_status = 'Preparing'
        order.payment_method = 'Razorpay Online (UPI/Card)'
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Payment verified successfully!',
            'redirect_url': url_for('order_confirmation', order_number=order.order_number)
        })
    else:
        return jsonify({'success': False, 'message': 'Payment verification failed. Invalid signature.'}), 400


@app.route('/order-confirmation/<order_number>')
def order_confirmation(order_number):
    """Order confirmation receipt with order status and items summary"""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_confirmation.html', order=order)


@app.route('/track-order', methods=['GET', 'POST'])
def track_order():
    """Customer order tracking lookup"""
    order = None
    searched_order_no = ''
    if request.method == 'POST':
        searched_order_no = request.form.get('order_number', '').strip().upper()
        if searched_order_no:
            order = Order.query.filter_by(order_number=searched_order_no).first()
            if not order:
                flash(f'No order found with tracking number "{searched_order_no}". Please check and try again.', 'danger')

    return render_template('track_order.html', order=order, searched_order_no=searched_order_no)


# ========================================================
# ADMIN DASHBOARD & MANAGEMENT ROUTES
# ========================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Secure admin authentication"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            session['admin_name'] = admin.full_name or admin.username
            admin.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome back, {admin.full_name or admin.username}!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    session.pop('admin_name', None)
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Dashboard statistics and recent orders"""
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(order_status='Pending').count()
    preparing_orders = Order.query.filter_by(order_status='Preparing').count()
    ready_orders = Order.query.filter_by(order_status='Ready').count()
    delivered_orders = Order.query.filter_by(order_status='Delivered').count()

    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0.0
    total_reservations = TableReservation.query.count()
    pending_reservations = TableReservation.query.filter_by(status='Pending').count()
    total_items = FoodItem.query.count()
    total_categories = Category.query.count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    recent_reservations = TableReservation.query.order_by(TableReservation.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           preparing_orders=preparing_orders,
                           ready_orders=ready_orders,
                           delivered_orders=delivered_orders,
                           total_revenue=total_revenue,
                           total_reservations=total_reservations,
                           pending_reservations=pending_reservations,
                           total_items=total_items,
                           total_categories=total_categories,
                           recent_orders=recent_orders,
                           recent_reservations=recent_reservations)


# --- Admin Food Items Management ---
@app.route('/admin/items')
@admin_required
def admin_items():
    """List and manage all menu items"""
    items = FoodItem.query.order_by(FoodItem.created_at.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/items.html', items=items, categories=categories)


@app.route('/admin/items/add', methods=['GET', 'POST'])
@admin_required
def admin_add_item():
    """Add a new food item"""
    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id', type=int)
        description = request.form.get('description', '').strip()
        price = request.form.get('price', type=float)
        is_veg = bool(request.form.get('is_veg'))
        image_url = request.form.get('image_url', '').strip()
        is_available = bool(request.form.get('is_available', True))
        is_featured = bool(request.form.get('is_featured', False))
        preparation_time = request.form.get('preparation_time', '20-25 mins').strip()

        if not name or not category_id or price is None or not image_url:
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin/item_form.html', categories=categories, item=None, action='Add')

        new_item = FoodItem(
            name=name,
            category_id=category_id,
            description=description,
            price=price,
            is_veg=is_veg,
            image_url=image_url,
            is_available=is_available,
            is_featured=is_featured,
            preparation_time=preparation_time
        )
        db.session.add(new_item)
        db.session.commit()

        flash(f'Dish "{name}" added successfully to the menu!', 'success')
        return redirect(url_for('admin_items'))

    return render_template('admin/item_form.html', categories=categories, item=None, action='Add')


@app.route('/admin/items/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_item(id):
    """Edit an existing food item"""
    item = FoodItem.query.get_or_404(id)
    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == 'POST':
        item.name = request.form.get('name', '').strip()
        item.category_id = request.form.get('category_id', type=int)
        item.description = request.form.get('description', '').strip()
        item.price = request.form.get('price', type=float)
        item.is_veg = bool(request.form.get('is_veg'))
        item.image_url = request.form.get('image_url', '').strip()
        item.is_available = bool(request.form.get('is_available'))
        item.is_featured = bool(request.form.get('is_featured'))
        item.preparation_time = request.form.get('preparation_time', '20-25 mins').strip()

        db.session.commit()
        flash(f'Dish "{item.name}" updated successfully.', 'success')
        return redirect(url_for('admin_items'))

    return render_template('admin/item_form.html', categories=categories, item=item, action='Edit')


@app.route('/admin/items/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_item(id):
    """Delete a food item"""
    item = FoodItem.query.get_or_404(id)
    item_name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f'Dish "{item_name}" has been deleted.', 'info')
    return redirect(url_for('admin_items'))


@app.route('/admin/items/toggle/<int:id>', methods=['POST'])
@admin_required
def admin_toggle_item(id):
    """Toggle food availability status"""
    item = FoodItem.query.get_or_404(id)
    item.is_available = not item.is_available
    db.session.commit()
    return jsonify({'success': True, 'is_available': item.is_available})


# --- Admin Categories Management ---
@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    """List and create menu categories"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        display_order = request.form.get('display_order', 0, type=int)

        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin_categories'))

        slug = name.lower().replace(' ', '-').replace('&', 'and')
        # Check duplicate
        existing = Category.query.filter((Category.name == name) | (Category.slug == slug)).first()
        if existing:
            flash(f'Category "{name}" already exists.', 'warning')
            return redirect(url_for('admin_categories'))

        new_cat = Category(
            name=name,
            slug=slug,
            description=description,
            image_url=image_url or 'https://images.unsplash.com/photo-1544025162-d76694265947?w=800',
            display_order=display_order,
            is_active=True
        )
        db.session.add(new_cat)
        db.session.commit()
        flash(f'Category "{name}" added successfully.', 'success')
        return redirect(url_for('admin_categories'))

    categories = Category.query.order_by(Category.display_order.asc()).all()
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin/categories/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_category(id):
    """Delete a category"""
    category = Category.query.get_or_404(id)
    cat_name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{cat_name}" and its associated items removed.', 'info')
    return redirect(url_for('admin_categories'))


# --- Admin Orders Management ---
@app.route('/admin/orders')
@admin_required
def admin_orders():
    """View and filter customer food orders"""
    status_filter = request.args.get('status', 'all')
    query = Order.query.order_by(Order.created_at.desc())
    if status_filter != 'all':
        query = query.filter_by(order_status=status_filter)

    orders = query.all()
    return render_template('admin/orders.html', orders=orders, current_status=status_filter)


@app.route('/admin/orders/<int:id>')
@admin_required
def admin_order_detail(id):
    """View specific order details"""
    order = Order.query.get_or_404(id)
    return render_template('admin/order_detail.html', order=order)


@app.route('/admin/orders/update-status/<int:id>', methods=['POST'])
@admin_required
def admin_update_order_status(id):
    """Update order status: Pending, Preparing, Ready, Delivered, Cancelled"""
    order = Order.query.get_or_404(id)
    new_status = request.form.get('order_status')
    payment_status = request.form.get('payment_status')

    if new_status in ['Pending', 'Preparing', 'Ready', 'Delivered', 'Cancelled']:
        order.order_status = new_status

    if payment_status in ['Pending', 'Paid']:
        order.payment_status = payment_status

    db.session.commit()
    flash(f'Order #{order.order_number} status updated to "{order.order_status}".', 'success')

    # Allow redirect back to referrer or orders page
    return redirect(request.referrer or url_for('admin_orders'))


# --- Admin Reservations Management ---
@app.route('/admin/reservations')
@admin_required
def admin_reservations():
    """View and manage table reservations"""
    reservations = TableReservation.query.order_by(TableReservation.created_at.desc()).all()
    return render_template('admin/reservations.html', reservations=reservations)


@app.route('/admin/reservations/update-status/<int:id>', methods=['POST'])
@admin_required
def admin_update_reservation_status(id):
    """Update reservation status: Confirmed, Pending, Completed, Cancelled"""
    reservation = TableReservation.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['Confirmed', 'Pending', 'Completed', 'Cancelled']:
        reservation.status = new_status
        db.session.commit()
        flash(f'Reservation {reservation.reservation_code} updated to "{new_status}".', 'success')
    return redirect(url_for('admin_reservations'))


@app.route('/admin/reservations/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_reservation(id):
    """Delete a reservation"""
    res = TableReservation.query.get_or_404(id)
    db.session.delete(res)
    db.session.commit()
    flash(f'Reservation {res.reservation_code} removed.', 'info')
    return redirect(url_for('admin_reservations'))


# --- Admin Contact Messages Management ---
@app.route('/admin/messages')
@admin_required
def admin_messages():
    """Customer inquiries inbox"""
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)


@app.route('/admin/messages/mark-read/<int:id>', methods=['POST'])
@admin_required
def admin_mark_message_read(id):
    """Toggle message read/unread"""
    msg = ContactMessage.query.get_or_404(id)
    msg.is_read = not msg.is_read
    db.session.commit()
    return jsonify({'success': True, 'is_read': msg.is_read})


@app.route('/admin/messages/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_message(id):
    """Delete a contact message"""
    msg = ContactMessage.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'info')
    return redirect(url_for('admin_messages'))


# ========================================================
# AUTO INITIALIZATION ON STARTUP
# ========================================================
def init_app_state():
    with app.app_context():
        try:
            db.create_all()
            # If database is completely empty, automatically seed initial data
            if Admin.query.count() == 0 or Category.query.count() == 0:
                print("[APP INIT] Empty database detected. Auto-seeding initial restaurant catalog...")
                from seed_data import seed_database
                seed_database()
        except Exception as e:
            print(f"[APP INIT NOTICE] Database auto-check: {e}")

init_app_state()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
