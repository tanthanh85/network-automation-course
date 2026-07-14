from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file

usernam = os.getenv("username")
password = os.getenv("password")
