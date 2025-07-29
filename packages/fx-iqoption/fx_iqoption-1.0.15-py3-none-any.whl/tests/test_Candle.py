import unittest
import os
from dotenv import load_dotenv
from fxiqoption.stable_api import IQ_Option
import logging
import time
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')

# Cargar variables de entorno desde .env
load_dotenv()

email = os.getenv("IQ_OPTION_EMAIL")
password = os.getenv("IQ_OPTION_PASSWORD")

if not email or not password:
    raise ValueError("Las variables de entorno email y password deben estar configuradas en el archivo .env")
class TestCandle(unittest.TestCase):
  
    def test_Candle(self):
        #login
        api = IQ_Option(email, password)
        try:
            api.connect(timeout=30)
            api.change_balance("PRACTICE")
        except Exception as e:
            self.fail(f"Error en la conexión: {str(e)}")
        api.reset_practice_balance()
        self.assertEqual(api.check_connect(), True)
        #start test binary option
        ALL_Asset=api.get_all_open_time()
        if ALL_Asset["turbo"]["EURUSD"]["open"]:
            ACTIVES="EURUSD"
        else:
            ACTIVES="EURUSD-OTC"

        api.get_candles(ACTIVES, 60, 1000, time.time())
        #realtime candle
        size="all"
        api.start_candles_stream(ACTIVES,size,10)
        api.get_realtime_candles(ACTIVES,size)
        api.stop_candles_stream(ACTIVES,size)

