from peewee import *

database = MySQLDatabase('mgtoa_vessels', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': 'localhost', 'port': 3306, 'user': 'linus', 'password': 'R00t247'})

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

    class Meta:
        table_name = 'toa_ship'

class ToaArrival(BaseModel):
    date_arrival = DateTimeField()
    ship = ForeignKeyField(column_name='ship', field='id', model=ToaShip, null=True)

    class Meta:
        table_name = 'toa_arrival'

