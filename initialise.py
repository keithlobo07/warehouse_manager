import sqlite3
from func import *

db_connect()
create_tables()
init_database()
view_tables("suppliers")
view_tables("products")