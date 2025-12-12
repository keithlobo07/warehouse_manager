"""
---Database Functions Module---\n
This module provides functions to connect to the SQLite database,
create necessary tables, reset tables, and initialize the database
with example data.
"""

import sqlite3
from tabulate import tabulate


'''---Database Connection---'''
def db_connect():
    """
    Connect to the SQLite database (or create it if it doesn't exist).
    Returns the connection object.
    """
    global conn, cursor
    try:
        conn = sqlite3.connect('warehouse.db')
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"An error occurred while connecting to the database: {e}")
        
def db_close():
    """
    Close the database connection.
    """
    try:
        conn.close()
    except sqlite3.Error as e:
        print(f"An error occurred while closing the database connection: {e}")

'''---Delete and Recreate Tables---'''
def reset_tables():
    """
    Delete existing tables and recreate them.
    """
    cursor.execute('DROP TABLE IF EXISTS transactions;')
    cursor.execute('DROP TABLE IF EXISTS stock;')
    cursor.execute('DROP TABLE IF EXISTS products;')
    cursor.execute('DROP TABLE IF EXISTS suppliers;')
    cursor.execute('DROP TABLE IF EXISTS spaces;')
    cursor.execute('DROP TABLE IF EXISTS warehouse;')
    conn.commit()
    create_tables()

'''---Create Tables---'''
def create_tables():
    """
    Create the necessary tables in the database if they do not already exist.
    
    :Tables:
    1. warehouse\n
    warehouseID - Unique identifier for the warehouse (Primary Key)\n
    name - Name of the warehouse (Default: 'Default name')\n
    width - Width of the warehouse in grid units (Not Null)\n
    height - Height of the warehouse in grid units (Not Null)\n
    2. spaces\n
    warehouseID - Identifier for the warehouse (Foreign Key referencing warehouse table)\n
    xPos - X coordinate of the space in the warehouse grid (Not Null)\n
    yPos - Y coordinate of the space in the warehouse grid (Not Null)\n
    type - Type of space ('path' or 'shelf') (Not Null)\n
    3. suppliers\n
    supplierID - 3 digit unique supplier identifier (Primary Key)\n
    supplierName - Name of the supplier (Not Null)\n
    contactName - Name of the contact person at the supplier\n
    email - Email address of the contact person\n
    4. products\n
    productID - 6 digit unique product identifier (Primary Key) Format: XXXYYY (supplierID + unique product code)\n
    productName - Name of the product (Not Null, Unique)\n
    ean - 13 digit European Article Number (Not Null, Unique)\n
    price - Price of the product (Not Null)\n
    supplierID - 3 digit unique supplier identifier (Foreign Key referencing suppliers table)\n
    5. stock\n
    itemID - 10 digit unique stock item identifier (Primary Key) Format: XXXXXXZZZZ (productID + location)\n
    productID - 6 digit unique product identifier (Foreign Key referencing products table)\n
    location - Cartesian location code in the warehouse (Not Null, Unique) Format: xxyy where xx is the row and yy is the column\n
    quantity - Quantity of the product at the location (Not Null)\n
    expiry - Expiry date of the product (if applicable)\n
    warehouseID - Identifier for the warehouse (Foreign Key referencing warehouse table)\n
    6. transactions\n
    transactionID - 10 digit unique transaction identifier (Primary Key)\n
    productID - 6 digit unique product identifier (Foreign Key referencing products table)\n
    transactionDate - Date of the transaction (Not Null)\n
    quantityChange - Change in quantity (positive for IN, negative for OUT) (Not Null, Check constraint to ensure non-zero)\n
    transactionType - Type of transaction ('IN' or 'OUT') (Not Null, Check constraint)\n
    """
    
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS warehouse(
                    warehouseID INTEGER,
                    name TEXT DEFAULT 'Default name',
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    PRIMARY KEY(warehouseID AUTOINCREMENT)
                    );
                   '''
                   )
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS spaces(
                    warehouseID INTEGER,
                    xPos INTEGER,
                    yPos INTEGER,
                    type TEXT NOT NULL CHECK (type IN ('path', 'shelf')),
                    PRIMARY KEY(warehouseID, xPos, yPos),
                    FOREIGN KEY(warehouseID) REFERENCES warehouse(warehouseID)
                    );
                   '''
                   )
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS suppliers(
                    supplierID INTEGER(3) UNIQUE PRIMARY KEY,
                    supplierName TEXT NOT NULL,
                    contactName TEXT,
                    email TEXT
                    );
                    '''
                    )
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products(
                    productID TEXT(6) UNIQUE PRIMARY KEY,
                    productName TEXT NOT NULL UNIQUE,
                    ean TEXT(13) NOT NULL UNIQUE,
                    price REAL NOT NULL,
                    supplierID INTEGER(3),
                    FOREIGN KEY (supplierID) REFERENCES suppliers(supplierID)
                    );
                    '''
                    )
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock(
                    itemID TEXT(10) AS (productID || location),
                    productID TEXT(6),
                    location TEXT(4) PRIMARY KEY,
                    quantity INTEGER NOT NULL,
                    expiry DATE,
                    warehouseID INTEGER,
                    FOREIGN KEY (productID) REFERENCES products(productID),
                    FOREIGN KEY (warehouseID) REFERENCES warehouse(warehouseID)
                    );
                    '''
                    )
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions(
                    transactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    productID TEXT(6) NOT NULL,
                    location TEXT(4) NOT NULL,
                    transactionDate DATE NOT NULL,
                    quantityChange INTEGER NOT NULL CHECK (quantityChange != 0),
                    transactionType TEXT NOT NULL CHECK (transactionType IN ('IN', 'OUT')),
                    FOREIGN KEY (productID) REFERENCES products(productID)
                    );
                    '''
                    )
    conn.commit()
  
