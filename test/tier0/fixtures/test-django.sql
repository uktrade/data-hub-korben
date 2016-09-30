CREATE TABLE "categories" (
    "id" INTEGER NOT NULL,
    "name" TEXT,
    PRIMARY KEY ("id")
);
CREATE TABLE "suppliers" (
    "id" INTEGER NOT NULL,
    "name" TEXT,
    "address_street" TEXT,
    "address_city" TEXT,
    "address_state" TEXT,
    "address_zipcode" TEXT,
    "address_country" TEXT,
    "concurrency" INTEGER NOT NULL,
    PRIMARY KEY ("id")
);
CREATE TABLE "products" (
    "id" INTEGER NOT NULL,
    "name" TEXT,
    "description" TEXT,
    "release_date" TIMESTAMP NOT NULL,
    "discontinued_date" TIMESTAMP,
    "rating" INTEGER NOT NULL,
    "price" DECIMAL(10,0) NOT NULL,
    "products_category_categories_id" INTEGER,
    "products_supplier_suppliers_id" INTEGER,
    PRIMARY KEY ("id")
);

ALTER TABLE "products"
    ADD CONSTRAINT "products_category_categories"
        FOREIGN KEY ("products_category_categories_id")
        REFERENCES "categories"("id"),
    ADD CONSTRAINT "products_supplier_suppliers"
        FOREIGN KEY ("products_supplier_suppliers_id")
        REFERENCES "suppliers"("id");
