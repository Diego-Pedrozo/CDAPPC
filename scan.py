import tkinter as tk
from tkinter import ttk
import pyautogui

#Instalar pyautogui
#pip install pyautogui

ruta_archivo = './codigos.txt'

class EscanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Escaner de Códigos de Barras")

        self.codigos_escaneados = []

        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.boton_scan = ttk.Button(self.frame, text="Scan", command=self.iniciar_escaneo)
        self.boton_scan.grid(column=0, row=0)

        self.lista_codigos = tk.Listbox(self.frame)
        self.lista_codigos.grid(column=0, row=1, pady=10, sticky=(tk.W, tk.E))

    def iniciar_escaneo(self):
        self.mostrar_conteo(3) 

    def mostrar_conteo(self, segundos_restantes):
        if segundos_restantes > 0:
            self.boton_scan.configure(state='disabled')  
            self.lista_codigos.insert(tk.END, f"Esperando... {segundos_restantes} segundos")
            self.root.after(1000, lambda: self.mostrar_conteo(segundos_restantes - 1))
        else:
            self.boton_scan.configure(state='normal') 
            self.lista_codigos.delete(0, tk.END)  
            self.realizar_escaneo()

    def realizar_escaneo(self):
        try:
            with open(ruta_archivo, "r") as file:
                codigos = file.readlines()

                for codigo in codigos:
                    codigo = codigo.strip()
                    pyautogui.write(codigo)
                    pyautogui.press('enter')
                    self.codigos_escaneados.append(codigo)
                    self.actualizar_lista_codigos()
                    self.root.update()

        except FileNotFoundError:
            print("No se encontró el archivo 'codigos.txt' en el escritorio.")

    def actualizar_lista_codigos(self):
        self.lista_codigos.delete(0, tk.END)

        for codigo in self.codigos_escaneados:
            self.lista_codigos.insert(tk.END, codigo)

if __name__ == "__main__":
    root = tk.Tk()
    app = EscanerApp(root)
    root.mainloop()
