class LoadDdsTask:
    def execute(self, connection) -> str:
        cur = connection.cursor()
        try:
            # Truncate all tables in correct order
            cur.execute("""
                TRUNCATE TABLE dds.fact_sales CASCADE;
                TRUNCATE TABLE dds.dim_branch CASCADE;
                TRUNCATE TABLE dds.dim_product_category CASCADE;
                TRUNCATE TABLE dds.dim_payment CASCADE;
                TRUNCATE TABLE dds.dim_customer CASCADE;
                TRUNCATE TABLE dds.dim_date CASCADE;
            """)

            # 1. Load branch dimension
            cur.execute(
                """
                INSERT INTO dds.dim_branch (branch_id, branch, city)
                SELECT branch_id, branch, city FROM nds.branch
                ON CONFLICT DO NOTHING
            """
            )

            # 2. Load product category dimension
            cur.execute(
                """
                INSERT INTO dds.dim_product_category (product_category_id, product_line)
                SELECT product_category_id, product_line FROM nds.product_category
                ON CONFLICT DO NOTHING
            """
            )

            # 3. Load payment dimension
            cur.execute(
                """
                INSERT INTO dds.dim_payment (payment_id, payment)
                SELECT payment_id, payment FROM nds.payment
                ON CONFLICT DO NOTHING
            """
            )

            # 4. Load customer dimension
            cur.execute(
                """
                INSERT INTO dds.dim_customer (customer_type, gender)
                SELECT DISTINCT customer_type, gender FROM nds.sales
                ON CONFLICT DO NOTHING
            """
            )

            # 5. Load date dimension
            cur.execute("SELECT DISTINCT date FROM nds.sales")
            dates = [row[0] for row in cur.fetchall()]

            date_records = []
            for date in dates:
                date_records.append(
                    (
                        date,
                        date.year,
                        date.month,
                        date.day,
                        date.weekday(),
                        (date.month - 1) // 3 + 1,
                    )
                )

            date_insert = """
                INSERT INTO dds.dim_date (date, year, month, day, weekday, quarter)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """
            cur.executemany(date_insert, date_records)

            # 6. Load fact sales
            cur.execute(
                """
                INSERT INTO dds.fact_sales (
                    invoice_id, branch_id, product_category_id, payment_id,
                    customer_type, gender, date, time, unit_price, quantity,
                    tax_5, total, cogs, gross_margin_percentage, gross_income, rating
                )
                SELECT 
                    invoice_id, branch_id, product_category_id, payment_id,
                    customer_type, gender, date, time, unit_price, quantity,
                    tax_5, total, cogs, gross_margin_percentage, gross_income, rating
                FROM nds.sales
                ON CONFLICT DO NOTHING
            """
            )

            connection.commit()

            # Get number of processed records
            cur.execute("SELECT COUNT(*) FROM dds.fact_sales")
            record_count = cur.fetchone()[0]

            return f"Successfully loaded {record_count} records into DDS"

        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cur.close()


if __name__ == "__main__":
    from config.database import default_connection

    try:
        task = LoadDdsTask()
        result = task.execute(default_connection)
        print(result)
    finally:
        default_connection.close()
