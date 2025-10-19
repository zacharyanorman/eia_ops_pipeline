import os
from dotenv import load_dotenv

load_dotenv()
EIA_API_KEY = os.getenv('EIA_API_KEY')

print(EIA_API_KEY)