from flask import Flask, render_template, flash, request, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from data import *
import json


app = Flask(__name__)

app.config['SECRET_KEY'] = 'cr8ivecloud'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'flask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
#product = Products()

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        password = sha256_crypt.hash(request.form['password'])
        email = request.form['email']
        city = request.form['city']
        

        cur = mysql.connection.cursor()  

        cur.execute('''SELECT 1 FROM users WHERE phone=%s''', [phone])

        if cur.rowcount == 1:
            flash('an account has been registered with this number', 'red')
            return redirect(request.url)
        else:
            cur.execute('''INSERT INTO Users(username, phone, password, email, city) VALUES (%s, %s, %s, %s, %s)''', (username, phone, password, email, city))
            mysql.connection.commit()
            cur.close()
            flash('you are now registered and can log in', 'green')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    cart_data = []
    if request.method == 'POST':
        phone = request.form['phone']
        password_1 = request.form['password_1']
        
        cur = mysql.connection.cursor()
        result = cur.execute(''' SELECT * FROM users WHERE phone = %s ''', [phone])
        if result > 0:
            data = cur.fetchone()    
            password = data['password']
            if sha256_crypt.verify(password_1, password):
                session['logged_in'] = True
                session['username'] = data['username']
                session['phone'] = phone
                flash('login successful', 'green')
                return redirect(url_for('store'))
        
            else:
                flash('invalid login details', 'red')
                return redirect(request.url)
        
        else:
            flash('no user', 'red')
            return redirect(request.url)
    
    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    data = []
    cart_data = []
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
     
    result = cur.execute('''SELECT * FROM products''')
    products = cur.fetchall()
    if result > 0:
        return render_template('dashboard.html', products=products)

    return render_template('dashboard.html')

@app.route('/add_to_cart/<int:i>/', methods=['POST'])
def add_to_cart(i):
    data = []
    if request.method == 'POST':
        if i in cart_data:
            print('i is already in cart')
        else:
            cart_data.append(i)
            
            
        
        return '{"cart_data":cart_data}'

@app.route('/remove_cart_item/<int:id>/', methods=['POST'])
def remove_cart_item(id):
    for i in data:
        if i['id'] == id:
            data.remove(i)
            for x in cart_data:
                if i['id'] == x:
                    cart_data.remove(x)
            return render_template('cart.html', data=data)

    return redirect(url_for('cart'))


@app.route('/cart', methods=['POST','GET'])
def cart():
    cur = mysql.connection.cursor()
    for i in cart_data:
        cur.execute('''SELECT * FROM products WHERE id = %s''', [i])
        result = cur.fetchall()
        #print(result[0])
        for i in result:
            if i in data:
                pass
            else:
                data.append(i)

        #
        #for i in result:
        #    ab = i
        #print(data)
    

    return render_template('cart.html', data=data)

@app.route('/store')
def store():
    cur = mysql.connection.cursor()
    
    result = cur.execute('''SELECT * FROM products''')
    products = cur.fetchall()
    if result > 0:
        return render_template('store.html', products=products, product=product)

    #cur.execute(''' ALTER TABLE Users MODIFY password VARCHAR(256)''')
    #cur.execute('''CREATE TABLE users(id INTEGER AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50), password VARCHAR(256), email VARCHAR(50), city VARCHAR(50))''')
    #cur.execute('''CREATE TABLE users(phone INTEGER PRIMARY KEY, username VARCHAR(50), password VARCHAR(256), email VARCHAR(50), city VARCHAR(50))''')

    else:
        return render_template('store.html')
    
    cur.close()


@app.route('/add_product', methods=['GET','POST'])
@is_logged_in
def add_product():
    cur = None
    #cur.execute('''ALTER TABLE products ADD image VARCHAR(150)''')
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        image = request.files['image']

        cur.execute('''INSERT INTO products(name, price, description, image) VALUES (%s, %s, %s, %s)''', (name, price, description, image.filename))
        
        mysql.connection.commit()
        
        cur.close()
        
        return redirect(url_for('dashboard'))
  
    
    return render_template('add_product.html')

    
@app.route('/product/<string:id>/', methods=['GET','POST'])
@is_logged_in
def product(id):
    cur = mysql.connection.cursor()
    result = cur.execute('''SELECT * FROM products WHERE id = %s''', [id])
    product = cur.fetchone()    
    return render_template('product.html', product=product)


@app.route('/edit_product/<string:id>/', methods=['GET','POST'])
@is_logged_in
def edit_product(id):
    cur = mysql.connection.cursor()

    result = cur.execute(''' SELECT * FROM products WHERE id = %s''', [id])
    product = cur.fetchone()
    #app.logger.info(product['price'])
    #request.form['name'] = product['name']  
    #request.form['price'] = product['price']
    #request.form['description'] = product['description']

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        cur.execute('''UPDATE products  SET name=%s , price=%s, description=%s WHERE id=%s''', (name, price, description, id))
        
        mysql.connection.commit()
        
        cur.close()
        
        return redirect(url_for('dashboard'))

    return render_template('edit_product.html', product=product)



@app.route('/delete_product/<string:id>/', methods=['GET','POST'])
@is_logged_in
def delete_product(id):
    cur = mysql.connection.cursor()
     
    cur.execute('''DELETE FROM products WHERE id = %s''', [id])

    mysql.connection.commit()

    cur.close()

    msg = 'product deleted'
     
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)