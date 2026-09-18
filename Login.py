from tkinter import *
from PIL import Image, ImageTk
import mysql.connector
import bcrypt
from tkinter import messagebox
from datetime import datetime, timedelta
import secrets
import subprocess

global session_token
global usuario_actual
session_token = None
usuario_actual = None
session_label = None  # Referencia global a la etiqueta de sesión





x = 1300
y = 650

B="White" 
L="Black"
BgButton="#3289c8"
BgButton_Selet="#08acef"

###PRUEBA NADA MAS SOBRE OTRO LOGIN####
def abrir_Home():
    menu.destroy()
    hora_arg = hora_inicio_sesion.isoformat() if 'hora_inicio_sesion' in globals() and hora_inicio_sesion else datetime.now().isoformat()
    subprocess.Popen(["python", "Inventario menu  prueba 1.13.py", usuario_actual or "Invitado", hora_arg])
#-----------------------

#------------------Frame menu default-----------------
menu = Tk()

menu.title("Gestion de inventarios")
menu.resizable(True, True)
menu.iconbitmap("Img/icon.ico")
menu.geometry(f"{x}x{y}-100-100")
menu.config(bg=B)

#-----------------------------------------------------
def cambio_de_tema():
    global B, L
    B="Black"
    L="White"
    if 'login_screen' in globals():
        login_frame.destroy()
    login_screen()
def cambio_de_tema_blanco():
    global B, L
    B="White"
    L="Black"
    if 'login_screen' in globals():
        login_frame.destroy()
    login_screen()

def crear_toggle_tema(parent, relx, rely):
    ancho, alto = 60, 30
    canvas_tema = Canvas(parent, width=ancho, height=alto, bg=B, highlightthickness=0)
    canvas_tema.place(relx=relx, rely=rely, anchor=CENTER)

    oscuro = (B == "Black")
    color_pista = "#4a4a4a" if oscuro else "#3289c8"
    color_circulo = "#f2c14e" if oscuro else "#ffffff"
    canvas_tema.create_oval(0, 0, alto, alto, fill=color_pista, outline="")
    canvas_tema.create_oval(ancho - alto, 0, ancho, alto, fill=color_pista, outline="")
    canvas_tema.create_rectangle(alto / 2, 0, ancho - alto / 2, alto, fill=color_pista, outline="")
    cx = ancho - alto / 2 if oscuro else alto / 2
    canvas_tema.create_oval(cx - alto / 2 + 3, 3, cx + alto / 2 - 3, alto - 3, fill=color_circulo, outline="")
    canvas_tema.create_text(cx, alto / 2, text=("🌙" if oscuro else "☀"), font=("Arial", 12))

    def alternar(event=None):
        if B == "White":
            cambio_de_tema()
        else:
            cambio_de_tema_blanco()

    canvas_tema.bind("<Button-1>", alternar)
    return canvas_tema



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
    global session_token, usuario_actual, hora_inicio_sesion
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
#------------------Mostrar sugerencias en los cuadros de texto de ingreso-----------------
class Nombre(Entry):
    def __init__(self, master, nombre, **kwargs):
        super().__init__(master, **kwargs)
        self.nombre = nombre
        self.insert(0, nombre)
        self.config(fg="gray")
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        
    def on_focus_in(self, event):
        if self.get() == self.nombre:
            self.delete(0, END)
            self.config(fg=L)

    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.nombre )
            self.config(fg="gray")

class Usuario(Entry):
    def __init__(self, master, usuario, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.insert(0, usuario)
        self.config(fg="gray")
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        if self.get() == self.usuario:
            self.delete(0, END)
            self.config(fg=L)

    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.usuario)
            self.config(fg="gray")

class Password(Entry):
    def __init__(self, master, password, **kwargs):
        super().__init__(master, **kwargs)
        self.password = password
        self.insert(0, password)
        self.config(fg="gray")
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.show_password = False

    def on_focus_in(self, event):
        if self.get() == self.password:
            self.delete(0, END)
            self.config(fg=L)
            self.config(show="°")

    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.password)
            self.config(fg="gray")
            self.config(show="")

    def show_hide_password(self):
        if self.show_password:
            self.config(show="°")
        else:
            self.config(show="")
        self.show_password = not self.show_password

class ConfirmarPassword(Entry):
    def __init__(self, master, password1, **kwargs):
        super().__init__(master, **kwargs)
        self.password1 = password1
        self.insert(0, "Confirmar contraseña")
        self.config(fg="gray")
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.show_password = False

    def on_focus_in(self, event):
        if self.get() == "Confirmar contraseña":
            self.delete(0, END)
            self.config(fg=L)
            self.config(show="°")

    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, "Confirmar contraseña")
            self.config(fg="gray")
            self.config(show="")

    def show_hide_password1(self):
        if self.show_password:
            self.config(show="°")
        else:
            self.config(show="")
        self.show_password = not self.show_password
    

