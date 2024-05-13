


from flask_mail import Message, Mail
from models import app
from os import getenv
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv

load_dotenv()


app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=587
sender_email = getenv('EMAIL')
sender_password = getenv('PASSWORD')
app.config["MAIL_USERNAME"]=sender_email
app.config['MAIL_PASSWORD']=sender_password
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False
# app.config['MAIL_DEBUG'] = True

mail = Mail(app)


class Mailer:
    uri = getenv('PRODUCTION_URI')
    def __init__(self, recipient, subject='Verify Email') -> None:
        if not isinstance(subject, str):
            raise TypeError('subject must be string')
        if not isinstance(recipient, str):
            raise TypeError('recipient must be string')
        self.__token = None
        self.__subject = subject
        self.__recipient = recipient

    def set_token(self):
        serializer = URLSafeTimedSerializer(secret_key=getenv('SECRET_KEY'))
        self.__token = serializer.dumps(self.__recipient,
                                        salt=getenv('EMAIL_SALT'))
        return self.__token

    def set_body(self):
        if self.__token is not None:
            self.__body = f'''
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Email Verification</title>
                    </head>
                    <body>
                        <div style="max-width: 600px; margin: 0 auto;">
                            <h2>Email Verification</h2>
                            <p>Thank you for registering. To complete your registration, please click the link below to verify your email address:</p>
                            <p><a href="{self.uri}{self.__token}">Verify Email</a></p>
                            <p>If you didn't register on our website, you can safely ignore this email.</p>
                            <p>Best regards,<br></p>
                        </div>
                    </body>
                    </html>

                    '''
    def send_mail(self):
        msg = Message(subject=self.__subject,
                      sender='Noreply@attendance.com',
                      recipients=[self.__recipient])
        msg.html = self.__body
        mail.send(msg)
        return

    @staticmethod
    def get_email(token):
        serializer = URLSafeTimedSerializer(secret_key=getenv('SECRET_KEY'))
        return serializer.loads(token,
                                salt=getenv('EMAIL_SALT'),
                                max_age=3600)