'''---Initialise Tables---'''
def load_grid_from_txt_to_db(filePath, warehouseName):
    """
    Load warehouse layout from a text file into the database.
    
    :param filePath: Path to the warehouse layout text file
    :param warehouseName: Name of the warehouse to be stored in the database
    """
    #This function takes a filepath to a warehouse "layout" and inserts a new warehouse into the database.
    warehouseFile = open(filePath) #An example of a warehouse layout can be seen in layout.txt, P = path, S = shelf
    xPosition = 0
    yPosition = 0
    height = 0 #Variable to track height of warehouse (Incremented as we read file)
    width = 0 #Variable to track width of warehouse (Incremented as we read file)
    widthCounted = False

    for line in warehouseFile: #For each line in the warehouseFile, increment height by 1
        height += 1
    if (not widthCounted):
        sLine = line.strip()
        for char in sLine: #Count characters on a line, increment width
            width += 1
    widthCounted = True

    cursor.execute("INSERT into warehouse(warehouseID, name, width, height) values (?,?, ?, ?)", (6, warehouseName, width, height)) #After the size of our warehouse is found we create a new warehouse
    conn.commit()

    newWarehouseID = cursor.lastrowid #Gets the ID of the newly created warehouse

    warehouseFile.seek(0)
    for line in warehouseFile: #This block loops over the txt file and adds each space to the spaces table.
        goodLine = line.strip()
        for char in goodLine:
            goodChar = char.strip()
            if (yPosition == height):
                break
            if (xPosition == width):
                xPosition = 0
                yPosition += 1
            
            if (goodChar == "P"):
                cursor.execute("INSERT INTO spaces(warehouseID, xPos, yPos, type) values (?, ?, ?, ?)",(newWarehouseID, xPosition, yPosition, 'path'))
                conn.commit()
            elif (goodChar == "S"):
                cursor.execute("INSERT INTO spaces(warehouseID, xPos, yPos, type) values (?, ?, ?, ?)",(newWarehouseID, xPosition, yPosition, 'shelf'))
                conn.commit()
            #print(xPosition,",",yPosition,"",char)
            xPosition += 1
    warehouseFile.close()

def init_suppliers():
    """
    Initialize the suppliers table with example data.
    """
    # Example suppliers data
    suppliers=[
            (101, 'Tesco', 'Ludovic Magerand', 'l.magerand@dundee.ac.uk'),
            (102, 'Currys', 'Femi Samuel', 'osamuel002@dundee.ac.uk'),
            (103, 'Lidl', 'John Lawrence', 'j.lawrence@dundee.ac.uk'),
            (104, 'Ikea', 'Craig Ramsay', 'c.d.ramsay@dundee.ac.uk')
            ]
    
    # Error Handling
    if not suppliers:
        print("Supplier data is empty. No suppliers to initialize.")
        return
    
    try:
        cursor.executemany('INSERT OR IGNORE INTO suppliers (supplierID, supplierName, contactName, email) VALUES (?, ?, ?, ?);', suppliers)
        conn.commit()
    except Exception as e:
        print(f"An error occurred while initializing suppliers: {e}")

