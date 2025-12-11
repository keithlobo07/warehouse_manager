# initialise.py
# RUN THIS FILE FIRST TO SET UP THE DATABASE
# (Also, run every time you want to reset the database)

import sqlite3
from db_func import *

db_connect()
reset_tables()
create_tables()
init_database()
db_close()