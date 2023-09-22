from flask import Flask,render_template,url_for,request,redirect
import sqlite3
import datetime

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        db = Flask._database = sqlite3.connect(DATABASE,check_same_thread=False)
    return db

def close_connection(exception):
    db = getattr(Flask, '_database', None)
    if db is not None:
        db.close()


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
        lista = [nom, desc, img, preu, cat, seller, data_actual, data_actual]
        query = "INSERT INTO PRODUCTS (title, description, photo, price, category_id, seller_id, created, updated) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor = get_db().execute(query, lista) 
        mydb.commit()
        return redirect(url_for('list_products'))

@app.route('/products/update/<int:id>', methods=["GET", "POST"])
def products_update(id):
    if request.method == 'GET':
        data = read_product(id)
        app.logger.info(data)
        return render_template('products/update.html',resource=data)
    elif request.method == 'POST':
        data =  request.form
        mydb = get_db()
        nom=data.get('nom')
        cognom1=data.get('cognom1')
        cognom2=data.get('cognom2')
        dept=data.get('dept')
        mycursor = mydb.cursor()
        sql = ("UPDATE empleat SET nom = %s, cognom1 = %s, cognom2 = %s, departament = %s where id = %s")
        mycursor.execute(sql, (nom, cognom1, cognom2, dept, id))
        mydb.commit()
        mycursor.close()