import os

BG_DATABASE = os.getenv('DATABASE_NAME', default='test_graph_db')
BG_USER = os.getenv('DATABASE_USER', default='postgres')
BG_PASSWORD = os.getenv('DATABASE_PASSWORD', default='admin')
BG_HOST = os.getenv('DATABASE_HOST', default='localhost')
BG_PORT = os.getenv('DATABASE_PORT', default='5432')
MG_DATABASE = os.getenv('DATABASE_NAME', default='test_graph_db')
MG_USER = os.getenv('DATABASE_USER', default='postgres')
MG_PASSWORD = os.getenv('DATABASE_PASSWORD', default='admin')
MG_HOST = os.getenv('DATABASE_HOST', default='localhost')
MG_PORT = os.getenv('DATABASE_PORT', default='5432')
