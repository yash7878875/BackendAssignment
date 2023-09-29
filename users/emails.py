import random
from django.core.mail import send_mail
from BackendAssignment import settings
from .models import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP


def send_otp_via_email(email, forgot):
    if forgot:

        otp = random.randint(100000, 999999)
        user_obj = User.objects.get(email=email)
        user_obj.forgot_otp = str(otp)
        user_obj.save()

        EMAIL_CONFIRMATION_MSG = "<p>your otp is: {otp}</p><br>"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your Forgot Password Otp emails'
        msg['to'] = email
        SERVER = "localhost"
        FROM = "test@yopmail.com"
        TO = email
        part1 = MIMEText(EMAIL_CONFIRMATION_MSG.format(otp=otp), 'html')
        msg.attach(part1)

        # Send the mail
        server = SMTP(SERVER)
        server.sendmail(FROM, TO, msg.as_string())

        user_obj = User.objects.get(email=email)
        user_obj.forgot_otp = str(otp)
        user_obj.save()

        server.quit()
    else:

        otp = random.randint(100000, 999999)
        user_obj = User.objects.get(email=email)
        user_obj.otp = str(otp)
        user_obj.save()
        EMAIL_CONFIRMATION_MSG = "<p>your otp is: {otp}</p><br>"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your account verification emails'
        msg['to'] = email
        SERVER = "localhost"
        FROM = "test@yopmail.com"
        TO = email
        part1 = MIMEText(EMAIL_CONFIRMATION_MSG.format(otp=otp), 'html')
        msg.attach(part1)

        # Send the mail
        server = SMTP(SERVER)
        server.sendmail(FROM, TO, msg.as_string())

        user_obj = User.objects.get(email=email)
        user_obj.otp = str(otp)
        user_obj.save()

        server.quit()
