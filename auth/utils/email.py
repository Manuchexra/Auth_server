import os 
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.EMAIL_USER,
    MAIL_PASSWORD=config.EMAIL_PASSWORD,
    MAIL_FROM=config.EMAIL_FROM,
    MAIL_PORT=config.EMAIL_PORT,
    MAIL_SERVER=config.EMAIL_HOST_USER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_verify_email(email_to: str, token: str):
    verify_link = f"http://localhost:8000/auth/verify-email?token={token}"
    html = f"""
    <html>
    <body>
        <h2>Email tasdiqlash</h2>
        <p>Iltimos, quyidagi link orqali emailingizni tasdiqlang:</p>
        <a href = "{verify_link}">{verify_link}</a>
        <p>Link 1 kun davomida amal qiladi.</p>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Email tasdiqlash",
        recipients=[email_to],
        body=html,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)