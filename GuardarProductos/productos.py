import tkinter as tk
import sqlite3
import serial

class ProductoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registrar Productos")

        self.frame = tk.Frame(self.root, padx=30, pady=10)
        self.frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.label_codigo = tk.Label(self.frame, text="Código de Barras:")
        self.label_codigo.grid(column=0, row=0, pady=5, sticky=tk.W)

        self.entry_codigo = tk.Entry(self.frame)
        self.entry_codigo.grid(column=1, row=0, pady=5, sticky=tk.W)

        self.label_nombre = tk.Label(self.frame, text="Nombre:")
        self.label_nombre.grid(column=0, row=1, pady=5, sticky=tk.W)

        self.entry_nombre = tk.Entry(self.frame)
        self.entry_nombre.grid(column=1, row=1, pady=5, sticky=tk.W)

        self.label_descripcion = tk.Label(self.frame, text="Descripción:")
        self.label_descripcion.grid(column=0, row=2, pady=5, sticky=tk.W)

        self.entry_descripcion = tk.Entry(self.frame)
        self.entry_descripcion.grid(column=1, row=2, pady=5, sticky=tk.W)

        self.label_peso = tk.Label(self.frame, text="Peso:")
        self.label_peso.grid(column=0, row=3, pady=5, sticky=tk.W)

        self.entry_peso = tk.Entry(self.frame)
        self.entry_peso.grid(column=1, row=3, pady=5, sticky=tk.W)

        self.label_precio = tk.Label(self.frame, text="Precio:")
        self.label_precio.grid(column=0, row=4, pady=5, sticky=tk.W)

        self.entry_precio = tk.Entry(self.frame)
        self.entry_precio.grid(column=1, row=4, pady=5, sticky=tk.W)

        self.boton_guardar = tk.Button(self.frame, text="Guardar Producto", command=self.guardar_producto)
        self.boton_guardar.grid(column=0, row=5, columnspan=2, pady=10)

        self.inicializar_base_datos()

        self.serial_port = serial.Serial('COM5', baudrate=9600, timeout=1)

        self.root.after(100, self.leer_puerto_serial)

        self.leer_siguiente_codigo()

        self.entry_codigo.focus_set()

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

    def guardar_producto(self):
        codigo_barras = self.entry_codigo.get()
        nombre = self.entry_nombre.get()
        descripcion = self.entry_descripcion.get()
        peso = float(self.entry_peso.get())
        precio = float(self.entry_precio.get())

        if not self.codigo_barras_existente(codigo_barras):
            self.cursor.execute('''
                INSERT INTO productos (codigo_barras, nombre, descripcion, peso, precio)
                VALUES (?, ?, ?, ?, ?)
            ''', (codigo_barras, nombre, descripcion, peso, precio))

            self.conn.commit()

            self.entry_codigo.delete(0, tk.END)
            self.entry_nombre.delete(0, tk.END)
            self.entry_descripcion.delete(0, tk.END)
            self.entry_peso.delete(0, tk.END)
            self.entry_precio.delete(0, tk.END)

            self.leer_siguiente_codigo()
            self.entry_codigo.focus_set()
        else:
            print(f"El código de barras {codigo_barras} ya existe en la base de datos.")

    def codigo_barras_existente(self, codigo_barras):
        self.cursor.execute('SELECT COUNT(*) FROM productos WHERE codigo_barras = ?', (codigo_barras,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def leer_siguiente_codigo(self):
        ruta_archivo = './GuardarProductos/codigos.txt'
        try:
            if not hasattr(self, 'indice_codigo'):
                self.indice_codigo = 0

            with open(ruta_archivo, 'r') as file:
                codigos = [line.strip() for line in file.readlines()]

            if codigos and self.indice_codigo < len(codigos):
                proximo_codigo = codigos[self.indice_codigo]
                self.entry_codigo.delete(0, tk.END)
                self.entry_codigo.insert(tk.END, proximo_codigo)

                print(codigos[self.indice_codigo + 1:])

                self.indice_codigo += 1
            else:
                print("No hay más códigos en el txt.")

        except FileNotFoundError:
            print("No se encontró el archivo de códigos.")

    
    def leer_puerto_serial(self):
        try:
            if self.serial_port.in_waiting > 0:
                peso_serial = self.serial_port.readline().decode().strip()
                print(peso_serial)

                self.entry_peso.delete(0, tk.END)
                self.entry_peso.insert(tk.END, peso_serial)
        except serial.SerialException:
            print("Error al leer del puerto serial")

        self.root.after(100, self.leer_puerto_serial)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductoApp(root)
    root.mainloop()
