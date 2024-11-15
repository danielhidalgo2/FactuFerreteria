import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import A5
from reportlab.lib.pagesizes import landscape
import os
from ttkthemes import ThemedTk
import tkinter.font as font
from tkinter import PhotoImage  # Para manejar los íconos


# =================== BASE DE DATOS =================== #
def conectar_db():
    """Conecta o crea la base de datos en un directorio fijo."""
    ruta_db = os.path.join(os.path.expanduser("~"), "ferreteria.db")
    return sqlite3.connect(ruta_db)


def crear_tablas():
    """Crea las tablas de la base de datos si no existen."""
    conn = conectar_db()
    cursor = conn.cursor()

    # Crear la tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            codigo TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            cantidad INTEGER DEFAULT 0
        )
    ''')

    # Crear la tabla de historial de transacciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_factura INTEGER,
            tipo TEXT NOT NULL,
            producto TEXT,
            cantidad INTEGER,
            precio REAL,
            total REAL,
            fecha TEXT
        )
    ''')

    # Crear la tabla de facturas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            id_factura INTEGER PRIMARY KEY,
            cliente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            total REAL NOT NULL
        )
    ''')
    
    # Crear la tabla de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacion_fiscal TEXT NOT NULL,
            nombre_fiscal TEXT NOT NULL,
            nombre_comercial TEXT,
            direccion TEXT,
            codigo_postal TEXT,
            poblacion TEXT,
            provincia TEXT,
            pais TEXT,
            telefono TEXT
        )
    ''')


    conn.commit()
    conn.close()



# =================== FUNCIONES PARA FACTURAS =================== #
def registrar_factura(id_factura, cliente, fecha, total):
    """Registra una factura en la base de datos."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO facturas (id_factura, cliente, fecha, total) 
        VALUES (?, ?, ?, ?)
    ''', (id_factura, cliente, fecha, total))
    conn.commit()
    conn.close()  # Asegúrate de cerrar la conexión


def obtener_facturas(cliente='', producto='', fecha=''):
    """Obtiene el historial de facturas filtrado por cliente, producto o fecha."""
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT id_factura, cliente, fecha, total FROM facturas WHERE 1=1"
    params = []

    if cliente:
        query += " AND cliente LIKE ?"
        params.append(f"%{cliente}%")
    if producto:
        query += " AND id_factura IN (SELECT id_factura FROM historial WHERE producto LIKE ?)"
        params.append(f"%{producto}%")
    if fecha:
        query += " AND fecha LIKE ?"
        params.append(f"%{fecha}%")

    cursor.execute(query, params)
    facturas = cursor.fetchall()
    conn.close()
    return facturas



# =================== FUNCIONES PARA EL HISTORIAL =================== #
def registrar_transaccion(id_factura, tipo, producto, cantidad, precio, total, fecha):
    """Registra una transacción en el historial."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO historial (id_factura, tipo, producto, cantidad, precio, total, fecha) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (id_factura, tipo, producto, cantidad, precio, total, fecha))
    conn.commit()
    conn.close()

def obtener_historial():
    """Obtiene el historial de transacciones."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_factura, tipo, producto, cantidad, precio, total, fecha FROM historial ORDER BY fecha DESC")
    historial = cursor.fetchall()
    conn.close()
    return historial

def generar_id_factura():
    """Genera un nuevo ID único para las facturas."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id_factura) FROM facturas")
    max_id = cursor.fetchone()[0]
    conn.close()
    return (max_id or 0) + 1

# =================== FUNCIONES PARA GESTIÓN DE PRODUCTOS =================== #
def actualizar_stock(producto_id, cantidad_vendida):
    """Actualiza el stock de un producto tras una venta."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT cantidad FROM productos WHERE id= ?", (producto_id,))
    cantidad_actual = cursor.fetchone()[0]
    nueva_cantidad = cantidad_actual - cantidad_vendida
    cursor.execute("UPDATE productos SET cantidad=? WHERE id=?", (nueva_cantidad, producto_id))
    conn.commit()
    conn.close()

def añadir_producto(nombre, codigo, descripcion, precio, cantidad):
    """Añade un producto a la base de datos."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO productos (nombre, codigo, descripcion, precio, cantidad) VALUES (?, ?, ?, ?, ?)
    ''', (nombre, codigo, descripcion, precio, cantidad))
    conn.commit()
    conn.close()

def modificar_producto(id, nombre, codigo, descripcion, precio, cantidad):
    """Modifica un producto existente en la base de datos."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE productos SET nombre=?, codigo=?, descripcion=?, precio=?, cantidad=? WHERE id=?
    ''', (nombre, codigo, descripcion, precio, cantidad, id))
    conn.commit()
    conn.close()

def eliminar_producto(id):
    """Elimina un producto de la base de datos por su ID."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id=?', (id,))
    conn.commit()
    conn.close()

def obtener_productos():
    """Obtiene todos los productos de la base de datos."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

# =================== FUNCIONES PARA CLIENTES =================== #