def init_products():
    """
    Initialize the products table with example data.
    """
    # Example products data
    products=[
            # 101 - Tesco
            ('101001', 'Frosted Flakes 500g', '5000119123831', 0.95, 101),
            ('101002', 'Digestive Biscuits 400g', '5059739501064', 0.60, 101),
            ('101003', 'Free Range Eggs (12-pack)', '5057753178044', 3.50, 101),
            ('101004', 'White Bread (Medium)', '5059690184090', 1.00, 101),
            ('101005', 'Bananas (Bunch of 5)', '0266419328006', 0.99, 101),
            ('101006', 'Frozen Peas 1kg', '5054778129701', 1.50, 101),
            ('101007', 'Orange Juice (Smooth)', '5059739501538', 2.00, 101),
            ('101008', 'Kitchen Towels (4-pack)', '5059690199018', 4.50, 101),
            ('101009', 'Cat Food (Tuna)', '5059690188763', 0.65, 101),
            ('101010', 'Frozen Chips 900g', '5059690177789', 2.20, 101),
            ('101011', 'Salmon Fillets (2-pack)', '5059690199049', 5.50, 101),
            ('101012', 'Salted Butter 250g', '5059690180214', 1.80, 101),
            ('101013', 'Premium Toilet Rolls (9-pack)', '5059690177703', 7.95, 101),
            ('101014', 'Canned Diced Tomatoes', '5059690165008', 0.55, 101),
            ('101015', 'Olive Oil (Extra Virgin) 1L', '5059690154031', 6.50, 101),
            ('101016', 'Basmati Rice 1kg', '5059690143899', 3.00, 101),
            ('101017', 'Washing Up Liquid', '5059690132101', 1.20, 101),
            ('101018', 'Chicken Breast (4-pack)', '5059690129810', 4.90, 101),
            ('101019', 'Block Cheddar Cheese 350g', '5059690111195', 3.10, 101),
            ('101020', 'Black Pepper Grinder', '5059690100100', 1.75, 101),
            ('101021', 'A-Batteries (4-pack)', '5059690100099', 2.50, 101),
            ('101022', 'Frozen Pizza (Margherita)', '5059690190010', 2.50, 101),
            ('101023', 'Crisp Multi-Pack (Salt & Vinegar)', '5059690185001', 3.20, 101),
            ('101024', 'Instant Coffee Jar 100g', '5059690177002', 2.80, 101),
            ('101025', 'Chocolate Bar (Milk)', '5059690166011', 0.80, 101),
            ('101026', 'Sparkling Water 6x1L', '5059690150033', 3.99, 101),
            ('101027', 'Red Grapes 500g', '5059690140088', 2.40, 101),
            ('101028', 'Tuna Chunks in Brine (4-pack)', '5059690130001', 3.80, 101),
            
            # 102 - Currys
            ('102001', 'APPLE MacBook Air', '0195949837913', 948.99, 102),
            ('102002', 'SAMSUNG Galaxy S25 256GB', '8806095852072', 858.99, 102),
            ('102003', 'GOOGLE Pixel 10 Pro XL 256GB', '0840353927742', 999.00, 102),
            ('102004', 'SONY Bravia 55" OLED TV', '4548736122692', 1299.00, 102),
            ('102005', 'Bose QuietComfort Earbuds II', '017817844053', 259.99, 102),
            ('102006', 'Logitech Wireless Mouse', '5099206095209', 15.99, 102),
            ('102007', 'SanDisk 1TB Portable SSD', '619659178330', 99.99, 102),
            ('102008', 'HP DeskJet Printer', '0889899385579', 49.99, 102),
            ('102009', 'Amazon Echo Dot (5th Gen)', '0840080536783', 34.99, 102),
            ('102010', 'Nintendo Switch Lite Console', '0045496453472', 199.00, 102),
            ('102011', 'Power Extension Cable (4-way)', '5055819747209', 12.50, 102),
            ('102012', 'Samsung 32" Curved Monitor', '8806094595854', 289.00, 102),
            ('102013', 'External Web Camera (1080p)', '607421008035', 29.99, 102),
            
            # 103 - Lidl
            ('103001', 'Scottish Whole Milk 4 pint', '4056489755562', 1.65, 103),
            ('103002', 'Deluxe Italian Prosciutto', '4002422005877', 3.20, 103),
            ('103003', 'Fairtrade Ground Coffee 500g', '4056489110012', 4.50, 103),
            ('103004', 'Organic Red Wine (Merlot)', '4056489991234', 6.99, 103),
            ('103005', 'Artisan Sourdough Loaf', '4056489880055', 2.10, 103),
            ('103006', 'Premium Dark Chocolate 70%', '4056489777123', 1.89, 103),
            ('103007', 'Fresh Basil Plant', '4056489660991', 1.50, 103),
            ('103008', 'Greek Style Yogurt 500g', '4056489555002', 1.10, 103),
            ('103009', 'Frozen Seafood Mix 750g', '4056489440011', 5.99, 103),
            ('103010', 'Premium Lager 6-Pack', '4056489333003', 7.50, 103),
            ('103011', 'Pistachio Ice Cream 500ml', '4056489222112', 3.99, 103),
            ('103012', 'Large Avocados (2-pack)', '4056489111001', 2.99, 103),
            ('103013', 'Premium Balsamic Vinegar', '4056489000555', 4.20, 103),
            ('103014', 'Feta Cheese Block 200g', '4056489000123', 2.30, 103),
                    
            # 104 - Ikea
            ('104001', 'Insulated Travel Mug', '2051357019955', 8.00, 104),
            ('104002', 'Bag (Medium)', '0720189711077', 0.50, 104),
            ('104003', 'Side Table (Black)', '0880001298916', 10.00, 104),
            ('104003', 'Side Table (Black)', '0880001298916', 10.00, 104),
            ('104004', 'Desk Lamp (White)', '0032543209876', 15.00, 104),
            ('104005', 'Set of 4 Dining Chairs (Grey)', '5042543219800', 99.00, 104),
            ('104006', 'Small Plant Pot', '1011122334455', 3.00, 104),
            ('104007', 'Billy Bookcase (Oak)', '6010001000701', 45.00, 104),
            ('104008', 'Dinner Plate Set (4-pack)', '4009876543210', 14.99, 104),
            ('104009', 'Set of 3 Food Containers', '3034567890123', 5.50, 104),
            ('104010', 'Large Woven Storage Basket', '2023456789012', 12.00, 104),
            ('104011', 'Candle Holder (Silver)', '1012345678901', 3.50, 104),
            ('104012', 'Queen Sized Duvet Cover', '5045799743843', 25.00, 104),
            ('104013', 'Picture Frame (A4)', '8030037332383', 4.00, 104),
            ('104014', 'Small Flat-Pack Drawer Unit', '1025104534945', 29.00, 104),
            ('104015', 'Rug (Small, Grey)', '5042683532434', 19.99, 104),
            
            ]
    
    # Error Handling
    if not products:
        print("Products data is empty. No products to initialize.")
        return
    
    try:
        cursor.executemany('INSERT OR IGNORE INTO products (productID, productName, ean, price, supplierID) VALUES (?, ?, ?, ?, ?);', products)
        conn.commit()
    except Exception as e:
        print(f"An error occurred while initializing products: {e}")

