# Data Engineer Diploma Project

**Objective:** Create ETL process documentation based on the provided dataset

## Project Phases
1. Data processing and analysis
2. Design normalized data schema (NDS) 
3. Define fact and dimension tables (DDS)
4. Develop ETL processes for:
   - Loading data into NDS
   - Creating data marts
5. Define metrics and create dashboards
6. Document results and conclusions

## Requirements

### ETL Development
Create and document data loading processes for:
- NDS (normalized storage)
- DDS (star schema)
- Data Quality layer (optional enhancement)

### Dashboard Creation
Build Tableau dashboards based on DDS

## Technical Implementation Options

### ETL Processing
- Python (pandas) + SQL

### Data Sources
- Provided CSV dataset
- External API integration (optional enhancement)

### Additional Components
- Airflow orchestration (optional)
- Metadata layer with loading statistics dashboards (optional)

## Deliverables
1. Interactive dashboards
2. Data warehouse schema documentation
3. ETL process documentation



```mermaid
erDiagram
    dim_branch ||--o{ fact_sales : "branch_id"
    dim_product_category ||--o{ fact_sales : "product_category_id"
    dim_payment ||--o{ fact_sales : "payment_id"
    dim_customer ||--o{ fact_sales : "customer_type, gender"
    dim_date ||--o{ fact_sales : "date"

    dim_branch {
        varchar branch_id PK
        varchar branch
        varchar city
    }

    dim_product_category {
        varchar product_category_id PK
        varchar product_line
    }

    dim_payment {
        varchar payment_id PK
        varchar payment
    }

    dim_customer {
        varchar customer_type PK
        varchar gender PK
    }

    dim_date {
        date date PK
        integer year
        integer month
        integer day
        integer weekday
        integer quarter
    }

    fact_sales {
        varchar invoice_id PK
        varchar branch_id FK
        varchar product_category_id FK
        varchar payment_id FK
        varchar customer_type FK
        varchar gender FK
        date date FK
        time time
        decimal unit_price
        integer quantity
        decimal tax_5
        decimal total
        decimal cogs
        decimal gross_margin_percentage
        decimal gross_income
        decimal rating
    }

```