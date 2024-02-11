import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import sqlite3
from tkinter import simpledialog
import serial

import tkinter.messagebox as messagebox

class RegistroProductosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Productos")
        self.root.geometry("800x700")

        self.estilo = ThemedStyle(self.root)
        self.estilo.set_theme("plastik")

        self.productos_en_carrito = {}
        self.total_pagar = tk.DoubleVar()
        self.peso_total = 0.0
        self.peso_actual = tk.DoubleVar()
        self.peso_anterior = 0.0

        self.configurar_interfaz()

        self.conn = sqlite3.connect('productos.db')
        self.cursor = self.conn.cursor()

        self.puerto_serial = serial.Serial('COM5', 9600)

        self.root.after(100, self.leer_puerto_serial)

    def configurar_interfaz(self):
        self.frame_principal = ttk.Frame(self.root)
        self.frame_principal.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.lista_productos = ttk.Treeview(self.frame_principal, columns=("Nombre", "Descripción", "Precio", "Cantidad"))
        self.lista_productos.heading("#0", text="Código de Barras")
        self.lista_productos.heading("Nombre", text="Nombre")
        self.lista_productos.heading("Descripción", text="Descripción")
        self.lista_productos.heading("Precio", text="Precio")
        self.lista_productos.heading("Cantidad", text="Cantidad")
        self.lista_productos.column("#0", width=100, anchor=tk.CENTER)
        self.lista_productos.column("Nombre", width=150, anchor=tk.W)
        self.lista_productos.column("Descripción", width=200, anchor=tk.W)
        self.lista_productos.column("Precio", width=100, anchor=tk.E)
        self.lista_productos.column("Cantidad", width=100, anchor=tk.CENTER)
        self.lista_productos.pack(pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(self.frame_principal, text="Total a Pagar:").pack(pady=5)
        ttk.Entry(self.frame_principal, textvariable=self.total_pagar, state="readonly", font=("Arial", 12)).pack(pady=5)

        ttk.Label(self.frame_principal, text="Código de Barras:").pack(pady=5)
        self.codigo_barras_var = tk.StringVar()
        ttk.Entry(self.frame_principal, textvariable=self.codigo_barras_var, font=("Arial", 12)).pack(pady=5)
        ttk.Button(self.frame_principal, text="Escanear Producto", command=self.solicitar_peso).pack(pady=10)

        ttk.Button(self.frame_principal, text="Eliminar Producto", command=self.eliminar_producto_por_peso).pack(pady=5)

        self.btn_finalizar_compra = ttk.Button(self.frame_principal, text="Finalizar Compra", command=self.finalizar_compra, state="disabled")
        self.btn_finalizar_compra.pack(pady=10)

        self.etiqueta_mensaje = ttk.Label(self.frame_principal, text="")
        self.etiqueta_mensaje.pack(pady=10)

    def leer_puerto_serial(self):
        try:
            if self.puerto_serial.in_waiting > 0:
                peso_recibido = self.puerto_serial.readline().decode().strip()
                self.peso_actual = float(peso_recibido)
                print(self.peso_actual)
                #self.peso_actual.set(float(peso_recibido))

        except serial.SerialException:
            print("Error al leer del puerto serial")

        self.root.after(100, self.leer_puerto_serial)

    def solicitar_peso(self):
        codigo_barras = self.codigo_barras_var.get()

        self.cursor.execute('''
            SELECT nombre, descripcion, precio, peso
            FROM productos
            WHERE codigo_barras = ?
        ''', (codigo_barras,))

        resultado = self.cursor.fetchone()

        if resultado:
            nombre, descripcion, precio, peso_producto = resultado

            peso_calculado = peso_producto + self.peso_total

            mensaje = f"Coloque el producto en la balanza. Peso calculado: {peso_calculado:.2f}"
            confirmacion = messagebox.askquestion("Ubicar producto", mensaje)

            if confirmacion == "yes":
                try:
                    peso_actual_com5 = float(self.puerto_serial.readline().decode().strip())
                except (ValueError, TypeError):
                    self.etiqueta_mensaje.config(text="Error al obtener el peso del COM5.", foreground="red")
                    return

                margen_tolerancia = 0.2

                if abs(peso_actual_com5 - peso_calculado) <= margen_tolerancia:
                    if codigo_barras in self.productos_en_carrito:
                        self.productos_en_carrito[codigo_barras]['Cantidad'] += 1
                    else:
                        self.productos_en_carrito[codigo_barras] = {'Nombre': nombre, 'Descripción': descripcion,
                                                                    'Precio': precio, 'Cantidad': 1, 'Peso': peso_producto}

                    self.actualizar_lista_productos()

                    total_actual = self.total_pagar.get()
                    self.total_pagar.set(total_actual + precio)

                    self.peso_total += peso_producto

                    self.etiqueta_mensaje.config(text="")

                    self.btn_finalizar_compra.config(state="active")
                else:
                    self.etiqueta_mensaje.config(text="El peso del producto no coincide con el esperado.", foreground="red")
            else:
                self.etiqueta_mensaje.config(text="Operación cancelada.", foreground="orange")
        else:
            self.etiqueta_mensaje.config(text="Producto no encontrado en la base de datos.", foreground="red")

    def eliminar_producto_por_peso(self):
        codigo_barras = simpledialog.askstring("Eliminar Producto por Peso", "Ingrese el código de barras del producto:")

        if codigo_barras in self.productos_en_carrito:
            detalles = self.productos_en_carrito[codigo_barras]

            try:
                peso_a_eliminar = float(simpledialog.askstring("Eliminar Producto por Peso", f"Ingrese el peso a eliminar del producto '{detalles['Nombre']}':"))
            except (ValueError, TypeError):
                self.etiqueta_mensaje.config(text="Ingrese un valor válido para el peso.", foreground="red")
                return

            if peso_a_eliminar == detalles['Peso']:
                detalles['Cantidad'] -= 1

                if detalles['Cantidad'] == 0:
                    del self.productos_en_carrito[codigo_barras]
                else:
                    total_actual = self.total_pagar.get()
                    self.total_pagar.set(total_actual - detalles['Precio'])

                self.peso_total -= peso_a_eliminar

                self.actualizar_lista_productos()

                #self.peso_actual_label.config(text=self.peso_total)

                self.etiqueta_mensaje.config(text="")
            else:
                self.etiqueta_mensaje.config(text="El peso a eliminar no coincide con el peso del producto.", foreground="red")
        else:
            self.etiqueta_mensaje.config(text="Producto no encontrado en el carrito.", foreground="red")

    def finalizar_compra(self):
        if self.verificar_pesos_al_finalizar_compra():
            self.limpiar_interfaz()
            self.etiqueta_mensaje.config(text="Compra finalizada. ¡Gracias por su compra!", foreground="green")

            self.btn_finalizar_compra.config(state="disabled")

    def actualizar_lista_productos(self):
        for item in self.lista_productos.get_children():
            self.lista_productos.delete(item)

        for codigo_barras, detalles in self.productos_en_carrito.items():
            self.lista_productos.insert("", "end", text=codigo_barras,
                                        values=(detalles['Nombre'], detalles['Descripción'],
                                                detalles['Precio'], detalles['Cantidad']))
            
    def verificar_pesos_al_finalizar_compra(self):
        try:
            self.peso_actual = float(self.puerto_serial.readline().decode().strip())

        except (ValueError, TypeError):
            self.etiqueta_mensaje.config(text="Error al obtener el peso del COM5.", foreground="red")
            return False

        margen_tolerancia = 0.2

        if abs(self.peso_total - self.peso_actual) <= margen_tolerancia:
            return True
        else:
            self.etiqueta_mensaje.config(text="No se puede finalizar la compra. Los pesos no coinciden.", foreground="red")
            return False

    def limpiar_interfaz(self):
        for item in self.lista_productos.get_children():
            self.lista_productos.delete(item)

        self.total_pagar.set(0.0)
        self.peso_total = 0.0

        self.productos_en_carrito = {}

        self.codigo_barras_var.set("")
        self.etiqueta_mensaje.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroProductosApp(root)
    root.mainloop()
