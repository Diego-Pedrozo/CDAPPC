import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import uuid
from escpos.printer import Usb

class Ticket:
    def __init__(self, detalles_venta):
        #Info general
        self.nombre_comercio = "Mi Comercio"
        self.numero_factura = self.generar_numero_factura()
        self.fecha_hora = datetime.now()

        #Detalles venta
        # self.detalle_venta = [
        #     {"cantidad": 2, "descripcion": "Producto 1", "subtotal": 10.0},
        #     {"cantidad": 1, "descripcion": "Producto 2", "subtotal": 5.0}
        # ]
        self.detalle_venta = detalles_venta
        self.subtotal = sum(item["subtotal"] for item in self.detalle_venta)
        self.total = self.subtotal * 1.19
        
        self.texto_agradecimiento = "Gracias por su compra!"
        self.codigo_qr = self.generar_codigo_qr()

    def generar_numero_factura(self):
        numero_uuid = uuid.uuid4()
        numero_factura = abs(hash(numero_uuid))
        return numero_factura

    def generar_codigo_qr(self):
        return qrcode.make(f"Factura: {self.numero_factura}")

    def generar_imagen_ticket(self):
        imagen = Image.new("RGB", (400, 600), "white")
        draw = ImageDraw.Draw(imagen)

        #font_titulo = ImageFont.load_default(size=36, )
        #font_texto = ImageFont.load_default(size=12)
        font_titulo = ImageFont.truetype("arial.ttf", 36)
        font_normal = ImageFont.truetype("arial.ttf", 12)
        font_bold = ImageFont.truetype("arialbd.ttf", 14)
        font_media = ImageFont.truetype("arial.ttf", 20)
 
        y = 20
        draw.text((20, y), self.nombre_comercio, fill="black", font=font_titulo)
        y += 50
        draw.text((20, y), f"Fecha y Hora: {self.fecha_hora}", fill="black", font=font_normal)
        y += 20
        draw.text((20, y), f"# Factura: {self.numero_factura}", fill="black", font=font_normal)
        y += 30
        draw.text((20, y), "Detalles de la venta:", fill="black", font=font_normal)
        for item in self.detalle_venta:
            y += 20
            draw.text((40, y), f"{item['cantidad']} {item['descripcion']}: ${item['subtotal']}", fill="black", font=font_normal)
        y += 30
        draw.text((20, y), f"Subtotal: ${self.subtotal}", fill="black", font=font_normal)
        y += 20
        draw.text((20, y), f"Total: ${self.total}", fill="black", font=font_bold)
        y += 40
        draw.text((20, y), self.texto_agradecimiento, fill="black", font=font_media)

        qr_image = self.codigo_qr.resize((200, 200))
        imagen.paste(qr_image, (100, 400))

        return imagen
    
    def imprimir(self):
        try:
            printer = Usb(0x0416, 0x5011) #configurar los valores VID y PID de la impresora

            imagen_ticket = self.generar_imagen_ticket()

            printer.image(imagen_ticket)

            printer.cut()
            
            printer.close()

            print("Ticket impreso exitosamente")

        except Exception as e:
            print(f"Error al imprimir el ticket: {str(e)}")

# ticket = Ticket()
# imagen_ticket = ticket.generar_imagen_ticket()
# imagen_ticket.show()
