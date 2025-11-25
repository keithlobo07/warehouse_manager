--File to store all the table creates

CREATE TABLE "warehouse" (
	"warehouseID"	INTEGER,
	"name"	TEXT DEFAULT "Default name",
	"width"	INTEGER NOT NULL,
	"height"	INTEGER NOT NULL,
	PRIMARY KEY("warehouseID" AUTOINCREMENT)
)

CREATE TABLE "spaces" (
	"warehouseID"	INTEGER,
	"xPos"	INTEGER,
	"yPos"	INTEGER,
	"type"	TEXT,
	PRIMARY KEY("warehouseID","xPos","yPos"),
	FOREIGN KEY("warehouseID") REFERENCES "warehouse"("warehouseID")
)