#--------------------------------------------------------------------------
#----------------------Frame Login-----------------------------
def login_screen():
    global imagenUser, user, lock  
    global login_frame

    inicio.destroy()
    if 'registro_frame' in globals():
        registro_frame.destroy()
    if 'recuperacion_frame' in globals():
        recuperacion_frame.destroy()


    login_frame = Frame(menu, width=x, height=y, bg=B)
    login_frame.pack(fill=BOTH, expand=TRUE)
    login_frame.pack_propagate(FALSE)
    imagenUser = PhotoImage(file="Img/user.png")
    
    Img_user=Label(login_frame, image=imagenUser, bg=B).place(relx=0.5, y=150, anchor=CENTER)

    Useringreso = Frame(login_frame, bg=B)
    Useringreso.pack()
    crear_toggle_tema(login_frame, 0.70, 0.15)

    global cuadroUsuario
    cuadroUsuario = Usuario(Useringreso, "Usuario", bg=B)
    cuadroUsuario.grid(row=0, column=1)
    cuadroUsuario.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")

    user = PhotoImage(file="Img/user1.png")
    user=Label(login_frame, image=user, bg=B).grid(row=0, column=0, padx=10, pady=10)

    global cuadroPassword
    cuadroPassword = Password(Useringreso, "Contraseña",bg=B)
    cuadroPassword.grid(row=1, column=1)
    cuadroPassword.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")
    global imagen_mostrar
    # Botón para mostrar/ocultar contraseña
    imagen_mostrar = PhotoImage(file="Img/mostrar.png")
    botonMostrarContrasena = Button(Useringreso, image=imagen_mostrar, bg="White", font=("Arial", 10),  command=cuadroPassword.show_hide_password)
    botonMostrarContrasena.grid(row=1, column=2, padx=10)
    botonMostrarContrasena.bind("<Enter>", lambda event: botonMostrarContrasena.config(bg=BgButton))
    botonMostrarContrasena.bind("<Leave>", lambda event: botonMostrarContrasena.config(bg="White"))

    lock = PhotoImage(file="Img/lock.png")
    Label(Useringreso, image=lock, bg=B).grid(row=1, column=0, padx=10, pady=10)

    Useringreso.place(relx=0.5, y=370, anchor=CENTER)
    botonIngresar = Button(login_frame, text="Ingresar", fg=L, bg=BgButton, font=("Comic Sans MS", 12), relief=GROOVE, borderwidth=2, command=verificar_usuario)
    botonIngresar.place(relx=0.5, y=450, anchor=CENTER, width=100, height=20)
    botonIngresar.bind("<Enter>", lambda event: botonIngresar.config(bg=BgButton_Selet))
    botonIngresar.bind("<Leave>", lambda event: botonIngresar.config(bg=BgButton))

    botonCrearCuenta = Button(login_frame, text="Crear cuenta", fg=L, bg=B, font=("Comic Sans MS", 12), relief=GROOVE, borderwidth=0, command=registro_screen)
    botonCrearCuenta.place(relx=0.5, y=490, anchor=CENTER, width=100, height=20)
    botonCrearCuenta.bind("<Enter>", lambda event: botonCrearCuenta.config(bg=BgButton_Selet))
    botonCrearCuenta.bind("<Leave>", lambda event: botonCrearCuenta.config(bg=B))

    botonRecuperarContrasena = Button(login_frame, text="Recuperar contraseña", fg=L, bg=B, font=("Comic Sans MS", 12), relief=GROOVE, borderwidth=0, command=recuperacion_screen)
    botonRecuperarContrasena.place(relx=0.5, y=530, anchor=CENTER, width=180, height=20)
    botonRecuperarContrasena.bind("<Enter>", lambda event: botonRecuperarContrasena.config(bg=BgButton_Selet))
    botonRecuperarContrasena.bind("<Leave>", lambda event: botonRecuperarContrasena.config(bg=B))



#------------------------------------------------------------------

