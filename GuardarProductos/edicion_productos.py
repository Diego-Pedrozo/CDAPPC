import tkinter as tk
from tkinter import ttk
import sqlite3
from productos import ProductoApp
import serial

class VisualizacionEdicionProductosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualización y Edición de Productos")
        #self.root.geometry("1200x400")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (1200 // 2)
        y = (screen_height // 2) - (400 // 2) 
        self.root.geometry(f"1200x400+{x}+{y}")

        # Frame principal
        self.frame_principal = tk.Frame(self.root)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Frame de visualización de productos
        self.frame_visualizacion = tk.Frame(self.frame_principal, bd=2, relief=tk.GROOVE)
        self.frame_visualizacion.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.frame_visualizacion, columns=("Código de Barras", "Nombre", "Peso", "Precio"))
        self.tree.heading("Código de Barras", text="Código de Barras")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Peso", text="Peso")
        self.tree.heading("Precio", text="Precio")
        self.tree.bind("<Double-1>", self.ir_a_edicion)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.inicializar_base_datos()
        self.cargar_productos()

        # Frame de edición de productos
        self.frame_edicion = tk.Frame(self.frame_principal, bd=2, relief=tk.GROOVE)
        self.frame_edicion.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.label_codigo = tk.Label(self.frame_edicion, text="Código de Barras:")
        self.label_codigo.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_codigo = tk.Entry(self.frame_edicion, state="readonly")
        self.entry_codigo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        self.label_nombre = tk.Label(self.frame_edicion, text="Nombre:")
        self.label_nombre.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_nombre = tk.Entry(self.frame_edicion, state="readonly")
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        self.label_descripcion = tk.Label(self.frame_edicion, text="Descripción:")
        self.label_descripcion.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_descripcion = tk.Entry(self.frame_edicion, state="readonly")
        self.entry_descripcion.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        self.label_peso = tk.Label(self.frame_edicion, text="Peso:")
        self.label_peso.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_peso = tk.Entry(self.frame_edicion, state="readonly")
        self.entry_peso.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        self.label_precio = tk.Label(self.frame_edicion, text="Precio:")
        self.label_precio.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_precio = tk.Entry(self.frame_edicion, state="readonly")
        self.entry_precio.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.boton_actualizar = tk.Button(self.frame_edicion, text="Actualizar Producto", command=self.actualizar_producto)
        self.boton_actualizar.grid(row=5, column=0, columnspan=2, pady=10)
        self.boton_actualizar.config(state="disabled")

        self.boton_eliminar = tk.Button(self.frame_edicion, text="Eliminar Producto", command=self.eliminar_producto)
        self.boton_eliminar.grid(row=6, column=0, columnspan=2)
        self.boton_eliminar.config(state="disabled")

        self.boton_eliminar = tk.Button(self.frame_edicion, text="Eliminar Producto", command=self.eliminar_producto)
        self.boton_eliminar.grid(row=6, column=0, columnspan=2)
        self.boton_eliminar.config(state="disabled")

        self.boton_agregar = tk.Button(self.frame_edicion, text="Agregar Producto", command=self.app_agregar_productos)
        self.boton_agregar.grid(pady=7, column=0, columnspan=2)
    
    def inicializar_base_datos(self):
        self.conn = sqlite3.connect('productos.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT,
                nombre TEXT,
                descripcion TEXT,
                peso REAL,
                precio REAL
            )
        ''')

        self.conn.commit()

    def cargar_productos(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect('productos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo_barras, nombre, peso, precio FROM productos")
        productos = cursor.fetchall()
        for producto in productos:
            self.tree.insert("", "end", text="", values=producto[1:], tags=(producto[0],))

        self.tree.column("#0", width=0, stretch=tk.NO)

        for column in self.tree['columns']:
            self.tree.column(column, anchor='center')

        conn.close()

    def ir_a_edicion(self, event):
        item = self.tree.selection()[0]
        id_producto = self.tree.item(item, "tags")[0]
        self.cargar_producto_seleccionado(id_producto)

    def cargar_producto_seleccionado(self, id_producto=None):
        if id_producto is None:
            id_producto = self.tree.item(self.tree.selection()[0], "tags")[0]

        conn = sqlite3.connect('productos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id=?", (id_producto,))
        producto = cursor.fetchone()
        if producto:
            self.entry_codigo.config(state="normal")
            self.entry_codigo.delete(0, tk.END)
            self.entry_codigo.insert(0, producto[1])
            self.entry_codigo.config(state="readonly")
            self.entry_nombre.config(state="normal")
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, producto[2])
            self.entry_descripcion.config(state="normal")
            self.entry_descripcion.delete(0, tk.END)
            self.entry_descripcion.insert(0, producto[3])
            self.entry_peso.config(state="normal")
            self.entry_peso.delete(0, tk.END)
            self.entry_peso.insert(0, producto[4])
            self.entry_precio.config(state="normal")
            self.entry_precio.delete(0, tk.END)
            self.entry_precio.insert(0, producto[5])
        conn.close()
        self.boton_actualizar.config(state="normal")
        self.boton_eliminar.config(state="normal")

    def actualizar_producto(self):
        id_producto = self.tree.item(self.tree.selection()[0], "tags")[0]
        nombre = self.entry_nombre.get()
        descripcion = self.entry_descripcion.get()
        peso = self.entry_peso.get()
        precio = self.entry_precio.get()
        conn = sqlite3.connect('productos.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET nombre=?, descripcion=?, peso=?, precio=? WHERE id=?", (nombre, descripcion, peso, precio, id_producto))
        conn.commit()
        conn.close()
        self.cargar_productos()
        self.limpiar()


    def eliminar_producto(self):
        id_producto = self.tree.item(self.tree.selection()[0], "tags")[0]
        conn = sqlite3.connect('productos.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id=?", (id_producto,))
        conn.commit()
        conn.close()
        self.cargar_productos()
        self.limpiar()
                
    def app_agregar_productos(self):
        ventana_agregar = tk.Toplevel(self.root)
        app_agregar = ProductoApp(ventana_agregar, self)

    def limpiar(self):
        self.entry_codigo.config(state="normal")
        self.entry_codigo.delete(0, tk.END)
        self.entry_codigo.config(state="readonly")
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.config(state="readonly")
        self.entry_descripcion.delete(0, tk.END)
        self.entry_descripcion.config(state="readonly")
        self.entry_peso.delete(0, tk.END)
        self.entry_peso.config(state="readonly")
        self.entry_precio.delete(0, tk.END)
        self.entry_precio.config(state="readonly")
        self.boton_actualizar.config(state="disabled")
        self.boton_eliminar.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualizacionEdicionProductosApp(root)
    root.mainloop()