def añadir_cliente(identificacion_fiscal, nombre_fiscal, nombre_comercial, direccion, codigo_postal, poblacion, provincia, pais, telefono):
    """Añade un cliente a la base de datos."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clientes (identificacion_fiscal, nombre_fiscal, nombre_comercial, direccion, codigo_postal, poblacion, provincia, pais, telefono) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (identificacion_fiscal, nombre_fiscal, nombre_comercial, direccion, codigo_postal, poblacion, provincia, pais, telefono))
    conn.commit()
    conn.close()

def obtener_clientes():
    """Obtiene todos los clientes de la base de datos."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def eliminar_cliente(id_cliente):
    """Elimina un cliente de la base de datos por su ID."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE id_cliente=?', (id_cliente,))
    conn.commit()
    conn.close()



# =================== INTERFAZ GRÁFICA =================== #
def crear_ventana_principal():
    """Crea la ventana principal de la aplicación."""
    crear_tablas()
    ventana = ThemedTk(theme="breeze")  # Puedes probar otros temas como 'arc', 'clam', etc.
    ventana.title("Sistema de Facturación Profesional")
    ventana.geometry("1024x768")
    style = ttk.Style()
    style.configure("TButton", padding=8, font=('Arial', 12, 'bold'), background='#4CAF50', foreground='white')
    style.configure("TLabel", font=('Arial', 12, 'bold'), foreground='#333333', background='#f5f5f5')
    style.configure("TEntry", padding=5, font=('Arial', 11), background='#f5f5f5')
    ventana.configure(bg="#f5f5f5")  # Fondo de la ventana principal


    notebook = ttk.Notebook(ventana)
    notebook.pack(expand=True, fill='both')

    menu_bar = tk.Menu(ventana)
    ventana.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Salir", command=ventana.quit)
    menu_bar.add_cascade(label="Archivo", menu=file_menu)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Acerca de", command=lambda: messagebox.showinfo("Acerca de", "Sistema de Facturación Profesional v2.0"))
    menu_bar.add_cascade(label="Ayuda", menu=help_menu)
    
    status_bar = tk.Label(ventana, text="Listo", bd=1, relief="sunken", anchor="w")
    status_bar.pack(side="bottom", fill="x")

    def update_status(text):
        status_bar.config(text=text)



    # =================== PESTAÑA DE HISTORIAL DE FACTURAS =================== #
    tab_historial_facturas = ttk.Frame(notebook)
    notebook.add(tab_historial_facturas, text="Historial de Facturación")
    notebook.pack(expand=True, fill='both', padx=10, pady=10)


    # Marco de búsqueda
    search_frame = tk.Frame(tab_historial_facturas)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Buscar por Cliente:").grid(row=0, column=0)
    entry_cliente = tk.Entry(search_frame)
    entry_cliente.grid(row=0, column=1)

    tk.Label(search_frame, text="Buscar por Producto:").grid(row=1, column=0)
    entry_producto = tk.Entry(search_frame)
    entry_producto.grid(row=1, column=1)

    tk.Label(search_frame, text="Buscar por Fecha (YYYY-MM-DD):").grid(row=2, column=0)
    entry_fecha = tk.Entry(search_frame)
    entry_fecha.grid(row=2, column=1)

    # Tabla para mostrar facturas
    columnas_facturas = ('ID Factura', 'Cliente', 'Fecha', 'Total')
    tree_facturas = ttk.Treeview(tab_historial_facturas, columns=columnas_facturas, show='headings')
    for col in columnas_facturas:
        tree_facturas.heading(col, text=col)
        tree_facturas.column(col, width=150)
    tree_facturas.pack(expand=True, fill='both')

    # Función de búsqueda
    def buscar_facturas():
        cliente = entry_cliente.get().strip()
        producto = entry_producto.get().strip()
        fecha = entry_fecha.get().strip()

        facturas = obtener_facturas(cliente, producto, fecha)

        # Limpiar la tabla
        tree_facturas.delete(*tree_facturas.get_children())

        # Mostrar resultados
        for factura in facturas:
            tree_facturas.insert('', 'end', values=factura)

    btn_buscar = tk.Button(search_frame, text="Buscar", command=buscar_facturas)
    btn_buscar.grid(row=3, column=1, pady=10)
    
    
    # =================== PESTAÑA DE HISTORIAL =================== #
    tab_historial = ttk.Frame(notebook)
    notebook.add(tab_historial, text="Historial de Transacciones")

    columnas_historial = ('ID Factura', 'Tipo', 'Producto', 'Cantidad', 'Precio', 'Total', 'Fecha')
    tree_historial = ttk.Treeview(tab_historial, columns=columnas_historial, show='headings')
    for col in columnas_historial:
        tree_historial.heading(col, text=col)
        tree_historial.column(col, width=100 if col == 'ID Factura' else 150)
    tree_historial.pack(expand=True, fill='both')

    def cargar_historial():
        tree_historial.delete(*tree_historial.get_children())
        for transaccion in obtener_historial():
            tree_historial.insert('', 'end', values=transaccion)

    cargar_historial()
    # =================== PESTAÑA DE PRODUCTOS =================== #
    tab_productos = ttk.Frame(notebook)
    notebook.add(tab_productos, text="Productos")
    form_frame = tk.Frame(tab_productos, bg="#f0f0f0", bd=2, relief="groove")
    form_frame.pack(pady=10, padx=5)


    # Marco de búsqueda
    search_frame = tk.Frame(tab_productos)
    search_frame.pack(pady=10)
    tk.Label(search_frame, text="Buscar Producto:", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=5)
    entry_busqueda = tk.Entry(search_frame, font=('Arial', 12), width=25)
    entry_busqueda.grid(row=0, column=1, padx=5)

    # Función de búsqueda
    def buscar_productos():
        search_term = entry_busqueda.get().strip()
        tree.delete(*tree.get_children())
        for producto in obtener_productos():
            if search_term.lower() in producto[1].lower() or search_term in producto[2]:
                tree.insert('', 'end', values=producto)

    # Botón "Buscar" mejorado
    btn_buscar = tk.Button(search_frame, text="Buscar", command=buscar_productos, font=('Arial', 12, 'bold'),
                        bg='#4CAF50', fg='white', activebackground='#45a049', activeforeground='white',
                        relief="raised", padx=10, pady=5)
    btn_buscar.grid(row=0, column=2, padx=10)


    # =================== Tabla de Productos =================== #
    columnas = ('ID', 'Nombre', 'Código', 'Descripción', 'Precio', 'Cantidad')
    tree = ttk.Treeview(tab_productos, columns=columnas, show='headings')
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(expand=True, fill='both')

    # Cargar productos en la tabla
    def cargar_productos():
        tree.delete(*tree.get_children())
        for producto in obtener_productos():
            tree.insert('', 'end', values=producto)

    cargar_productos()


    # Crear campos de entrada para los detalles del producto
    labels = ["Nombre", "Código", "Descripción", "Precio", "Cantidad"]
    entries = {}
    for i, text in enumerate(labels):
        tk.Label(form_frame, text=text + ":", font=('Arial', 12)).grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(form_frame, font=('Arial', 12))
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[text] = entry

    # Botones de acción
    def agregar_producto():
        try:
            nombre = entries["Nombre"].get().strip()
            codigo = entries["Código"].get().strip()
            descripcion = entries["Descripción"].get().strip()
            precio = float(entries["Precio"].get().strip())
            cantidad = int(entries["Cantidad"].get().strip())
            if not nombre or not codigo:
                messagebox.showerror("Error", "El nombre y código no pueden estar vacíos.")
                return
            añadir_producto(nombre, codigo, descripcion, precio, cantidad)
            messagebox.showinfo("Éxito", "Producto añadido correctamente.")
            cargar_productos()
        except ValueError:
            messagebox.showerror("Error", "Revisa los campos de precio y cantidad.")
    def modificar_producto_seleccionado():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Por favor, selecciona un producto para modificar.")
            return

        producto = tree.item(selected_item[0], 'values')
        try:
            nombre = entries['Nombre'].get().strip()
            codigo = entries['Código'].get().strip()
            descripcion = entries['Descripción'].get().strip()
            precio = float(entries['Precio'].get().strip())
            cantidad = int(entries['Cantidad'].get().strip())
            modificar_producto(producto[0], nombre, codigo, descripcion, precio, cantidad)
            messagebox.showinfo("Éxito", "Producto modificado correctamente.")
            limpiar_campos()
            cargar_productos()
        except ValueError:
            messagebox.showwarning("Error", "Revisa los campos, el precio y la cantidad deben ser números.")

    def eliminar_producto_seleccionado():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Por favor, selecciona un producto para eliminar.")
            return

        producto = tree.item(selected_item[0], 'values')
        respuesta = messagebox.askyesno("Confirmar eliminación", f"¿Está seguro de que desea eliminar el producto {producto[1]}?")
        if respuesta:
            eliminar_producto(producto[0])
            messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            cargar_productos()
            update_status("Producto eliminado.")


    def limpiar_campos():
        for entry in entries.values():
            entry.delete(0, tk.END)

    btn_agregar = tk.Button(tab_productos, text="Agregar Producto Manualmente", command=agregar_producto)
    btn_agregar.pack(pady=10)

    btn_modificar = tk.Button(tab_productos, text="Modificar Producto", command=modificar_producto_seleccionado)
    btn_modificar.pack(pady=5)

    btn_eliminar = tk.Button(tab_productos, text="Eliminar Producto", command=eliminar_producto_seleccionado)
    btn_eliminar.pack(pady=5)

    # Añadir funcionalidad de escaneo de código de barras
    def escanear_codigo():
        # Solicitar el código de barras mediante un cuadro de diálogo
        codigo = tk.simpledialog.askstring("Escanear Código", "Introduce el código de barras:")
        if codigo:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo,))
            producto = cursor.fetchone()
            conn.close()

            if producto:
                # Mostrar los detalles del producto si existe
                entries['Nombre'].delete(0, tk.END)
                entries['Código'].delete(0, tk.END)
                entries['Descripción'].delete(0, tk.END)
                entries['Precio'].delete(0, tk.END)
                entries['Cantidad'].delete(0, tk.END)

                entries['Nombre'].insert(0, producto[1])
                entries['Código'].insert(0, producto[2])
                entries['Descripción'].insert(0, producto[3])
                entries['Precio'].insert(0, producto[4])
                entries['Cantidad'].insert(0, producto[5])
            else:
                # Preguntar si se desea crear un nuevo producto si el código no existe
                respuesta = messagebox.askyesno("Producto no encontrado", "No existe un producto con este código de barras. ¿Quieres crearlo?")
                if respuesta:
                    # Llenar el campo del código de barras con el valor escaneado
                    entries['Código'].delete(0, tk.END)
                    entries['Código'].insert(0, codigo)
                    # Limpia los demás campos para que se pueda crear el producto
                    entries['Nombre'].delete(0, tk.END)
                    entries['Descripción'].delete(0, tk.END)
                    entries['Precio'].delete(0, tk.END)
                    entries['Cantidad'].delete(0, tk.END)
                    messagebox.showinfo("Nuevo producto", "Introduce los datos para crear el nuevo producto y luego presiona 'Agregar Producto Manualmente'.")
                    # Botón para escanear el código de barras
    btn_escanear_codigo = tk.Button(tab_productos, text="Escanear Código de Barras", command=escanear_codigo)
    btn_escanear_codigo.pack(pady=5)



    def seleccionar_producto(event):
        selected_item = tree.selection()
        if not selected_item:
            return

        producto = tree.item(selected_item[0], 'values')
        entries['Nombre'].delete(0, tk.END)
        entries['Código'].delete(0, tk.END)
        entries['Descripción'].delete(0, tk.END)
        entries['Precio'].delete(0, tk.END)
        entries['Cantidad'].delete(0, tk.END)

        entries['Nombre'].insert(0, producto[1])
        entries['Código'].insert(0, producto[2])
        entries['Descripción'].insert(0, producto[3])
        entries['Precio'].insert(0, producto[4])
        entries['Cantidad'].insert(0, producto[5])

    tree.bind('<ButtonRelease-1>', seleccionar_producto)
    
    # =================== FUNCIONES PARA ACTUALIZACIÓN DE STOCK =================== #
    def actualizar_stock(producto_id, cantidad_vendida):
        """Actualiza el stock de un producto tras una venta."""
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT cantidad FROM productos WHERE id=?", (producto_id,))
        cantidad_actual = cursor.fetchone()[0]
        nueva_cantidad = cantidad_actual - cantidad_vendida
        cursor.execute("UPDATE productos SET cantidad=? WHERE id=?", (nueva_cantidad, producto_id))
        conn.commit()
        conn.close()
        
    # =================== PESTAÑA DE FACTURACIÓN =================== #
    tab_factura = ttk.Frame(notebook)
    notebook.add(tab_factura, text="Generar Factura")

    # Formulario para datos del cliente
    frame_cliente = tk.Frame(tab_factura)
    frame_cliente.pack(pady=10)

    tk.Label(frame_cliente, text="Nombre Cliente:").grid(row=0, column=0)
    tk.Label(frame_cliente, text="Dirección:").grid(row=1, column=0)

    entry_cliente_nombre = tk.Entry(frame_cliente)
    entry_cliente_direccion = tk.Entry(frame_cliente)

    entry_cliente_nombre.grid(row=0, column=1)
    entry_cliente_direccion.grid(row=1, column=1)

    # Seleccionar productos para la factura
    tk.Label(tab_factura, text="Seleccionar Productos:").pack(pady=10)

    productos_seleccionados = []

    def agregar_producto_factura():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Por favor, selecciona un producto para agregar a la factura.")
            return

        producto = tree.item(selected_item[0], 'values')
        cantidad = simpledialog.askinteger("Cantidad", "Introduce la cantidad del producto:")
        if cantidad and cantidad > 0:
            total = cantidad * float(producto[4])  # Asegurando que el precio es float
            productos_seleccionados.append((producto[1], cantidad, float(producto[4]), total))
            cargar_productos_factura()
        else:
            messagebox.showwarning("Error", "La cantidad debe ser un número mayor que 0.")

    btn_agregar_producto_factura = tk.Button(tab_factura, text="Agregar Producto a Factura", command=agregar_producto_factura)
    btn_agregar_producto_factura.pack(pady=5)

    # Tabla para productos en la factura
    tree_factura = ttk.Treeview(tab_factura, columns=('Descripción', 'Cantidad', 'Precio', 'Total'), show='headings')
    tree_factura.heading('Descripción', text='Descripción')
    tree_factura.heading('Cantidad', text='Cantidad')
    tree_factura.heading('Precio', text='Precio')
    tree_factura.heading('Total', text='Total')
    tree_factura.pack(expand=True, fill='both')

    def cargar_productos_factura():
        tree_factura.delete(*tree_factura.get_children())
        for item in productos_seleccionados:
            tree_factura.insert('', 'end', values=item)

    def obtener_ruta_escritorio():
        """Obtiene la ruta del escritorio del usuario."""
        return os.path.join(os.path.expanduser("~"), "Desktop")


    def generar_factura():
        nombre_cliente = entry_cliente_nombre.get()
        direccion_cliente = entry_cliente_direccion.get()
        if not nombre_cliente or not direccion_cliente or not productos_seleccionados:
            messagebox.showwarning("Error", "Por favor, completa todos los campos y selecciona productos.")
            return

        # Crear ID único para la factura
        id_factura = generar_id_factura()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calcular el total de la factura con IVA
        total_con_iva = sum([item[3] for item in productos_seleccionados])

        # Registrar la factura en la base de datos
        registrar_factura(id_factura, nombre_cliente, fecha_actual, total_con_iva)

        # Registrar cada producto como una transacción en el historial y actualizar stock
        for producto in productos_seleccionados:
            descripcion, cantidad, precio, total = producto[0], producto[1], producto[2], producto[3]
            registrar_transaccion(id_factura, 'Venta', descripcion, cantidad, precio, total, fecha_actual)

            # Actualizar stock del producto
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM productos WHERE nombre=?", (descripcion,))
            producto_id = cursor.fetchone()[0]
            conn.close()
            actualizar_stock(producto_id, cantidad)  # Llama a la función de actualización de stock

        # Obtener la ruta del escritorio
        ruta_escritorio = obtener_ruta_escritorio()

        # Crear PDF de la factura en el escritorio con tamaño A5 (cuartilla)
        pdf_filename = os.path.join(ruta_escritorio, f"factura_{id_factura}.pdf")
        c = canvas.Canvas(pdf_filename, pagesize=A5)

        # Ajustar el contenido para estar cerca del borde superior
        top_position = 570  # Posición inicial alta

        # Estilos de la cabecera
        c.setFont("Helvetica-Bold", 9)
        c.drawString(20, top_position, f"Factura ID: {id_factura}")
        c.setFont("Helvetica", 8)
        c.drawString(20, top_position - 15, f"Cliente: {nombre_cliente}")
        c.drawString(20, top_position - 25, f"Dirección: {direccion_cliente}")
        c.drawString(20, top_position - 35, f"Fecha: {fecha_actual}")
        c.drawString(200, top_position - 8, "C/San Maximiliano 57")
        c.drawString(200, top_position - 18, "28017 MADRID")
        c.drawString(200, top_position - 28, "juanjobarja@gmail.com")
        c.drawString(200, top_position - 38, "33338853P")
        c.drawString(200, top_position - 48, "Telf. 688 902 949")

        # Nombre de la ferretería centrado
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(150, top_position - 60, "FERRETERIA JJBARJA")

        # Crear tabla de productos
        data = [['Descripción / Producto', 'Cantidad', 'Precio', 'Total']]  # Encabezado de la tabla
        iva_porcentaje = 21  # IVA del 21%

        for item in productos_seleccionados:
            descripcion, cantidad, precio, total = item[0], item[1], item[2], item[3]
            data.append([descripcion, str(cantidad), f"{precio:.2f} €", f"{total:.2f} €"])

        # Crear tabla usando Platypus
        table = Table(data, colWidths=[120, 50, 40, 40])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),  # Establecer el tamaño de fuente a 6 puntos
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        # Calcular la altura de la tabla basada en el número de filas
        num_filas = len(data)
        table_height = num_filas * 18  # Ajuste de altura de la fila para un espaciado adecuado

        # Colocar la tabla en el PDF
        table.wrapOn(c, 280, 300)
        table.drawOn(c, 20, top_position - 120 - table_height)

        # Calcular la posición para los totales y observaciones debajo de la tabla
        y_position = top_position - 120 - table_height - 30  # Ajuste de 30 para crear un espacio adecuado

        # Calcular total sin IVA y mostrar el desglose de IVA
        total_sin_iva = total_con_iva / (1 + iva_porcentaje / 100)
        iva_total = total_con_iva - total_sin_iva

        # Mostrar desglose de IVA y total
        c.setFont("Helvetica-Bold", 8)
        c.drawString(150, y_position, "Subtotal (sin IVA):")
        c.drawRightString(250, y_position, f"{total_sin_iva:.2f} €")
        c.drawString(150, y_position - 15, f"IVA ({iva_porcentaje}%):")
        c.drawRightString(250, y_position - 15, f"{iva_total:.2f} €")
        c.drawString(150, y_position - 30, "Total (con IVA):")
        c.drawRightString(250, y_position - 30, f"{total_con_iva:.2f} €")

        # Observaciones, ajustando su posición para evitar superposición
        c.setFont("Helvetica", 7)
        c.drawString(20, y_position - 50, "Observaciones:")
        c.drawString(20, y_position - 60, "Para cambios y devoluciones, dispone de 15 días; el artículo debe estar en perfecto estado y con su ticket.")
        c.drawString(20, y_position - 70, "Las devoluciones se efectuarán mediante vale sin fecha de caducidad. No se admiten cambios en herramientas,")
        c.drawString(20, y_position - 80, "salvo defecto de fábrica. Todos los artículos tienen garantía según RDL 1/2007 del 16 de noviembre.")

        # Guardar el PDF
        c.save()
        messagebox.showinfo("Éxito", f"Factura generada en el escritorio: {pdf_filename}")

        # Actualizar el historial y lista de productos
        cargar_historial()
        cargar_productos()  # Refresca la tabla de productos en la interfaz para reflejar el nuevo stock



    
    btn_generar_factura = tk.Button(tab_factura, text="Generar Factura", command=generar_factura)
    btn_generar_factura.pack(pady=10)
    
    # =================== PESTAÑA DE ALBARANES =================== #
    tab_albaran = ttk.Frame(notebook)
    notebook.add(tab_albaran, text="Generar Albarán")

    # Formulario para datos del cliente en el albarán
    frame_cliente_albaran = tk.Frame(tab_albaran)
    frame_cliente_albaran.pack(pady=10)

    tk.Label(frame_cliente_albaran, text="Nombre Cliente:").grid(row=0, column=0)
    tk.Label(frame_cliente_albaran, text="Dirección:").grid(row=1, column=0)

    entry_cliente_nombre_albaran = tk.Entry(frame_cliente_albaran)
    entry_cliente_direccion_albaran = tk.Entry(frame_cliente_albaran)

    entry_cliente_nombre_albaran.grid(row=0, column=1)
    entry_cliente_direccion_albaran.grid(row=1, column=1)

    # Seleccionar productos para el albarán
    tk.Label(tab_albaran, text="Seleccionar Productos:").pack(pady=10)

    productos_seleccionados_albaran = []

    def agregar_producto_albaran():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Por favor, selecciona un producto para agregar al albarán.")
            return

        producto = tree.item(selected_item[0], 'values')
        cantidad = simpledialog.askinteger("Cantidad", "Introduce la cantidad del producto:")
        if cantidad and cantidad > 0:
            total = cantidad * float(producto[4])  # Asegurando que el precio es float
            productos_seleccionados_albaran.append((producto[1], cantidad, float(producto[4]), total))
            cargar_productos_albaran()
        else:
            messagebox.showwarning("Error", "La cantidad debe ser un número mayor que 0.")

    btn_agregar_producto_albaran = tk.Button(tab_albaran, text="Agregar Producto a Albarán", command=agregar_producto_albaran)
    btn_agregar_producto_albaran.pack(pady=5)

    # Tabla para productos en el albarán
    tree_albaran = ttk.Treeview(tab_albaran, columns=('Descripción', 'Cantidad', 'Precio', 'Total'), show='headings')
    tree_albaran.heading('Descripción', text='Descripción')
    tree_albaran.heading('Cantidad', text='Cantidad')
    tree_albaran.heading('Precio', text='Precio')
    tree_albaran.heading('Total', text='Total')
    tree_albaran.pack(expand=True, fill='both')

    def cargar_productos_albaran():
        tree_albaran.delete(*tree_albaran.get_children())
        for item in productos_seleccionados_albaran:
            tree_albaran.insert('', 'end', values=item)

    def generar_albaran():
        nombre_cliente = entry_cliente_nombre_albaran.get()
        direccion_cliente = entry_cliente_direccion_albaran.get()
        if not nombre_cliente or not direccion_cliente or not productos_seleccionados_albaran:
            messagebox.showwarning("Error", "Por favor, completa todos los campos y selecciona productos.")
            return

        # Crear ID único para el albarán
        id_albaran = generar_id_factura()  # Puedes crear una función separada para generar ID de albarán si prefieres
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Registrar cada producto como una transacción en el historial
        for producto in productos_seleccionados_albaran:
            descripcion, cantidad, precio, total = producto[0], producto[1], producto[2], producto[3]
            registrar_transaccion(id_albaran, 'Albarán', descripcion, cantidad, precio, total, fecha_actual)

        # Calcular el total del albarán (IVA incluido)
        total_albaran = sum([item[3] for item in productos_seleccionados_albaran])

        # Crear PDF del albarán
        ruta_escritorio = obtener_ruta_escritorio()
        pdf_filename = os.path.join(ruta_escritorio, f"albaran_{id_albaran}.pdf")
        c = canvas.Canvas(pdf_filename, pagesize=A5)

        top_position = 570

        # Encabezado del albarán
        c.setFont("Helvetica-Bold", 9)
        c.drawString(20, top_position, f"Albarán ID: {id_albaran}")
        c.setFont("Helvetica", 8)
        c.drawString(20, top_position - 15, f"Cliente: {nombre_cliente}")
        c.drawString(20, top_position - 25, f"Dirección: {direccion_cliente}")
        c.drawString(20, top_position - 35, f"Fecha: {fecha_actual}")

        # Información del emisor en el PDF del albarán
        c.drawString(200, top_position - 15, "C/San Maximiliano 57")
        c.drawString(200, top_position - 25, "28017 MADRID")
        c.drawString(200, top_position - 35, "juanjobarja@gmail.com")
        c.drawString(200, top_position - 45, "33338853P")
        c.drawString(200, top_position - 55, "Telf. 688 902 949")

        # Título de la ferretería
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(150, top_position - 70, "FERRETERIA JJBARJA - ALBARÁN")

        # Tabla de productos
        data = [['Descripción / Producto', 'Cantidad', 'Precio', 'Total']]
        for item in productos_seleccionados_albaran:
            descripcion, cantidad, precio, total = item[0], item[1], item[2], item[3]
            data.append([descripcion, str(cantidad), f"{precio:.2f} €", f"{total:.2f} €"])

        # Crear y configurar la tabla
        table = Table(data, colWidths=[120, 50, 40, 40])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),  # Establecer el tamaño de fuente a 6 puntos
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        # Ajustar la posición de la tabla para evitar superposición
        table_height = 20 * len(data)  # Ajuste de la altura según el número de filas
        table.wrapOn(c, 280, 300)
        table.drawOn(c, 20, top_position - 100 - table_height)  # Ajusta top_position según el tamaño de la tabla

        # Mostrar el total del albarán (sin desglose de IVA)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(150, top_position - 120 - table_height, "TOTAL ALBARÁN:")
        c.drawRightString(250, top_position - 120 - table_height, f"{total_albaran:.2f} €")

        # Observaciones específicas para el albarán
        c.setFont("Helvetica", 7)
        c.drawString(20, top_position - 140 - table_height, "Observaciones:")
        c.drawString(20, top_position - 150 - table_height, "No se admiten reclamaciones ni devoluciones pasados 7 días.")

        c.save()
        messagebox.showinfo("Éxito", f"Albarán generado en el escritorio: {pdf_filename}")


    btn_generar_albaran = tk.Button(tab_albaran, text="Generar Albarán", command=generar_albaran)
    btn_generar_albaran.pack(pady=10)


    
# =================== PESTAÑA DE CLIENTES =================== #
    tab_clientes = ttk.Frame(notebook)
    notebook.add(tab_clientes, text="Clientes")

    # Formulario para datos del cliente
    frame_cliente = tk.Frame(tab_clientes)
    frame_cliente.pack(pady=10)

    # Crear campos para los detalles del cliente
    labels_cliente = ["Identificación Fiscal", "Nombre Fiscal", "Nombre Comercial", "Dirección", "Código Postal", "Población", "Provincia", "País", "Teléfono"]
    entries_cliente = {}
    for i, text in enumerate(labels_cliente):
        tk.Label(frame_cliente, text=text + ":", font=('Arial', 12)).grid(row=i, column=0, padx=5, pady=5)
        entry_cliente = tk.Entry(frame_cliente, font=('Arial', 12))
        entry_cliente.grid(row=i, column=1, padx=5, pady=5)
        entries_cliente[text] = entry_cliente

    # Botón para agregar clientes
    def agregar_cliente():
        try:
            identificacion_fiscal = entries_cliente["Identificación Fiscal"].get().strip()
            nombre_fiscal = entries_cliente["Nombre Fiscal"].get().strip()
            nombre_comercial = entries_cliente["Nombre Comercial"].get().strip()
            direccion = entries_cliente["Dirección"].get().strip()
            codigo_postal = entries_cliente["Código Postal"].get().strip()
            poblacion = entries_cliente["Población"].get().strip()
            provincia = entries_cliente["Provincia"].get().strip()
            pais = entries_cliente["País"].get().strip()
            telefono = entries_cliente["Teléfono"].get().strip()
            if not identificacion_fiscal or not nombre_fiscal:
                messagebox.showerror("Error", "La identificación fiscal y el nombre fiscal son obligatorios.")
                return
            añadir_cliente(identificacion_fiscal, nombre_fiscal, nombre_comercial, direccion, codigo_postal, poblacion, provincia, pais, telefono)
            messagebox.showinfo("Éxito", "Cliente añadido correctamente.")
            cargar_clientes()  # Refresca la tabla después de agregar
        except ValueError:
            messagebox.showerror("Error", "Revisa los campos.")

    btn_agregar_cliente = tk.Button(tab_clientes, text="Agregar Cliente", command=agregar_cliente)
    btn_agregar_cliente.pack(pady=10)

    # Barra de búsqueda para clientes
    search_frame_clientes = tk.Frame(tab_clientes)
    search_frame_clientes.pack(pady=10)
    tk.Label(search_frame_clientes, text="Buscar Cliente:", font=('Arial', 12)).grid(row=0, column=0, padx=5)
    entry_busqueda_cliente = tk.Entry(search_frame_clientes, font=('Arial', 12))
    entry_busqueda_cliente.grid(row=0, column=1, padx=5)

    # Función para buscar clientes en la base de datos
    def buscar_clientes():
        term = entry_busqueda_cliente.get().strip().lower()
        tree_clientes.delete(*tree_clientes.get_children())
        for cliente in obtener_clientes():
            # Buscamos en nombre fiscal, nombre comercial y dirección
            if term in cliente[2].lower() or term in cliente[3].lower() or term in cliente[4].lower():
                tree_clientes.insert('', 'end', values=cliente)

    btn_buscar_cliente = tk.Button(search_frame_clientes, text="Buscar", command=buscar_clientes)
    btn_buscar_cliente.grid(row=0, column=2, padx=5)

    # Tabla para mostrar los clientes
    columnas_clientes = ('ID', 'Identificación Fiscal', 'Nombre Fiscal', 'Nombre Comercial', 'Dirección', 'Código Postal', 'Población', 'Provincia', 'País', 'Teléfono')
    tree_clientes = ttk.Treeview(tab_clientes, columns=columnas_clientes, show='headings')
    for col in columnas_clientes:
        tree_clientes.heading(col, text=col)
        tree_clientes.column(col, width=150)
    tree_clientes.pack(expand=True, fill='both')

    # Función para cargar clientes en la tabla
    def cargar_clientes():
        tree_clientes.delete(*tree_clientes.get_children())
        for cliente in obtener_clientes():
            tree_clientes.insert('', 'end', values=cliente)

    btn_cargar_clientes = tk.Button(tab_clientes, text="Cargar Clientes", command=cargar_clientes)
    btn_cargar_clientes.pack(pady=5)

    # Función para seleccionar cliente
    def seleccionar_cliente(event=None):
        selected_item = tree_clientes.selection()
        if not selected_item:
            return

        cliente = tree_clientes.item(selected_item[0], 'values')

        # Pasa los datos del cliente seleccionado a los campos de facturación
        entry_cliente_nombre.delete(0, tk.END)
        entry_cliente_nombre.insert(0, cliente[2])  # Nombre Comercial
        entry_cliente_direccion.delete(0, tk.END)
        entry_cliente_direccion.insert(0, cliente[3])  # Dirección

        # Cambiar a la pestaña de "Generar Factura"
        notebook.select(tab_factura)

    # Botón para generar factura desde cliente seleccionado
    btn_generar_factura_cliente = tk.Button(tab_clientes, text="Generar Factura para Cliente Seleccionado", command=seleccionar_cliente)
    btn_generar_factura_cliente.pack(pady=10)

    # Función para eliminar cliente seleccionado
    def eliminar_cliente_seleccionado():
        selected_item = tree_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Por favor, selecciona un cliente para eliminar.")
            return

        cliente = tree_clientes.item(selected_item[0], 'values')
        respuesta = messagebox.askyesno("Confirmar eliminación", f"¿Está seguro de que desea eliminar al cliente {cliente[2]}?")
        if respuesta:
            eliminar_cliente(cliente[0])  # Elimina el cliente usando el ID
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
            cargar_clientes()  # Refresca la tabla de clientes

    # Botón para eliminar cliente
    btn_eliminar_cliente = tk.Button(tab_clientes, text="Eliminar Cliente", command=eliminar_cliente_seleccionado)
    btn_eliminar_cliente.pack(pady=5)

    # Cargar todos los clientes al iniciar la pestaña
    cargar_clientes()



    
    # =================== FUNCIONES PARA GENERAR TICKETS =================== #
    def generar_ticket():
        # Crear un ID único para el ticket
        id_ticket = generar_id_factura()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Registrar cada producto como una transacción en el historial y actualizar stock
        for producto in productos_seleccionados:
            descripcion, cantidad, precio, total = producto[0], producto[1], producto[2], producto[3]
            registrar_transaccion(id_ticket, 'Ticket', descripcion, cantidad, precio, total, fecha_actual)

            # Actualizar stock del producto
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM productos WHERE nombre=?", (descripcion,))
            producto_id = cursor.fetchone()[0]
            conn.close()
            actualizar_stock(producto_id, cantidad)  # Llama a la función de actualización de stock

        # Configurar el tamaño dinámico del ticket según la cantidad de productos
        ticket_width = 3 * inch
        ticket_height = 1.5 * inch + (len(productos_seleccionados) * 0.3 * inch) + 2 * inch  # Ajustar altura dinámica

        # Obtener la ruta del escritorio y definir el nombre del archivo para el ticket
        ruta_escritorio = obtener_ruta_escritorio()
        pdf_filename = os.path.join(ruta_escritorio, f"ticket_{id_ticket}.pdf")

        # Crear el PDF con el tamaño personalizado
        c = canvas.Canvas(pdf_filename, pagesize=(ticket_width, ticket_height))

        # Encabezado del ticket con los datos de la tienda
        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, ticket_height - 20, "FERRETERIA JJBARJA")
        c.setFont("Helvetica", 10)
        c.drawString(10, ticket_height - 40, "C/San Maximiliano 57, 28017 Madrid")
        c.drawString(10, ticket_height - 60, "Teléfono: 688 902 949")

        # Fecha
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10, ticket_height - 100, f"Fecha: {fecha_actual}")

        # Encabezado de productos
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10, ticket_height - 130, "Producto")
        c.drawString(120, ticket_height - 130, "Cant.")
        c.drawString(170, ticket_height - 130, "Precio")
        c.drawString(220, ticket_height - 130, "Total")

        # Detalle de productos y acumulación del total
        y_position = ticket_height - 150
        total_con_iva = 0

        for item in productos_seleccionados:
            c.setFont("Helvetica", 10)
            c.drawString(10, y_position, item[0])
            c.drawString(120, y_position, str(item[1]))
            c.drawString(170, y_position, f"{item[2]:.2f} €")
            c.drawString(220, y_position, f"{item[3]:.2f} €")
            total_con_iva += item[3]  # Acumula el total aquí
            y_position -= 20

        # Mostrar el total final
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10, y_position - 20, "TOTAL: " + f"{total_con_iva:.2f} €")

        # Mensaje de agradecimiento
        c.setFont("Helvetica", 8)
        c.drawCentredString(ticket_width / 2, y_position - 50, "¡Gracias por su visita!")

        # Guardar el PDF
        c.save()
        messagebox.showinfo("Éxito", f"Ticket generado en el escritorio: {pdf_filename}")

        # Actualizar la lista de productos en la interfaz
        cargar_productos()  # Refresca la tabla de productos en la interfaz para reflejar el nuevo stock



    # Luego creas el botón para generar ticket
    btn_generar_ticket = tk.Button(tab_factura, text="Generar Ticket", command=generar_ticket)
    btn_generar_ticket.pack(pady=10)
   
    
    # Crear tablas al iniciar
    crear_tablas()
    # Iniciar la ventana principal
    ventana.mainloop()

# Iniciar la ventana principal
crear_ventana_principal()
