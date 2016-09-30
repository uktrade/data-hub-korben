--
-- Data for Name: Categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "Categories" ("ID", "Name") VALUES (0, 'Food');
INSERT INTO "Categories" ("ID", "Name") VALUES (1, 'Beverages');
INSERT INTO "Categories" ("ID", "Name") VALUES (2, 'Electronics');


--
-- Data for Name: Products; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (0, 'Bread', 'Whole grain bread', '1992-01-01 00:00:00', NULL, 4, 3, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (1, 'Milk', 'Low fat milk', '1995-10-01 00:00:00', NULL, 3, 4, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (2, 'Vint soda', 'Americana Variety - Mix of 6 flavors', '2000-10-01 00:00:00', NULL, 3, 21, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (3, 'Havina Cola', 'The Original Key Lime Cola', '2005-10-01 00:00:00', '2006-10-01 00:00:00', 3, 20, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (4, 'Fruit Punch', 'Mango flavor, 8.3 Ounce Cans (Pack of 24)', '2003-01-05 00:00:00', NULL, 3, 23, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (5, 'Cranberry Juice', '16-Ounce Plastic Bottles (Pack of 12)', '2006-08-04 00:00:00', NULL, 3, 23, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (6, 'Pink Lemonade', '36 Ounce Cans (Pack of 3)', '2006-11-05 00:00:00', NULL, 3, 19, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (7, 'DVD Player', '1080P Upconversion DVD Player', '2006-11-15 00:00:00', NULL, 3, 36, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (8, 'LCD HDTV', '42 inch 1080p LCD with Built-in Blu-ray Disc Player', '2008-05-08 00:00:00', NULL, 3, 1089, NULL, NULL);


--
-- Data for Name: Suppliers; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "Suppliers" ("ID", "Name", "Address_Street", "Address_City", "Address_State", "Address_ZipCode", "Address_Country", "Concurrency") VALUES (0, 'Exotic Liquids', 'NE 228th', 'Sammamish', 'WA', '98074', 'USA', 0);
INSERT INTO "Suppliers" ("ID", "Name", "Address_Street", "Address_City", "Address_State", "Address_ZipCode", "Address_Country", "Concurrency") VALUES (1, 'Tokyo Traders', 'NE 40th', 'Redmond', 'WA', '98052', 'USA', 0);
