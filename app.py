from flask import Flask,render_template,url_for,request,redirect,flash
from werkzeug.utils import secure_filename
import sqlite3
import datetime,os

DATABASE = 'database.db'
UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        db = Flask._database = sqlite3.connect(DATABASE,check_same_thread=False)
    return db

def close_connection(exception):
    db = getattr(Flask, '_database', None)
    if db is not None:
        db.close()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/prueba', methods=['GET', 'POST'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/prueba', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route("/")
def inicio():
    return render_template('hello.html')        



@app.route("/products/list")
def list_products():
    query = "SELECT * FROM PRODUCTS"
    cursor = get_db().execute(query)
    result = cursor.fetchall()
    datos = []
    for x in result:
        data = {
        'id': x[0],
        'nom': x[1],
        'descripcio': x[2],
        'imatge': x[3],
        'preu': x[4],
        'idcat': x[5],
        'vendedor': x[6],
        'creado': x[7],
        'actualizado': x[8],
        }
        datos.append(data)
    cursor.close()
    return render_template('products/list.html',results=datos)

# FUNCIÓN PARA LEER INFO CATEGORIAS
def mostrar_cat():
    cursor = get_db().execute("SELECT * FROM CATEGORIES")
    result = cursor.fetchall()
    data = []
    for x in result:
        datos = {
            'id': x[0],
            'nom': x[1],
            'slug': x[2]
        }
        data.append(datos)
    cursor.close()
    return data

# FUNCIÓN LEER INFORMACIÓN PRODUCTO
def read_product(id):
    mydb = get_db()
    data=[]
    mycursor = mydb.cursor()
    sql = ("SELECT * FROM products where id = ?")
    val=(id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    for x in result:
        data = {
        'id': x[0],
        'nom': x[1],
        'descripcio': x[2],
        'imatge': x[3],
        'preu': x[4],
        'idcat': x[5],
        'vendedor': x[6],
        'creado': x[7],
        'actualizado': x[8],
        }
    mycursor.close()
    return data

# FUNCIÓN PARA MOSTRAR NOMBRE CATEGORIA A PARTIR DE ID
def mostrar_nomcat(idcat):
    listacat = mostrar_cat()
    for categoria in listacat:
        if categoria['id'] == idcat:
            return categoria['nom']

# FUNCIÓN PARA VALIDAR CADENA DE ENTRADA 
errores = []
def validar_cadena(campo, valor):
    if len(valor) < 1:
        flash(f"{campo} no pot estar buit.")
        errores.append("1")
    elif len(valor) > 255:
        flash(f"{campo} no pot superar els 255 caràcters.")
        errores.append("2")
    elif campo == 'Categoria':
        categorias = mostrar_cat()
        idcategorias = [i['id'] for i in categorias]
        if int(valor) not in idcategorias:
            flash(f"{campo} no s'ha seleccionat un valor correcte")
            errores.append("error")
        

@app.route('/products/create', methods=["GET", "POST"])
def product_create():
    if request.method == 'GET':
        # guardamos la lista de categorias en data
        data = mostrar_cat()
        # Enviamos a página create
        return render_template('products/create.html',datos = data)
    elif request.method == 'POST':
        data =  request.form
        mydb = get_db()
        nom = data.get('nom')
        desc = data.get('desc')
        img = data.get('img')
        preu = data.get('preu')
        cat = data.get('cat')
        seller = '1' #Seller Temporal
        dia = datetime.datetime.now()
        data_actual = dia.strftime("%Y-%m-%d %H:%M:%S")
        
        validar_cadena("Nom", nom)
        validar_cadena("Descripcio", desc)
        validar_cadena("Preu", preu)
        validar_cadena("Categoria", cat)

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))

        if errores:
            errores.clear()
            return redirect(request.url)
        else:
            lista = [nom, desc, img, preu, cat, seller, data_actual, data_actual]
            query = "INSERT INTO PRODUCTS (title, description, photo, price, category_id, seller_id, created, updated) \
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cursor = get_db().execute(query, lista) 
            mydb.commit()
            return redirect(url_for('list_products'))

@app.route('/products/update/<int:id>', methods=["GET", "POST"])
def products_update(id):
    if request.method == 'GET':
        cat = mostrar_cat()
        data = read_product(id)
        nomcat = mostrar_nomcat(data['idcat'])
        return render_template('products/update.html', resource=data, categorias=cat, nom_categorias=nomcat)
    elif request.method == 'POST':
        data = request.form
        nom = data.get('nom')
        desc = data.get('desc')
        img = data.get('img')
        preu = data.get('preu')
        cat = data.get('cat')
        dia = datetime.datetime.now()
        data_actual = dia.strftime("%Y-%m-%d %H:%M:%S")
        
        validar_cadena("Nom", nom)
        validar_cadena("Descripcio", desc)
        validar_cadena("Preu", preu)
        validar_cadena("Categoria", cat)

        if errores:
            errores.clear()
            return redirect(request.url)
        else:
            mydb = get_db()
            query = ("UPDATE PRODUCTS SET title = ?, description = ?, photo = ?, price = ?, category_id = ?, updated = ? where id = ?")
            mydb.execute(query, (nom, desc, img, preu, cat, data_actual, id))
            mydb.commit()
            return redirect(url_for('list_products'))


@app.route('/products/read/<int:id>')
def products_read(id):
    data = read_product(id)
    nomcat = mostrar_nomcat(data['idcat'])
    return render_template('products/read.html',resource=data,nombre_categoria=nomcat)

@app.route('/products/delete/<int:id>')
def products_delete(id):
    mydb = get_db()
    query = ("DELETE FROM PRODUCTS where id = ?")
    val=(id,)
    mydb.execute(query, val)
    mydb.commit()
    return redirect(url_for('list_products'))