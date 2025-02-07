from peewee import *
import os

database = MySQLDatabase(
    'mgtoa_vessels', 
    **{
        'charset': 'utf8', 
        'sql_mode': 'PIPES_AS_CONCAT',
        'use_unicode': True, 
        'host': 'localhost', 
        'port': 3306, 
        'user': os.getenv("DB_USER"), 
        'password': os.getenv("DB_PWD")
    }
)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class ToaShip(BaseModel):
    call_sign = CharField()
    flag = CharField(null=True)
    flag_url = CharField(null=True)
    gross_tonnage = IntegerField(null=True)
    imo = CharField(null=True, unique=True)
    ship_type = CharField(null=True)
    year = CharField(null=True)

    class Meta:
        table_name = 'toa_ship'

class ToaSchedule(BaseModel):
    schedule_date = DateTimeField()
    ship = ForeignKeyField(column_name='ship', field='id', model=ToaShip, null=True)
    schedule_type = CharField(null=True)

    class Meta:
        table_name = 'toa_schedule'

