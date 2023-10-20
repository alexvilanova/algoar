from flask import Blueprint, redirect, url_for, render_template, request, flash
from .models import Category, User, Product
from . import db_manager as db
from werkzeug.utils import secure_filename, os
from datetime import datetime

# Blueprint
main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static"
)

# SUBIDA DE IMAGENES
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# main_bp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(photoname):
    return '.' in photoname and photoname.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        if int(valor) not in categories:
            flash(f"{campo} no s'ha seleccionat una categoria correcte")
            errores.append("error")
            
@main_bp.route("/")
def inicio():
    return redirect(url_for('main_bp.list_products'))
       
@main_bp.route("/products/list")
def list_products():
    lista = db.session.query(Product, Category).join(Category).order_by(Product.id.asc()).all()
    return render_template('products/list.html',results=lista)

@main_bp.route('/products/create', methods=["GET", "POST"])
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
            photo.save(os.path.join(main_bp.config['UPLOAD_FOLDER'], filename))
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
            return redirect(url_for('main_bp.list_products'))
        
@main_bp.route('/products/update/<int:id>', methods=["GET", "POST"])
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
        
        
        if product.photo:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(main_bp.config['UPLOAD_FOLDER'], filename))

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
            return redirect(url_for('main_bp.list_products'))
        
@main_bp.route('/products/read/<int:id>')
def products_read(id):
    (product, category) = db.session.query(Product, Category).join(Category).filter(Product.id == id).one()
    return render_template('products/read.html', product = product, category = category)

@main_bp.route('/products/delete/<int:id>',methods = ['GET', 'POST'])
def products_delete(id):
    item = db.session.query(Product).filter(Product.id == id).one()

    if request.method == 'GET':
        return render_template('products/delete.html', item = item)
    else:
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for('main_bp.list_products'))