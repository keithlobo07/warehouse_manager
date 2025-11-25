import sqlite3

dbConnection = sqlite3.connect("warehouse.db")
dbCursor = dbConnection.cursor()

def createWarehouseFromTxt(filePath, warehouseName): #This function takes a filepath to a warehouse "layout" and inserts it into the database.
    warehouseFile = open(filePath) #An example of a warehouse layout can be seen in layout.txt, P = path, S = shelf
    xPosition = 0
    yPosition = 0
    height = 0
    width = 0
    widthCounted = False

    for line in warehouseFile: #Loop to initiate the size of our warehouse
        height += 1
    if (not widthCounted):
        sLine = line.strip()
        for char in sLine:
            width += 1
    widthCounted = True

    dbCursor.execute("INSERT into warehouse(name, width, height) values (?, ?, ?)", (warehouseName, width, height)) #After the size of our warehouse is found we insert the warehouse
    dbConnection.commit()

    newWarehouseIDTup = dbCursor.execute("SELECT MAX(warehouseID) from warehouse") #This finds the biggest warehouseID so we can associate the spaces to it
    newWarehouseID = newWarehouseIDTup.fetchone()[0] #If we ever delete a warehouse this could break

    warehouseFile.seek(0)
    for line in warehouseFile:
        goodLine = line.strip()
        for char in goodLine:
            goodChar = char.strip()
            if (yPosition == height):
                break
            if (xPosition == width):
                xPosition = 0
                yPosition += 1
            
            if (goodChar == "P"):
                dbCursor.execute("INSERT INTO spaces(warehouseID, xPos, yPos, type) values (?, ?, ?, ?)",(newWarehouseID, xPosition, yPosition, 'path'))
                dbConnection.commit()
            elif (goodChar == "S"):
                dbCursor.execute("INSERT INTO spaces(warehouseID, xPos, yPos, type) values (?, ?, ?, ?)",(newWarehouseID, xPosition, yPosition, 'shelf'))
                dbConnection.commit()
            print(xPosition,",",yPosition,"",char)
            xPosition += 1
    warehouseFile.close()
    dbConnection.close()