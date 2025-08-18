# Email utilities
import smtplib
from email.mime.text import MIMEText

def send_credentials(email, password, name):
    msg = MIMEText(f'Hello {name},\nYour IQAC portal login credentials are:\nEmail: {email}\nPassword: {password}')
    msg['Subject'] = 'IQAC Portal Credentials'
    msg['From'] = 'noreply@iqac.in'
    msg['To'] = email

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('your_email@gmail.com', 'your_app_password')
    s.send_message(msg)
    s.quit()
