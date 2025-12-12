"""
---main2.py---
This is the main interface for the warehouse manager application.
It allows users to interact with the system through a menu-driven approach.
"""

import sqlite3
from db_func import *
from setGrid import *
from search import a_star_search
from func import *

print('---------------------WAREHOUSE MANAGER-----------------------\n')
print("Welcome to Warehouse Manager!\n")

while True:
    menu()
    choice = int(input("Choose an option: "))
    
    match choice:
        case 1:
            print("------------------Add supplier------------------\n")
            # Input and Input validation for supplier details
            supID = input("Enter Supplier ID: ")
            if not supID.isdigit():
                print("Supplier ID must be numeric.\n")
                continue
            supName = input("Enter Supplier Name: ")
            contactName = input("Enter Contact Name: ")
            contactEmail = input("Enter Contact Email: ")
            # Call function to add supplier
            add_supplier(supID, supName, contactName, contactEmail)
        case 2:
            print("------------------Remove supplier------------------\n")
            # Input and Input validation for supplier ID
            supID = input("Enter Supplier ID to remove: ")
            if not supID.isdigit():
                print("Supplier ID must be numeric.\n")
                continue
            # Call function to remove supplier
            remove_supplier(supID)
        case 3:
            print("------------------View suppliers------------------\n")
            # Call function to view suppliers
            view_tables("suppliers")
        case 4:
            print("--------------------Add product--------------------\n")
            # Call function to add product
            prodID = input("Enter Product ID: ")
            if not prodID.isdigit():
                print("Product ID must be numeric.\n")
                continue
            prodName = input("Enter Product Name: ")
            ean = input("Enter EAN: ")
            price = int(input("Enter Price: "))
            supID = input("Enter Supplier ID: ")
            if not supID.isdigit():
                print("Supplier ID must be numeric.\n")
                continue
            add_product(prodID, prodName, ean, price, supID)
        case 5:
            print("-----------------Remove product-----------------\n")
            # Call function to remove product
            prodID = input("Enter Product ID to remove: ")
            if not prodID.isdigit():
                print("Product ID must be numeric.\n")
                continue
            remove_product(prodID)
        case 6:
            print("-----------------View products-----------------\n")
            # Call function to view products
            view_tables("products")
        case 7:
            print("-----------------Update stock-----------------\n")
            # Call function to update stock
            itemID = input("Enter Item ID to update stock: ")
            if not itemID.isdigit():
                print("Item ID must be numeric.\n")
                continue
            quantity = int(input("Enter new stock quantity: "))
            if not quantity.isdigit():
                print("Quantity must be numeric.\n")
                continue
            if int(quantity) < 0:
                print("Quantity cannot be negative.\n")
                continue
            update_stock(prodID, quantity)
        case 8:
            print("-----------------Perform stock check-----------------\n")
            # Call function to perform stock check
            stock_check()
        case 9:
            print("-----------------View stock for itemID-----------------\n")
            # Call function to view stock for specific itemID
            prodID = input("Enter Product ID to view stock: ")
            if not prodID.isdigit():
                print("Product ID must be numeric.\n")
                continue
            view_stock(prodID)
        case 10:
            print("-----------------Find item in warehouse-----------------\n")
            # Call function to find item in warehouse
            #run inference.py
            import os
            os.system("python inference.py")
            print("Inference complete. Check 'grid_data1.json' for results.\n")
        case 0:
            print("EXITING\n")
            exit(0)
        case _:
            print("Invalid choice. Please choose again.\n")

db_close(conn)