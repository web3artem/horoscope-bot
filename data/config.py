import os

from dotenv import load_dotenv

load_dotenv()

# Получаем токен бота
API_TOKEN = os.getenv("API_TOKEN")

# Список администраторов
ADMINS = [6083753042, 645837666, 1590165003]

# БД
ip = os.getenv('ip')
PGUSER = str(os.getenv('PGUSER'))
PGPASSWORD = str(os.getenv('PGPASSWORD'))
DATABASE = str(os.getenv('DATABASE'))

POSTGRES_URI = f"postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}"
