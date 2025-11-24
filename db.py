import sqlite3

warehouseFile = open("layout.txt")

xPos = 0
yPos = 0

for line in warehouseFile:

    goodLine = line.strip()
    for char in goodLine:
        if (yPos == 8):
            break
        if (xPos == 31):
            xPos = 0
            yPos += 1

        print(xPos,",",yPos,"",char)
        xPos += 1
warehouseFile.close()

# dbConnection = sqlite3.connect("warehouse.db")

# dbCursor = dbConnection.cursor()

# #dbCursor.execute("CREATE TABLE warehouse(warhouseID int(2), width int NOT NULL, height int NOT NULL)")

# for row in dbCursor.execute("SELECT * FROM warehouse"):
#     print(row)




#Dont remove this
#dbConnection.close()