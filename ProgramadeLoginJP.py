import mysql.connector
from pymongo import MongoClient
import bcrypt
import getpass  # Para ocultar la contraseña en la terminal
from dotenv import load_dotenv
import os
import re
import time 
import random #Para la recuperación de la contraseña
import datetime

load_dotenv()

# Conexión a MySQL
def conectar_mysql():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )
# Conexión a MongoDB
def conectar_mongo():
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    return client["auth_system"]["usuarios"]


def validar_email(email):
    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'  
    if re.match(patron, email):
        return True
    else:
        print("El email no es válido. Asegúrate de ingresar un formato correcto.")
        return False
    
def validar_contraseña(password):
    if len(password) < 8:
        print("La contraseña debe tener al menos 8 caracteres.")
        return False
    if not any(char.isdigit() for char in password):
        print("La contraseña debe contener al menos un número.")
        return False
    if not any(char.islower() for char in password):
        print("La contraseña debe contener al menos una letra minúscula.")
        return False
    if not any(char.isupper() for char in password):
        print("La contraseña debe contener al menos una letra mayúscula.")
        return False
    if not any(char in '!@#$%^&*()_+' for char in password):
        print("La contraseña debe contener al menos un carácter especial.")
        return False
    return True

# Registrar nuevo usuario
def registrar_usuario():
    username = input("Ingrese su nombre de usuario: ")

    while True:
        email = input("Ingrese su email: ")
        if validar_email(email):
            break   
    while True:
        password = getpass.getpass("Ingrese su contraseña: ")
        if validar_contraseña(password):
            break  

    # Hash de la contraseña con bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    mysql_db = conectar_mysql()
    mongo_db = conectar_mongo()
    cur = mysql_db.cursor()
    try:
        cur.execute("INSERT INTO usuarios (username, email, password_hash) VALUES (%s,%s,%s)", (username, email, hashed))
        mysql_db.commit()
        print("Usuario registrado en MySQL.")
    except mysql.connector.Error as e:
        print("Error MySQL:", e)
    
    try:
        mongo_db.insert_one({"username": username, "email": email, "password_hash": hashed, "activo": True})
        print("Usuario registrado en MongoDB.")
    except Exception as e:
        print("Error MongoDB:", e)

    cur.close()
    mysql_db.close()

usuario_logueado = None
def login_usuario():
    global usuario_logueado  #Se usa la variable global

    if usuario_logueado is not None:
        print("Ya hay un usuario logueado.")
        return  

    while True:
        email = input("Ingrese su email: ")
        if validar_email(email):
            break  

    while True:
        password = getpass.getpass("Ingrese su contraseña: ")
        if password:  
            break
        print("La contraseña no puede estar vacía.")

    # Conectar a MySQL y MongoDB
    mysql_db = conectar_mysql()
    mongo_db = conectar_mongo()

    cursor = mysql_db.cursor()
    cursor.execute("SELECT email, password_hash FROM usuarios WHERE email = %s", (email,))
    user_mysql = cursor.fetchone()

    user_mongo = mongo_db.find_one({"email": email})
    login_exitoso = False

    if user_mysql:
        if bcrypt.checkpw(password.encode('utf-8'), user_mysql[1].encode('utf-8')):
            print("\nLogin exitoso en MySQL!")
            print(f"Bienvenido {user_mysql[0]}")
            usuario_logueado = user_mysql[0]  # Guardamos el email del usuario logueado
            login_exitoso = True
            registrar_log_login(email, "exitoso")  # Logs de Registro
        else:
            print("Contraseña incorrecta en MySQL.")
            registrar_log_login(email, "fallido")  # Log de Registro login fallido

    if user_mongo:
        if bcrypt.checkpw(password.encode('utf-8'), user_mongo["password_hash"]):
            print("Login exitoso en MongoDB!")
            print(f"Bienvenido {user_mongo['email']}")
            usuario_logueado = user_mongo['email']  
            login_exitoso = True
            registrar_log_login(email, "exitoso")  # Registrar log de login exitoso
        else:
            print("Contraseña incorrecta en MongoDB.")
            registrar_log_login(email, "fallido")  # Registrar log de login fallido
    
    if not login_exitoso:
        print("Usuario no encontrado o contraseña incorrecta. Intente nuevamente.")
        registrar_log_login(email, "fallido")  # Registrar log de login fallido
    
    cursor.close()
    mysql_db.close()


def ver_usuario():
    # Verificar si hay un usuario logueado
    if usuario_logueado is None:
        print("No hay ningún usuario logueado.")
        return  

    # Conectar a MySQL y MongoDB
    mysql_db = conectar_mysql()
    mongo_db = conectar_mongo()

    cursor = mysql_db.cursor()
    cursor.execute("SELECT username, email FROM usuarios WHERE email = %s", (usuario_logueado,))
    user_mysql = cursor.fetchone()

    user_mongo = mongo_db.find_one({"email": usuario_logueado})

    if user_mysql:
        print(f"Usuario logueado : {user_mysql[0]} | Email: {user_mysql[1]}")
    else:
        print("Usuario no encontrado en ninguna base de datos.")
    
    cursor.close()
    mysql_db.close()



