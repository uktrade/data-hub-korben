CREATE TABLE "Categories" (
    "ID" INTEGER NOT NULL,
    "Name" TEXT,
    PRIMARY KEY ("ID")
);
CREATE TABLE "Suppliers" (
    "ID" INTEGER NOT NULL,
    "Name" TEXT,
    "Address_Street" TEXT,
    "Address_City" TEXT,
    "Address_State" TEXT,
    "Address_ZipCode" TEXT,
    "Address_Country" TEXT,
    "Concurrency" INTEGER NOT NULL,
    PRIMARY KEY ("ID")
);
CREATE TABLE "Products" (
    "ID" INTEGER NOT NULL,
    "Name" TEXT,
    "Description" TEXT,
    "ReleaseDate" TIMESTAMP NOT NULL,
    "DiscontinuedDate" TIMESTAMP,
    "Rating" INTEGER NOT NULL,
    "Price" DECIMAL(10,0) NOT NULL,
    "Products_Category_Categories_ID" INTEGER,
    "Products_Supplier_Suppliers_ID" INTEGER,
    PRIMARY KEY ("ID")
);
