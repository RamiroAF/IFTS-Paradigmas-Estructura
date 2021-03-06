#!/usr/bin/env python
import csv
import sys
import pandas
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_script import Manager

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

#Formularios para las consultas al archivo CSV.

class Consulta_Cliente(FlaskForm):
    criterio = StringField('Por cual cliente desea filtrar? ', validators=[DataRequired()])

class Consulta_Producto(FlaskForm):
    criterio = StringField('Por cual producto desea filtrar? ', validators=[DataRequired()])

class Consulta_Cantidad(FlaskForm):
    criterio = IntegerField('Por que cantidad de productos desea filtrar? ', validators=[DataRequired()])

class Consulta_Precio(FlaskForm):
    criterio = IntegerField('Por que precio de productos desea filtrar? ', validators=[DataRequired()])

#Formulario para cambio de contraseña.

class Cambio_Password(FlaskForm):
    actual = StringField('Ingrese contraseña actual: ', validators=[DataRequired()])
    nueva = StringField('Ingrese nueva contraseña: ', validators=[DataRequired()])

#Formulario para logueo del usuario.

class Formulario_Logueo(FlaskForm):
    name = StringField('Ingrese Usuario', validators=[DataRequired()])
    password = StringField('Ingrese contraseña', validators=[DataRequired()])

#Formulario para registro de un nuevo usuario.

class Formulario_Registro(FlaskForm):
    name = StringField('Ingrese Usuario', validators=[DataRequired()])
    password1 = StringField('Ingrese Contraseña', validators=[DataRequired()])
    password2 = StringField('Ingrese Contraseña nuevamente', validators=[DataRequired()])

app.config['SECRET_KEY'] = 'un string que funcione como llave'

#Se trata de abrir los archivos CSV, en caso de que no se encuentrar mostrará un mensaje en la consola.

try:
    with open('usuarios') as archivo:
        pass
except FileNotFoundError:
    print('No se encuentra el archivo CSV de Usuarios')


try:
    with open('busqueda') as archivo:
        pass
except FileNotFoundError:
    print('No se encuentra el archivo CSV para las busquedas')

try:
    with open('ventas') as archivo:
        pass
except FileNotFoundError:
    print('No se encuentra el archivo CSV de Ventas')

@app.route('/')
def index():
#Lee la sesion para ver si el usuario esta logueado, en caso de que no le este le mostrara un mensaje pidiendo loguearse.
    if 'username' in session:
        return render_template('index.html', fecha_actual=datetime.utcnow(), username=session.get('username'))
    return redirect('/login')

@app.route('/desloguearse', methods=['GET', 'POST'])
#Se hace un "pop" al diccionario que contiene el usuario, asi cerrando la sesion
def desloguearse():
    session.pop('username', None)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_logueo = Formulario_Logueo()
#Se abre el archivo que contiene los usuarios y contraseñas, y si las credenciales que ingresa el usuario son encontradas en el archivo, lo loguea.
    if form_logueo.validate_on_submit():
        try:
            with open("usuarios") as archivo:
                f = csv.reader(archivo)
                for linea in f:
                    p = linea
                    a = p[0]
                    b = p[1]
                    if form_logueo.name.data == a and form_logueo.password.data == b:
                        session['username'] = form_logueo.name.data
                        session['password'] = form_logueo.password.data
                        return redirect('/ventas')
        except FileNotFoundError:
            return 'No se encuentra el archivo de Usuarios'
    return render_template('login.html', form=form_logueo, username=session.get('username'))

#abre el archivo csv con la información a mostrar en la tabla, los headers los guarda en una variable, y el resto de la lista en la otra, luego se envía las variables a la plantilla html para que de formato y muestre la tabla.

@app.route('/ventas', methods=['GET'])
def ventas():
    if 'username' in session:
        try:
            with open('ventas', 'r') as archivo:
                lista_ventas = csv.reader(archivo)
                primera_linea = next(lista_ventas)
                return render_template('ventas.html', cabeza=primera_linea, cuerpo=lista_ventas, username=session.get('username'))
        except FileNotFoundError:
            return 'No se encuentra el archivo CSV'
    return redirect('/login')

