import os
from dotenv import load_dotenv


load_dotenv('../.env')

login = os.getenv('EMAIL_LOGIN')
password = os.getenv('EMAIL_PASSWORD')