#----------------------cambio de frame a Registro-----------------------------
def registro_screen():
    global imagenUser1, user1, lock1 
    global registro_frame

    inicio.destroy()
    if 'login_frame' in globals():
        login_frame.destroy()
    if 'recuperacion_frame' in globals():
        recuperacion_frame.destroy()

    registro_frame = Frame(menu, width=x, height=y, bg=B)
    registro_frame.pack(fill=BOTH, expand=TRUE)
    registro_frame.pack_propagate(FALSE)
    imagenUser1 = PhotoImage(file="Img/user.png")
    Label(registro_frame, image=imagenUser1, bg=B).place(relx=0.5, y=150, anchor=CENTER)

    Useringreso = Frame(registro_frame, bg=B)
    Useringreso.pack()

    global cuadroNombre
    cuadroNombre = Nombre(Useringreso, "Nombre", bg=B)
    cuadroNombre.grid(row=0, column=1)
    cuadroNombre.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")
        
    global cuadroUsuario
    cuadroUsuario = Usuario(Useringreso, "Usuario", bg=B)
    cuadroUsuario.grid(row=1, column=1)
    cuadroUsuario.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")

    user1 = PhotoImage(file="Img/user1.png")
    Label(Useringreso, image=user1, bg=B).grid(row=1, column=0, padx=10, pady=10)

    global cuadroPassword
    cuadroPassword = Password(Useringreso, "Contraseña", bg=B)
    cuadroPassword.grid(row=2, column=1)
    cuadroPassword.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")
    
    global cuadroConfirmarPassword
    cuadroConfirmarPassword = ConfirmarPassword(Useringreso, "Confirmar contraseña", bg=B)
    cuadroConfirmarPassword.grid(row=3, column=1)
    cuadroConfirmarPassword.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")

    lock1 = PhotoImage(file="Img/lock.png")
    Label(Useringreso, image=lock1, bg=B).grid(row=2, column=0, padx=10, pady=10)

    Useringreso.place(relx=0.5, y=390, anchor=CENTER)
    
    global imagen_mostrar
    # Botón para mostrar/ocultar contraseña
    imagen_mostrar = PhotoImage(file="Img/mostrar.png")
    botonMostrarContrasena = Button(Useringreso, image=imagen_mostrar, fg=L, bg="WHITE", font=("Arial", 10), relief=GROOVE, borderwidth=1,  command=cuadroPassword.show_hide_password)
    botonMostrarContrasena.grid(row=2, column=2, padx=10)
    botonMostrarContrasena.bind("<Enter>", lambda event: botonMostrarContrasena.config(bg=BgButton))
    botonMostrarContrasena.bind("<Leave>", lambda event: botonMostrarContrasena.config(bg="WHITE"))

    # Botón para mostrar/ocultar contraseña
    botonMostrarContrasenaConfirmada = Button(Useringreso,  image=imagen_mostrar, fg=L, bg="WHITE", font=("Arial", 10), relief=GROOVE, borderwidth=1, command=cuadroConfirmarPassword.show_hide_password1)
    botonMostrarContrasenaConfirmada.grid(row=3, column=2, padx=10)
    botonMostrarContrasenaConfirmada.bind("<Enter>", lambda event: botonMostrarContrasenaConfirmada.config(bg=BgButton))
    botonMostrarContrasenaConfirmada.bind("<Leave>", lambda event: botonMostrarContrasenaConfirmada.config(bg="WHITE"))


    
    botonCrearCuenta = Button(registro_frame, text="Crear cuenta",  fg=L, bg=BgButton, font=("Comic Sans MS", 12), relief=GROOVE, borderwidth=2, command=crear_usuario )
    botonCrearCuenta.place(relx=0.5, y=500, anchor=CENTER, width=100, height=20)
    botonCrearCuenta.bind("<Enter>", lambda event: botonCrearCuenta.config(bg=BgButton_Selet))
    botonCrearCuenta.bind("<Leave>", lambda event: botonCrearCuenta.config(bg=BgButton))

    botonVolverALogin = Button(registro_frame, text="Volver a Login", fg=L, bg=B, font=("Comic Sans MS", 12), relief=GROOVE, borderwidth=0, command=login_screen )
    botonVolverALogin.place(relx=0.5, y=530, anchor=CENTER, width=150, height=20)
    botonVolverALogin.bind("<Enter>", lambda event: botonVolverALogin.config(bg=BgButton_Selet))
    botonVolverALogin.bind("<Leave>", lambda event: botonVolverALogin.config(bg=B))
#------------------------------------------------------------------
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

