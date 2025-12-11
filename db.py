import sqlite3

dbConnection = sqlite3.connect('warehouse.db')
dbCursor = dbConnection.cursor()

#THIS FUNCTION ONLY WORKS WITH SQUARE / RECTANGULAR WAREHOUSE LAYOUTS
def loadGridFromTxtToDB(filePath, warehouseName): #This function takes a filepath to a warehouse "layout" and inserts a new warehouse into the database.
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

    dbCursor.execute("INSERT into warehouse(name, width, height) values (?, ?, ?)", (warehouseName, width, height)) #After the size of our warehouse is found we create a new warehouse
    dbConnection.commit()

    newWarehouseID = dbCursor.lastrowid #Gets the ID of the newly created warehouse

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
                dbCursor.execute("INSERT INTO spaces(warehouseID, xPos, yPos, type) values (?, ?, ?, ?)",(newWarehouseID, xPosition, yPosition, 'path'))
                dbConnection.commit()
            elif (goodChar == "S"):
                dbCursor.execute("INSERT INTO spaces(warehouseID, xPos, yPos, type) values (?, ?, ?, ?)",(newWarehouseID, xPosition, yPosition, 'shelf'))
                dbConnection.commit()
            print(xPosition,",",yPosition,"",char)
            xPosition += 1
    warehouseFile.close()


def loadGridFromDB(dbCursor, warehouseID): #Loads the shelves and paths from the DB, returns the warehouse as a 2D array.

    dbCursor.execute("Select width, height FROM warehouse where warehouseID = ?", (warehouseID,))
    row = dbCursor.fetchone()
    if row is None:
        raise ValueError("No warehouse found with ID {warehouseID}")
    
    width, height = row

    grid = [["?" for x in range(width)] for _ in range(height)]

    spaces = dbCursor.execute("SELECT xPos, yPos, type FROM spaces WHERE warehouseID = ? ORDER BY yPos ASC, xPos ASC;", (warehouseID,))

    for xPos, yPos, type in spaces: #Translating the "path" and "shelf" from the DB back to P and S for our txt file
        if type == "path":
            grid[yPos][xPos] = "P"
        elif type == "shelf":
            grid[yPos][xPos] = "S"
        else:
            grid[yPos][xPos] = "?"

    return(grid) #Returns a 2D array of the basic warehouse layout, shelves = "S" and paths = "P"


def displayWarehouseGrid(warehouseID): #Displays the warehouse in the same format as the txt file, path = "P" shelf = "S"

    layout = loadGridFromDB(dbCursor, warehouseID)

    textLine = ""
    for line in layout:
        for character in line:
            textLine += character
        print(textLine)
        textLine = ""


#def gridToTxt(): #Creates the file for the AI to use, 0 = path, 1 = shelf

displayWarehouseGrid(6)

dbConnection.close()













