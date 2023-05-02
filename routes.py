from datetime import timedelta
import hashlib
import os
from flask import flash, redirect, request, render_template, session, url_for, send_from_directory
from app import app
from app import db
from models import Product, User
from auth import check_login
from werkzeug.utils import secure_filename

@app.route('/')
def home_page():
   profile = check_login()
   products = Product.query.all()
   return render_template('index.html', current_user=profile, 
                          products=products)

@app.route('/login')
def login_page():
   return render_template('login.html')

@app.route('/process-login', methods=['POST'])
def process_login():
   email = request.form.get('email')
   password = request.form.get('password')
   if email == '':
      flash('Please enter email.')
      return redirect(url_for('login_page'))
   # find user in database
   correct_user = User.query.filter(User.email == email).first()
   if correct_user is None:
      flash('Invalid email or password')
      return redirect(url_for('login_page'))
   # hash password
   pw = hashlib.sha256(password.encode()).hexdigest()
   # check if password is the same
   if correct_user.password_hash != pw:
      flash('Invalid email or password')
      return redirect(url_for('login_page'))
   # login is correct 
   session['id'] = correct_user.id
   resp = redirect(url_for('home_page'))
   # set cookie
   resp.set_cookie('id', str(correct_user.id), max_age=timedelta(days=5))
   resp.set_cookie('p_hash', pw, max_age=timedelta(days=5))
   return resp


@app.route('/signup')
def sign_up():
   return render_template('signup.html')

@app.route('/do-signup', methods=['POST'])
def do_signup():
   username = request.form.get('username')
   email = request.form.get('email')
   phone = request.form.get('phone')
   password = request.form.get('password')
   # check username
   if username == '':
      flash('Please enter your username!')
      return redirect(url_for('sign_up'))
   elif password == '':
      flash('Please enter your password')
      return redirect(url_for('sign_up'))
   # hash the password
   pw = hashlib.sha256(password.encode()).hexdigest()
   # save the user details 
   new_user = User(username = username, email=email, phone = phone, 
                   password_hash=pw)
   db.session.add(new_user)
   db.session.commit()
   flash('Account Created successfully, please login.')
   return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
   # clear session
   session.pop('id')
   # expire cookies
   resp = redirect(url_for('login_page'))
   resp.set_cookie('id', expires=0)
   resp.set_cookie('p_hash', expires=0)
   flash("You don logout!")
   return resp


@app.route('/add-product', methods=['POST', 'GET'])
def add_product():
   if request.method == 'GET':
      return render_template('add-product.html')
   else:
      title = request.form.get('title')
      price = request.form.get('price')
      category = request.form.get('category')
      description = request.form.get('description')
      picture = request.files['picture']

      if picture is None or picture.filename is None:
         flash("Please select product picture")
         return redirect(url_for('add_product'))
      filename = secure_filename(picture.filename)

      # save picture
      picture.save(os.path.join('uploads', filename))
      product = Product(title=title, price=price, category=category, 
                        description=description, image=filename)
      db.session.add(product)
      db.session.commit()
      flash(f"{title} added successfully!")
      resp = redirect(url_for('home_page'))
      return resp
   
@app.route('/uploads/<filename>')
def view_file(filename):
   return send_from_directory('uploads', filename)
   

@app.route('/edit/<pid>', methods=['GET', 'POST'])
def edit_product(pid):
   # look for product in the database
   product = Product.query.filter(Product.id == pid).first()
   # if product not found
   if product is None:
      flash('Product not found')
      return redirect(url_for('home_page'))

   # check if method is get
   if request.method == 'GET':
      return render_template('edit-product.html', product=product)
   else:
      # collect form and update product
      title = request.form.get('title')
      price = request.form.get('price')
      category = request.form.get('category')
      description = request.form.get('description')
      picture = request.files['picture']

      if picture is None or picture.filename is None:
         flash("Please select product picture")
         return redirect(url_for('edit_product'))
      filename = secure_filename(picture.filename)

      # save picture
      picture.save(os.path.join('uploads', filename))
      # update product
      product.title = title
      product.price = price
      product.category = category
      product.description = description
      product.image = filename
      # save the update
      db.session.commit()
      flash(f'{title} updated successfully')
      return redirect(url_for('home_page'))


@app.route('/delete/<pid>')
def delete_product(pid):
   # look for product in the database
   product = Product.query.filter(Product.id == pid).first()
   # if product not found
   if product is None:
      flash('Product not found')
      return redirect(url_for('home_page'))
   # delete product
   db.session.delete(product)
   db.session.commit()
   flash('Product deleted successfully')
   return redirect(url_for('home_page'))