def init_stock():
    """
    Initialize the stock table with example data.
    """
    # Example stock data
    stock=[
            [# 101 - Tesco
            # Row 01
            ('101001', '0101', 150, '2026-06-30', 6),
            ('101002', '0301', 200, '2026-08-01', 6),
            ('101003', '0501', 30, '2026-01-15', 6),
            ('101004', '0701', 100, '2026-01-25', 6),
            ('101005', '0901', 50, '2026-01-20', 6),
            ('101006', '1101', 120, '2026-10-30', 6),
            ('101007', '1301', 80, '2026-06-30', 6),
            ('101008', '1501', 60, None, 6),
            ('101009', '1701', 180, '2026-09-01', 6),
            ('101010', '1901', 110, '2026-10-30', 6),
            ('101011', '2101', 25, '2026-02-10', 6),
            ('101012', '2301', 75, '2026-02-15', 6),
            ('101013', '2501', 40, '2026-06-30', 6),
            ('101014', '2701', 250, '2027-01-01', 6),
            ('101015', '2901', 30, '2028-01-01', 6),
            ('101016', '3101', 150, '2027-06-30', 6),
            ('101017', '3301', 80, None, 6),
            ('101018', '3501', 40, '2026-01-20', 6),
            ('101019', '3701', 50, '2026-03-01', 6),
            ('101020', '3901', 100, '2027-06-30', 6),
            ('101021', '4101', 90, '2028-01-01', 6),
            ('101022', '4301', 70, '2026-10-30', 6),
            ('101023', '4501', 100, '2026-06-30', 6),
            ('101024', '4701', 80, '2027-01-01', 6),
            ('101025', '4901', 250, '2026-08-01', 6),
            ('101026', '5101', 90, '2027-01-01', 6),
            ('101027', '5301', 45, '2026-01-18', 6),
            ('101028', '5501', 80, '2027-01-01', 6),
            ('101001', '5701', 150, '2026-06-30', 6),
            ('101002', '5901', 200, '2026-08-01', 6),
            ('101003', '6101', 30, '2026-01-15', 6),
            
            # Row 02
            ('101004', '0102', 100, '2026-01-25', 6),
            ('101005', '0302', 50, '2026-01-20', 6),
            ('101006', '0502', 120, '2026-10-30', 6),
            ('101007', '0702', 80, '2026-06-30', 6),
            ('101008', '0902', 60, None, 6),
            ('101009', '1102', 180, '2026-09-01', 6),
            ('101010', '1302', 110, '2026-10-30', 6),
            ('101011', '1502', 25, '2026-02-10', 6),
            ('101012', '1702', 75, '2026-02-15', 6),
            ('101013', '1902', 40, '2026-06-30', 6),
            ('101014', '2102', 250, '2027-01-01', 6),
            ('101015', '2302', 30, '2028-01-01', 6),
            ('101016', '2502', 150, '2027-06-30', 6),
            ('101017', '2702', 80, None, 6),
            ('101018', '2902', 40, '2026-01-20', 6),
            ('101019', '3102', 50, '2026-03-01', 6),
            ('101020', '3302', 100, '2027-06-30', 6),
            ('101021', '3502', 90, '2028-01-01', 6),
            ('101022', '3702', 70, '2026-10-30', 6),
            ('101023', '3902', 100, '2026-06-30', 6),
            ('101024', '4102', 80, '2027-01-01', 6),
            ('101025', '4302', 250, '2026-08-01', 6),
            ('101026', '4502', 90, '2027-01-01', 6),
            ('101027', '4702', 45, '2026-01-18', 6),
            ('101028', '4902', 80, '2027-01-01', 6),
            ('101001', '5102', 150, '2026-06-30', 6),
            ('101002', '5302', 200, '2026-08-01', 6),
            ('101003', '5502', 30, '2026-01-15', 6),
            ('101004', '5702', 100, '2026-01-25', 6),
            ('101005', '5902', 50, '2026-01-20', 6),
            ('101006', '6102', 120, '2026-10-30', 6),
            # Row 03
            ('101007', '0103', 80, '2026-06-30', 6),
            ('101008', '0303', 60, None, 6),
            ('101009', '0503', 180, '2026-09-01', 6),
            ('101010', '0703', 110, '2026-10-30', 6),
            ('101011', '0903', 25, '2026-02-10', 6),
            ('101012', '1103', 75, '2026-02-15', 6),
            ('101013', '1303', 40, '2026-06-30', 6),
            ('101014', '1503', 250, '2027-01-01', 6),
            ('101015', '1703', 30, '2028-01-01', 6),
            ('101016', '1903', 150, '2027-06-30', 6),
            ('101017', '2103', 80, None, 6),
            ('101018', '2303', 40, '2026-01-20', 6),
            ('101019', '2503', 50, '2026-03-01', 6),
            ('101020', '2703', 100, '2027-06-30', 6),
            ('101021', '2903', 90, '2028-01-01', 6),
            ('101022', '3103', 70, '2026-10-30', 6),
            ('101023', '3303', 100, '2026-06-30', 6),
            ('101024', '3503', 80, '2027-01-01', 6),
            ('101025', '3703', 250, '2026-08-01', 6),
            ('101026', '3903', 90, '2027-01-01', 6),
            ('101027', '4103', 45, '2026-01-18', 6),
            ('101028', '4303', 80, '2027-01-01', 6),
            ('101001', '4503', 150, '2026-06-30', 6),
            ('101002', '4703', 200, '2026-08-01', 6),
            ('101003', '4903', 30, '2026-01-15', 6),
            ('101004', '5103', 100, '2026-01-25', 6),
            ('101005', '5303', 50, '2026-01-20', 6),
            ('101006', '5503', 120, '2026-10-30', 6),
            ('101007', '5703', 80, '2026-06-30', 6),
            ('101008', '5903', 60, None, 6),
            ('101009', '6103', 180, '2026-09-01', 6),
            
            # Row 04
            ('101010', '0104', 110, '2026-10-30', 6),
            ('101011', '0304', 25, '2026-02-10', 6),
            ('101012', '0504', 75, '2026-02-15', 6),
            ('101013', '0704', 40, '2026-06-30', 6),
            ('101014', '0904', 250, '2027-01-01', 6),
            ('101015', '1104', 30, '2028-01-01', 6),
            ('101016', '1304', 150, '2027-06-30', 6),
            ('101017', '1504', 80, None, 6),
            ('101018', '1704', 40, '2026-01-20', 6),
            ('101019', '1904', 50, '2026-03-01', 6),
            ('101020', '2104', 100, '2027-06-30', 6),
            ('101021', '2304', 90, '2028-01-01', 6),
            ('101022', '2504', 70, '2026-10-30', 6),
            ('101023', '2704', 100, '2026-06-30', 6),
            ('101024', '2904', 80, '2027-01-01', 6),
            ('101025', '3104', 250, '2026-08-01', 6),
            ('101026', '3304', 90, '2027-01-01', 6),
            ('101027', '3504', 45, '2026-01-18', 6),
            ('101028', '3704', 80, '2027-01-01', 6),
            ('101001', '3904', 150, '2026-06-30', 6),
            ('101002', '4104', 200, '2026-08-01', 6),
            ('101003', '4304', 30, '2026-01-15', 6),
            ('101004', '4504', 100, '2026-01-25', 6),
            ('101005', '4704', 50, '2026-01-20', 6),
            ('101006', '4904', 120, '2026-10-30', 6),
            ('101007', '5104', 80, '2026-06-30', 6),
            ('101008', '5304', 60, None, 6),
            ('101009', '5504', 180, '2026-09-01', 6),
            ('101010', '5704', 110, '2026-10-30', 6),
            ('101011', '5904', 25, '2026-02-10', 6),
            ('101012', '6104', 75, '2026-02-15', 6)],
            
            
            [# 102 - Currys
             
            # Row 05
            ('102001', '0105', 2, None, 6),
            ('102002', '0305', 3, None, 6),
            ('102003', '0505', 3, None, 6),
            ('102004', '0705', 1, None, 6),
            ('102005', '0905', 10, None, 6),
            ('102006', '1105', 50, None, 6),
            ('102007', '1305', 20, None, 6),
            ('102008', '1505', 10, None, 6),
            ('102009', '1705', 35, None, 6),
            ('102010', '1905', 5, None, 6),
            ('102011', '2105', 40, None, 6),
            ('102012', '2305', 5, None, 6),
            ('102013', '2505', 30, None, 6),
            ('102001', '2705', 2, None, 6),
            ('102002', '2905', 3, None, 6),
            ('102003', '3105', 3, None, 6),
            ('102004', '3305', 1, None, 6),
            ('102005', '3505', 10, None, 6),
            ('102006', '3705', 50, None, 6),
            ('102007', '3905', 20, None, 6),
            ('102008', '4105', 10, None, 6),
            ('102009', '4305', 35, None, 6),
            ('102010', '4505', 5, None, 6),
            ('102011', '4705', 40, None, 6),
            ('102012', '4905', 5, None, 6),
            ('102013', '5105', 30, None, 6),
            ('102001', '5305', 2, None, 6),
            ('102002', '5505', 3, None, 6),
            ('102003', '5705', 3, None, 6),
            ('102004', '5905', 1, None, 6),
            ('102005', '6105', 10, None, 6),

            # Row 07 (0701 -> 0751)
            ('102006', '0107', 50, None, 6),
            ('102007', '0307', 20, None, 6),
            ('102008', '0507', 10, None, 6),
            ('102009', '0707', 35, None, 6),
            ('102010', '0907', 5, None, 6),
            ('102011', '1107', 40, None, 6),
            ('102012', '1307', 5, None, 6),
            ('102013', '1507', 30, None, 6),
            ('102001', '1707', 2, None, 6),
            ('102002', '1907', 3, None, 6),
            ('102003', '2107', 3, None, 6),
            ('102004', '2307', 1, None, 6),
            ('102005', '2507', 10, None, 6),
            ('102006', '2707', 50, None, 6),
            ('102007', '2907', 20, None, 6),
            ('102008', '3107', 10, None, 6),
            ('102009', '3307', 35, None, 6),
            ('102010', '3507', 5, None, 6),
            ('102011', '3707', 40, None, 6),
            ('102012', '3907', 5, None, 6),
            ('102013', '4107', 30, None, 6),
            ('102001', '4307', 2, None, 6),
            ('102002', '4507', 3, None, 6),
            ('102003', '4707', 3, None, 6),
            ('102004', '4907', 1, None, 6),
            ('102005', '5107', 10, None, 6)],
            
            
            [# 103 - Lidl
            
            # Row 07 (0753 -> 0761)
            ('103001', '5307', 60, '2026-01-12', 6),
            ('103002', '5507', 2, '2026-03-01', 6),
            ('103003', '5707', 70, '2027-06-30', 6),
            ('103004', '5907', 50, '2030-01-01', 6),
            ('103005', '6107', 30, '2026-01-12', 6),
            
            # Row 08
            ('103006', '0108', 90, '2026-08-01', 6),
            ('103007', '0308', 50, '2026-01-15', 6),
            ('103008', '0508', 70, '2026-01-20', 6),
            ('103009', '0708', 40, '2026-10-30', 6),
            ('103010', '0908', 60, '2026-12-31', 6),
            ('103011', '1108', 35, '2026-06-30', 6),
            ('103012', '1308', 45, '2026-01-17', 6),
            ('103013', '1508', 50, '2030-01-01', 6),
            ('103014', '1708', 60, '2026-02-01', 6),
            ('103001', '1908', 60, '2026-01-12', 6),
            ('103002', '2108', 2, '2026-03-01', 6),
            ('103003', '2308', 70, '2027-06-30', 6),
            ('103004', '2508', 50, '2030-01-01', 6),
            ('103005', '2708', 30, '2026-01-12', 6),
            ('103006', '2908', 90, '2026-08-01', 6),
            ('103007', '3108', 50, '2026-01-15', 6),
            ('103008', '3308', 70, '2026-01-20', 6),
            ('103009', '3508', 40, '2026-10-30', 6),
            ('103010', '3708', 60, '2026-12-31', 6),
            ('103011', '3908', 35, '2026-06-30', 6),
            ('103012', '4108', 45, '2026-01-17', 6),
            ('103013', '4308', 50, '2030-01-01', 6),
            ('103014', '4508', 60, '2026-02-01', 6),
            ('103001', '4708', 60, '2026-01-12', 6),
            ('103002', '4908', 2, '2026-03-01', 6),
            ('103003', '5108', 70, '2027-06-30', 6),
            ('103004', '5308', 50, '2030-01-01', 6),
            ('103005', '5508', 30, '2026-01-12', 6),
            ('103006', '5708', 90, '2026-08-01', 6),
            ('103007', '5908', 50, '2026-01-15', 6),
            ('103008', '6108', 70, '2026-01-20', 6),
            
            # Row 09 (0901 -> 0951)
            ('103009', '0109', 40, '2026-10-30', 6),
            ('103010', '0309', 60, '2026-12-31', 6),
            ('103011', '0509', 35, '2026-06-30', 6),
            ('103012', '0709', 45, '2026-01-17', 6),
            ('103013', '0909', 50, '2030-01-01', 6),
            ('103014', '1109', 60, '2026-02-01', 6),
            ('103001', '1309', 60, '2026-01-12', 6),
            ('103002', '1509', 2, '2026-03-01', 6),
            ('103003', '1709', 70, '2027-06-30', 6),
            ('103004', '1909', 50, '2030-01-01', 6),
            ('103005', '2109', 30, '2026-01-12', 6),
            ('103006', '2309', 90, '2026-08-01', 6),
            ('103007', '2509', 50, '2026-01-15', 6),
            ('103008', '2709', 70, '2026-01-20', 6),
            ('103009', '2909', 40, '2026-10-30', 6),
            ('103010', '3109', 60, '2026-12-31', 6),
            ('103011', '3309', 35, '2026-06-30', 6),
            ('103012', '3509', 45, '2026-01-17', 6),
            ('103013', '3709', 50, '2030-01-01', 6),
            ('103014', '3909', 60, '2026-02-01', 6),
            ('103001', '4109', 60, '2026-01-12', 6),
            ('103002', '4309', 2, '2026-03-01', 6),
            ('103003', '4509', 70, '2027-06-30', 6),
            ('103004', '4709', 50, '2030-01-01', 6),
            ('103005', '4909', 30, '2026-01-12', 6),
            ('103006', '5109', 90, '2026-08-01', 6)],
            
            
            [# 104 - Ikea
            
            # Row 09 (0953 -> 0961)
            ('104001', '5309', 25, None, 6),
            ('104002', '5509', 300, None, 6),
            ('104003', '5709', 15, None, 6),
            ('104004', '5909', 10, None, 6),
            ('104005', '6109', 5, None, 6),
            # Row 10
            ('104006', '0110', 40, None, 6),
            ('104007', '0310', 8, None, 6),
            ('104008', '0510', 20, None, 6),
            ('104009', '0710', 40, None, 6),
            ('104010', '0910', 15, None, 6),
            ('104011', '1110', 50, None, 6),
            ('104012', '1310', 20, None, 6),
            ('104013', '1510', 30, None, 6),
            ('104014', '1710', 10, None, 6),
            ('104015', '1910', 12, None, 6),
            ('104001', '2110', 25, None, 6),
            ('104002', '2310', 300, None, 6),
            ('104003', '2510', 15, None, 6),
            ('104004', '2710', 10, None, 6),
            ('104005', '2910', 5, None, 6),
            ('104006', '3110', 40, None, 6),
            ('104007', '3310', 8, None, 6),
            ('104008', '3510', 20, None, 6),
            ('104009', '3710', 40, None, 6),
            ('104010', '3910', 15, None, 6),
            ('104011', '4110', 50, None, 6),
            ('104012', '4310', 20, None, 6),
            ('104013', '4510', 30, None, 6),
            ('104014', '4710', 10, None, 6),
            ('104015', '4910', 12, None, 6),
            ('104001', '5110', 25, None, 6),
            ('104002', '5310', 300, None, 6),
            ('104003', '5510', 15, None, 6),
            ('104004', '5710', 10, None, 6),
            ('104005', '5910', 5, None, 6),
            ('104006', '6110', 40, None, 6),

            # Row 11
            ('104007', '0111', 8, None, 6),
            ('104008', '0311', 20, None, 6),
            ('104009', '0511', 40, None, 6),
            ('104010', '0711', 15, None, 6),
            ('104011', '0911', 50, None, 6),
            ('104012', '1111', 20, None, 6),
            ('104013', '1311', 30, None, 6),
            ('104014', '1511', 10, None, 6),
            ('104015', '1711', 12, None, 6),
            ('104001', '1911', 25, None, 6),
            ('104002', '2111', 300, None, 6),
            ('104003', '2311', 15, None, 6),
            ('104004', '2511', 10, None, 6),
            ('104005', '2711', 5, None, 6),
            ('104006', '2911', 40, None, 6),
            ('104007', '3111', 8, None, 6),
            ('104008', '3311', 20, None, 6),
            ('104009', '3511', 40, None, 6),
            ('104010', '3711', 15, None, 6),
            ('104011', '3911', 50, None, 6),
            ('104012', '4111', 20, None, 6),
            ('104013', '4311', 30, None, 6),
            ('104014', '4511', 10, None, 6),
            ('104015', '4711', 12, None, 6),
            ('104001', '4911', 25, None, 6),
            ('104002', '5111', 300, None, 6),
            ('104003', '5311', 15, None, 6),
            ('104004', '5511', 10, None, 6),
            ('104005', '5711', 5, None, 6),
            ('104006', '5911', 40, None, 6),
            ('104007', '6111', 8, None, 6)]
            ]
    
    # Error Handling
    if not stock:
        print("No stock data to initialize.")
        return
    
    try:
        for i in stock:
            cursor.executemany('INSERT OR IGNORE INTO stock (productID, location, quantity, expiry, warehouseID) VALUES (?, ?, ?, ?, ?);', i)
        conn.commit()
    except Exception as e:
        print(f"An error occurred while initializing stock: {e}")

