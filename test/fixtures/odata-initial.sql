--
-- Data for Name: Categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "Categories" ("ID", "Name") VALUES (0, 'Food');
INSERT INTO "Categories" ("ID", "Name") VALUES (1, 'Beverages');
INSERT INTO "Categories" ("ID", "Name") VALUES (2, 'Electronics');


--
-- Data for Name: Products; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (0, NULL, NULL, '1992-01-01 00:00:00', NULL, 4, 3, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (1, NULL, NULL, '1995-10-01 00:00:00', NULL, 3, 4, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (2, NULL, NULL, '2000-10-01 00:00:00', NULL, 3, 21, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (3, NULL, NULL, '2005-10-01 00:00:00', '2006-10-01 00:00:00', 3, 20, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (4, NULL, NULL, '2003-01-05 00:00:00', NULL, 3, 23, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (5, NULL, NULL, '2006-08-04 00:00:00', NULL, 3, 23, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (6, NULL, NULL, '2006-11-05 00:00:00', NULL, 3, 19, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (7, NULL, NULL, '2006-11-15 00:00:00', NULL, 3, 36, NULL, NULL);
INSERT INTO "Products" ("ID", "Name", "Description", "ReleaseDate", "DiscontinuedDate", "Rating", "Price", "Products_Category_Categories_ID", "Products_Supplier_Suppliers_ID") VALUES (8, NULL, NULL, '2008-05-08 00:00:00', NULL, 3, 1089, NULL, NULL);


--
-- Data for Name: Suppliers; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "Suppliers" ("ID", "Name", "Address_Street", "Address_City", "Address_State", "Address_ZipCode", "Address_Country", "Concurrency") VALUES (0, 'Exotic Liquids', 'NE 228th', 'Sammamish', 'WA', '98074', 'USA', 0);
INSERT INTO "Suppliers" ("ID", "Name", "Address_Street", "Address_City", "Address_State", "Address_ZipCode", "Address_Country", "Concurrency") VALUES (1, 'Tokyo Traders', 'NE 40th', 'Redmond', 'WA', '98052', 'USA', 0);
