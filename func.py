"""
--- func.py ---
Various helper functions for the warehouse manager application.
"""

import sqlite3
from tabulate import tabulate
import time
import random
from db_func import *
from setGrid import *
from search import a_star_search

conn, cursor = db_connect()

def menu():
    print('---------------------MENU-----------------------\n')
    print("1. Add supplier")
    print("2. Remove supplier")
    print("3. View suppliers")
    print("4. Add product")
    print("5. Remove product")
    print("6. View products")
    print("7. Update stock")
    print("8. Perform stock check")
    print("9. View stock for itemID")
    print("10. Find item in warehouse")
    
    print("0. Exit\n")

def grid_to_json(grid, start, target_item, filename='grid_data1.json'):
    """
    Save the warehouse grid, start position, and target item to a JSON file.
    
    :param grid: 2D list representing the warehouse grid
    :param start: Tuple (x, y) representing the robot's starting position
    :param target_item: Integer representing the target item ID
    :param filename: Name of the JSON file to save the data
    """
    import json
    data = {
        "grid": grid,
        "start": start,
        "target_item": target_item
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def stock_check():
    """
    Perform a stock check to identify low stock items and expiring items.
    Prints a table of low stock items and expiring items, and takes action on expired items.
    """
    # Function to perform stock check
    cursor.execute("SELECT itemID, quantity FROM stock WHERE quantity < 50;")
    low_stock_items = cursor.fetchall()
    if low_stock_items:
        print("Low stock items:")
        print(tabulate(low_stock_items, headers=["Item ID", "Remaining Stock"]))
    else:
        print("All items have sufficient stock.")
    cursor.execute("SELECT itemID, quantity, expiry FROM stock WHERE expiry<='2026-01-30';")
    expiring_items = cursor.fetchall()
    if expiring_items:
        print("\nExpiring items:")
        print(tabulate(expiring_items, headers=["Item ID", "Remaining Stock", "Expiry Date"]))
        for item in expiring_items:
            itemID, quantity, expiry = item
            if expiry >= '2025-12-15':
                print(f"Item {itemID} is expiring on {expiry}. Consider discounting or removing it from stock.")
            elif expiry < '2025-12-15':
                print(f"Item {itemID} expired on {expiry}. Removing it from stock immediately.")
                remove_stockALL(itemID)
    else:
        print("No items are expiring soon.")