def init_database():
    """
    Initialize the database with example data.
    """
    # Initialize tables
    load_grid_from_txt_to_db("layout.txt", 'NewWarehouse')
    init_suppliers()
    init_products()
    init_stock()
    print("Database initialized with example data.")

'''---Table Functions---'''
def add_supplier(supID, supName, contactName, contactEmail):
    """
    Add a new supplier to the suppliers table.
    
    :param supID: Supplier ID (3-digit supplier identifier)
    :param supName: Supplier Name
    :param contactName: Contact Name
    :param contactEmail: Contact Email
    """
    # Error handling
    if not supID or not supName:
        print("Supplier ID and Supplier Name are required.")
        return
    try:
        cursor.execute('INSERT INTO suppliers (supplierID, supplierName, contactName, email) VALUES (?, ?, ?, ?);',
                   (supID, supName, contactName, contactEmail))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    else:
        print("Supplier added successfully.")

def add_initial_stock(prodID, x, y, quantity, expiry, warehouseID):
    """
    Add stock entry to the stock table.
    
    :param prodID: Product ID
    :param x: X coordinate of the location
    :param y: Y coordinate of the location
    :param quantity: Quantity of the product
    :param expiry: Expiry date of the product
    :param warehouseID: Warehouse ID
    """
    # Error handling
    if not prodID:
        print("Product ID is required.")
        return
    if not x or not y:
        print("Location is required.")
        return
    loc=(x,y)
    if loc not in get_Empty_Locations():
        print("The specified location is already occupied or invalid.")
        return
    if quantity is None or quantity < 0:
        print("Quantity must be a non-negative number.")
        return
    if not warehouseID:
        print("Warehouse ID is required.")
        return
    
    location=str(x).zfill(2)+str(y).zfill(2)
    
    try:
        cursor.execute('INSERT INTO stock (productID, location, quantity, expiry, warehouseID) VALUES (?, ?, ?, ?, ?);',
                   (prodID, location, quantity, expiry, warehouseID))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while adding stock: {e}")
    else:
        print("Initial stock added successfully.")

