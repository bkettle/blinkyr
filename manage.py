import argparse
from peewee import *
from playhouse.db_url import connect

from models import db, Page, FlashObject

def create_tables(recreate=False):
    tables = [Page, FlashObject]
    with db:
        if recreate:
            print("Dropping Database Tables", flush=True)
            db.drop_tables(tables)
        print("Creating Database Tables")
        db.create_tables(tables)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='commands')
parser_create = subparsers.add_parser("create", help="create the database tables")
parser_create.set_defaults(func=create_tables) # create tables without dropping
parser_reset = subparsers.add_parser("reset", help="drop all old tables before creating new ones")
parser_reset.set_defaults(func=lambda: create_tables(True)) # drop and create tables
args = parser.parse_args()

args.func()