def cerrar_sesion():
    global usuario_logueado
    if usuario_logueado is None:
        print("No hay ningún usuario logueado.")
    else:
        print(f"Usuario {usuario_logueado} ha cerrado sesión.")
        time.sleep(1)
        usuario_logueado = None  

def recuperar_contraseña():
    if usuario_logueado is None:
        print("No hay ningún usuario logueado.")
        return  

    while True:
        email = input("Ingrese el email a recuperar contraseña: ")
        if validar_email(email):
            break  

    if email != usuario_logueado:
        print("El email no coincide con el usuario logueado.")
        return  

    #Aquí pensé que al ser algo simulado, seería bacán que "mande" un codigo de recuperación
    codigo_recuperacion = str(random.randint(100000, 999999))  # Código de 6 dígitos
    print(f"\nSe ha generado un código de recuperación: {codigo_recuperacion}")  

    codigo_ingresado = input("Ingrese el código de recuperación que ha recibido: ")

    if codigo_ingresado == codigo_recuperacion:
        print("\nCódigo de recuperación correcto.")
        nueva_contraseña = getpass.getpass("Ingrese su nueva contraseña: ")
        if validar_contraseña(nueva_contraseña):  
            hashed = bcrypt.hashpw(nueva_contraseña.encode('utf-8'), bcrypt.gensalt())

            # Conectar a MySQL y MongoDB
            mysql_db = conectar_mysql()
            mongo_db = conectar_mongo()

            cursor = mysql_db.cursor()
            try:
                cursor.execute("UPDATE usuarios SET password_hash = %s WHERE email = %s", (hashed, email))
                mysql_db.commit()
                print("\nContraseña actualizada en MySQL.")
            except mysql.connector.Error as e:
                print("Error MySQL:", e)

            try:
                mongo_db.update_one({"email": email}, {"$set": {"password_hash": hashed}})
                print("Contraseña actualizada en MongoDB.")
            except Exception as e:
                print("Error MongoDB:", e)

            cursor.close()
            mysql_db.close()
        else:
            print("La nueva contraseña no cumple con los requisitos.")
    else:
        print("Código de recuperación incorrecto.")

def editar_perfil():
    global usuario_logueado  

    if usuario_logueado is None:
        print("No hay ningún usuario logueado.")
        return  

    # Conectar a MySQL y MongoDB
    mysql_db = conectar_mysql()
    mongo_db = conectar_mongo()

    cursor = mysql_db.cursor()
    cursor.execute("SELECT email, username FROM usuarios WHERE email = %s", (usuario_logueado,))
    user_mysql = cursor.fetchone()

    user_mongo = mongo_db.find_one({"email": usuario_logueado})

    if not user_mysql and not user_mongo:
        print("No se encontró el usuario en ninguna base de datos.")
        return  

    print("\nEditando perfil de usuario:")
    nuevo_username = input(f"Nuevo nombre de usuario (actual: {user_mysql[1]}): ") or user_mysql[1]
    nuevo_email = input(f"Nuevo email (actual: {user_mysql[0]}): ") or user_mysql[0]

    while True:
        if validar_email(nuevo_email):
            cursor.execute("SELECT email FROM usuarios WHERE email = %s", (nuevo_email,))
            if cursor.fetchone():
                print("Este email ya está registrado. Elija otro.")
            else:
                break
        else:
            nuevo_email = input("Ingrese un email válido: ")

    try:
        cursor.execute("UPDATE usuarios SET username = %s, email = %s WHERE email = %s", 
                       (nuevo_username, nuevo_email, usuario_logueado))
        mysql_db.commit()
        print("Perfil actualizado en MySQL.")
    except mysql.connector.Error as e:
        print("Error MySQL:", e)

    try:
        mongo_db.update_one({"email": usuario_logueado}, 
                            {"$set": {"username": nuevo_username, "email": nuevo_email}})
        print("Perfil actualizado en MongoDB.")
    except Exception as e:
        print("Error MongoDB:", e)

    # Actualizamos la variable global usuario_logueado en caso de que se haya modificado el email
    usuario_logueado = nuevo_email

    cursor.close()
    mysql_db.close()


def registrar_log_login(email, login_status):
    mongo_db = conectar_mongo()

    # Crear un documento para el log
    log = {
        "email": email,
        "login_status": login_status,
        "timestamp": datetime.datetime.now(),  # Fecha y hora actual
    }

    try:
        mongo_db["logs"].insert_one(log)  # Insertamos en la colección 'logs'
        print("Log de login registrado con éxito.")
    except Exception as e:
        print(f"Error al registrar log de login: {e}")

def main():
    while True:
        print("\n1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Ver información del usuario")
        print("4. Recuperar la Contraseña")
        print("5. Editar Perfil")
        print("6. Cerrar Sesión")
        print("7. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            login_usuario()
        elif opcion == "3":
            ver_usuario()
        elif opcion == "4":
            recuperar_contraseña()
        elif opcion == "5":
            editar_perfil()
        elif opcion == "6":
            cerrar_sesion()
        elif opcion == "7":
            print("Saliendo del programa...")
            time.sleep(2)
            break
        else:
            print("Opción no válida.")