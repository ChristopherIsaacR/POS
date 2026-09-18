
from tkinter import *
import mysql.connector
import bcrypt
from tkinter import messagebox
from datetime import datetime, timedelta
import secrets


from main_app import *
#global crear_usuario, recuperar_contrasena



#----conexion a la base de datos------
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # Cambia esto por tu nombre de usuario de MySQL
        password="",  # Cambia esto por tu contraseña de MySQL
        database="inventario2024"
    )
#--------------------------------------
#---------Agregar datos a usuario nuevo en base de datos------------
import re
def crear_usuario():
    nombre = cuadroNombre.get()
    usuario = cuadroUsuario.get()
    contrasena = cuadroPassword.get()
    confirmar_contrasena = cuadroConfirmarPassword.get()

    # Textos de muestra
    texto_muestra_nombre = "Nombre"
    texto_muestra_usuario = "Usuario"
    texto_muestra_contrasena = "Contraseña"

    if (nombre and usuario and contrasena and confirmar_contrasena and
        nombre != texto_muestra_nombre and
        usuario != texto_muestra_usuario and
        contrasena != texto_muestra_contrasena and
        contrasena == confirmar_contrasena):

        # Validación de nombre de usuario y contraseña
        if len(usuario) < 5:
            messagebox.showerror('Error', 'El nombre de usuario debe tener al menos 5 caracteres')
            return
        if not re.match("^[a-zA-Z0-9_.-]+$", usuario):
            messagebox.showerror('Error', 'El nombre de usuario solo puede contener letras, números y ._-')
            return
        if len(contrasena) < 8:
            messagebox.showerror('Error', 'La contraseña debe tener al menos 8 caracteres')
            return

        hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("INSERT INTO password (nombre_usuario, username, password) VALUES (%s, %s, %s)",
                           (nombre, usuario, hashed))
            conexion.commit()
            print("Usuario creado exitosamente")
            messagebox.showinfo('Éxito', 'Usuario creado exitosamente')
            login_screen()
        except mysql.connector.Error as err:
            if err.errno == 1062:
                print("Error: Nombre de usuario duplicado")
                messagebox.showerror('Error', 'Nombre de usuario ya existe. Por favor, elige otro.')
            else:
                print(f"Error: {err}")
                messagebox.showerror('Error', f'Error en la base de datos: {err}')
        finally:
            cursor.close()
            conexion.close()
    else:
        print("Por favor, completa todos los campos correctamente")
        messagebox.showerror('Error', 'Por favor, completa todos los campos correctamente')


#-------Validacion de datos del login en la base de datos-------------

# Función verificar_usuario actualizada
def verificar_usuario():
    global session_token, usuario_actual
    usuario = cuadroUsuario.get()
    contrasena = cuadroPassword.get()

    if usuario and contrasena:
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT password, intentos_fallidos, fecha_bloqueo FROM password WHERE username = %s", (usuario,))
            result = cursor.fetchone()
            if result:
                hashed_password, intentos_fallidos, fecha_bloqueo = result
                if bcrypt.checkpw(contrasena.encode('utf-8'), hashed_password.encode('utf-8')):
                    print("Login exitoso")
                    session_token = generate_session_token()
                    usuario_actual = usuario  # Actualiza el usuario actual
                    hora_inicio_sesion = datetime.now()
                    hora_fin_sesion = datetime.now()

                    # Cerrar todas las sesiones abiertas
                    cursor.execute("UPDATE password SET session_id = NULL, hora_fin_sesion = %s WHERE session_id IS NOT NULL AND username != %s",
                                   (hora_fin_sesion, usuario))
                    conexion.commit()

                    # Iniciar sesión para el usuario actual
                    cursor.execute("UPDATE password SET session_id = %s, hora_inicio_sesion = %s, hora_fin_sesion = NULL WHERE username = %s", 
                                   (session_token, hora_inicio_sesion, usuario))
                    conexion.commit()
                    messagebox.showinfo('Éxito', 'Has iniciado sesión correctamente')
                    verificar_sesion_activa()
                    # Abrir la ventana principal o continuar con la sesión activa
                else:
                    if intentos_fallidos is None:
                        intentos_fallidos = 0
                    intentos_fallidos += 1
                    cursor.execute("UPDATE password SET intentos_fallidos = %s WHERE username = %s", (intentos_fallidos, usuario))
                    conexion.commit()
                    if intentos_fallidos >= 3:
                        cursor.execute("UPDATE password SET fecha_bloqueo = NOW() WHERE username = %s", (usuario,))
                        conexion.commit()
                        messagebox.showerror('Error', 'Tu cuenta ha sido bloqueada debido a varios intentos fallidos')
                        desbloquear_cuenta(usuario)
                        return
                    else:
                        messagebox.showerror('Login failed', 'Usuario o contraseña incorrectos')
            else:
                messagebox.showerror('Login failed', 'Usuario no encontrado')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conexion.close()
    else:
        messagebox.askretrycancel("Campo vacio", "Por favor, completa todos los campos")



