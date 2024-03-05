#Proyecto Taller Desarrollo de Software Avanzado Grupo #1.
import os
from flask import Flask
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_mysqldb import MySQL


app=Flask(__name__)
app.static_folder = 'static'
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST') or '127.0.0.1' # localhost
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER') or 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD') or ''
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB') or 'usuarios_asociacion'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


app.secret_key = 'mysecretkey'

@app.route('/secretaria', methods=['GET', 'POST'])
def obtener_atletas():
    if request.method == 'POST':
        id_atleta = request.form['id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM atletas WHERE id_atleta = %s", (id_atleta,))
        atleta = cursor.fetchone()
        cursor.close()

        if atleta:
            return render_template('secretaria.html', atleta=atleta)
        else:
            return render_template('secretaria.html', mensaje="No se encontró el atleta con el ID: " + id_atleta)

    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM atletas")
        atletas = cursor.fetchall() 
        cursor.close()
        return render_template('secretaria.html', atletas=atletas)
    


@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/iniciar_sesion')
def iniciar_sesion():
    return render_template('iniciar_sesion.html')

@app.route('/registrar')
def regis():
    return render_template('Registrar.html')

@app.route('/representantes')
def representantes():
    return render_template('representantes.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/registrar_pago')
def registrar_pago():
    return render_template('Registro_Pago.html')

@app.route('/nosotros')
def nosotros():
    return render_template('Nosotros.html')

@app.route('/inscripcion', methods=['GET','POST'])
def inscripcion():
    if request.method == 'POST':
        # Obtener datos del atleta
        fullname = request.form.get('fullname')
        lastname = request.form.get('lastname')
        direccion = request.form.get('direccion')
        date = request.form.get('date-nac')
        genero = request.form.get('genero')

        #representante
        fullnameR = request.form.get('fullnameR')
        lastnameR = request.form.get('lastnameR')
        number = request.form.get('number')
        cedula_representante = request.form.get('id')
        email = request.form.get('email')

        # Almacenar datos en variables temporales
        session['fullname'] = fullname
        session['lastname'] = lastname
        session['direccion'] = direccion
        session['date'] = date
        session['genero'] = genero
        session['fullnameR'] = fullnameR
        session['lastnameR'] = lastnameR
        session['number'] = number
        session['cedula_representante'] = cedula_representante
        session['email'] = email

        cur = mysql.connection.cursor()
        cur.execute("SELECT id_atleta FROM atletas ORDER BY id_atleta DESC LIMIT 1")
        ultimo_id = cur.fetchone()
        
        id_atleta = ultimo_id.get('id_atleta')
        nuevo_id = id_atleta + 1
        session['numero'] = nuevo_id
        print(session['numero'])

        # Redirigir al segundo formulario con los datos como parámetros
        return render_template('pago_inscripcion.html')

    return render_template('inscripcion.html')

@app.route('/pago_inscripcion', methods=['GET','POST'])
def pago():
    if request.method == 'POST':
        # Obtener datos de pago
        banco = request.form.get('Bancos')
        fecha = request.form.get('fecha')
        refe = request.form.get('refe')

        # Obtener datos del atleta y representante de las variables temporales
        fullname = session['fullname']
        lastname = session['lastname']
        direccion = session['direccion']
        date = session['date']
        genero = session['genero']

        #representate
        fullnameR = session['fullnameR']
        lastnameR = session['lastnameR']
        number = session['number']
        #cedula_representante = session['id']
        cedula_representante = session['cedula_representante']
        email = session['email']
        # Combinar datos y crear entrada en la base de datos
        cur = mysql.connection.cursor()
        

        # Buscar representante por cédula
        cur.execute("SELECT * FROM representantes WHERE cedula_representante = %s", (cedula_representante,))
        representante_encontrado = cur.fetchone()

        #busca el ultimo id
        cur.execute("SELECT id_atleta FROM atletas ORDER BY id_atleta DESC LIMIT 1")
        ultimo_id = cur.fetchone()
        
        id_atleta = ultimo_id.get('id_atleta')
        nuevo_id = id_atleta + 1


        # Si el representante no existe, crearlo
        if not representante_encontrado:
            cur.execute("INSERT INTO representantes (nombre, apellido, numero_telefono, cedula_representante, email) VALUES (%s, %s, %s, %s, %s)", (fullnameR, lastnameR, number, cedula_representante, email))

        # Insertar atleta con la cédula del representante
  
        cur.execute("INSERT INTO atletas (nombre, apellido, direccion, edad, genero, cedula_representante) VALUES (%s, %s, %s, %s, %s, %s)", (fullname, lastname, direccion, date, genero, cedula_representante))
        cur.execute("INSERT INTO pagos (referencia, id_atleta, cedula_representante, monto, fecha_pago, Banco, verificado) VALUES (%s, %s, %s, %s, %s, %s, %s)", (refe, nuevo_id, cedula_representante, 480, fecha, banco, 0))
        mysql.connection.commit()


        # Mostrar mensaje de éxito o redireccionar a otra página
        return render_template('representantes.html')

    return render_template('pago_inscripcion.html')



@app.route('/iniciar_sesion', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        fullname = request.form.get('fullname') 
        clave = request.form.get('clave')  
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM usuarios WHERE fullname = %s AND clave = %s"
        cursor.execute(query, (fullname, clave))
        user = cursor.fetchone()

        if user:
            return render_template('representantes.html')  
        else:
            flash('Usuario o contraseña incorrectos')
            return render_template('iniciar_sesion.html')

    return render_template('iniciar_sesion.html') 

@app.route('/registrarse', methods=['GET','POST'])
def registrar():
    if request.method == 'POST':
        fullname = request.form['fullname']
        clave = request.form['clave']
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO usuarios (fullname, clave) VALUES (%s, %s)", (fullname, clave))
        mysql.connection.commit()
        flash('Usuario agregado satisfactoriamente')
        return render_template('iniciar_sesion.html') 


if __name__ == '__main__':
    app.run(port = 5000, debug=True)