def add_product(prodID, prodName, ean, price, supID):
    """
    Add a new product to the products table.
    
    :param prodID: Product ID (6-digit unique identifier, XXXYYY format where XXX is supplier ID and YYY is product number)
    :param prodName: Product Name
    :param ean: EAN code (13-digit European Article Number)
    :param price: Price of the product
    :param supID: Supplier ID (3-digit supplier identifier, must exist in suppliers table)
    """
    # Error handling
    if not prodID:
        print("Product ID is required.")
        return
    if not prodName:
        print("Product Name is required.")
        return
    if price is None or price < 0:
        print("Price must be a non-negative number.")
        return
    if not supID:
        print("Supplier ID is required.")
        return
    
    try:
        cursor.execute('INSERT INTO products (productID, productName, ean, price, supplierID) VALUES (?, ?, ?, ?, ?);',
                   (prodID, prodName, ean, price, supID))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while adding product: {e}")
        return
    else:
        print("Product added successfully.")
    
    ask=input("Do you want to add initial stock for this product? (y/n): ")
    if ask.lower()=='y':
        print("-- Add Initial Stock ---")
        print("Available Locations (xPos, yPos):")
        if not get_Empty_Locations():
            print("No empty locations available. Cannot add initial stock.")
            return
        for loc in get_Empty_Locations():
            print(loc)
        x=input("Enter location X coordinate: ")
        if not x.isdigit():
            print("Invalid X coordinate. No initial stock added.")
            return
        y=input("Enter location Y coordinate: ")
        if not y.isdigit():
            print("Invalid Y coordinate. No initial stock added.")
            return
        quantity=int(input("Enter quantity: "))
        exp=input("Do you want to add an expiry date? (y/n): ")
        if exp.lower()=='y':
            expiry=input("Enter expiry date (YYYY-MM-DD) or leave blank for none: ")
        else:
            expiry=None
        if expiry and expiry.strip()=='':
            expiry=None
        warehouseID=int(input("Enter warehouse ID: "))
        add_initial_stock(prodID, x, y, quantity, expiry, warehouseID)
    elif ask.lower()=='n':
        print("No initial stock added.")
    else:
        print("Invalid input. No initial stock added.")