def generate_session_token():
    return secrets.token_hex(16)  # Genera un token hexadecimal de 16 bytes

def verificar_sesion_activa():
    global session_token, usuario_actual, session_label
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT username FROM password WHERE session_id = %s", (session_token,))
    result = cursor.fetchone()
    if result:
        usuario_actual = result[0]
        print(f"Sesión activa para {usuario_actual}")
        if session_label:
            session_label.destroy()
        session_label = Label(menu,text=usuario_actual + " en Sesión", bg=B, fg="#3289c8", font=("Comic Sans MS", 12),borderwidth=0, relief="ridge").pack(side=BOTTOM)
        #session_label.place(relx=.85,rely=.92 )
        abrir_Home()
        # Lógica para mostrar la ventana principal o continuar con la sesión activa
        return True
    else:
        print("No hay sesión activa")
        return False


def cerrar_sesion():
    global session_token, usuario_actual, session_label
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE password SET session_id = NULL, hora_fin_sesion = %s WHERE username = %s", 
                   (datetime.now(), usuario_actual))
    conexion.commit()
    cursor.close()
    conexion.close()
    session_token = None
    usuario_actual = None
    if session_label:
        session_label.config(text="")
    messagebox.showinfo('Éxito', 'Has cerrado sesión correctamente')
    #login_screen()




#----------------------------------------------------

#------------Desbloqueo de cuenta en 1 horas----------------
def desbloquear_cuenta(usuario):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT fecha_bloqueo FROM password WHERE username = %s", (usuario,))
        result = cursor.fetchone()
        if result:
            fecha_bloqueo = result[0]
            if fecha_bloqueo + timedelta(hours=1) < datetime.now():  # Desbloquear después de 1 hora
                cursor.execute("UPDATE password SET intentos_fallidos = 0, fecha_bloqueo = NULL WHERE username = %s", (usuario,))
                messagebox.showinfo('Éxito', 'La cuenta ha sido desbloqueada')
            else:
                messagebox.showerror('Error', 'La cuenta aún está bloqueada espera 1 hora')
        else:
            messagebox.showerror('Error', 'La cuenta no existe')
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conexion.close()
#-------------------------------------------------------------------       
#----------------------Funcion para recuperar contraseña-----------------------------
def recuperar_contrasena():
    usuario = cuadroUsuario.get()
    nueva_contrasena = cuadroPassword.get()
    confirmar_contrasena = cuadroConfirmarPassword.get()
    
    if not usuario:
        messagebox.showerror("Error", "Por favor, ingresa el nombre de usuario o nombre")
        return
    
    if len(nueva_contrasena) < 8:
            messagebox.showerror('Error', 'La contraseña debe tener al menos 8 caracteres')
            return
    if not nueva_contrasena or not confirmar_contrasena:
        messagebox.showerror("Error", "Por favor, ingresa y confirma la nueva contraseña")
        return
    
    if nueva_contrasena != confirmar_contrasena:
        messagebox.showerror("Error", "Las contraseñas no coinciden")
        return

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT username FROM password WHERE username = %s OR nombre_usuario = %s", (usuario, usuario))
        result = cursor.fetchone()
        if result:
            nombre_usuario = result[0]
            hashed_password = bcrypt.hashpw(nueva_contrasena.encode('utf-8'), bcrypt.gensalt())

            cursor.execute("UPDATE password SET password = %s WHERE username = %s", (hashed_password, nombre_usuario))
            conexion.commit()

            messagebox.showinfo("Contraseña recuperada", "Tu contraseña ha sido actualizada correctamente")
            login_screen()
        else:
            messagebox.showerror("Error", "Usuario no encontrado")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conexion.close()
      
#------------------------------------------------------------------------------------------------------------------
