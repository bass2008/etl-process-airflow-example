import pandas as pd
import uuid


class LoadNdsTask:
    def execute(self, connection) -> str:
        cur = connection.cursor()
        try:
            # Truncate all tables
            cur.execute("""
                TRUNCATE TABLE nds.sales CASCADE;
                TRUNCATE TABLE nds.branch CASCADE;
                TRUNCATE TABLE nds.product_category CASCADE;
                TRUNCATE TABLE nds.payment CASCADE;
            """)

            # 1. Load staging data
            cur.execute("SELECT * FROM staging.supermarket_sales")
            staging_data = cur.fetchall()

            # Get column names
            col_names = [desc[0] for desc in cur.description]
            df = pd.DataFrame(staging_data, columns=col_names)

            # 2. Transform and load branch data
            branch_df = df[['branch', 'city']].drop_duplicates(subset=['branch'])
            branch_df['branch_id'] = branch_df['branch'].apply(lambda x: str(uuid.uuid5(uuid.NAMESPACE_DNS, x)))

            branch_insert = """
                INSERT INTO nds.branch (branch_id, branch, city)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """
            cur.executemany(branch_insert, branch_df[['branch_id', 'branch', 'city']].values.tolist())

            # 3. Transform and load product category data
            product_category_df = df[['product_line']].drop_duplicates()
            product_category_df['product_category_id'] = product_category_df['product_line'].apply(
                lambda x: str(uuid.uuid5(uuid.NAMESPACE_DNS, x)))

            category_insert = """
                INSERT INTO nds.product_category (product_category_id, product_line)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """
            cur.executemany(category_insert, product_category_df[['product_category_id', 'product_line']].values.tolist())

            # 4. Transform and load payment data
            payment_df = df[['payment']].drop_duplicates()
            payment_df['payment_id'] = payment_df['payment'].apply(lambda x: str(uuid.uuid5(uuid.NAMESPACE_DNS, x)))

            payment_insert = """
                INSERT INTO nds.payment (payment_id, payment)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """
            cur.executemany(payment_insert, payment_df[['payment_id', 'payment']].values.tolist())

            # 5. Prepare sales data by merging with dimension tables
            sales_df = df.merge(branch_df, on=['branch', 'city'])
            sales_df = sales_df.merge(product_category_df, on='product_line')
            sales_df = sales_df.merge(payment_df, on='payment')

            # Convert data types
            sales_df['unit_price'] = pd.to_numeric(sales_df['unit_price'])
            sales_df['quantity'] = pd.to_numeric(sales_df['quantity'])
            sales_df['tax_5'] = pd.to_numeric(sales_df['tax_5'])
            sales_df['total'] = pd.to_numeric(sales_df['total'])
            sales_df['date'] = pd.to_datetime(sales_df['date']).dt.date
            sales_df['time'] = pd.to_datetime(sales_df['time'], format='%H:%M').dt.time
            sales_df['cogs'] = pd.to_numeric(sales_df['cogs'])
            sales_df['gross_margin_percentage'] = pd.to_numeric(sales_df['gross_margin_percentage'])
            sales_df['gross_income'] = pd.to_numeric(sales_df['gross_income'])
            sales_df['rating'] = pd.to_numeric(sales_df['rating'])

            # 6. Insert sales data
            sales_insert = """
                INSERT INTO nds.sales (
                    invoice_id, branch_id, product_category_id, payment_id,
                    customer_type, gender, unit_price, quantity,
                    tax_5, total, date, time, cogs,
                    gross_margin_percentage, gross_income, rating
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT DO NOTHING
            """

            sales_values = sales_df[[
                'invoice_id', 'branch_id', 'product_category_id', 'payment_id',
                'customer_type', 'gender', 'unit_price', 'quantity',
                'tax_5', 'total', 'date', 'time', 'cogs',
                'gross_margin_percentage', 'gross_income', 'rating'
            ]].values.tolist()

            cur.executemany(sales_insert, sales_values)

            connection.commit()
            return f"Successfully processed {len(sales_df)} sales records"

        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cur.close()


if __name__ == "__main__":
    from config.database import default_connection

    try:
        task = LoadNdsTask()
        result = task.execute(default_connection)
        print(result)
    finally:
        default_connection.close()