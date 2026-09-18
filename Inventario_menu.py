from tkinter import *
import tkinter as tk
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from tkinter import messagebox, filedialog
import shutil
import sqlite3
import sys
from datetime import datetime



# Variables globales
indice_actual = 0
datos_por_pagina = 28

usuario_actual = sys.argv[1] if len(sys.argv) > 1 else "Invitado"
try:
    hora_inicio_sesion = datetime.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.now()
except ValueError:
    hora_inicio_sesion = datetime.now()

cliente_actual = {"nombre": None}

x = 1300
y = 700

B="White" 
L="Black"

BgBorde_button="gray"
BgBorde_button_C="gray"
BgButton="gray"
# ------------------Frame menu default-----------------
menu = Tk()

menu.title("Gestion de inventarios")
menu.resizable(False, False)
menu.iconbitmap("Img/icon.ico")
menu.geometry(f"{x}x{y}-100-80")
menu.config(bg="White")

# -----------------------------------------------------

# ----conexion a la base de datos------
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia esto por tu nombre de usuario de MySQL
        password="",  # Cambia esto por tu contraseña de MySQL
        database="inventario2024"
    )
# --------------------------------------

def asegurar_tablas_ventas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha DATETIME,
            total DECIMAL(10,2),
            forma_pago VARCHAR(50),
            cliente_nombre VARCHAR(150),
            usuario VARCHAR(100)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venta_detalle (
            id INT AUTO_INCREMENT PRIMARY KEY,
            venta_id INT,
            nombre_producto VARCHAR(150),
            cantidad INT,
            precio_unitario DECIMAL(10,2),
            subtotal DECIMAL(10,2)
        )
    """)

    cursor.execute("SHOW COLUMNS FROM ventas")
    columnas_ventas = [fila[0] for fila in cursor.fetchall()]
    columnas_necesarias_ventas = {
        "fecha": "DATETIME",
        "total": "DECIMAL(10,2)",
        "forma_pago": "VARCHAR(50)",
        "cliente_nombre": "VARCHAR(150)",
        "usuario": "VARCHAR(100)"
    }
    for columna, tipo in columnas_necesarias_ventas.items():
        if columna not in columnas_ventas:
            cursor.execute(f"ALTER TABLE ventas ADD COLUMN {columna} {tipo}")

    cursor.execute("SHOW COLUMNS FROM venta_detalle")
    columnas_detalle = [fila[0] for fila in cursor.fetchall()]
    columnas_necesarias_detalle = {
        "venta_id": "INT",
        "nombre_producto": "VARCHAR(150)",
        "cantidad": "INT",
        "precio_unitario": "DECIMAL(10,2)",
        "subtotal": "DECIMAL(10,2)"
    }
    for columna, tipo in columnas_necesarias_detalle.items():
        if columna not in columnas_detalle:
            cursor.execute(f"ALTER TABLE venta_detalle ADD COLUMN {columna} {tipo}")

    conn.commit()
    cursor.close()
    conn.close()

try:
    asegurar_tablas_ventas()
except mysql.connector.Error as e:
    print(f"No se pudieron verificar las tablas de ventas: {e}")

home = Frame(menu, width=x, height=y, bg=B)
home.pack(fill=BOTH, expand=TRUE)
home.pack_propagate(FALSE)

# Crear un frame para el menú de lado izquierdo
menu_frame = Frame(home, bg="#163e64", width=50)
menu_frame.pack(side=LEFT, fill=Y, anchor=W)

#-------------Tamaño de los iconos del menu------------------------------------------
Ximg = 80
Yimg = 80
#------------------------------------------------------------------------------------

#-------------Tamaño de los iconos de los sub----------------------------------------
Ximg_1 = 40
Yimg_1 = 40
#------------------------------------------------------------------------------------

def cambio_de_tema():
    global B, L
    B="Black"
    L="White"
    catalogo()
def cambio_de_tema_blanco():
    global B, L
    B="White"
    L="Black"
    catalogo()

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


#-----------------Sugerencias en las elecciones de categoria y proveedores----------------------
# Función para obtener todas las Ubicacion
def obtener_ubicacion():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT ubicacion FROM productos")
    ubicacion = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ubicacion
# Función para obtener todas las categorías
def obtener_categorias():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM categorias")
    categorias = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categorias

# Función para obtener todos los proveedores
def obtener_proveedores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM proveedores")
    proveedores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return proveedores
#---------mostrar imagenes en ventana Ventas--------------------
indice_actual_pagina_ventas = 0
datos_por_pagina_ventas = 8
# Diccionario para almacenar los productos en el carrito
carrito = {}


def agregar_al_carrito(nombre, precio):
    if nombre in carrito:
        # Incrementar la cantidad si el producto ya está en el carrito
        carrito[nombre]['cantidad_var'].set(carrito[nombre]['cantidad_var'].get() + 1)
    else:
        # Crear frame para el producto
        producto_frame = Frame(Carrito_frame_productos, bg="white")
        producto_frame.pack(fill=X, padx=10, pady=5)

        # Checkbox de selección
        seleccionado_var = BooleanVar(value=False)
        check_seleccion = Checkbutton(producto_frame, variable=seleccionado_var, bg="white")
        check_seleccion.pack(side=LEFT, padx=2)

        # Nombre del producto
        nombre_label = Label(producto_frame, text=nombre, bg="white", font=("Arial", 12))
        nombre_label.pack(side=LEFT, padx=5)

        # Cantidad del producto
        cantidad_var = IntVar(value=1)
        cantidad_entry = Spinbox(producto_frame, from_=1, to=100, textvariable=cantidad_var, font=("Arial", 12), width=5)
        cantidad_entry.pack(side=LEFT, padx=5)

        # Precio del producto
        precio_label = Label(producto_frame, text=f"{precio}", bg="white", font=("Arial", 12))
        precio_label.pack(side=LEFT, padx=5)

        # Botón de eliminar
        img_x = Image.open("img/x_carrito.png").resize((20, 20))
        img_x = ImageTk.PhotoImage(img_x)
        eliminar_button = Button(producto_frame, image=img_x, bg="white", borderwidth=0, command=lambda: eliminar_del_carrito(nombre, producto_frame))
        eliminar_button.image = img_x
        eliminar_button.pack(side=LEFT, padx=5)

        # Guardar el producto en el diccionario del carrito
        carrito[nombre] = {
            'frame': producto_frame,
            'cantidad_var': cantidad_var,
            'precio': precio,
            'seleccionado_var': seleccionado_var
        }

        # Actualizar la vista del canvas
        actualizar_scrollregion()

def actualizar_scrollregion():
    Carrito_frame_canvas.update_idletasks()
    Carrito_frame_canvas.config(scrollregion=Carrito_frame_canvas.bbox("all"))
    
def eliminar_del_carrito(nombre, producto_frame):
    producto_frame.destroy()
    del carrito[nombre]
    actualizar_scrollregion()

def eliminar_seleccionados_carrito():
    seleccionados = [nombre for nombre, datos in carrito.items() if datos['seleccionado_var'].get()]
    if not seleccionados:
        messagebox.showinfo("Eliminar", "Selecciona al menos un producto del carrito para eliminarlo")
        return
    for nombre in seleccionados:
        carrito[nombre]['frame'].destroy()
        del carrito[nombre]
    actualizar_scrollregion()

def mostrar_productos_galeria():
    global indice_actual_pagina_ventas, datos_por_pagina_ventas

    # Conectar a la base de datos
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, precio, cantidad_stock, codigo_barra FROM productos")

        # Obtener todos los productos
        rows = cursor.fetchall()

        # Limpiar el frame anterior si ya existe
        global Galeria_Productos_Frame
        if 'Galeria_Productos_Frame' in globals():
            Galeria_Productos_Frame.destroy()

        # Crear el frame para la galería de productos
        Galeria_Productos_Frame = Frame(venta_frame, bg=B)
        Galeria_Productos_Frame.place(relx=0.65, rely=0.48, anchor=tk.CENTER)

        # Extensiones de imágenes soportadas
        extensiones = ['.png', '.jpg', '.jpeg', '.gif']

        # Mostrar productos en la página actual
        start = indice_actual_pagina_ventas * datos_por_pagina_ventas
        end = start + datos_por_pagina_ventas
        productos_pagina = rows[start:end]
        text_table="gray"
        row, col = 0, 0
        for (nombre, precio, cantidad_stock, codigo_barra) in productos_pagina:
            imagen_encontrada = False
            for ext in extensiones:
                foto_path = os.path.join("imagenes_productos", f"{codigo_barra}{ext}")
                if os.path.isfile(foto_path):
                    try:
                        imagen = Image.open(foto_path)
                        imagen = imagen.resize((120, 120))
                        foto = ImageTk.PhotoImage(imagen)
        
                        # Mostrar la imagen
                        label_imagen = Label(Galeria_Productos_Frame, image=foto, bg=B, fg=text_table)
                        label_imagen.image = foto  # keep a reference
                        label_imagen.grid(row=row, column=col, padx=20, pady=20)

                        # Mostrar nombre del producto
                        label_nombre = Label(Galeria_Productos_Frame, text=nombre, bg=B, fg=text_table)
                        label_nombre.grid(row=row+1, column=col)

                        # Mostrar precio
                        label_precio = Label(Galeria_Productos_Frame, text=f"Precio: {precio}", bg=B, fg=text_table)
                        label_precio.grid(row=row+2, column=col)

                        # Mostrar stock
                        label_stock = Label(Galeria_Productos_Frame, text=f"Stock: {cantidad_stock}", bg=B, fg=text_table)
                        label_stock.grid(row=row+3, column=col)
                        # Botón de agregar al carrito
                        agregar_button = Button(Galeria_Productos_Frame, text="Agregar al carrito", bg=B, command=lambda n=nombre, p=precio: agregar_al_carrito(n, p))
                        agregar_button.grid(row=row+5, column=col)

                        imagen_encontrada = True
                        break
                    except Exception as e:
                        print(f"Error abriendo la imagen {foto_path}: {e}")

            if not imagen_encontrada:
                # Si no se encontró ninguna imagen, mostrar una imagen por defecto
                try:
                    default_img_path = "img/imagen_no_disponible.jpg"
                    imagen = Image.open(default_img_path)
                    imagen = imagen.resize((120, 120))
                    foto = ImageTk.PhotoImage(imagen)

                    # Mostrar la imagen por defecto
                    label_imagen = Label(Galeria_Productos_Frame, image=foto, bg=B)
                    label_imagen.image = foto  # keep a reference
                    label_imagen.grid(row=row, column=col, padx=20, pady=20)
                except Exception as e:
                    print(f"Error abriendo la imagen por defecto {default_img_path}: {e}")
                
                # Mostrar nombre del producto
                label_nombre = Label(Galeria_Productos_Frame, text=nombre, bg=B, fg=text_table)
                label_nombre.grid(row=row+2, column=col)

                # Mostrar precio
                label_precio = Label(Galeria_Productos_Frame, text=f"Precio: {precio}", bg=B, fg=text_table)
                label_precio.grid(row=row+3, column=col)

                # Mostrar stock
                label_stock = Label(Galeria_Productos_Frame, text=f"Stock: {cantidad_stock}", bg=B, fg=text_table)
                label_stock.grid(row=row+4, column=col)
                # Botón de agregar al carrito
                agregar_button = Button(Galeria_Productos_Frame, text="Agregar al carrito", bg=B, command=lambda n=nombre, p=precio: agregar_al_carrito(n, p))
                agregar_button.grid(row=row+5, column=col)
                

            col += 1
            if col > 3:
                col = 0
                row += 6  # Aumentar el número de filas para el siguiente conjunto de productos

        # Botones de navegación
        def pagina_anterior_V():
            global indice_actual_pagina_ventas
            if indice_actual_pagina_ventas > 0:
                indice_actual_pagina_ventas -= 1
                mostrar_productos_galeria()
        
        def siguiente_pagina_V():
            global indice_actual_pagina_ventas
            if (indice_actual_pagina_ventas + 1) * datos_por_pagina_ventas < len(rows):
                indice_actual_pagina_ventas += 1
                mostrar_productos_galeria()

        # Crear frame para los botones de navegación
        global botones_sig_ant_Frame
        if 'botones_sig_ant_Frame' in globals():
            botones_sig_ant_Frame.destroy()
        botones_sig_ant_Frame= Frame(venta_frame, width=600, height=80, bg=B)
        botones_sig_ant_Frame.place(relx=.40, rely=.85, width=600)


        

        # Botón Anterior
        btn_anterior_V_img = Image.open("Img/prev.png")
        btn_anterior_V_img_hover = Image.open("Img/prev_1.png")
        btn_anterior_V_img = btn_anterior_V_img.resize((50, 50))
        btn_anterior_V_img_hover = btn_anterior_V_img_hover.resize((50, 50))
        btn_anterior_V_ico = ImageTk.PhotoImage(btn_anterior_V_img)
        btn_anterior_V_ico_hover = ImageTk.PhotoImage(btn_anterior_V_img_hover)
        btn_anterior_V = Button(botones_sig_ant_Frame, image=btn_anterior_V_ico, bg=B, borderwidth=0, command=pagina_anterior_V)
        btn_anterior_V.bind("<Enter>", lambda event: btn_anterior_V.config(image=btn_anterior_V_ico_hover))
        btn_anterior_V.bind("<Leave>", lambda event: btn_anterior_V.config(image=btn_anterior_V_ico))
        if indice_actual_pagina_ventas == 0:
            btn_anterior_V.pack_forget()  # Ocultar el botón "Anterior" en la primera página
        else:
            btn_anterior_V.pack(side=tk.LEFT, padx=20, pady=10)

        # Botón Siguiente
        btn_siguiente_V_img = Image.open("Img/Next.png")
        btn_siguiente_V_img_hover = Image.open("Img/Next_1.png")
        btn_siguiente_V_img = btn_siguiente_V_img.resize((50, 50))
        btn_siguiente_V_img_hover = btn_siguiente_V_img_hover.resize((50, 50))
        btn_siguiente_V_ico = ImageTk.PhotoImage(btn_siguiente_V_img)
        btn_siguiente_V_ico_hover = ImageTk.PhotoImage(btn_siguiente_V_img_hover)
        btn_siguiente_V = Button(botones_sig_ant_Frame, image=btn_siguiente_V_ico, bg=B, borderwidth=0, command=siguiente_pagina_V)
        btn_siguiente_V.bind("<Enter>", lambda event: btn_siguiente_V.config(image=btn_siguiente_V_ico_hover))
        btn_siguiente_V.bind("<Leave>", lambda event: btn_siguiente_V.config(image=btn_siguiente_V_ico))
        if indice_actual_pagina_ventas + 1 >= len(rows) / datos_por_pagina_ventas:
            btn_siguiente_V.pack_forget()  # Ocultar el botón "Siguiente" si no hay más páginas
        else:
            btn_siguiente_V.pack(side=tk.RIGHT, padx=20, pady=10)

                # Actualizar la etiqueta de la página actual
        pagina_actual_V = indice_actual_pagina_ventas + 1
        total_paginas_V = (len(rows) + datos_por_pagina_ventas - 1) // datos_por_pagina_ventas  # Calcular el número total de páginas
        etiqueta_pagina_V = Label(botones_sig_ant_Frame, text=f"Página {pagina_actual_V} de {total_paginas_V}", background=B, foreground=L)
        etiqueta_pagina_V.pack(side=TOP, padx=180, pady=10)
        etiqueta_pagina_V.place(relx=0.43 , rely=.20)
        #etiqueta_pagina_V.place(width=100)

        # Cerrar conexión y cursor
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"Error de conexión a MySQL: {e}")    
#-------------------------------
#mostrar imagenes
def mostrar_imagen_producto(nombre_archivo_sin_extension):
    # Limpiar el frame anterior si ya existe
    global Imagen_Producto_Frame
    if 'Imagen_Producto_Frame' in globals():
        Imagen_Producto_Frame.destroy()

    Imagen_Producto_Frame = Frame(Catalogo_Frame, bg=B, width=200, height=200)
    Imagen_Producto_Frame.place(relx=0.85, rely=0.15, anchor=CENTER)
    
    # Extensiones de imagenes soportadas
    extensiones = ['.png', '.jpg', '.jpeg', '.gif']
    
    imagen_encontrada = False
    for ext in extensiones:
        foto_path = os.path.join("imagenes_productos", nombre_archivo_sin_extension + ext)
        if os.path.isfile(foto_path):
            try:
                imagen = Image.open(foto_path)
                imagen = imagen.resize((120, 120))
                foto = ImageTk.PhotoImage(imagen)

                label_imagen = Label(Imagen_Producto_Frame, image=foto, bg=B)
                label_imagen.image = foto  # keep a reference
                label_imagen.pack(pady=40)
                
                imagen_encontrada = True
                break
            except Exception as e:
                print(f"Error abriendo la imagen {foto_path}: {e}")
    
    if not imagen_encontrada:
        label_error = Label(Imagen_Producto_Frame, text="Sin imagen", fg="red", bg=B)
        label_error.pack(pady=60)

def sort_column(tree, col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))
# Función para mostrar todos los productos en la tabla
def mostrar_productos_seleccionados():
    global indice_actual, rows

    conn = conectar()
    cursor = conn.cursor()

    # Consulta SQL con JOIN para obtener nombres de categoría y proveedor
    cursor.execute("""
        SELECT p.nombre, CONCAT('$', p.precio) AS precio_con_moneda, p.cantidad_stock, c.nombre AS categoria, 
               p.color, p.modelo, p.talla, p.descripcion, p.material, 
               p.codigo_barra, prov.nombre AS proveedor, p.Ubicacion, p.Foto, p.id 
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
    """)
    
    rows = cursor.fetchall()
    conn.close()

    # Limpiar datos anteriores en el Treeview
    for row in tree.get_children():
        tree.delete(row)

    # Mostrar los datos de la página actual
    if indice_actual >= len(rows):
        # Si no hay más datos que mostrar, actualizar el índice actual y salir
        indice_actual = len(rows)
        return
    
    for row in rows[indice_actual:indice_actual + datos_por_pagina]:
        tree.insert("", "end", values=row)

    # Actualizar la etiqueta de la página actual
    pagina_actual = int(indice_actual / datos_por_pagina) +1
    total_paginas = (len(rows) + datos_por_pagina - 1) // datos_por_pagina  # Calcular el número total de páginas
    etiqueta_pagina.config(text=f"Página {pagina_actual} de {total_paginas}")

    # Actualizar el estado de los botones de navegación
    if indice_actual == 0:
        btn_anterior.pack_forget()  # Ocultar el botón "Anterior" en la primera página
    else:
        btn_anterior.pack(side=LEFT, padx=10, pady=10)
        

    if indice_actual + datos_por_pagina >= len(rows):
        btn_siguiente.pack_forget()  # Ocultar el botón "Siguiente" si no hay más páginas
    else:
        btn_siguiente.pack(side=RIGHT, padx=10, pady=10)


def siguiente_pagina():
    global indice_actual
    indice_actual += datos_por_pagina
    if indice_actual >= len(rows):
        indice_actual = len(rows) - 1  
    if indice_actual >= len(rows):
        # Si no hay más datos que mostrar, actualizar el índice actual y salir
        indice_actual = len(rows)
        
    mostrar_productos_seleccionados()

def pagina_anterior():

    global indice_actual
    indice_actual = max(0, indice_actual - datos_por_pagina)
    mostrar_productos_seleccionados()

# Función para agregar un nuevo producto
def agregar_producto():
    nombre = entry_nombre.get()
    descripcion = entry_descripcion.get()
    precio = entry_precio.get()
    cantidad_stock = entry_cantidad_stock.get()
    codigo_barra = entry_codigo_barra.get()
    modelo = entry_modelo.get()
    color = entry_color.get()
    talla = entry_talla.get()
    material = entry_material.get()
    proveedor_nombre = entry_proveedor.get()  # Nombre del proveedor
    ubicacion = entry_ubicacion.get()
    categoria_nombre = entry_categoria.get()  # Nombre de la categoría

    # Seleccionar la imagen
    foto_path = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
    if not foto_path:
        messagebox.showerror("Error", "Debe seleccionar una imagen.")
        return

    # Crear la ruta para almacenar la imagen
    foto_dir = "imagenes_productos"
    os.makedirs(foto_dir, exist_ok=True)
    _, extension = os.path.splitext(foto_path)
    nueva_foto_path = os.path.join(foto_dir, codigo_barra + extension)

    try:
        # Copiar la imagen a la carpeta de destino
        shutil.copy(foto_path, nueva_foto_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error al copiar la imagen: {e}")
        return

    conn = conectar()
    cursor = conn.cursor()

    # Obtener el ID del proveedor y de la categoría por nombre
    cursor.execute("SELECT id FROM proveedores WHERE nombre = %s", (proveedor_nombre,))
    proveedor_id = cursor.fetchone()
    if proveedor_id:
        proveedor_id = proveedor_id[0]
    else:
        messagebox.showerror("Error", "El proveedor seleccionado no existe.")
        conn.close()
        return

    cursor.execute("SELECT id FROM categorias WHERE nombre = %s", (categoria_nombre,))
    categoria_id = cursor.fetchone()
    if categoria_id:
        categoria_id = categoria_id[0]
    else:
        messagebox.showerror("Error", "La categoría seleccionada no existe.")
        conn.close()
        return

    # Verificar si el producto ya existe basado en un campo único, como 'nombre' o 'codigo_barra'
    cursor.execute("SELECT COUNT(*) FROM productos WHERE nombre = %s OR codigo_barra = %s", (nombre, codigo_barra))
    resultado = cursor.fetchone()

    if resultado[0] > 0:
        messagebox.showerror("Error", "El producto con ese nombre o código de barras ya existe.")
    else:
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, precio, cantidad_stock, codigo_barra, modelo, color, talla, material, proveedor_id, ubicacion, categoria_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, cantidad_stock, codigo_barra, modelo, color, talla, material, proveedor_id, ubicacion, categoria_id))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto agregado exitosamente")

    conn.close()
    mostrar_productos_seleccionados()
# Función para eliminar un producto
def eliminar_producto():
    selected_item = tree.selection()[0]
    producto_id = tree.item(selected_item, 'values')[13]
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
    conn.commit()
    conn.close()
    
    mostrar_productos_seleccionados()
    messagebox.showinfo("Éxito", "Producto eliminado exitosamente")

# Función para modificar un producto
def modificar_producto():
    selected_item = tree.selection()[0]
    producto_id = tree.item(selected_item, 'values')[13]  # Obtener el ID del producto
    nombre = entry_nombre.get()
    descripcion = entry_descripcion.get()
    precio = entry_precio.get()
    cantidad_stock = entry_cantidad_stock.get()
    codigo_barra = entry_codigo_barra.get()
    modelo = entry_modelo.get()
    color = entry_color.get()
    talla = entry_talla.get()
    material = entry_material.get()
    proveedor_nombre = entry_proveedor.get()  # Nombre del proveedor
    ubicacion = entry_ubicacion.get()
    categoria_nombre = entry_categoria.get()  # Nombre de la categoría

    # Seleccionar la imagen (opcional)
    if messagebox.askyesno("Foto del producto", "¿Deseas actualizar la foto del producto?"):
        foto_path = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        if foto_path:
            foto_dir = "imagenes_productos"
            os.makedirs(foto_dir, exist_ok=True)
            _, extension = os.path.splitext(foto_path)
            nueva_foto_path = os.path.join(foto_dir, codigo_barra + extension)

            try:
                shutil.copy(foto_path, nueva_foto_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error al copiar la imagen: {e}")
                return

    conn = conectar()
    cursor = conn.cursor()

    # Obtener el ID del proveedor y de la categoría por nombre
    cursor.execute("SELECT id FROM proveedores WHERE nombre = %s", (proveedor_nombre,))
    proveedor_id = cursor.fetchone()
    if proveedor_id:
        proveedor_id = proveedor_id[0]
    else:
        messagebox.showerror("Error", "El proveedor seleccionado no existe.")
        conn.close()
        return

    cursor.execute("SELECT id FROM categorias WHERE nombre = %s", (categoria_nombre,))
    categoria_id = cursor.fetchone()
    if categoria_id:
        categoria_id = categoria_id[0]
    else:
        messagebox.showerror("Error", "La categoría seleccionada no existe.")
        conn.close()
        return

    cursor.execute("""
        UPDATE productos
        SET nombre = %s, descripcion = %s, precio = %s, cantidad_stock = %s, codigo_barra = %s, modelo = %s, color = %s, talla = %s, material = %s, proveedor_id = %s, ubicacion = %s, categoria_id = %s
        WHERE id = %s
    """, (nombre, descripcion, precio, cantidad_stock, codigo_barra, modelo, color, talla, material, proveedor_id, ubicacion, categoria_id, producto_id))
    conn.commit()
    conn.close()

    mostrar_productos_seleccionados()
    messagebox.showinfo("Éxito", "Producto modificado exitosamente")

def buscar_producto():
    filtro = entry_buscar.get()
    

    conn = conectar()
    cursor = conn.cursor()
    # Crear la consulta SQL con filtrado y concatenación del símbolo de moneda
    query = """
        SELECT p.nombre, 
               CONCAT('$', p.precio) AS precio, 
               p.cantidad_stock, 
               c.nombre AS categoria, 
               p.color, 
               p.modelo, 
               p.talla, 
               p.descripcion, 
               p.material, 
               p.codigo_barra, 
               prov.nombre AS proveedor, 
               p.Ubicacion, 
               p.Foto, 
               p.id 
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
        WHERE p.id LIKE %s
           OR p.nombre LIKE %s
           OR p.precio LIKE %s
           OR p.cantidad_stock LIKE %s
           OR p.codigo_barra LIKE %s
           OR p.modelo LIKE %s
           OR p.talla LIKE %s
           OR p.material LIKE %s
           OR p.proveedor_id LIKE %s
           OR p.ubicacion LIKE %s
           OR p.categoria_id LIKE %s
           OR prov.nombre LIKE %s
           OR c.nombre LIKE %s
    """


    # Ejecutar la consulta con el filtro para todos los campos
    cursor.execute(query, tuple(f"%{filtro}%" for _ in range(13)))
    
    rows = cursor.fetchall()
    conn.close()

    # Limpiar datos anteriores en el Treeview
    for row in tree.get_children():
        tree.delete(row)
    
    # Insertar los datos en el Treeview
    for row in rows:
        tree.insert("", "end", values=row)

# Función para crear la vista de catálogo
def catalogo():
    #menu_frame.destroy()
    global Catalogo_Frame
    cerrar_otras_pantallas()

    global B, L

    Catalogo_Frame = Frame(home, width=x, height=y, bg=B)
    Catalogo_Frame.pack(fill=BOTH, expand=TRUE)

    
    Catalogo_title = Label(Catalogo_Frame, text="Catalogo de Productos", fg="#3289c8", bg=B, font=("Comic Sans MS", 28), relief=GROOVE, borderwidth=0)
    Catalogo_title.place(relx=0.25, rely=.05, anchor=CENTER)
    
    global entry_nombre, entry_descripcion, entry_precio, entry_cantidad_stock, entry_foto, entry_codigo_barra, entry_modelo, entry_color, entry_talla, entry_material, entry_proveedor_id, entry_ubicacion, entry_categoria_id, entry_buscar, tree, entry_proveedor, entry_categoria
    
    Y1=0.43
    X1=0.73
    Ex1=0.84

    Label(Catalogo_Frame, text="Nombre:", bg=B, fg=L).place(relx=X1, rely=Y1)
    entry_nombre = Entry(Catalogo_Frame)
    entry_nombre.place(relx=Ex1, rely=Y1)
    entry_nombre.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)


    Label(Catalogo_Frame, text="Descripción:", bg=B, fg=L).place(relx=X1, rely=Y1+.04)
    entry_descripcion = Entry(Catalogo_Frame)
    entry_descripcion.place(relx=Ex1, rely=Y1+.04)
    entry_descripcion.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    
    Label(Catalogo_Frame, text="Precio:", bg=B, fg=L).place(relx=X1, rely=Y1+.08)
    entry_precio = Entry(Catalogo_Frame)
    entry_precio.place(relx=Ex1, rely=Y1+.08)
    entry_precio.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    
    Label(Catalogo_Frame, text="Cantidad Stock:", bg=B, fg=L).place(relx=X1, rely=Y1+.12)
    entry_cantidad_stock = Entry(Catalogo_Frame)
    entry_cantidad_stock.place(relx=Ex1, rely=Y1+.12)
    entry_cantidad_stock.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    

    Label(Catalogo_Frame, text="Categoria :", bg=B, fg=L).place(relx=X1, rely=Y1+.16)
    categorias = obtener_categorias()
    entry_categoria = ttk.Combobox(Catalogo_Frame, values=categorias)
    entry_categoria.place(relx=Ex1, rely=Y1+.16,width=125)
    
    Label(Catalogo_Frame, text="Código de Barra:", bg=B, fg=L).place(relx=X1, rely=Y1+.20)
    entry_codigo_barra = Entry(Catalogo_Frame)
    entry_codigo_barra.place(relx=Ex1, rely=Y1+.20)
    entry_codigo_barra.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    
    Label(Catalogo_Frame, text="Modelo:", bg=B, fg=L).place(relx=X1, rely=Y1+.24)
    entry_modelo = Entry(Catalogo_Frame)
    entry_modelo.place(relx=Ex1, rely=Y1+.24)
    entry_modelo.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    
    Label(Catalogo_Frame, text="Color:", bg=B, fg=L).place(relx=X1, rely=Y1+.28)
    entry_color = Entry(Catalogo_Frame)
    entry_color.place(relx=Ex1, rely=Y1+.28)
    entry_color.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    
    Label(Catalogo_Frame, text="Talla:", bg=B, fg=L).place(relx=X1, rely=Y1+.32)
    entry_talla = Entry(Catalogo_Frame)
    entry_talla.place(relx=Ex1, rely=Y1+.32)
    entry_talla.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    
    Label(Catalogo_Frame, text="Material:", bg=B, fg=L).place(relx=X1, rely=Y1+.36)
    entry_material = Entry(Catalogo_Frame)
    entry_material.place(relx=Ex1, rely=Y1+.36)
    entry_material.config( font=("Arial", 8), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)

    Label(Catalogo_Frame, text="Proveedor:", bg=B, fg=L).place(relx=X1, rely=Y1+.40)
    proveedores = obtener_proveedores()
    entry_proveedor = ttk.Combobox(Catalogo_Frame, values=proveedores)
    entry_proveedor.place(relx=Ex1, rely=Y1+.40, width=125)
    
    Label(Catalogo_Frame, text="Ubicacion:", bg=B, fg=L).place(relx=X1, rely=Y1+.44)
    Ubicacion = obtener_ubicacion()
    entry_ubicacion = ttk.Combobox(Catalogo_Frame, values=Ubicacion)
    entry_ubicacion.place(relx=Ex1, rely=Y1+.44, width=125)


    global entry_buscar_proveedor, entry_buscar, order_var
        # Añadir entradas y botones para filtrado y ordenamiento
    entry_buscar = Entry(Catalogo_Frame)
    entry_buscar.config( font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    entry_buscar.place(relx=0.19, rely=.12, anchor=CENTER, width=300)


    button_buscar_img = Image.open("Img/Buscar.png")
    button_buscar_img_hover = Image.open("Img/Buscar_1.png")
    button_buscar_img = button_buscar_img.resize((Ximg_1, Yimg_1))
    button_buscar_img_hover = button_buscar_img_hover.resize((Ximg_1, Yimg_1))
    button_buscar_ico = ImageTk.PhotoImage(button_buscar_img)
    button_buscar_ico_hover = ImageTk.PhotoImage(button_buscar_img_hover)
    button_buscar = Button(Catalogo_Frame,image=button_buscar_ico, bg=B, borderwidth=0, command=buscar_producto)
    button_buscar.place(relx=0.35, rely=.12, anchor=CENTER)
    button_buscar.bind("<Enter>", lambda event: button_buscar.config(image=button_buscar_ico_hover))
    button_buscar.bind("<Leave>", lambda event: button_buscar.config(image=button_buscar_ico))

    #button_filtro_img = Image.open("Img/Filtro.png")
    #button_filtro_img_hover = Image.open("Img/Filtro_1.png")
    #button_filtro_img = button_filtro_img.resize((Ximg_1, Yimg_1))
    #button_filtro_img_hover = button_filtro_img_hover.resize((Ximg_1, Yimg_1))
    #button_filtro_ico = ImageTk.PhotoImage(button_filtro_img)
    #button_filtro_ico_hover = ImageTk.PhotoImage(button_filtro_img_hover)
    #button_filtro = Button(Catalogo_Frame,image=button_filtro_ico, bg=B, borderwidth=0, command=buscar_producto)
    #button_filtro.place(relx=0.4, rely=.12, anchor=CENTER)
    #button_filtro.bind("<Enter>", lambda event: button_filtro.config(image=button_filtro_ico_hover))
    #button_filtro.bind("<Leave>", lambda event: button_filtro.config(image=button_filtro_ico))
    


    

    

    Button_Agregar_img = Image.open("Img/ADD_.png")
    Button_Agregar_img_hover = Image.open("Img/ADD_1.png")
    Button_Agregar_img = Button_Agregar_img.resize((Ximg_1, Yimg_1))
    Button_Agregar_img_hover = Button_Agregar_img_hover.resize((Ximg_1, Yimg_1))
    Button_Agregar_ico = ImageTk.PhotoImage(Button_Agregar_img)
    Button_Agregar_ico_hover = ImageTk.PhotoImage(Button_Agregar_img_hover)
    Button_Agregar = Button(Catalogo_Frame,image=Button_Agregar_ico, bg=B, borderwidth=0,command=agregar_producto)
    Button_Agregar.place(relx=0.80, rely=.39, anchor=CENTER)
    Button_Agregar.bind("<Enter>", lambda event: Button_Agregar.config(image=Button_Agregar_ico_hover))
    Button_Agregar.bind("<Leave>", lambda event: Button_Agregar.config(image=Button_Agregar_ico))
    


    Button_modificar_img = Image.open("Img/Edit.png")
    Button_modificar_img_hover = Image.open("Img/Edit1.png")
    Button_modificar_img = Button_modificar_img.resize((Ximg_1, Yimg_1))
    Button_modificar_img_hover = Button_modificar_img_hover.resize((Ximg_1, Yimg_1))
    Button_modificar_ico = ImageTk.PhotoImage(Button_modificar_img)
    Button_modificar_ico_hover = ImageTk.PhotoImage(Button_modificar_img_hover)
    Button_modificar = Button(Catalogo_Frame,image=Button_modificar_ico, bg=B, borderwidth=0, command=modificar_producto)
    Button_modificar.place(relx=0.85, rely=.39, anchor=CENTER)
    Button_modificar.bind("<Enter>", lambda event: Button_modificar.config(image=Button_modificar_ico_hover))
    Button_modificar.bind("<Leave>", lambda event: Button_modificar.config(image=Button_modificar_ico))

    
    Button_Eliminar_img = Image.open("Img/Delete_1.png")
    Button_Eliminar_img_hover = Image.open("Img/Delete_2.png")
    Button_Eliminar_img = Button_Eliminar_img.resize((Ximg_1, Yimg_1))
    Button_Eliminar_img_hover = Button_Eliminar_img_hover.resize((Ximg_1, Yimg_1))
    Button_Eliminar_ico = ImageTk.PhotoImage(Button_Eliminar_img)
    Button_Eliminar_ico_hover = ImageTk.PhotoImage(Button_Eliminar_img_hover)
    Button_Eliminar = Button(Catalogo_Frame,image=Button_Eliminar_ico, bg=B, borderwidth=0, command=eliminar_producto)
    Button_Eliminar.place(relx=0.89, rely=.39, anchor=CENTER)
    Button_Eliminar.bind("<Enter>", lambda event: Button_Eliminar.config(image=Button_Eliminar_ico_hover))
    Button_Eliminar.bind("<Leave>", lambda event: Button_Eliminar.config(image=Button_Eliminar_ico))
    

    crear_toggle_tema(Catalogo_Frame, 0.60, 0.15)
    


    columns = ("Nombre","Precio","Cantidad_Stock", "Categoria_id", "Color", "Modelo", "Talla", "Descripcion")
    tree = ttk.Treeview(Catalogo_Frame, columns=columns, show="headings")
    
    for col in columns: 
        tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))
        tree.column(col, anchor=CENTER, width=100)
    
    tree.pack(pady=20, expand=True)
    tree.place(x=20, rely=.2, width=800, height=450)

    # Botones de navegación
    global btn_anterior, btn_siguiente
    Botones_sobre_menu = Frame(Catalogo_Frame, width=500, height=50, bg=B)
    #Botones_sobre_menu.pack(fill=BOTH, expand=TRUE)
    Botones_sobre_menu.place(relx=.017, rely=.90, width=800)
    
    btn_siguiente_img = Image.open("Img/Next.png")
    btn_siguiente_img_hover = Image.open("Img/Next_1.png")
    btn_siguiente_img = btn_siguiente_img.resize((Ximg_1, Yimg_1))
    btn_siguiente_img_hover = btn_siguiente_img_hover.resize((Ximg_1, Yimg_1))
    btn_siguiente_ico = ImageTk.PhotoImage(btn_siguiente_img)
    btn_siguiente_ico_hover = ImageTk.PhotoImage(btn_siguiente_img_hover)
    btn_siguiente = Button(Botones_sobre_menu,image=btn_siguiente_ico, bg=B, borderwidth=0, command=siguiente_pagina)
    btn_siguiente.bind("<Enter>", lambda event: btn_siguiente.config(image=btn_siguiente_ico_hover))
    btn_siguiente.bind("<Leave>", lambda event: btn_siguiente.config(image=btn_siguiente_ico))

    btn_anterior_img = Image.open("Img/prev.png")
    btn_anterior_img_hover = Image.open("Img/prev_1.png")
    btn_anterior_img = btn_anterior_img.resize((Ximg_1, Yimg_1))
    btn_anterior_img_hover = btn_anterior_img_hover.resize((Ximg_1, Yimg_1))
    btn_anterior_ico = ImageTk.PhotoImage(btn_anterior_img)
    btn_anterior_ico_hover = ImageTk.PhotoImage(btn_anterior_img_hover)
    btn_anterior = Button(Botones_sobre_menu,image=btn_anterior_ico, bg=B, borderwidth=0, command=pagina_anterior)
    btn_anterior.bind("<Enter>", lambda event: btn_anterior.config(image=btn_anterior_ico_hover))
    btn_anterior.bind("<Leave>", lambda event: btn_anterior.config(image=btn_anterior_ico))


    global etiqueta_pagina
    etiqueta_pagina = Label(Catalogo_Frame, text="", background=B, foreground=L)
    etiqueta_pagina.pack(side=TOP, padx=20, pady=10)
    etiqueta_pagina.place(relx=0.32 , rely=.94)

    # Estilo para Treeview
    style = ttk.Style()
    style.theme_use("clam")  # Selecciona un tema base para personalizar
    style.configure("Treeview", background=B, foreground=L, rowheight=15,fieldbackground=B)
    style.map("Treeview", background=[('selected', '#3289c8')], foreground=[('selected', 'white')])
    style.configure("Treeview.Heading", background=B, foreground=L, borderwidth=0, relief="flat", font=('Arial', 8, 'bold'),)
    style.map("Treeview.Heading", background=[('selected', B)], foreground=[('selected', B)])
        
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor=CENTER,width=30, stretch=True)

        

    mostrar_productos_seleccionados()
    tree.bind("<<TreeviewSelect>>", seleccionar_producto)

# Función para seleccionar un producto de la tabla y mostrarlo en los campos de entrada
def seleccionar_producto(event):
    selected_items = tree.selection()
    
    # Verificar si hay algún elemento seleccionado
    if not selected_items:
        return mostrar_productos_seleccionados()
    selected_item = tree.selection()[0]
    producto = tree.item(selected_item, 'values')

    entry_nombre.delete(0, END)
    entry_nombre.insert(0, producto[0])

    entry_descripcion.delete(0, END)
    entry_descripcion.insert(0, producto[7])

    entry_precio.delete(0, END)
    entry_precio.insert(0, producto[1])

    entry_cantidad_stock.delete(0, END)
    entry_cantidad_stock.insert(0, producto[2])

    entry_codigo_barra.delete(0, END)
    entry_codigo_barra.insert(0, producto[9])

    entry_modelo.delete(0, END)
    entry_modelo.insert(0, producto[5])

    entry_color.delete(0, END)
    entry_color.insert(0, producto[4])

    entry_talla.delete(0, END)
    entry_talla.insert(0, producto[6])

    entry_material.delete(0, END)
    entry_material.insert(0, producto[8])

    entry_proveedor.delete(0, END)
    entry_proveedor.insert(0, producto[10])  # Nombre del proveedor

    entry_ubicacion.delete(0, END)
    entry_ubicacion.insert(0, producto[11])

    entry_categoria.delete(0, END)
    entry_categoria.insert(0, producto[3])  # Nombre de la categoría

    # Mostrar la imagen del producto seleccionado
    foto_path = producto[9]  # La columna 12 es la columna de la foto

    # Mostrar la imagen del producto seleccionado
    mostrar_imagen_producto(foto_path)

    tree.bind('<Button-1>', lambda event: limpiar_seleccion())

def limpiar_seleccion():
    entry_nombre.delete(0, END)
    entry_descripcion.delete(0, END)
    entry_precio.delete(0, END)
    entry_cantidad_stock.delete(0, END)
    entry_codigo_barra.delete(0, END)
    entry_modelo.delete(0, END)
    entry_color.delete(0, END)
    entry_talla.delete(0, END)
    entry_material.delete(0, END)
    entry_proveedor.delete(0, END)
    entry_ubicacion.delete(0, END)
    entry_categoria.delete(0, END)
    # Limpiar la imagen del producto
    limpiar_imagen_producto()

def limpiar_imagen_producto():
    global Imagen_Producto_Frame
    if 'Imagen_Producto_Frame' in globals():
        Imagen_Producto_Frame.destroy()

def cerrar_otras_pantallas():
    for nombre_frame in ('venta_frame', 'Catalogo_Frame', 'Historial_Frame', 'Reporte_Frame', 'Usuario_Frame'):
        if nombre_frame in globals():
            globals()[nombre_frame].destroy()

def historial_ventas():
    global Historial_Frame
    cerrar_otras_pantallas()
    global B, L
    Historial_Frame = Frame(home, width=x, height=y, bg=B)
    Historial_Frame.pack(fill=BOTH, expand=TRUE)

    Label(Historial_Frame, text="Historial de Ventas", fg="#3289c8", bg=B, font=("Comic Sans MS", 28), relief=GROOVE, borderwidth=0).place(relx=0.25, rely=.05, anchor=CENTER)

    Label(Historial_Frame, text="Filtrar:", bg=B, fg=L).place(relx=0.55, rely=.06, anchor=CENTER)
    filtro_ventas = ttk.Combobox(Historial_Frame, values=["Hoy", "Últimos 7 días", "Este mes", "Todo el historial"], state="readonly")
    filtro_ventas.set("Últimos 7 días")
    filtro_ventas.place(relx=0.68, rely=.06, anchor=CENTER, width=180)

    columns = ("Fecha", "Cliente", "Forma de pago", "Total", "Usuario")
    tree_ventas = ttk.Treeview(Historial_Frame, columns=columns, show="headings")
    for col in columns:
        tree_ventas.heading(col, text=col)
        tree_ventas.column(col, anchor=CENTER, width=140)
    tree_ventas.place(relx=0.03, rely=.15, width=850, height=350)

    label_total_periodo = Label(Historial_Frame, text="", bg=B, fg=L, font=("Arial", 12, "bold"))
    label_total_periodo.place(relx=0.03, rely=.62)

    def cargar_ventas():
        for fila in tree_ventas.get_children():
            tree_ventas.delete(fila)

        opcion = filtro_ventas.get()
        condicion = ""
        if opcion == "Hoy":
            condicion = "WHERE DATE(fecha) = CURDATE()"
        elif opcion == "Últimos 7 días":
            condicion = "WHERE fecha >= NOW() - INTERVAL 7 DAY"
        elif opcion == "Este mes":
            condicion = "WHERE MONTH(fecha) = MONTH(NOW()) AND YEAR(fecha) = YEAR(NOW())"

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(f"SELECT fecha, cliente_nombre, forma_pago, total, usuario FROM ventas {condicion} ORDER BY fecha DESC")
            filas = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial: {e}")
            return

        total_periodo = 0
        for fila in filas:
            tree_ventas.insert("", "end", values=fila)
            total_periodo += float(fila[3])

        label_total_periodo.config(text=f"Total del periodo: ${total_periodo:.2f}   |   Ventas: {len(filas)}")

    filtro_ventas.bind("<<ComboboxSelected>>", lambda event: cargar_ventas())
    cargar_ventas()

def reporte_stock():
    global Reporte_Frame
    cerrar_otras_pantallas()
    global B, L
    Reporte_Frame = Frame(home, width=x, height=y, bg=B)
    Reporte_Frame.pack(fill=BOTH, expand=TRUE)

    Label(Reporte_Frame, text="Reporte de Stock", fg="#3289c8", bg=B, font=("Comic Sans MS", 28), relief=GROOVE, borderwidth=0).place(relx=0.25, rely=.05, anchor=CENTER)

    Label(Reporte_Frame, text="Stock mínimo de alerta:", bg=B, fg=L).place(relx=0.55, rely=.06, anchor=CENTER)
    entry_umbral = Entry(Reporte_Frame, width=6)
    entry_umbral.insert(0, "10")
    entry_umbral.place(relx=0.70, rely=.06, anchor=CENTER)

    columns = ("Producto", "Categoria", "Stock actual", "Precio", "Valor en inventario")
    tree_reporte = ttk.Treeview(Reporte_Frame, columns=columns, show="headings")
    for col in columns:
        tree_reporte.heading(col, text=col)
        tree_reporte.column(col, anchor=CENTER, width=150)
    tree_reporte.tag_configure("bajo_stock", background="#f5b7b1")
    tree_reporte.place(relx=0.03, rely=.15, width=900, height=400)

    label_resumen = Label(Reporte_Frame, text="", bg=B, fg=L, font=("Arial", 12, "bold"))
    label_resumen.place(relx=0.03, rely=.68)

    def cargar_reporte():
        for fila in tree_reporte.get_children():
            tree_reporte.delete(fila)
        try:
            umbral = int(entry_umbral.get())
        except ValueError:
            umbral = 10

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.nombre, c.nombre, p.cantidad_stock, p.precio
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                ORDER BY p.cantidad_stock ASC
            """)
            filas = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")
            return

        valor_total = 0
        bajo_stock_count = 0
        for nombre, categoria, stock, precio in filas:
            valor = float(precio) * stock
            valor_total += valor
            etiquetas = ("bajo_stock",) if stock <= umbral else ()
            if stock <= umbral:
                bajo_stock_count += 1
            tree_reporte.insert("", "end", values=(nombre, categoria, stock, f"${precio}", f"${valor:.2f}"), tags=etiquetas)

        label_resumen.config(text=f"Valor total en inventario: ${valor_total:.2f}   |   Productos con stock bajo: {bajo_stock_count}")

    Button(Reporte_Frame, text="Actualizar", command=cargar_reporte, bg="#3289c8", fg="white").place(relx=0.85, rely=.06, anchor=CENTER)

    cargar_reporte()

