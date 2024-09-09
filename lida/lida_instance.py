import os
from dotenv import load_dotenv


load_dotenv('../.env')

login = os.getenv('email_login')
password = os.getenv('email_password')
