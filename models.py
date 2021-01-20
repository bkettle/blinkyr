from peewee import *
from playhouse.db_url import connect
import os
import datetime

db = connect(os.environ['DATABASE_URL'])

# db models
class BaseModel(Model):
    class Meta:
        database = db

class Page(BaseModel):
    source_url = CharField(unique=True)
    pid = IntegerField(unique=True)
    timestamp = TimestampField(default=datetime.datetime.now)
    title = CharField(unique=True)

class FlashObject(BaseModel):
    page = ForeignKeyField(Page, backref='objects')
    oid = IntegerField()
    swf_url = CharField()
    title = CharField()
