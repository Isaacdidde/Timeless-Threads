import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email, subject, message):
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    email_host = os.getenv("EMAIL_HOST")
    email_port = int(os.getenv("EMAIL_PORT"))

    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "html"))

    try:
        server = smtplib.SMTP(email_host, email_port)
        server.starttls()
        server.login(email_user, email_pass)
        server.sendmail(email_user, to_email, msg.as_string())
        server.quit()
        print("✔ Email Sent")
        return True
    except Exception as e:
        print("✘ Email Failed:", e)
        return False
