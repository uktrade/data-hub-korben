ALTER TABLE "Products"
    ADD CONSTRAINT "Products_Category_Categories"
        FOREIGN KEY ("Products_Category_Categories_ID")
        REFERENCES "Categories"("ID"),
    ADD CONSTRAINT "Products_Supplier_Suppliers"
        FOREIGN KEY ("Products_Supplier_Suppliers_ID")
        REFERENCES "Suppliers"("ID");
