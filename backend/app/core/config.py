import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / '.env')


DB_USER = os.getenv('POSTGRES_USER', 'sentinel')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'sentinel')
DB_NAME = os.getenv('POSTGRES_DB', 'sentinel')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

DATABASE_URL = (
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}'
    f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# arquivo de origem usado pelo pipeline de ingestao
SOURCE_FILE = BASE_DIR / 'data' / 'LW-DATASET.xlsx'