import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from fastapi import HTTPException
import os

def send_email(to_email: str, subject: str, participant_name: str):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        from_email = "contato01mulheresconnectadas@gmail.com"
        from_password = "vrhm dubd xxgs nuld"

        # Criação da mensagem principal
        msg = MIMEMultipart('related')
        msg["From"] = formataddr(("Equipe Mulheres Conectadas", from_email))
        msg["To"] = to_email
        msg["Subject"] = subject

        # Parte alternativa para texto puro e HTML
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)

        # Corpo do e-mail em HTML
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <p>Olá {participant_name},</p>
            <div style="text-align: center; margin: 20px 0;">
                <img src="cid:logo" style="width: 100%; max-width: 500px; height: auto;"/>
            </div>
            <p>Caso tenha dúvidas, você pode responder este e-mail.</p>
            <p>Atenciosamente,<br>Equipe Mulheres Conectadas</p>
        </body>
        </html>
        """
        msg_alternative.attach(MIMEText(html_body, 'html'))

        # Adiciona a imagem como parte relacionada
        image_path = "api/static/images/logo.jpeg"
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            img = MIMEImage(img_data, name="logo.jpeg")
            
            # Configuração dos headers para evitar o "noname"
            img.add_header('Content-ID', '<logo>')
            img.add_header('Content-Disposition', 'inline', filename='logo.jpeg')
            img.add_header('Content-Type', 'image/jpeg')
            img.add_header('X-Attachment-Id', 'logo')
            img.set_param('name', 'logo.jpeg')
            img.set_param('filename', 'logo.jpeg')
            
            msg.attach(img)

        # Envia o e-mail
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {e}")