#----------------------Frame recuperacion de contraseña--------------------
def recuperacion_screen():
    global imagenUser, user, lock  
    global recuperacion_frame

    inicio.destroy()
    if 'login_frame' in globals():
        login_frame.destroy()
    if 'registro_frame' in globals():
        registro_frame.destroy()

    recuperacion_frame = Frame(menu, width=x, height=y, bg=B)
    recuperacion_frame.pack(fill=BOTH, expand=TRUE)
    recuperacion_frame.pack_propagate(FALSE)
    imagenUser = PhotoImage(file="Img/user.png")
    Label(recuperacion_frame, image=imagenUser, bg=B).place(relx=0.5, y=150, anchor=CENTER)
    
    Useringreso = Frame(recuperacion_frame, bg=B)
    Useringreso.pack()

    global cuadroPassword
    global cuadroConfirmarPassword
    global cuadroUsuario
    
    Useringreso.place(relx=0.5, y=370, anchor=CENTER)

    lock = PhotoImage(file="Img/User1.png")
    Label(Useringreso, image=lock, bg=B).grid(row=0, column=0, padx=10, pady=10)
    
    cuadroUsuario = Usuario(Useringreso, "Usuario", bg=B)
    cuadroUsuario.grid(row=0, column=1)
    cuadroUsuario.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")

    user1 = PhotoImage(file="Img/user1.png")
    Label(Useringreso, image=user1, bg=B).grid(row=1, column=0, padx=10, pady=10)

    global cuadroPassword
    cuadroPassword = Password(Useringreso, "Contraseña", bg=B)
    cuadroPassword.grid(row=1, column=1)
    cuadroPassword.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")
    
    global cuadroConfirmarPassword
    cuadroConfirmarPassword = ConfirmarPassword(Useringreso, "Confirmar contraseña", bg=B)
    cuadroConfirmarPassword.grid(row=2, column=1)
    cuadroConfirmarPassword.config(justify="center", font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=2, highlightcolor="blue", highlightbackground="#3ba3ee")

    botonRecuperarContrasena = Button(recuperacion_frame, text=" Aceptar", fg=L, bg="#3289c8", font=("Comic Sans MS", 12), relief=GROOVE, borderwidth=2, command=recuperar_contrasena)
    botonRecuperarContrasena.place(relx=0.5, y=500, anchor=CENTER, width=150, height=20)
    botonRecuperarContrasena.bind("<Enter>", lambda event: botonRecuperarContrasena.config(bg="#08acef"))
    botonRecuperarContrasena.bind("<Leave>", lambda event: botonRecuperarContrasena.config(bg="#3289c8"))
    

    botonVolverALogin = Button(recuperacion_frame, text="Volver a Login", fg=L, bg="#3289c8", font=("Comic Sans MS", 12), relief=GROOVE, borderwidth=2, command=login_screen )
    botonVolverALogin.place(relx=0.5, y=530, anchor=CENTER, width=150, height=20)
    botonVolverALogin.bind("<Enter>", lambda event: botonVolverALogin.config(bg=BgButton_Selet))
    botonVolverALogin.bind("<Leave>", lambda event: botonVolverALogin.config(bg=BgButton))

    global imagen_mostrar
       # Botón para mostrar/ocultar contraseña
    imagen_mostrar = PhotoImage(file="Img/mostrar.png")
    botonMostrarContrasena = Button(Useringreso, image=imagen_mostrar, bg="White", font=("Arial", 10), relief=GROOVE, borderwidth=1,  command=cuadroPassword.show_hide_password)
    botonMostrarContrasena.grid(row=1, column=2, padx=10)
    botonMostrarContrasena.bind("<Enter>", lambda event: botonMostrarContrasena.config(bg="#3289c8"))
    botonMostrarContrasena.bind("<Leave>", lambda event: botonMostrarContrasena.config(bg="White"))

    # Botón para mostrar/ocultar contraseña
    botonMostrarContrasenaConfirmada = Button(Useringreso,  image=imagen_mostrar, fg="White", bg="White", font=("Arial", 10), relief=GROOVE, borderwidth=1, command=cuadroConfirmarPassword.show_hide_password1)
    botonMostrarContrasenaConfirmada.grid(row=2, column=2, padx=10)
    botonMostrarContrasenaConfirmada.bind("<Enter>", lambda event: botonMostrarContrasenaConfirmada.config(bg="#3289c8"))
    botonMostrarContrasenaConfirmada.bind("<Leave>", lambda event: botonMostrarContrasenaConfirmada.config(bg="White"))

#----------------------------------------------------------------------------------


#----------------------menu inicio para ingresar al login-----------------------------
inicio = Frame(menu, width=x, height=y, bg=B)
inicio.pack(fill=BOTH, expand=TRUE)
inicio.pack_propagate(FALSE)

bienvenida = Label(inicio, text="Bienvenido", fg="#3289c8", bg=B, font=("Comic Sans MS", 38), relief=GROOVE, borderwidth=0)
bienvenida.place(relx=0.5, y=100, anchor=CENTER)


botonIngresar = Button(inicio, text="Ingresar", command=login_screen, fg=L, bg="#3289c8", font=("Comic Sans MS", 18), relief=GROOVE, borderwidth=2)
botonIngresar.place(relx=0.5, y=400, anchor=CENTER)
botonIngresar.bind("<Enter>", lambda event: botonIngresar.config(bg=BgButton_Selet))
botonIngresar.bind("<Leave>", lambda event: botonIngresar.config(bg=BgButton))


menu.mainloop()