import unittest
import os
from dotenv import load_dotenv
from fxiqoption.stable_api import IQ_Option

# Cargar variables de entorno desde .env
load_dotenv()

email = os.getenv("IQ_OPTION_EMAIL")
password = os.getenv("IQ_OPTION_PASSWORD")

if not email or not password:
    raise ValueError("Las variables de entorno email y password deben estar configuradas en el archivo .env")
class TestLogin(unittest.TestCase):
  
    def test_login(self):
        api = IQ_Option(email, password)
        try:
            api.connect(timeout=30)
            api.change_balance("PRACTICE")
        except Exception as e:
            self.fail(f"Error en la conexión: {str(e)}")
        api.reset_practice_balance()
        self.assertEqual(api.check_connect(), True)
         
  