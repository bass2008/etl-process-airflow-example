### Staging

CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.supermarket_sales (
    invoice_id VARCHAR,
    branch VARCHAR,
    city VARCHAR,
    customer_type VARCHAR,
    gender VARCHAR,
    product_line VARCHAR,
    unit_price VARCHAR,
    quantity VARCHAR,
    tax_5 VARCHAR,
    total VARCHAR,
    date VARCHAR,
    time VARCHAR,
    payment VARCHAR,
    cogs VARCHAR,
    gross_margin_percentage VARCHAR,
    gross_income VARCHAR,
    rating VARCHAR
);

### NDS

CREATE SCHEMA IF NOT EXISTS nds;

CREATE TABLE nds.branch (
   branch_id VARCHAR,
   branch VARCHAR,
   city VARCHAR
);

CREATE TABLE nds.product_category (
   product_category_id VARCHAR,
   product_line VARCHAR
);

CREATE TABLE nds.payment (
   payment_id VARCHAR,
   payment VARCHAR
);

CREATE TABLE nds.sales (
   invoice_id VARCHAR,
   branch_id VARCHAR,
   product_category_id VARCHAR,
   payment_id VARCHAR,
   customer_type VARCHAR,
   gender VARCHAR,
   unit_price DECIMAL,
   quantity INTEGER,
   tax_5 DECIMAL,
   total DECIMAL,
   date DATE,
   time TIME,
   cogs DECIMAL,
   gross_margin_percentage DECIMAL,
   gross_income DECIMAL,
   rating DECIMAL
);

### DDS

CREATE SCHEMA IF NOT EXISTS dds;

CREATE TABLE dds.dim_branch (
    branch_id VARCHAR PRIMARY KEY,
    branch VARCHAR,
    city VARCHAR
);

CREATE TABLE dds.dim_product_category (
    product_category_id VARCHAR PRIMARY KEY,
    product_line VARCHAR
);

CREATE TABLE dds.dim_payment (
    payment_id VARCHAR PRIMARY KEY,
    payment VARCHAR
);

CREATE TABLE dds.dim_customer (
    customer_type VARCHAR,
    gender VARCHAR,
    PRIMARY KEY (customer_type, gender)
);

CREATE TABLE dds.dim_date (
    date DATE PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    weekday INTEGER,
    quarter INTEGER
);

CREATE TABLE dds.fact_sales (
    invoice_id VARCHAR PRIMARY KEY,
    branch_id VARCHAR REFERENCES dds.dim_branch(branch_id),
    product_category_id VARCHAR REFERENCES dds.dim_product_category(product_category_id),
    payment_id VARCHAR REFERENCES dds.dim_payment(payment_id),
    customer_type VARCHAR,
    gender VARCHAR,
    date DATE REFERENCES dds.dim_date(date),
    time TIME,
    unit_price DECIMAL,
    quantity INTEGER,
    tax_5 DECIMAL,
    total DECIMAL,
    cogs DECIMAL,
    gross_margin_percentage DECIMAL,
    gross_income DECIMAL,
    rating DECIMAL,
    FOREIGN KEY (customer_type, gender) REFERENCES dds.dim_customer(customer_type, gender)
);

CREATE INDEX idx_fact_sales_branch ON dds.fact_sales(branch_id);
CREATE INDEX idx_fact_sales_product ON dds.fact_sales(product_category_id);
CREATE INDEX idx_fact_sales_payment ON dds.fact_sales(payment_id);
CREATE INDEX idx_fact_sales_customer ON dds.fact_sales(customer_type, gender);
CREATE INDEX idx_fact_sales_date ON dds.fact_sales(date);
CREATE INDEX idx_dim_date_year_month ON dds.dim_date(year, month);