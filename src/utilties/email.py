import smtplib
from email.message import EmailMessage
from utilties.constants import Constants
from celery import Celery
from config import SMTP_USER, SMTP_PASSWORD

celery = Celery("tasks", broker="redis://localhost:6379")


class Email:
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 465

    @staticmethod
    def get_email_template(username: str, subject: str, email_destiny: str, token: str or None):
        email = EmailMessage()
        email['Subject'] = subject
        email['From'] = SMTP_USER
        email['To'] = email_destiny
        if subject == Constants.EMAIL_CONFIRM:
            email.set_content(
                f'''<center><div dir="rtl">
                <h1>ثوثيق البريد الإلكتروني</h1>
                <h2>مرحبا {username}</h2>
                <p>شكرا لاختيارك خدماتنا, الرجاء توثيق البريد الإلكتروني من خلال الضغط على الرابط أدناه</p>
                <a href=http://localhost:8000/auth/verify?token={token}><p>اضغط هنا</p></a>
                </div><center>''',
                subtype='html'
            )
        elif subject == Constants.RESET_PASSWORD:
            email.set_content(
                f'''<center><div dir="rtl">
                <h1>إعادة تعيين كلمة المرور</h1>
                <h2>مرحبا {username}</h2>
                <p>الرجاء نسخ الرمز الآتي ولصقه في التطيبق من أجل إعادة تعيين كلمة المرور</p>
                <p>{token}</p>
                </div></center>''',
                subtype='html'
            )

        return email


@celery.task()
def send_email(username: str, subject, email_destiny: str, token: str or None):
    email = Email.get_email_template(username, subject, email_destiny, token)
    with smtplib.SMTP_SSL(Email.SMTP_HOST, Email.SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)
