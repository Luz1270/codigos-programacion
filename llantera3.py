import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import sys

# Función para poner fondo en cualquier ventana
def poner_fondo(ventana, width=600, height=400):
    try:
        fondo_img = Image.open("fondo.png").resize((width, height))
        fondo = ImageTk.PhotoImage(fondo_img)
        canvas = tk.Canvas(ventana, width=width, height=height)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=fondo, anchor="nw")
        canvas.fondo = fondo  # evitar recolección
        return canvas
    except:
        canvas = tk.Canvas(ventana, width=width, height=height, bg="#003366")
        canvas.pack(fill="both", expand=True)
        return canvas

# ----------------- BASE DE DATOS -----------------
def inicializar_db():
    try:
        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                contraseña TEXT,
                rol TEXT
            )
        ''')
        if cur.execute("SELECT COUNT(*) FROM empleados").fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO empleados (usuario, contraseña, rol) VALUES (?, ?, ?)",
                [("Caja", "1234", "cajero"), ("Gerente", "12345", "gerente"), ("Almacen", "123456", "almacenista")]
            )

        cur.execute('''
            CREATE TABLE IF NOT EXISTS llantas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT,
                medida TEXT,
                precio REAL,
                cantidad INTEGER
            )
        ''')
        if cur.execute("SELECT COUNT(*) FROM llantas").fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO llantas (marca, medida, precio, cantidad) VALUES (?, ?, ?, ?)",
                [
                    ("Michelin", "205/55R16", 1500, 5),
                    ("Pirelli", "195/65R15", 1350, 3),
                    ("Continental", "215/60R17", 1650, 0)
                ]
            )

        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                telefono TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                llanta_id INTEGER,
                fecha_hora TEXT
            )
        ''')

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Error Base de Datos", f"No se pudo inicializar la base de datos:\n{e}")
        sys.exit(1)

# ----------------- PANTALLA INICIO -----------------
def mostrar_inicio():
    root = tk.Tk()
    root.title("SYSTEM TIRE")
    root.geometry("600x400")
    root.resizable(False, False)

    canvas = poner_fondo(root, 600, 400)

    canvas.create_text(300, 40, text="BIENVENIDO", font=("Arial Black", 18), fill="white")
    canvas.create_text(300, 80, text="SYSTEM TIRE", font=("Arial Black", 24), fill="#FFD700")
    canvas.create_text(300, 360,
        text="Tu herramienta integral para administrar inventario,\nventas y operaciones de la llantera.",
        font=("Arial", 10), fill="white", justify="center")

    def ir_login():
        root.destroy()
        mostrar_login()

    boton = tk.Button(root, text="Iniciar sesión", font=("Arial", 9),
                      bg="#28a745", fg="white", width=12, height=1, command=ir_login)
    canvas.create_window(590, 20, window=boton, anchor="ne")

    root.mainloop()