def remove_supplier(supID):
    """
    Remove a supplier from the suppliers table.
    
    :param supID: Supplier ID
    """
    # Error handling
    if not supID:
        print("Supplier ID is required.")
        return
    try:
        cursor.execute('SELECT COUNT(*) FROM products WHERE supplierID = ?;', (supID,))
        count = cursor.fetchone()[0]
        if count > 0:
            try:
                cursor.execute('SELECT productID FROM products WHERE supplierID = ?;', (supID,))
                products = cursor.fetchall()
                for product in products:
                    prodID = product[0]
                    remove_product(prodID)
            except Exception as e:
                print("Cannot remove supplier without removing associated products.")
                return
    except Exception as e:
        print(f"An error occurred while checking associated products: {e}")
        print("Cannot remove supplier without removing associated products.")
        return
    
    try:
        cursor.execute('DELETE FROM suppliers WHERE supplierID = ?;', (supID,))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while removing supplier: {e}")
    else:
        print("Supplier removed successfully.")

def remove_stockALL(prodID):
    """
    Remove all stock entries for a given product ID.
    
    :param prodID: Product ID
    """
    # Error handling
    if not prodID:
        print("Product ID is required.")
        return
    
    try:
        cursor.execute('DELETE FROM stock WHERE productID = ?;', (prodID,))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while removing stock: {e}")
        
