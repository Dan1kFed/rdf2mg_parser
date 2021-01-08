import os

BG_DATABASE = os.getenv('DATABASE_NAME', default='db_bg')
BG_USER = os.getenv('DATABASE_USER', default='admin')
BG_PASSWORD = os.getenv('DATABASE_PASSWORD', default='123456789')
BG_HOST = os.getenv('DATABASE_HOST', default='localhost')
BG_PORT = os.getenv('DATABASE_PORT', default='5432')

MG_DATABASE = os.getenv('DATABASE_NAME', default='db_mg')
MG_USER = os.getenv('DATABASE_USER', default='admin')
MG_PASSWORD = os.getenv('DATABASE_PASSWORD', default='123456789')
MG_HOST = os.getenv('DATABASE_HOST', default='localhost')
MG_PORT = os.getenv('DATABASE_PORT', default='5432')
