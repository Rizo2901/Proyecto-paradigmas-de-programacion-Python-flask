import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Servicio para envío de correos electrónicos"""
    
    # Configuración SMTP (se puede usar Gmail, Outlook, etc.)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Pokemon Carts - Tienda Online")
    
    @staticmethod
    def enviar_confirmacion_pedido(email_destino, nombre_cliente, id_pedido, total, detalles_items=None):
        """
        Envía un correo de confirmación de pedido al cliente.
        
        Args:
            email_destino: Email del cliente
            nombre_cliente: Nombre del cliente
            id_pedido: Número de pedido
            total: Total del pedido
            detalles_items: Lista de items del pedido (opcional)
        """
        if not email_destino or not EmailService.SMTP_USER:
            print(f"[EmailService] No se puede enviar correo: email_destino={email_destino}, SMTP configurado={bool(EmailService.SMTP_USER)}")
            return {"error": "Configuración de correo incompleta"}
        
        try:
            # Crear el mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'✅ Confirmación de Pedido #{id_pedido} - Pokemon Carts'
            msg['From'] = f"{EmailService.SMTP_FROM_NAME} <{EmailService.SMTP_USER}>"
            msg['To'] = email_destino
            
            # Crear lista de productos si hay detalles
            productos_html = ""
            if detalles_items:
                productos_html = "<ul style='list-style: none; padding: 0;'>"
                for item in detalles_items:
                    nombre = item.get('NombreProducto', f"Producto {item.get('IdProducto', 'N/A')}")
                    cantidad = item.get('Cantidad', 1)
                    subtotal = item.get('Subtotal', 0)
                    productos_html += f"""
                    <li style='padding: 10px; border-bottom: 1px solid #eee;'>
                        <strong>{nombre}</strong> x {cantidad} - ₡{subtotal:.2f}
                    </li>
                    """
                productos_html += "</ul>"
            
            # Contenido HTML del correo
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">🎴 Pokemon Carts</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Tu tienda de cartas Pokémon</p>
                    </div>
                    
                    <!-- Contenido -->
                    <div style="padding: 30px;">
                        <h2 style="color: #333; margin-top: 0;">¡Hola {nombre_cliente}! 👋</h2>
                        
                        <p style="color: #555; font-size: 16px; line-height: 1.6;">
                            ¡Gracias por tu compra! Hemos recibido tu pedido correctamente.
                        </p>
                        
                        <!-- Info del pedido -->
                        <div style="background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); border-radius: 12px; padding: 20px; margin: 20px 0; color: white;">
                            <h3 style="margin: 0 0 15px 0;">📦 Detalles del Pedido</h3>
                            <p style="margin: 5px 0;"><strong>Número de Pedido:</strong> #{id_pedido}</p>
                            <p style="margin: 5px 0;"><strong>Total:</strong> ₡{total:.2f}</p>
                            <p style="margin: 5px 0;"><strong>Estado:</strong> Pendiente de pago</p>
                        </div>
                        
                        {f'<div style="margin: 20px 0;"><h3 style="color: #333;">🛒 Productos:</h3>{productos_html}</div>' if productos_html else ''}
                        
                        <!-- Siguiente paso -->
                        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                            <h4 style="color: #856404; margin: 0 0 10px 0;">⏳ ¿Qué sigue?</h4>
                            <p style="color: #856404; margin: 0; font-size: 14px;">
                                Pronto nos pondremos en contacto contigo para gestionar el pago de tu pedido. 
                                Puedes responder a este correo si tienes alguna pregunta.
                            </p>
                        </div>
                        
                        <p style="color: #555; font-size: 14px; line-height: 1.6;">
                            Si tienes alguna duda sobre tu pedido, no dudes en contactarnos.
                        </p>
                        
                        <p style="color: #333; margin-top: 30px;">
                            ¡Gracias por confiar en nosotros! 🙏<br>
                            <strong>El equipo de Pokemon Carts</strong>
                        </p>
                    </div>
                    
                    <!-- Footer -->
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                        <p style="color: #888; font-size: 12px; margin: 0;">
                            Este es un correo automático, por favor no respondas directamente.<br>
                            © 2025 Pokemon Carts - Tienda Online
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Contenido texto plano (fallback)
            text_content = f"""
            ¡Hola {nombre_cliente}!
            
            ¡Gracias por tu compra! Hemos recibido tu pedido correctamente.
            
            DETALLES DEL PEDIDO:
            - Número de Pedido: #{id_pedido}
            - Total: ₡{total:.2f}
            - Estado: Pendiente de pago
            
            ¿QUÉ SIGUE?
            Pronto nos pondremos en contacto contigo para gestionar el pago de tu pedido.
            
            Si tienes alguna duda sobre tu pedido, no dudes en contactarnos.
            
            ¡Gracias por confiar en nosotros!
            El equipo de Pokemon Carts
            """
            
            # Adjuntar contenido
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar el correo
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.SMTP_USER, EmailService.SMTP_PASSWORD)
                server.sendmail(EmailService.SMTP_USER, email_destino, msg.as_string())
            
            print(f"[EmailService] ✅ Correo enviado exitosamente a {email_destino}")
            return {"success": True, "message": f"Correo enviado a {email_destino}"}
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EmailService] ❌ Error de autenticación SMTP: {str(e)}")
            return {"error": "Error de autenticación con el servidor de correo"}
        except smtplib.SMTPException as e:
            print(f"[EmailService] ❌ Error SMTP: {str(e)}")
            return {"error": f"Error al enviar correo: {str(e)}"}
        except Exception as e:
            print(f"[EmailService] ❌ Error inesperado: {str(e)}")
            return {"error": f"Error inesperado: {str(e)}"}