def remove_product(prodID):
    """
    Remove a product from the products table.
    
    :param prodID: Product ID
    """
    # Error handling
    if not prodID:
        print("Product ID is required.")
        return
    try:
        cursor.execute('SELECT COUNT(*) FROM stock WHERE productID = ?;', (prodID,))
        count = cursor.fetchone()[0]
        if count > 0:
            try:
                remove_stockALL(prodID)
            except Exception as e:
                print("Cannot remove product without removing associated stock.")
                return
    except Exception as e:
        print(f"An error occurred while removing associated stock: {e}")
        print("Cannot remove product without removing associated stock.")
        return
    try:
        cursor.execute('DELETE FROM products WHERE productID = ?;', (prodID,))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while removing product: {e}")
    else:
        print("Product removed successfully.")

def remove_stock(itemID, quantity):
    """
    Remove stock from the stock table.
    
    :param itemID: Item ID (100%-unique identifier for stock entries, XXXYYYZZZZ format where XXX is supplier ID, YYY is product number, and ZZZZ is location code)
    :param quantity: Quantity to remove
    """
    # Error handling
    if not itemID:
        print("Item ID is required.")
        return
    if quantity is None or quantity <= 0:
        print("Quantity must be a positive number.")
        return
    
    try:
        cursor.execute('SELECT quantity FROM stock WHERE itemID = ?;', (itemID,))
        result = cursor.fetchone()
        if not result:
            print("Item ID not found.")
            return
        current_quantity = result[0]
        if quantity > current_quantity:
            print("Insufficient stock to remove the requested quantity.")
            return
        new_quantity = current_quantity - quantity
        if new_quantity == 0:
            cursor.execute('DELETE FROM stock WHERE itemID = ?;', (itemID,))
        else:
            cursor.execute('UPDATE stock SET quantity = ? WHERE itemID = ?;', (new_quantity, itemID))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while removing stock: {e}")
    else:
        print("Stock removed successfully.")

def add_transaction(prodID, location, quantity, transType):
    """
    Add a transaction to the transactions table.
    
    :param prodID: Product ID (6-digit unique identifier))
    :param location: Location of the product (XXYY format where XX is the x-position and YY is the y-position)
    :param quantity: Quantity of the product
    :param transType: Type of the transaction ('in' or 'out')
    """
    # Error handling
    if not prodID:
        print("Product ID is required.")
        return
    if not location:
        print("Location is required.")
        return
    if quantity is None or quantity <= 0:
        print("Quantity must be a positive number.")
        return
    if transType not in ['in', 'out']:
        print("Transaction type must be either 'in' or 'out'.")
        return
    
    try:
        cursor.execute('INSERT INTO transactions (productID, location, quantity, transType, transDate) VALUES (?, ?, ?, ?, DATE("now"));',
                   (prodID, location, quantity, transType))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while adding transaction: {e}")
    else:
        print("Transaction added successfully.")

def get_stock(itemID):
    """
    Get stock for a given item ID.
    
    :param itemID: Item ID
    """
    # Error handling
    if not itemID:
        print("Item ID is required.")
        return None
    
    try:
        cursor.execute('SELECT * FROM stock WHERE itemID = ?;', (itemID,))
        result = cursor.fetchone()
        if not result:
            print("Item ID not found.")
            return None
        #print(tabulate(result, headers=[desc[0] for desc in cursor.description], tablefmt="grid"))
        return result[3]
    except Exception as e:
        print(f"An error occurred while retrieving stock: {e}")
        return None

def update_stock(itemID, quantity):
    """
    Update stock quantity for a given item ID.
    
    :param itemID: Item ID
    :param quantity: New quantity
    """
    # Error handling
    if not itemID:
        print("Item ID is required.")
        return
    if quantity is None or quantity < 0:
        print("Quantity must be a non-negative number.")
        return
    
    try:
        cursor.execute('UPDATE stock SET quantity = ? WHERE itemID = ?;', (quantity, itemID))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while updating stock: {e}")
    else:
        print("Stock updated successfully.")

#util functions
def get_Empty_Locations():
    """
    Utility function to get all empty locations.
    """
    cursor.execute("SELECT xPos, yPos FROM spaces WHERE type='shelf';")
    rows = cursor.fetchall()
    locations=[]
    for k in rows:
        locations.append(k)
    cursor.execute("SELECT location FROM stock;")
    occupied = cursor.fetchall()
    for i in occupied:
        x=i[0][:2]
        x=int(x)
        y=i[0][2:]
        y=int(y)
        if (x,y) in locations:
            locations.remove((x,y))

    return locations

def view_tables(table):
    """
    Utility function to view contents of a table.
    
    :param table: Table name
    """
    cursor.execute(f"SELECT * FROM {table};")
    rows = cursor.fetchall()
    print(f"{table.capitalize()} Table:")
    print(tabulate(rows, headers=[desc[0] for desc in cursor.description], tablefmt="grid"))
    
def view_stock(prodID):
    """
    Utility function to view stock for a given product ID.
    
    :param prodID: Product ID
    """
    cursor.execute('SELECT * FROM stock WHERE productID = ?;', (prodID,))
    rows = cursor.fetchall()
    print(f"Stock for Product ID {prodID}:")
    print(tabulate(rows, headers=[desc[0] for desc in cursor.description], tablefmt="grid"))