def mostrar_usuario():
    global Usuario_Frame
    cerrar_otras_pantallas()
    global B, L
    Usuario_Frame = Frame(home, width=x, height=y, bg=B)
    Usuario_Frame.pack(fill=BOTH, expand=TRUE)

    Label(Usuario_Frame, text="Usuario en sesión", fg="#3289c8", bg=B, font=("Comic Sans MS", 28), relief=GROOVE, borderwidth=0).place(relx=0.5, rely=.15, anchor=CENTER)
    Label(Usuario_Frame, text=usuario_actual, fg=L, bg=B, font=("Arial", 22, "bold")).place(relx=0.5, rely=.28, anchor=CENTER)

    label_tiempo = Label(Usuario_Frame, text="", fg=L, bg=B, font=("Arial", 14))
    label_tiempo.place(relx=0.5, rely=.36, anchor=CENTER)

    def actualizar_tiempo():
        if not label_tiempo.winfo_exists():
            return
        transcurrido = datetime.now() - hora_inicio_sesion
        horas, resto = divmod(int(transcurrido.total_seconds()), 3600)
        minutos, segundos = divmod(resto, 60)
        label_tiempo.config(text=f"Tiempo conectado: {horas:02d}:{minutos:02d}:{segundos:02d}")
        Usuario_Frame.after(1000, actualizar_tiempo)

    actualizar_tiempo()

    def cerrar_sesion_app():
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar la sesión y salir?"):
            menu.destroy()

    boton_salir = Button(Usuario_Frame, text="Cerrar sesión", fg="white", bg="#c0392b", font=("Arial", 12), relief=GROOVE, borderwidth=0, command=cerrar_sesion_app)
    boton_salir.place(relx=0.5, rely=.45, anchor=CENTER, width=160, height=35)


