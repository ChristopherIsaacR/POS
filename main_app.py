from tkinter import *
from PIL import Image, ImageTk
import subprocess
from datetime import datetime

from db_connection import crear_usuario, verificar_usuario, verificar_sesion_activa, cerrar_sesion, recuperar_contrasena

#global cuadroNombre, cuadroUsuario

session_token = None
usuario_actual = None
session_label = None  # Referencia global a la etiqueta de sesión



x = 1300
y = 650

B="White" 
L="Black"
BgButton="#3289c8"
BgButton_Selet="#08acef"


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
    Button_Tema_img = Image.open("Img/TemaB.png")
    Button_Tema_img = Button_Tema_img.resize((40, 40))
    Button_Tema_ico = ImageTk.PhotoImage(Button_Tema_img)
    Button_Tema = Button(login_frame,image=Button_Tema_ico, bg=B, borderwidth=0, command=cambio_de_tema)
    Button_Tema.place(relx=0.75, rely=.15, anchor=CENTER)
    Button_Tema.bind("<Enter>", lambda event: Button_Tema.config(image=Button_Tema_ico))
    Button_Tema.bind("<Leave>", lambda event: Button_Tema.config(image=Button_Tema_ico))

    Button_Tema_B_img = Image.open("Img/Tema.png")
    Button_Tema_B_img = Button_Tema_B_img.resize((40, 40))
    Button_Tema_B_ico = ImageTk.PhotoImage(Button_Tema_B_img)
    Button_Tema_B = Button(login_frame,image=Button_Tema_B_ico, bg=B, borderwidth=0, command=cambio_de_tema_blanco)
    Button_Tema_B.place(relx=0.65, rely=.15, anchor=CENTER)
    Button_Tema_B.bind("<Enter>", lambda event: Button_Tema_B.config(image=Button_Tema_B_ico))
    Button_Tema_B.bind("<Leave>", lambda event: Button_Tema_B.config(image=Button_Tema_B_ico))

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
    

    botonVolverALogin = Button(recuperacion_frame, text="Volver a Login", fg=L, bg=B, font=("Comic Sans MS", 12), relief=GROOVE, borderwidth=2, command=login_screen )
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
