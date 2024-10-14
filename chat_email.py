import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(
    subject,
    body,
    to_email,
    from_email,
    smtp_server,
    smtp_port,
    smtp_user,
    smtp_password,
):
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # Conectarse al servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)

    # Enviar el correo
    server.sendmail(from_email, to_email, msg.as_string())

    # Cerrar la conexión
    server.quit()
