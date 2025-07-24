from flask import render_template, redirect, url_for, flash, request, session, g
from Beauty.models import db, User, Product, Order, OrderItem
from functools import wraps
import math

ITEMS_PER_PAGE = 8

def init_app(app):
    
    # Authentication decorator
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Landlord only decorator
    def landlord_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page', 'warning')
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user.is_landlord:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = User.query.get(user_id)
    
    @app.route('/')
    def index():
        
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/contact')
    def contact():
        return render_template('contact.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                session['user_id'] = user.id
                flash('You have been logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Login unsuccessful. Please check your username and password', 'danger')
                
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            is_landlord = 'is_landlord' in request.form
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'danger')
                return render_template('register.html')
            
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already registered. Please use a different one.', 'danger')
                return render_template('register.html')
            
            user = User(username=username, email=email, is_landlord=is_landlord)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        return render_template('register.html')
    
    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/product/<int:product_id>')
    def product(product_id):
        product = Product.query.get_or_404(product_id)
        return render_template('product.html', product=product)
    
    @app.route('/view_static_product', methods=['POST'])
    def view_static_product():
        product_type = request.form.get('product_type')
        
        products = {
            # Foundation products
            'Foundation': {
                'name': 'Fit Me Foundation',
                'description': 'Blur imperfections, reduce shine, and achieve a flawless matte finish that lasts throughout the day.',
                'price': 3000,
                'category': 'Foundation',
                'image_url': 'images/foundation1.jpg',
                'stock': 15
            },
            'foundation_elf': {
                'name': 'Elf Foundation',
                'description': 'Lightweight liquid foundation with a natural finish.',
                'price': 1950,
                'category': 'Foundation',
                'image_url': 'images/foundation2.jpg',
                'stock': 20
            },
            'foundation_fenty': {
                'name': 'Fenty Beauty Foundation',
                'description': 'Hydrates with sodium hyaluronate. Instantly blurs + evens skin. Shine free. Longwear.',
                'price': 2800,
                'category': 'Foundation',
                'image_url': 'images/foundation3.jpg',
                'stock': 12
            },
        
            # Primer products
            'primer_benefit': {
                'name': 'Elf Primer',
                'description': 'Minimizes the appearance of pores and creates a smooth makeup base.',
                'price': 2500,
                'category': 'Primer',
                'image_url': 'images/primer1.jpg',
                'stock': 18
            },
            'primer_milk': {
                'name': 'Milk Hydro Grip Primer',
                'description': 'Hydrating primer that helps makeup stay in place all day.',
                'price': 2200,
                'category': 'Primer',
                'image_url': 'images/primer2.webp',
                'stock': 15
            },
            'primer_smashbox': {
                'name': 'Smashbox Photo Finish Primer',
                'description': 'Blurs imperfections and creates a perfect base for makeup.',
                'price': 2800,
                'category': 'Primer',
                'image_url': 'images/primer3.jpg',
                'stock': 20
            },
            
            # Concealer products
            'concealer_nars': {
                'name': 'NARS Radiant Creamy Concealer',
                'description': 'Full-coverage concealer that brightens and perfects the skin.',
                'price': 2300,
                'category': 'Concealer',
                'image_url': 'images/concealer1.jpg',
                'stock': 10
            },
            'concealer_tarte': {
                'name': 'Tarte Shape Tape Concealer',
                'description': 'Cult-favorite concealer with incredible coverage and staying power.',
                'price': 2600,
                'category': 'Concealer',
                'image_url': 'images/concealer2.jpg',
                'stock': 12
            },
            'concealer_maybelline': {
                'name': 'Maybelline Fit Me Concealer',
                'description': 'Lightweight concealer that blends seamlessly for a natural finish.',
                'price': 1800,
                'category': 'Concealer',
                'image_url': 'images/concealer3.webp',
                'stock': 25
            },
            
            # Mascara products
            'mascara_toofaced': {
                'name': 'Sky High Mascara',
                'description': 'Iconic mascara that provides extreme volume and dramatic length.',
                'price': 2400,
                'category': 'Mascara',
                'image_url': 'images/mascara1.jpg',
                'stock': 15
            },
            'mascara_benefit': {
                'name': 'Benefit Roller Lash Mascara',
                'description': 'Curl-holding mascara that lifts and separates lashes.',
                'price': 2200,
                'category': 'Mascara',
                'image_url': 'images/mascara2.jpg',
                'stock': 18
            },
            #lipstick products
            'mascara_maybelline': {
                'name': 'Maybelline Lash Sensational Mascara',
                'description': 'Fan-effect brush for full, fanned-out lashes with intense color.',
                'price': 1900,
                'category': 'Mascara',
                'image_url': 'images/mascara3.jpg',
                'stock': 20
            },
            'lipstick_maybelline': {
            'name': 'SuperStay Matte Ink Liquid Lipstick',
            'brand': 'Maybelline New York',
            'price': 1500,
            'category': 'Lipstick',
            'description': 'Long-lasting liquid lipstick with a matte finish that stays put all day and night.',
            'image_url': 'images/lipstick1.jpg',
            'stock': 18,
            'features': ['16-hour wear', 'No transfer', 'Intense pigment'],
            'shades': ['Pioneer', 'Lover', 'Dreamer', 'Seductress', 'Voyager'],
            
        },
        'lipstick_wearified': {
            'name': 'Lip Frosting Matte Liquid Lipstick',
            'brand': 'Wearified',
            'price': 2000,
            'category': 'Lipstick',
            'description': 'Highly pigmented matte liquid lipstick that transforms from butter to matte for comfortable long wear.',
            'image_url': 'images/lipstick2.jpg',
            'stock': 12,
            'features': ['High pigmentation', 'Butter to matte finish', 'Smudge-proof'],
            'shades': ['Berry Blush', 'Coral Crush', 'Nude Mood', 'Pink Perfection', 'Red Revival'],
            'skin_type': ['All skin types'],
            
        },
        'lipstick_huda': {
            'name': 'Power Bullet Matte Lipstick',
            'brand': 'Huda Beauty',
            'price': 2500,
            'category': 'Lipstick',
            'description': 'Luxury matte lipstick with intense color payoff and long-lasting wear.',
            'image_url': 'images/lipstick3.jpg',
            'stock': 8,
            'features': ['One-stroke application', 'Comfort matte formula', 'Intense pigmentation'],
            'shades': ['Interview', 'Prom Night', 'Ladies Night', 'Third Date', 'Wedding Day'],
            'skin_type': ['All skin types'],
            
        },
            
            # Blush products
            'blush_nars': {
                'name': 'NARS Orgasm Blush',
                'description': 'Iconic peachy-pink blush with subtle golden shimmer.',
                'price': 2200,
                'category': 'Blush',
                'image_url': 'images/blush1.jpg',
                'stock': 10
            },
            'blush_benefit': {
                'name': 'Benefit Dandelion Blush',
                'description': 'Soft, pale pink blush for a subtle, brightening effect.',
                'price': 1950,
                'category': 'Blush',
                'image_url': 'images/blush2.jpg',
                'stock': 12
            },
            'blush_milani': {
                'name': 'Milani Baked Blush',
                'description': 'Richly pigmented baked blush for a radiant flush of color.',
                'price': 850,
                'category': 'Blush',
                'image_url': 'images/blush3.webp',
                'stock': 15
            },
            
            # Eyeshadow products
            'eyeshadow_urban': {
                'name': 'Urban Decay Naked Palette',
                'description': '12 versatile neutral shades for endless looks.',
                'price': 3500,
                'category': 'Eyeshadow',
                'image_url': 'images/eyeshadow1.jpg',
                'stock': 8
            },
            'eyeshadow_huda': {
                'name': 'Huda Beauty Rose Gold Palette',
                'description': 'Luxurious mix of mattes and shimmers in rose gold tones.',
                'price': 4200,
                'category': 'Eyeshadow',
                'image_url': 'images/eyeshadow2.jpg',
                'stock': 10
            },
            'eyeshadow_morphe': {
                'name': 'Morphe Nature Glow Palette',
                'description': '35 highly pigmented shades in warm, earthy tones.',
                'price': 2500,
                'category': 'Eyeshadow',
                'image_url': 'images/eyeshadow3.webp',
                'stock': 12
            },
            
            # Powder products
            'powder_laura': {
                'name': 'Laura Mercier Translucent Powder',
                'description': 'Lightweight powder that sets makeup and minimizes shine.',
                'price': 2800,
                'category': 'Powder',
                'image_url': 'images/powder1.jpg',
                'stock': 15
            },
            'powder_huda': {
                'name': 'HUDA Beauty Easy Bake Powder',
                'description': 'Brightening loose powder for crease-free makeup.',
                'price': 3200,
                'category': 'Powder',
                'image_url': 'images/powder2.jpg',
                'stock': 10
            },
            'powder_mac': {
                'name': 'MAC Mineralize Skinfinish',
                'description': 'Natural finish powder with a radiant glow.',
                'price': 2300,
                'category': 'Powder',
                'image_url': 'images/powder3.jpg',
                'stock': 12
            },
            
            # Bronzer products
            'bronzer_benefit': {
                'name': 'Benefit Hoola Bronzer',
                'description': 'Matte bronzer for a natural sun-kissed glow.',
                'price': 2400,
                'category': 'Bronzer',
                'image_url': 'images/bronzer1.webp',
                'stock': 15
            },
            'bronzer_nars': {
                'name': 'NARS Laguna Bronzer',
                'description': 'Iconic bronzer with a subtle shimmer.',
                'price': 2700,
                'category': 'Bronzer',
                'image_url': 'images/bronzer2.jpg',
                'stock': 12
            },
            'bronzer_physicians': {
                'name': 'Physicians Formula Butter Bronzer',
                'description': 'Creamy bronzer with a natural, sun-kissed finish.',
                'price': 1800,
                'category': 'Bronzer',
                'image_url': 'images/bronzer3.jpg',
                'stock': 18
            },
            
            # Highlighter products
            'highlighter_fenty': {
                'name': 'Fenty Killawatt Highlighter',
                'description': 'Intense shimmer highlighter for a blinding glow.',
                'price': 3100,
                'category': 'Highlighter',
                'image_url': 'images/highlighter1.jpg',
                'stock': 10
            },
            'highlighter_becca': {
                'name': 'Becca Shimmering Skin Perfector',
                'description': 'Liquid highlighter for a natural, dewy glow.',
                'price': 2600,
                'category': 'Highlighter',
                'image_url': 'images/highlighter2.webp',
                'stock': 12
            },
            'highlighter_abh': {
                'name': 'ABH Glow Kit',
                'description': 'Multipan highlighter palette for versatile glow.',
                'price': 2900,
                'category': 'Highlighter',
                'image_url': 'images/highlighter3.webp',
                'stock': 15
            },
            
            # Lip Gloss products
            'lipgloss_fenty': {
                'name': 'Fenty Gloss Bomb',
                'description': 'Hydrating gloss with intense shine and plumping effect.',
                'price': 2200,
                'category': 'Lip Gloss',
                'image_url': 'images/lipgloss1.webp',
                'stock': 15
            },
            'lipgloss_nyx': {
                'name': 'NYX Butter Gloss',
                'description': 'Creamy, non-sticky gloss with vibrant color payoff.',
                'price': 1500,
                'category': 'Lip Gloss',
                'image_url': 'images/lipgloss2.jpg',
                'stock': 20
            },
            'lipgloss_rare': {
                'name': 'Rare Beauty Glossy Balm',
                'description': 'Hydrating lip balm with a sheer, glossy finish.',
                'price': 1800,
                'category': 'Lip Gloss',
                'image_url': 'images/lipgloss3.jpg',
                'stock': 18
            },
            
            # Skincare products
            'skincare_ordinary': {
                'name': 'The Ordinary Hyaluronic Acid',
                'description': 'Hydration serum with multi-molecular hyaluronic complex.',
                'price': 1200,
                'category': 'Skincare',
                'image_url': 'images/skincare1.jpeg',
                'stock': 20
            },
            'skincare_cetaphil': {
                'name': 'Cetaphil Moisturizer',
                'description': 'Intensive moisturizing cream for dry to sensitive skin.',
                'price': 1600,
                'category': 'Skincare',
                'image_url': 'images/skincare2.jpeg',
                'stock': 25
            },
            'skincare_laroche': {
                'name': 'La Roche-Posay Sunscreen',
                'description': 'Broad-spectrum SPF 50+ for daily sun protection.',
                'price': 2000,
                'category': 'Skincare',
                'image_url': 'images/skincare3.jpeg',
                'stock': 15
            },
            
            # Other products
            'other_beautyblender': {
                'name': 'Original Beauty Blender',
                'description': 'Professional makeup sponge for flawless application.',
                'price': 900,
                'category': 'Other',
                'image_url': 'images/other1.jpg',
                'stock': 30
            },
            'other_brushset': {
                'name': 'Professional Brush Set',
                'description': 'Complete set of high-quality makeup brushes.',
                'price': 2500,
                'category': 'Other',
                'image_url': 'images/other2.webp',
                'stock': 15
            },
            'other_organizer': {
                'name': 'Acrylic Makeup Organizer',
                'description': 'Clear storage solution for your beauty essentials.',
                'price': 1200,
                'category': 'Other',
                'image_url': 'images/other3.jpg',
                'stock': 20
            }
        }
        
        if product_type in products:
            product = products[product_type]
            return render_template('static_product.html', product=product)
        else:
            flash('Product not found', 'danger')
            return redirect(url_for('index'))
    
    @app.route('/create_makeup', methods=['GET', 'POST'])
    @landlord_required
    def create_makeup():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')
            stock = request.form.get('stock')
            
            # Get the selected image path from the form dropdown
            image_url = request.form.get('image_url')
            
            # Create a new product with the selected image path
            product = Product(
                name=name,
                description=description,
                price=int(price),
                category=category,
                stock=int(stock),
                image_url=image_url,
                seller_id=session['user_id']
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash('Your makeup product has been created!', 'success')
            return redirect(url_for('dashboard'))
            
        return render_template('create_makeup.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = User.query.get(session['user_id'])
        if user.is_landlord:
            products = Product.query.filter_by(seller_id=user.id).all()
            return render_template('dashboard.html', products=products)
        else:
            orders = Order.query.filter_by(user_id=user.id).all()
            return render_template('dashboard.html', orders=orders)
    
    @app.route('/buy/<int:product_id>', methods=['POST'])
    @login_required
    def buy_product(product_id):
        product = Product.query.get_or_404(product_id)
        
        if product.stock < 1:
            flash('Sorry, this product is out of stock!', 'danger')
            return redirect(url_for('product', product_id=product_id))
        
        # Create a new order
        order = Order(
            user_id=session['user_id'],
            total_amount=product.price,
            status='completed'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Add the item to the order
        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=1,
            price=product.price
        )
        
        db.session.add(order_item)
        
        # Decrease the stock
        product.stock -= 1
        
        db.session.commit()
        
        flash('You have successfully purchased this product!', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/buy_static_product', methods=['POST'])
    @login_required
    def buy_static_product():
        product_type = request.form.get('product_type')
        
        # Dictionary mapping product types to prices
        product_prices = {
            # Foundation products
        'Foundation': 3000,
        'foundation_elf': 1950,
        'foundation_fenty': 2800,
        
        # Primer products
        'primer_benefit': 2500,
        'primer_milk': 2200,
        'primer_smashbox': 2800,
        
        # Concealer products
        'concealer_nars': 2300,
        'concealer_tarte': 2600,
        'concealer_maybelline': 1800,
        
        # Mascara products
        'mascara_toofaced': 2400,
        'mascara_benefit': 2200,
        'mascara_maybelline': 1900,
        
        # Lipstick products
        'lipstick_maybelline': 1500,
        'lipstick_wearified': 2000,
        'lipstick_huda': 2500,
        
        # Blush products
        'blush_nars': 2200,
        'blush_benefit': 1950,
        'blush_milani': 850,
        
        # Eyeshadow products
        'eyeshadow_urban': 3500,
        'eyeshadow_huda': 4200,
        'eyeshadow_morphe': 2500,
        
        # Powder products
        'powder_laura': 2800,
        'powder_huda': 3200,
        'powder_mac': 2300,
        
        # Bronzer products
        'bronzer_benefit': 2400,
        'bronzer_nars': 2700,
        'bronzer_physicians': 1800,
        
        # Highlighter products
        'highlighter_fenty': 3100,
        'highlighter_becca': 2600,
        'highlighter_abh': 2900,
        
        # Lip Gloss products
        'lipgloss_fenty': 2200,
        'lipgloss_nyx': 1500,
        'lipgloss_rare': 1800,
        
        # Skincare products
        'skincare_ordinary': 1200,
        'skincare_cetaphil': 1600,
        'skincare_laroche': 2000,
        
        # Other products
        'other_beautyblender': 900,
        'other_brushset': 2500,
        'other_organizer': 1200
    }
    
    
        
        # Get the price for the product type
        price = product_prices.get(product_type)
        
        if not price:
            flash('Invalid product type', 'danger')
            return redirect(url_for('index'))
        
        # Create a new order
        order = Order(
            user_id=session['user_id'],
            total_amount=price,
            status='completed'
        )
        
        db.session.add(order)
        db.session.commit()
        
     
        flash(f'You have successfully purchased this product!', 'success')
        return redirect(url_for('dashboard'))