# Botones del menú
catalogo_img = Image.open("Img/Catalogo.png")
catalogo_img = catalogo_img.resize((Ximg, Yimg))  # Reducir el tamaño de la imagen
catalogo_ico = ImageTk.PhotoImage(catalogo_img)  # Convertir la imagen a un objeto PhotoImage
button_catalogo = Button(menu_frame, image=catalogo_ico, bg="#163e64", borderwidth=0, command=catalogo)
button_catalogo.pack(pady=10, padx=10, expand=TRUE)
button_catalogo.bind("<Enter>", lambda event: button_catalogo.config(bg="#3289c8"))
button_catalogo.bind("<Leave>", lambda event: button_catalogo.config(bg="#163e64"))



def agregar_cliente_venta():
    ventana_cliente = Toplevel(menu)
    ventana_cliente.title("Agregar cliente")
    ventana_cliente.geometry("300x160")
    ventana_cliente.config(bg=B)

    Label(ventana_cliente, text="Nombre del cliente:", bg=B, fg=L).pack(pady=(20, 5))
    entry_cliente = Entry(ventana_cliente, font=("Arial", 12))
    entry_cliente.pack(pady=5)
    if cliente_actual["nombre"]:
        entry_cliente.insert(0, cliente_actual["nombre"])

    def guardar_cliente():
        nombre = entry_cliente.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresa un nombre de cliente")
            return
        cliente_actual["nombre"] = nombre
        label_cliente_venta.config(text=f"Cliente: {nombre}")
        ventana_cliente.destroy()

    def quitar_cliente():
        cliente_actual["nombre"] = None
        label_cliente_venta.config(text="Cliente: General")
        ventana_cliente.destroy()

    Button(ventana_cliente, text="Guardar", command=guardar_cliente, bg="#3289c8", fg="white").pack(pady=10)
    Button(ventana_cliente, text="Venta sin cliente", command=quitar_cliente, bg=B, fg=L).pack()

