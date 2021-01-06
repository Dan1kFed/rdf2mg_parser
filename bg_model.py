import peewee
from globals import *

psql_db = peewee.PostgresqlDatabase(
    BG_DATABASE,  # Required by Peewee.
    user=BG_USER,  # Will be passed directly to psycopg2.
    password=BG_PASSWORD,  # Ditto.
    host=BG_HOST,  # Ditto.
    port=BG_PORT)


class BaseModel(peewee.Model):
    """Базовая модель которая использует нащу БД"""

    class Meta:
        database = psql_db


class Subject(BaseModel):
    id = peewee.AutoField(primary_key=True)
    name = peewee.TextField(null=True)

    class Meta:
        table_name = 'subject'


class Predicate(BaseModel):
    id = peewee.AutoField(primary_key=True)
    name = peewee.TextField()

    class Meta:
        table_name = 'predicate'


class BGraph(BaseModel):
    id = peewee.AutoField(primary_key=True)
    subject_id = peewee.ForeignKeyField(Subject)
    predicate_id = peewee.ForeignKeyField(Predicate)
    object_name = peewee.TextField(null=True)

    class Meta:
        table_name = 'bgraph'

