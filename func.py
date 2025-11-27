import sqlite3
from tabulate import tabulate

'''---Database Connection---'''

def db_connect():
    global conn, cursor
    conn = sqlite3.connect('warehouse.db')
    cursor = conn.cursor()
    conn.commit()
    return conn

'''---Create Tables---'''

def create_tables():
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS suppliers(
                    supplierID INTEGER(10) UNIQUE PRIMARY KEY,
                    supplierName TEXT NOT NULL,
                    contactName TEXT,
                    phone TEXT
                    )
                    '''
                  )
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products(
                    productID INTEGER(10) UNIQUE PRIMARY KEY,
                    productName TEXT NOT NULL UNIQUE,
                    ean INTEGER(13) NOT NULL UNIQUE,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    supplierID INTEGER(10),
                    FOREIGN KEY (supplierID) REFERENCES suppliers(supplierID)
                    )
                    '''
                  )
    conn.commit()
  

#util function

def view_tables():
    cursor.execute("SELECT * FROM products;")
    products = cursor.fetchall()
    print("Products Table:")
    print(tabulate(products, headers=["Product ID", "Product Name", "EAN", "Quantity", "Price", "Supplier ID"], tablefmt="grid"))