def finalizar_venta():
    if not carrito:
        messagebox.showerror("Error", "El carrito está vacío")
        return

    forma_pago = combobox_Forma_Pago.get()
    if forma_pago not in ("Tarjeta", "Efectivo"):
        messagebox.showerror("Error", "Selecciona una forma de pago")
        return

    detalle = []
    total = 0
    for nombre, datos in carrito.items():
        cantidad = datos['cantidad_var'].get()
        try:
            precio_num = float(str(datos['precio']).replace("$", ""))
        except ValueError:
            precio_num = 0
        subtotal = precio_num * cantidad
        total += subtotal
        detalle.append((nombre, cantidad, precio_num, subtotal))

    cliente_nombre = cliente_actual["nombre"] or "Cliente general"

    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ventas (fecha, total, forma_pago, cliente_nombre, usuario) VALUES (%s, %s, %s, %s, %s)",
            (datetime.now(), total, forma_pago, cliente_nombre, usuario_actual)
        )
        venta_id = cursor.lastrowid
        for nombre, cantidad, precio_num, subtotal in detalle:
            cursor.execute(
                "INSERT INTO venta_detalle (venta_id, nombre_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                (venta_id, nombre, cantidad, precio_num, subtotal)
            )
            cursor.execute(
                "UPDATE productos SET cantidad_stock = cantidad_stock - %s WHERE nombre = %s",
                (cantidad, nombre)
            )
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"No se pudo registrar la venta: {e}")
        return

    for datos in list(carrito.values()):
        datos['frame'].destroy()
    carrito.clear()
    actualizar_scrollregion()
    cliente_actual["nombre"] = None
    label_cliente_venta.config(text="Cliente: General")
    combobox_Forma_Pago.set("Formas de pago")

    messagebox.showinfo("Pago realizado", f"Venta finalizada con éxito.\nTotal: ${total:.2f}\nForma de pago: {forma_pago}")

