# wsgi.py

from dotenv import load_dotenv
load_dotenv()

from application import create_app
app = create_app()