#Busquedas en la tabla (para hacer las busquedas, utilizé el dataFrame de Pandas, que primero lee el archivo y lo guarda en una variable, luego, como argumento le hardcodeo el header de la columna en la cual quiero hacer la busqueda, y paso como dato lo que el usuario haya ingresado para buscar, si lo que se buscó se encuentra en el dataframe, guardara en la variable df2 el resultado. Luego, utilizando el metodo "to_csv" del dataframe, guardo en un archivo el resultado, con formato csv, y hago exactamente lo mismo que en la url anterior, abro el archivo, guardo los headers en una variable, los resultados en otra, y los envio a la plantilla html.

@app.route('/busqueda/cliente', methods=['GET', 'POST'])
def busqueda_cliente():
    if 'username' in session:
        try:
            with open('busqueda', 'w') as archivo:
                archivo.truncate()
        except FileNotFoundError:
            return 'No se encuentra el archivo csv utilizado para las busquedas'
        form_nombre = Consulta_Cliente()
        try:
            df = pandas.read_csv('ventas')
        except FileNotFoundError:
            return 'No se encuentra el archivo CSV de Ventas'    
        if form_nombre.validate_on_submit():
            if len(form_nombre.criterio.data) <= 3:
                flash('Debe ingresar un criterio de busqueda con más de tres caracteres')
                return redirect('/busqueda/cliente')
            df2 = df[(df['CLIENTE'].str.contains(form_nombre.criterio.data))]
            df2.to_csv('busqueda', index=None)
            if df2.empty is True:
                flash('No se encontraron resultados')
                return redirect('/busqueda/cliente')
            else:
                with open('busqueda') as archivo:
                    lista_resultado = csv.reader(archivo)
                    cabeza = next(lista_resultado)
                    return render_template('resultado.html', form=form_nombre, cabeza=cabeza, cuerpo=lista_resultado, username=session.get('username'))
        return render_template('busqueda_cliente.html', form=form_nombre, df=df, username=session.get('username'))
    return redirect('/login')

@app.route('/busqueda/producto', methods=['GET', 'POST'])
def busqueda_producto():
    if 'username' in session:
        try:
            with open('busqueda', 'w') as archivo:
                archivo.truncate()
        except FileNotFoundError:
            return 'No se encuentra el archivo csv utilizado para las busquedas'
        form_producto = Consulta_Producto()
        df = pandas.read_csv('ventas')
        if form_producto.validate_on_submit():
            df2 = df[(df['PRODUCTO'].str.contains(form_producto.criterio.data))]
            df2.to_csv('busqueda', index=None)
            if df2.empty is True:
                flash('No se encontraron resultados')
                return redirect('/busqueda/producto')
            else:
                with open('busqueda') as archivo:
                    lista_resultado = csv.reader(archivo)
                    cabeza = next(lista_resultado)
                    return render_template('resultado.html', form=form_producto, cabeza=cabeza, cuerpo=lista_resultado, username=session.get('username'))
        return render_template('busqueda_producto.html', form=form_producto, df=df, username=session.get('username'))
    return redirect('/login')

@app.route('/busqueda/cantidad', methods=['GET', 'POST'])
def busqueda_cantidad():
    if 'username' in session:
        try:
            with open('busqueda', 'w') as archivo:
                archivo.truncate()
        except FileNotFoundError:
            return 'No se encuentra el archivo csv utilizado para las busquedas'
        form_telefono = Consulta_Cantidad()
        df = pandas.read_csv('ventas')
        if form_telefono.validate_on_submit():
            df2 = df[(df['CANTIDAD']==int(form_telefono.criterio.data))]
            df2.to_csv('busqueda', index=None)
            if df2.empty is True:
                flash('No se encontraron resultados')
                return redirect('/busqueda/cantidad')
            else:
                with open('busqueda') as archivo:
                    lista_resultado = csv.reader(archivo)
                    cabeza = next(lista_resultado)
                    return render_template('resultado.html', form=form_telefono, cabeza=cabeza, cuerpo=lista_resultado, username=session.get('username'))
        return render_template('busqueda_cantidad.html', form=form_telefono, df=df, username=session.get('username'))
    return redirect('/login')

