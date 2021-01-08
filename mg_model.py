import peewee
from globals import *

psql_db = peewee.PostgresqlDatabase(
    MG_DATABASE,  # Required by Peewee.
    user=MG_USER,  # Will be passed directly to psycopg2.
    password=MG_PASSWORD,  # Ditto.
    host=MG_HOST,  # Ditto.
    port=MG_PORT)


class BaseModel(peewee.Model):
    """Базовая модель которая использует нащу БД"""

    class Meta:
        database = psql_db


class Vertex(BaseModel):
    id = peewee.AutoField(primary_key=True)
    name = peewee.TextField(null=True)
    attribute_prefix = peewee.TextField(null=True)
    attribute_value = peewee.TextField(null = True)

    class Meta:
        table_name = 'vertex'


class Edge(BaseModel):
    id = peewee.AutoField(primary_key=True)
    name = peewee.TextField()
    from_vertex_id = peewee.ForeignKeyField(Vertex)
    to_vertex_id = peewee.ForeignKeyField(Vertex)

    class Meta:
        table_name = 'edge'


class Relations(BaseModel):
    id = peewee.AutoField(primary_key=True)
    name = peewee.TextField()
    higher_vertex_id = peewee.ForeignKeyField(Vertex)
    lower_vertex_id = peewee.ForeignKeyField(Vertex)

    class Meta:
        table_name = 'relations'