def venta():
    global venta_frame, botones_sig_ant_Frame
    cerrar_otras_pantallas()
    global B, L
    venta_frame = Frame(home, width=x, height=y, bg=B)
    venta_frame.pack(fill=BOTH, expand=TRUE)

    Venta_Frame_title = Label(venta_frame, text="Ventas", fg="#3289c8", bg=B, font=("Comic Sans MS", 28), relief=GROOVE, borderwidth=0)
    Venta_Frame_title.place(relx=0.25, rely=.05, anchor=CENTER)


    
    global  entry_buscar


    # Añadir entradas y botones para filtrado y ordenamiento
    entry_buscar = Entry(venta_frame)
    entry_buscar.config( font=("Arial", 12), borderwidth=0, relief="ridge", highlightthickness=1, highlightcolor=BgBorde_button, highlightbackground=BgBorde_button_C)
    entry_buscar.place(relx=0.50, rely=.08, anchor=CENTER, width=300)

    button_buscar_img = Image.open("Img/Buscar.png")
    button_buscar_img_hover = Image.open("Img/Buscar_1.png")
    button_buscar_img = button_buscar_img.resize((Ximg_1, Yimg_1))
    button_buscar_img_hover = button_buscar_img_hover.resize((Ximg_1, Yimg_1))
    button_buscar_ico = ImageTk.PhotoImage(button_buscar_img)
    button_buscar_ico_hover = ImageTk.PhotoImage(button_buscar_img_hover)
    button_buscar = Button(venta_frame,image=button_buscar_ico, bg=B, borderwidth=0)#, command=buscar_producto)
    button_buscar.place(relx=0.65, rely=.08, anchor=CENTER)
    button_buscar.bind("<Enter>", lambda event: button_buscar.config(image=button_buscar_ico_hover))
    button_buscar.bind("<Leave>", lambda event: button_buscar.config(image=button_buscar_ico))
    
    Y1=0.43
    X1=0.73
    Ex1=0.84
    global Carrito_frame_buttons
    Carrito_frame_buttons = Frame(venta_frame, width=400, height=600, bg=B, highlightbackground=B, highlightthickness=2)
    Carrito_frame_buttons.place(relx=.012, rely=.10)
    Carrito_frame_buttons.pack_propagate(False)
    global Carrito_frame
    Carrito_frame = Frame(venta_frame, width=370, height=400, bg=B, highlightbackground=B, highlightthickness=2)
    Carrito_frame.place(relx=.0125, rely=.20)
    #Carrito_frame.pack_propagate(False)

    # Canvas y Scrollbar
    global Carrito_frame_canvas
    Carrito_frame_canvas = Canvas(Carrito_frame, width=370, height=400, bg=B, highlightbackground=B, highlightthickness=2)
    Carrito_frame_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(Carrito_frame, orient=VERTICAL, command=Carrito_frame_canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    Carrito_frame_canvas.config(yscrollcommand=scrollbar.set)

    global Carrito_frame_productos
    Carrito_frame_productos = Frame(Carrito_frame_canvas, bg=B)
    Carrito_frame_canvas.create_window((0, 0), window=Carrito_frame_productos, anchor="nw")

    # Actualizar la vista del canvas
    actualizar_scrollregion()


    button_Agregar_Cliente_img = Image.open("Img/add1.png")
    button_Agregar_Cliente_img_hover = Image.open("Img/add1_1.png")
    button_Agregar_Cliente_img = button_Agregar_Cliente_img.resize((Ximg_1, Yimg_1))
    button_Agregar_Cliente_img_hover = button_Agregar_Cliente_img_hover.resize((Ximg_1, Yimg_1))
    button_Agregar_Cliente_ico = ImageTk.PhotoImage(button_Agregar_Cliente_img)
    button_Agregar_Cliente_ico_hover = ImageTk.PhotoImage(button_Agregar_Cliente_img_hover)
    button_Agregar_Cliente = Button(Carrito_frame_buttons,image=button_Agregar_Cliente_ico, bg=B, borderwidth=0, command=agregar_cliente_venta)
    button_Agregar_Cliente.place(relx=0.05, rely=.05, anchor=CENTER)
    button_Agregar_Cliente.bind("<Enter>", lambda event: button_Agregar_Cliente.config(image=button_Agregar_Cliente_ico_hover))
    button_Agregar_Cliente.bind("<Leave>", lambda event: button_Agregar_Cliente.config(image=button_Agregar_Cliente_ico))

    global label_cliente_venta
    label_cliente_venta = Label(Carrito_frame_buttons, text=f"Cliente: {cliente_actual['nombre'] or 'General'}", bg=B, fg=L, font=("Arial", 9))
    label_cliente_venta.place(relx=0.30, rely=.05, anchor=CENTER)

    

    # Crear el Combobox para las opciones de forma de pago
    global combobox_Forma_Pago
    options = ["Tarjeta", "Efectivo"]
    combobox_Forma_Pago = ttk.Combobox(Carrito_frame_buttons, values=options, font=("Arial", 12))
    combobox_Forma_Pago.set("Formas de pago")  # Leyenda por defecto
    combobox_Forma_Pago.place(relx=0.24, rely=.82, anchor=tk.CENTER, width=180)

    button_Eliminar_carrito_img = Image.open("Img/Delete_1.png")
    button_Eliminar_carrito_img_hover = Image.open("Img/Delete_2.png")
    button_Eliminar_carrito_img = button_Eliminar_carrito_img.resize((60, 60))
    button_Eliminar_carrito_img_hover = button_Eliminar_carrito_img_hover.resize((Ximg_1, Yimg_1))
    button_Eliminar_carrito_ico = ImageTk.PhotoImage(button_Eliminar_carrito_img)
    button_Eliminar_carrito_ico_hover = ImageTk.PhotoImage(button_Eliminar_carrito_img_hover)
    button_Eliminar_carrito = Button(Carrito_frame_buttons,image=button_Eliminar_carrito_ico, bg=B, borderwidth=0, command=eliminar_seleccionados_carrito)
    button_Eliminar_carrito.place(relx=0.09, rely=.92, anchor=CENTER)
    button_Eliminar_carrito.bind("<Enter>", lambda event: button_Eliminar_carrito.config(image=button_Eliminar_carrito_ico_hover))
    button_Eliminar_carrito.bind("<Leave>", lambda event: button_Eliminar_carrito.config(image=button_Eliminar_carrito_ico))

    button_Imprimer_img = Image.open("Img/Print.png")
    button_Imprimer_img_hover = Image.open("Img/Print_1.png")
    button_Imprimer_img = button_Imprimer_img.resize((60, 60))
    button_Imprimer_img_hover = button_Imprimer_img_hover.resize((Ximg_1, Yimg_1))
    button_Imprimer_ico = ImageTk.PhotoImage(button_Imprimer_img)
    button_Imprimer_ico_hover = ImageTk.PhotoImage(button_Imprimer_img_hover)
    button_Imprimer = Button(Carrito_frame_buttons,image=button_Imprimer_ico, bg=B, borderwidth=0)#, command=buscar_producto)
    button_Imprimer.place(relx=0.29, rely=.92, anchor=CENTER)
    button_Imprimer.bind("<Enter>", lambda event: button_Imprimer.config(image=button_Imprimer_ico_hover))
    button_Imprimer.bind("<Leave>", lambda event: button_Imprimer.config(image=button_Imprimer_ico))

    button_Finalizar_img = Image.open("Img/Done.png")
    button_Finalizar_img_hover = Image.open("Img/Done_1.png")
    button_Finalizar_img = button_Finalizar_img.resize((150, 50))
    button_Finalizar_img_hover = button_Finalizar_img_hover.resize((150, 50))
    button_Finalizar_ico = ImageTk.PhotoImage(button_Finalizar_img)
    button_Finalizar_ico_hover = ImageTk.PhotoImage(button_Finalizar_img_hover)
    button_Finalizar = Button(Carrito_frame_buttons,image=button_Finalizar_ico, bg=B, borderwidth=0, command=finalizar_venta)
    button_Finalizar.place(relx=0.75, rely=.93, anchor=CENTER)
    button_Finalizar.bind("<Enter>", lambda event: button_Finalizar.config(image=button_Finalizar_ico_hover))
    button_Finalizar.bind("<Leave>", lambda event: button_Finalizar.config(image=button_Finalizar_ico))


    mostrar_productos_galeria()


 

venta_img = Image.open("Img/venta.png")
venta_img = venta_img.resize((Ximg, Yimg))  # Reducir el tamaño de la imagen
venta_ico = ImageTk.PhotoImage(venta_img)  # Convertir la imagen a un objeto PhotoImage
button_venta = Button(menu_frame, image=venta_ico, bg="#163e64", borderwidth=0, command=venta)
button_venta.pack(pady=10, padx=10, expand=TRUE)
button_venta.bind("<Enter>", lambda event: button_venta.config(bg="#3289c8"))
button_venta.bind("<Leave>", lambda event: button_venta.config(bg="#163e64"))



ventas_img = Image.open("Img/Ventas.png")
ventas_img = ventas_img.resize((Ximg, Yimg))  # Reducir el tamaño de la imagen
ventas_ico = ImageTk.PhotoImage(ventas_img)  # convertir la imagen en un objeto PhotoImage
button_ventas = Button(menu_frame, image=ventas_ico, bg="#163e64", borderwidth=0, command=historial_ventas)
button_ventas.pack(pady=10, padx=10, expand=TRUE)
button_ventas.bind("<Enter>", lambda event: button_ventas.config(bg="#3289c8"))
button_ventas.bind("<Leave>", lambda event: button_ventas.config(bg="#163e64"))

reportes_img = Image.open("Img/Reportes.png")
reportes_img = reportes_img.resize((Ximg, Yimg))  # Reducir el tamaño de la imagen
reportes_ico = ImageTk.PhotoImage(reportes_img)  # convertir la imagen en un objeto PhotoImage
button_reportes = Button(menu_frame, image=reportes_ico, bg="#163e64", borderwidth=0, command=reporte_stock)
button_reportes.pack(pady=10, padx=10, expand=TRUE)
button_reportes.bind("<Enter>", lambda event: button_reportes.config(bg="#3289c8"))
button_reportes.bind("<Leave>", lambda event: button_reportes.config(bg="#163e64"))

Usuario_PFP_img = Image.open("Img/Usuario.png")
Usuario_PFP_img = Usuario_PFP_img.resize((Ximg, Yimg))  # Reducir el tamaño de la imagen
Usuario_PFP_ico = ImageTk.PhotoImage(Usuario_PFP_img)  # convertir la imagen en un objeto PhotoImage
button_Usuario_PFP = Button(menu_frame, image=Usuario_PFP_ico, bg="#163e64", borderwidth=0, command=mostrar_usuario)
button_Usuario_PFP.pack(pady=10, padx=10, expand=TRUE)
button_Usuario_PFP.bind("<Enter>", lambda event: button_Usuario_PFP.config(bg="#3289c8"))
button_Usuario_PFP.bind("<Leave>", lambda event: button_Usuario_PFP.config(bg="#163e64"))

menu.mainloop()