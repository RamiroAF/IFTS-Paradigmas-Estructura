#!/usr/bin/env python
import csv
import sys
import pandas
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
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

#Se trata de abrir los archivos CSV, en caso de que no se encuentrar mostrará un mensaje en la consola. También, se guarda en una lista los usuarios existentes, para que sea más fácil consultar si cuando alguien registre un usuario nuevo, el nombre ya está utilizado o no.
lista_usuarios = []
try:
    with open('usuarios') as archivo:
        lector = csv.reader(archivo)
        for linea in lector:
            lista_usuarios.append(linea[0])
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
        return render_template('index.html', fecha_actual=datetime.utcnow())
    return render_template('deslogueado.html')

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
                        return redirect('/ventas')
        except FileNotFoundError:
            return 'No se encuentra el archivo de Usuarios'
    return render_template('login.html', form=form_logueo, username=session.get('username'))

#abre el archivo csv con la información a mostrar en la tabla, los headers los guarda en una variable, y el resto de la lista en la otra, luego se envía las variables a la plantilla html para que de formato y muestre la tabla.

@app.route('/ventas', methods=['GET', 'POST'])
def contactos():
    if 'username' in session:
        try:
            with open('ventas', 'r') as archivo:
                lista_ventas = csv.reader(archivo)
                primera_linea = next(lista_ventas)
                return render_template('ventas.html', cabeza=primera_linea, cuerpo=lista_ventas)
        except FileNotFoundError:
            return 'No se encuentra el archivo CSV'
    return render_template('deslogueado.html')

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
            df2 = df[(df['CLIENTE']==form_nombre.criterio.data)]
            df2 = df2.to_csv('busqueda', index=None)
            with open('busqueda') as archivo:
                lista_resultado = csv.reader(archivo)
                cabeza = next(lista_resultado)
                return render_template('resultado.html', form=form_nombre, cabeza=cabeza, cuerpo=lista_resultado)
        return render_template('busqueda_cliente.html', form=form_nombre, df=df)
    return render_template('deslogueado.html')

@app.route('/busqueda/producto', methods=['GET', 'POST'])
def busqueda_producto():
    if 'username' in session:
        try:
            with open('busqueda', 'w') as archivo:
                archivo.truncate()
        except FileNotFoundError:
            return 'No se encuentra el archivo csv utilizado para las busquedas'
        form_apellido = Consulta_Producto()
        df = pandas.read_csv('ventas')
        if form_apellido.validate_on_submit():
            df2 = df[(df['PRODUCTO']==form_apellido.criterio.data)]
            df2 = df2.to_csv('busqueda', index=None)
            with open('busqueda') as archivo:
                lista_resultado = csv.reader(archivo)
                cabeza = next(lista_resultado)
                return render_template('resultado.html', form=form_apellido, cabeza=cabeza, cuerpo=lista_resultado)
        return render_template('busqueda_producto.html', form=form_apellido, df=df)
    return render_template('deslogueado.html')

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
            df2 = df2.to_csv('busqueda', index=None)
            with open('busqueda') as archivo:
                lista_resultado = csv.reader(archivo)
                cabeza = next(lista_resultado)
                return render_template('resultado.html', form=form_telefono, cabeza=cabeza, cuerpo=lista_resultado)
        return render_template('busqueda_cantidad.html', form=form_telefono, df=df)
    return render_template('deslogueado.html')

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
            df2 = df2.to_csv('busqueda', index=None)
            with open('busqueda') as archivo:
                lista_resultado = csv.reader(archivo)
                cabeza = next(lista_resultado)
                return render_template('resultado.html', form=form_telefono, cabeza=cabeza, cuerpo=lista_resultado)
        return render_template('busqueda_precio.html', form=form_telefono, df=df)
    return render_template('deslogueado.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form_registro = Formulario_Registro()
    if form_registro.validate_on_submit():
        if form_registro.password1.data == form_registro.password2.data:
            try:
                with open('usuarios', 'a') as archivo:
                    escritor = csv.writer(archivo)
                    if form_registro.name.data in lista_usuarios:
                        return "Usuario existente"
                    else:
                        escritor.writerow([form_registro.name.data, form_registro.password1.data])
                        return redirect('login')
            except FileNotFoundError:
                return 'No se encuentra el archivo CSV de Usuarios'
        return "Revise la contraseña"
    return render_template('register.html', form=form_registro)

@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    manager.run()
