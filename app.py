from flask import Flask, render_template, redirect, url_for, request, flash
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__)) 
# Definimos secret key para poder enviar flash
app.secret_key = 'secretkey'

# SUBIDA DE IMAGENES
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(photoname):
    return '.' in photoname and photoname.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# paràmetre que farà servir SQLAlchemy per a connectar-se
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + basedir + "/database.db"
# mostre als logs les ordres SQL que s'executen
app.config["SQLALCHEMY_ECHO"] = True

# Inicio SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

# Crear clases de tablas
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    slug = db.Column(db.Text, unique=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    photo = db.Column(db.Text)
    price = db.Column(db.DECIMAL(10, 2))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



@app.route("/")
def inicio():
    return render_template('hello.html')        

@app.route("/products/list")
def list_products():
    lista = db.session.query(Product, Category).join(Category).order_by(Product.id.asc()).all()
    return render_template('products/list.html',results=lista)

# # FUNCIÓN PARA VALIDAR CADENA DE ENTRADA 
errores = []
def validar_cadena(campo, valor):
    if len(valor) < 1:
        flash(f"{campo} no pot estar buit.")
        errores.append("1")
    elif len(valor) > 255:
        flash(f"{campo} no pot superar els 255 caràcters.")
        errores.append("2")
    elif campo == 'Categoria':
        categories = [category.id for category in Category.query.all()]  # Obtén todas las categorías
        app.logger.info(categories)
        if int(valor) not in categories:
            flash(f"{campo} no s'ha seleccionat una categoria correcte")
            errores.append("error")
        

@app.route('/products/create', methods=["GET", "POST"])
def product_create():
    if request.method == 'GET':
        categories = db.session.query(Category).order_by(Category.id.asc()).all()
        return render_template('products/create.html', categories=categories)
    elif request.method == 'POST':
        data = request.form
        product = Product()
        product.title = data.get('title')
        product.description = data.get('description')
        photo = request.files['photo']
        product.price = data.get('price')
        product.category_id = data.get('category_id')
        product.created = datetime.now()
        product.updated = datetime.now()

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        product.photo = filename

        validar_cadena("Nom", product.title)
        validar_cadena("Descripcio", product.description)
        validar_cadena("Preu", product.price)
        validar_cadena("Categoria", product.category_id)

        if errores:
            errores.clear()
            return redirect(request.url)
        else:
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('list_products'))

@app.route('/products/update/<int:id>', methods=["GET", "POST"])
def products_update(id):
    (product, category) = db.session.query(Product, Category).join(Category).filter(Product.id == id).one()
    if request.method == 'GET':
        categories = db.session.query(Category).filter(Category.id != product.category_id).order_by(Category.id.asc()).all()
        return render_template('products/update.html', product=product, categories=categories, category=category)
    elif request.method == 'POST':
        data = request.form
        product.title = data.get('title')
        product.description = data.get('description')
        product.photo = data.get('photo')
        product.price = data.get('price')
        product.category_id = data.get('category_id')
        product.updated = datetime.now()
        
        validar_cadena("Nom", product.title)
        validar_cadena("Descripcio", product.description)
        validar_cadena("Preu", product.price)
        validar_cadena("Categoria", product.category_id)

        if errores:
            errores.clear()
            return redirect(request.url)
        else:
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('list_products'))


@app.route('/products/read/<int:id>')
def products_read(id):
    (product, category) = db.session.query(Product, Category).join(Category).filter(Product.id == id).one()
    return render_template('products/read.html', product = product, category = category)

@app.route('/products/delete/<int:id>',methods = ['GET', 'POST'])
def products_delete(id):
    item = db.session.query(Product).filter(Product.id == id).one()

    if request.method == 'GET':
        return render_template('products/delete.html', item = item)
    else:
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for('list_products'))