@app.route('/busqueda/precio', methods=['GET', 'POST'])
def busqueda_precio():
    if 'username' in session:
        try:
            with open('busqueda', 'w') as archivo:
                archivo.truncate()
        except FileNotFoundError:
            return 'No se encuentra el archivo csv utilizado para las busquedas'
        form_telefono = Consulta_Precio()
        df = pandas.read_csv('ventas')
        if form_telefono.validate_on_submit():
            df2 = df[(df['PRECIO']==int(form_telefono.criterio.data))]
            df2.to_csv('busqueda', index=None)
            if df2.empty is True:
                flash('No se encontraron resultados')
                return redirect('/busqueda/precio')
            else:
                with open('busqueda') as archivo:
                    lista_resultado = csv.reader(archivo)
                    cabeza = next(lista_resultado)
                    return render_template('resultado.html', form=form_telefono, cabeza=cabeza, cuerpo=lista_resultado, username=session.get('username'))
        return render_template('busqueda_precio.html', form=form_telefono, df=df, username=session.get('username'))
    return redirect('/login')

#Utilizando la función "send_file" de Flask, el cliente podrá bajar el archivo "busqueda", el cual siempre tendrá los resultados de la última busqueda hecha. También, utilizando el módulo "time", se configura para que el archivo siempre tenga como nombre la fecha y horario actual.

@app.route('/exportar', methods=['GET', 'POST'])
def exportar():
    with open('busqueda', 'r+') as archivo:
        res = archivo.read()
        archivo.seek(0)
        archivo.write('Resultados de la busqueda: \n' + res)
        return send_file('busqueda', as_attachment=True, attachment_filename='Resultados_' + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + ".csv")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form_registro = Formulario_Registro()
    if form_registro.validate_on_submit():
        lista_usuarios = []
        try:
            with open('usuarios') as archivo:
                lector = csv.reader(archivo)
                for linea in lector:
                    lista_usuarios.append(linea)
        except FileNotFoundError:
            print('No se encuentra el archivo CSV de Usuarios')
        if form_registro.password1.data == form_registro.password2.data:
            try:
                with open('usuarios', 'r') as archivo:
                    lector = csv.reader(archivo)
                    for linea in lector:
                        if form_registro.name.data in linea:
                            return "Usuario existente"
                        else:
                            with open('usuarios', 'a') as archivo:
                                escritor = csv.writer(archivo)
                                escritor.writerow([form_registro.name.data, form_registro.password1.data])
                                return redirect('login')
            except FileNotFoundError:
                return 'No se encuentra el archivo CSV de Usuarios'
        return "Revise la contraseña"
    return render_template('register.html', form=form_registro, username=session.get('username'))

@app.route('/cambiar', methods=['GET', 'POST'])
def cambiar():
    if "username" in session:
        form_cambiar = Cambio_Password()
        passwordactual = session.get('password')
        if form_cambiar.validate_on_submit():
            if form_cambiar.actual.data != passwordactual:
                flash('La contraseña actual ingresada no es correcta')
                return redirect('/cambiar')
            else:
                df = pandas.read_csv('usuarios')
                df.loc[df["PASSWORD"]==passwordactual, "PASSWORD"] = form_cambiar.nueva.data
                df.to_csv('usuarios', index=None)
                flash('La contraseña ha sido modificada correctamente')
                return redirect('/cambiar')
        return render_template('cambiar.html', form=form_cambiar)
    return redirect('/login')


@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    manager.run()

