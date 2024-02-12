from flask import Flask
from flask import render_template,redirect,request,url_for, session
from flask_mysqldb import MySQL
#libreria que se utiliza para el manejo de tiempo
from datetime import datetime
#libreria que se utiliza para obtener información de imagenes
from flask import send_from_directory
import os


app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "sitio"
app.secret_key = "mysecretkey"
mysql = MySQL(app)
#
### seccion del sitio
#
@app.route('/')
def index():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagener(imagen):

    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route('/css/<archivocss>')
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)

@app.route('/libros')
def libros():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM libros;")
    libros = cursor.fetchall()
    mysql.connection.commit()

    return render_template('sitio/libros.html', libros=libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')
#
### seccion administrador 
#
@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect("/admin/login")
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login',methods=['POST'])
def admin_login_sesion():
    _usuario = request.form['txtUsuario']
    _password = request.form['txtPassword']

    if _usuario == "admin" and _password == "12345":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template('admin/login.html',mensaje = "Acceso denegado")

@app.route('/admin/cerrar')
def admin_cerrar_sesion():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/libros')
def admin_libros():
    if not 'login' in session:
        return redirect("/admin/login")
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM libros;")
    libros = cursor.fetchall()
    mysql.connection.commit()

    return render_template('admin/libros.html', libros = libros)

@app.route('/admin/libros/guardar',methods=['POST'])
def admin_libros_guardar():
    if not 'login' in session:
        return redirect("/admin/login")
    
    _nombre = request.form['txtNombre']
    _url = request.form['txtUrl']
    _archivo = request.files['txtImagen']
    
    tiempo = datetime.now()
    horaActual = tiempo.strftime("%Y%H%M%S")

    if _archivo.filename != '':
        nuevoNombre = horaActual +"_"+ _archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)

    sql = "INSERT INTO libros (nombre, imagen, url) VALUES (%s, %s, %s);"
    datos = (_nombre,nuevoNombre,_url)
   
    cursor = mysql.connection.cursor()
    cursor.execute(sql,datos)
    mysql.connection.commit()
    
    return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():
    if not 'login' in session:
        return redirect("/admin/login")
    
    _id = request.form['txtId']

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT imagen FROM libros WHERE id=%s;',(_id))
    libro=cursor.fetchall()

    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):
        os.unlink("templates/sitio/img/"+str(libro[0][0]))

    cursor.execute("DELETE FROM libros WHERE id=%s;",(_id))
    mysql.connection.commit()

    return redirect('/admin/libros')


if __name__ == '__main__':
    app.run(debug=True)