# ----------------- LOGIN -----------------
def mostrar_login():
    login = tk.Tk()
    login.title("Inicio de sesión")
    login.geometry("300x200")
    login.resizable(False, False)

    canvas = poner_fondo(login, 300, 200)

    tk.Label(login, text="Usuario:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=30, y=30)
    usuario_entry = tk.Entry(login)
    usuario_entry.place(x=100, y=30)

    tk.Label(login, text="Contraseña:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=30, y=70)
    contraseña_entry = tk.Entry(login, show="*")
    contraseña_entry.place(x=100, y=70)

    def validar():
        usuario = usuario_entry.get()
        contraseña = contraseña_entry.get()
        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("SELECT rol FROM empleados WHERE usuario=? AND contraseña=?", (usuario, contraseña))
        resultado = cur.fetchone()
        conn.close()
        if resultado:
            login.destroy()
            mostrar_menu_por_rol(resultado[0])
        else:
            messagebox.showerror("Error", "Credenciales incorrectas.")

    btn_entrar = tk.Button(login, text="Entrar", bg="#007bff", fg="white", command=validar)
    btn_entrar.place(x=120, y=110)

    login.mainloop()

# ----------------- MENÚ POR ROL -----------------
def mostrar_menu_por_rol(rol):
    if rol == "almacenista":
        mostrar_menu_almacenista()
        return

    ventana = tk.Tk()
    ventana.title("Menú principal")
    ventana.geometry("300x300")

    canvas = poner_fondo(ventana, 300, 300)

    def cerrar_sesion():
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?"):
            ventana.destroy()
            mostrar_login()

    if rol == "cajero":
        tk.Label(ventana, text="Bienvenido, CAJERO", bg="#003366", fg="white", font=("Arial", 14, "bold")).place(x=70, y=30)
        tk.Button(ventana, text="Hacer venta", command=mostrar_registro).place(x=100, y=80)
        tk.Button(ventana, text="Ver productos disponibles", command=mostrar_inventario).place(x=70, y=120)

    elif rol == "gerente":
        tk.Label(ventana, text="Bienvenido, GERENTE", bg="#003366", fg="white", font=("Arial", 14, "bold")).place(x=70, y=30)
        tk.Button(ventana, text="Ver ventas totales", command=ver_ventas).place(x=90, y=80)
        tk.Button(ventana, text="Editar precios de llantas", command=editar_precios).place(x=70, y=120)
        tk.Button(ventana, text="Registrar nuevo empleado", command=registrar_empleado).place(x=60, y=160)

    tk.Button(ventana, text="Cerrar sesión", bg="#dc3545", fg="white", command=cerrar_sesion).place(x=90, y=220)

    ventana.mainloop()

# ----------------- MENÚ ALMACENISTA -----------------
def mostrar_menu_almacenista():
    ventana = tk.Tk()
    ventana.title("Menú Almacenista")
    ventana.geometry("300x250")

    canvas = poner_fondo(ventana, 300, 250)

    def cerrar_sesion():
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?"):
            ventana.destroy()
            mostrar_login()

    tk.Label(ventana, text="Bienvenido, ALMACENISTA", bg="#003366", fg="white", font=("Arial", 14, "bold")).place(x=50, y=30)
    tk.Button(ventana, text="Reabastecer llantas", width=20, command=mostrar_reabastecer).place(x=70, y=80)
    tk.Button(ventana, text="Agregar nueva llanta", width=20, command=mostrar_agregar_llanta).place(x=70, y=120)
    tk.Button(ventana, text="Cerrar sesión", bg="#dc3545", fg="white", command=cerrar_sesion).place(x=90, y=180)

    ventana.mainloop()

# ----------------- FUNCIONES ALMACENISTA -----------------
def mostrar_reabastecer():
    ventana = tk.Toplevel()
    ventana.title("Reabastecer llantas")
    ventana.geometry("400x350")

    canvas = poner_fondo(ventana, 400, 350)

    tk.Label(ventana, text="Selecciona la llanta:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=20)

    lista = tk.Listbox(ventana, width=50, height=10)
    lista.place(x=20, y=50)

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute("SELECT id, marca, medida, cantidad FROM llantas")
    llantas = cur.fetchall()
    conn.close()

    for l in llantas:
        lista.insert(tk.END, f"{l[0]} - {l[1]} {l[2]} | Cantidad actual: {l[3]}")

    tk.Label(ventana, text="Cantidad a agregar:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=270)
    entrada_cantidad = tk.Entry(ventana)
    entrada_cantidad.place(x=160, y=270)

    def reabastecer():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una llanta.")
            return
        try:
            cantidad = int(entrada_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Cantidad inválida.")
            return

        id_llanta = llantas[seleccion[0]][0]

        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("UPDATE llantas SET cantidad = cantidad + ? WHERE id = ?", (cantidad, id_llanta))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Inventario actualizado.")
        ventana.destroy()

    tk.Button(ventana, text="Reabastecer", bg="#198754", fg="white", command=reabastecer).place(x=150, y=310)

def mostrar_agregar_llanta():
    ventana = tk.Toplevel()
    ventana.title("Agregar nueva llanta")
    ventana.geometry("400x300")

    canvas = poner_fondo(ventana, 400, 300)

    tk.Label(ventana, text="Marca:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=30)
    entrada_marca = tk.Entry(ventana)
    entrada_marca.place(x=120, y=30)

    tk.Label(ventana, text="Medida:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=70)
    entrada_medida = tk.Entry(ventana)
    entrada_medida.place(x=120, y=70)

    tk.Label(ventana, text="Precio:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=110)
    entrada_precio = tk.Entry(ventana)
    entrada_precio.place(x=120, y=110)

    tk.Label(ventana, text="Cantidad:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=150)
    entrada_cantidad = tk.Entry(ventana)
    entrada_cantidad.place(x=120, y=150)

    def agregar():
        marca = entrada_marca.get().strip()
        medida = entrada_medida.get().strip()
        try:
            precio = float(entrada_precio.get())
            cantidad = int(entrada_cantidad.get())
            if precio < 0 or cantidad < 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Precio o cantidad inválidos.")
            return

        if not marca or not medida:
            messagebox.showwarning("Campos incompletos", "Llena todos los datos.")
            return

        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO llantas (marca, medida, precio, cantidad) VALUES (?, ?, ?, ?)",
                    (marca, medida, precio, cantidad))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Nueva llanta agregada.")
        ventana.destroy()

    tk.Button(ventana, text="Agregar llanta", bg="#0d6efd", fg="white", command=agregar).place(x=150, y=200)

# ----------------- FUNCIONES CAJERO -----------------
def mostrar_registro():
    app = tk.Toplevel()
    app.title("Registrar venta")
    app.geometry("400x500")

    canvas = poner_fondo(app, 400, 500)

    tk.Label(app, text="Nombre del Cliente:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=30)
    entrada_nombre = tk.Entry(app)
    entrada_nombre.place(x=160, y=30)

    tk.Label(app, text="Teléfono:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=70)
    entrada_telefono = tk.Entry(app)
    entrada_telefono.place(x=160, y=70)

    tk.Label(app, text="Selecciona una llanta:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=110)
    lista_llantas = tk.Listbox(app, height=10, width=40)
    lista_llantas.place(x=20, y=140)

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute("SELECT id, marca, medida, precio, cantidad FROM llantas")
    llantas = cur.fetchall()
    conn.close()

    for l in llantas:
        estado = "AGOTADO" if l[4] <= 0 else f"{l[4]} disponibles"
        lista_llantas.insert(tk.END, f"{l[1]} {l[2]} - ${l[3]:.2f} | {estado}")

    # Campo para cantidad a comprar
    tk.Label(app, text="Cantidad a comprar:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=380)
    entrada_cantidad = tk.Entry(app)
    entrada_cantidad.place(x=160, y=380)
    entrada_cantidad.insert(0, "1")

    def registrar():
        nombre = entrada_nombre.get().strip()
        telefono = entrada_telefono.get().strip()
        seleccion = lista_llantas.curselection()
        cantidad_str = entrada_cantidad.get().strip()

        if not nombre or not telefono or not seleccion or not cantidad_str:
            messagebox.showerror("Error", "Completa todos los campos.")
            return

        try:
            cantidad_comprar = int(cantidad_str)
            if cantidad_comprar <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Cantidad inválida.")
            return

        llanta_id, marca, medida, precio, cantidad = llantas[seleccion[0]]
        if cantidad_comprar > cantidad:
            messagebox.showerror("Error", f"No hay suficiente inventario. Solo quedan {cantidad} llantas disponibles.")
            return

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO clientes (nombre, telefono) VALUES (?, ?)", (nombre, telefono))
        cliente_id = cur.lastrowid
        for _ in range(cantidad_comprar):
            cur.execute("INSERT INTO compras (cliente_id, llanta_id, fecha_hora) VALUES (?, ?, ?)", (cliente_id, llanta_id, fecha_hora))
        cur.execute("UPDATE llantas SET cantidad = cantidad - ? WHERE id = ?", (cantidad_comprar, llanta_id))
        conn.commit()
        conn.close()

        recibo = f"""----- RECIBO -----
Cliente: {nombre}
Teléfono: {telefono}
Llanta: {marca} {medida}
Precio: ${precio:.2f}
Fecha y hora: {fecha_hora}
------------------"""

        with open("recibo_venta.txt", "w", encoding="utf-8") as f:
            f.write(recibo)

        messagebox.showinfo("Compra registrada", recibo)
        entrada_nombre.delete(0, tk.END)
        entrada_telefono.delete(0, tk.END)
        lista_llantas.selection_clear(0, tk.END)

    tk.Button(app, text="Registrar compra", bg="#198754", fg="white", command=registrar).place(x=140, y=400)

# ----------------- INVENTARIO -----------------
def mostrar_inventario():
    ventana = tk.Toplevel()
    ventana.title("Inventario de llantas")
    ventana.geometry("800x400")

    canvas = poner_fondo(ventana, 800, 400)

    tk.Label(ventana, text="Llantas disponibles:", bg="#003366", fg="white", font=("Arial", 12, "bold")).place(x=120, y=10)
    lista = tk.Listbox(ventana, width=60, height=12)
    lista.place(x=20, y=40)

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute("SELECT marca, medida, precio, cantidad FROM llantas")
    for marca, medida, precio, cantidad in cur.fetchall():
        estado = "AGOTADO" if cantidad <= 0 else f"{cantidad} disponibles"
        lista.insert(tk.END, f"{marca} {medida} - ${precio:.2f} | {estado}")
    conn.close()

# ----------------- FUNCIONES GERENTE -----------------
def ver_ventas():
    ventana = tk.Toplevel()
    ventana.title("Ventas Totales")
    ventana.geometry("500x350")

    canvas = poner_fondo(ventana, 500, 350)

    tk.Label(ventana, text="Historial de ventas:", bg="#003366", fg="white", font=("Arial", 12, "bold")).place(x=180, y=10)

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute('''
        SELECT clientes.nombre, clientes.telefono, llantas.marca, llantas.medida, llantas.precio, compras.fecha_hora
        FROM compras
        JOIN llantas ON compras.llanta_id = llantas.id
        JOIN clientes ON compras.cliente_id = clientes.id
        ORDER BY compras.fecha_hora DESC
    ''')
    ventas = cur.fetchall()
    conn.close()

    lista = tk.Listbox(ventana, width=70, height=15)
    lista.place(x=10, y=40)

    for v in ventas:
        lista.insert(tk.END, f"{v[0]} ({v[1]}) compró {v[2]} {v[3]} por ${v[4]:.2f} el {v[5]}")

def editar_precios():
    ventana = tk.Toplevel()
    ventana.title("Editar precios de llantas")
    ventana.geometry("400x350")

    canvas = poner_fondo(ventana, 400, 350)

    tk.Label(ventana, text="Selecciona la llanta:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=20)

    lista = tk.Listbox(ventana, width=50, height=10)
    lista.place(x=20, y=50)

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute("SELECT id, marca, medida, precio FROM llantas")
    llantas = cur.fetchall()
    conn.close()

    for l in llantas:
        lista.insert(tk.END, f"{l[1]} {l[2]} - ${l[3]:.2f}")

    tk.Label(ventana, text="Nuevo precio:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=270)
    entrada_precio = tk.Entry(ventana)
    entrada_precio.place(x=120, y=270)

    def actualizar_precio():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una llanta.")
            return
        try:
            nuevo_precio = float(entrada_precio.get())
            if nuevo_precio < 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Precio inválido.")
            return

        id_llanta = llantas[seleccion[0]][0]
        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("UPDATE llantas SET precio=? WHERE id=?", (nuevo_precio, id_llanta))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Precio actualizado.")
        ventana.destroy()

    tk.Button(ventana, text="Actualizar", bg="#0d6efd", fg="white", command=actualizar_precio).place(x=150, y=310)

def registrar_empleado():
    ventana = tk.Toplevel()
    ventana.title("Registrar nuevo empleado")
    ventana.geometry("350x300")

    canvas = poner_fondo(ventana, 350, 300)

    tk.Label(ventana, text="Usuario:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=30)
    entrada_usuario = tk.Entry(ventana)
    entrada_usuario.place(x=120, y=30)

    tk.Label(ventana, text="Contraseña:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=70)
    entrada_contra = tk.Entry(ventana, show="*")
    entrada_contra.place(x=120, y=70)

    tk.Label(ventana, text="Rol:", bg="#003366", fg="white", font=("Arial", 10, "bold")).place(x=20, y=110)
    entrada_rol = tk.Entry(ventana)
    entrada_rol.place(x=120, y=110)

    def agregar_empleado():
        usuario = entrada_usuario.get().strip()
        contra = entrada_contra.get().strip()
        rol = entrada_rol.get().strip().lower()

        if not usuario or not contra or not rol:
            messagebox.showwarning("Datos incompletos", "Completa todos los campos.")
            return

        if rol not in ("cajero", "gerente", "almacenista"):
            messagebox.showerror("Error", "Rol inválido. Debe ser cajero, gerente o almacenista.")
            return

        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO empleados (usuario, contraseña, rol) VALUES (?, ?, ?)", (usuario, contra, rol))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Empleado registrado.")
        ventana.destroy()

    tk.Button(ventana, text="Registrar", bg="#0d6efd", fg="white", command=agregar_empleado).place(x=130, y=160)

# ----------------- EJECUCIÓN -----------------
if __name__ == "__main__":
    inicializar_db()
    mostrar_inicio()
