from flask import Flask,render_template,url_for

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template('hello.html')        