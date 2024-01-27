#Instalar pyserial
#pip install pyserial


import tkinter as tk
from tkinter import ttk
import serial
import threading
import time

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comunicador serial")

        self.serial_port = None
        self.sending_thread = None
        self.sending = False

        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.connect_button = ttk.Button(self.frame, text="Connect", command=self.connect_serial)
        self.connect_button.grid(column=0, row=0)

        self.send_button = ttk.Button(self.frame, text="Send", command=self.send_data)
        self.send_button.grid(column=1, row=0)

        self.text_entry = ttk.Entry(self.frame)
        self.text_entry.grid(column=0, row=1, pady=10, columnspan=2, sticky=(tk.W, tk.E))

    def connect_serial(self):
        try:
            if self.serial_port is not None and self.serial_port.is_open:
                self.serial_port.close()
            self.serial_port = serial.Serial('COM5', baudrate=9600, timeout=1)
            print("Connected to COM5")
        except serial.SerialException:
            print("Error connecting to COM5")

    def send_data(self):
        data = self.text_entry.get()
        if self.serial_port is not None and self.serial_port.is_open:
            if self.sending_thread and self.sending_thread.is_alive():
                self.sending = False 
                self.sending_thread.join()

            self.sending = True
            self.sending_thread = threading.Thread(target=self._send_data_continuously, args=(data,), daemon=True)
            self.sending_thread.start()
            print(f"Sending data continuously: {data}")
        else:
            print("Not connected to COM5")

    def _send_data_continuously(self, data):
        while self.sending:
            try:
                self.serial_port.write((data + "\n").encode())
                time.sleep(0.1)
                print(f"Sent data: {data}")
            except serial.SerialException:
                print("Error writing to COM5")
                break 

    def on_closing(self):
        if self.sending:
            self.sending = False
            self.sending_thread.join()
        if self.serial_port is not None and self.serial_port.is_open:
            self.serial_port.close()
            print("Connection to COM5 closed")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
