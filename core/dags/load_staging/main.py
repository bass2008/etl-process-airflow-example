import os
import pandas as pd
from typing import List


class LoadDataTask:
    def __init__(self, path: str):
        self.path = os.path.expanduser(path)

    def get_csv_files(self) -> List[str]:
        """Get list of CSV files in the specified directory."""
        return [f for f in os.listdir(self.path) if f.endswith('.csv')]

    def clean_column_name(self, column: str) -> str:
        """Clean column name to make it SQL-friendly."""
        # Convert to lowercase and replace spaces with underscore
        cleaned = column.lower().replace(' ', '_')
        # Remove % symbol
        cleaned = cleaned.replace('%', '')
        return cleaned

    def clean_staging_table(self, cur):
        """Clean staging table before loading new data."""
        cur.execute("TRUNCATE TABLE staging.supermarket_sales")
        print("Staging table cleaned")

    def process_csv_file(self, file_path: str, cur) -> int:
        """Process a single CSV file and insert data into the database."""
        # Read CSV file
        print(f"Processing file: {file_path}")
        df = pd.read_csv(file_path)

        # Clean column names
        df.columns = [self.clean_column_name(col) for col in df.columns]

        # Prepare insert query
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"""
            INSERT INTO staging.supermarket_sales ({columns})
            VALUES ({placeholders})
        """

        # Convert DataFrame to list of tuples
        records = [tuple(row) for row in df.values]

        # Execute batch insert
        cur.executemany(insert_query, records)

        return len(records)

    def execute(self, connection) -> str:
        cur = connection.cursor()
        try:
            total_records = 0
            csv_files = self.get_csv_files()

            if not csv_files:
                return "No CSV files found in the specified directory"

            # Clean staging table before loading new data
            self.clean_staging_table(cur)

            for csv_file in csv_files:
                file_path = os.path.join(self.path, csv_file)
                records_inserted = self.process_csv_file(file_path, cur)
                total_records += records_inserted

            connection.commit()
            return f"Successfully processed {len(csv_files)} files. Inserted {total_records} records."

        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cur.close()


if __name__ == "__main__":
    from config.database import default_connection

    try:
        path = os.path.expanduser("~/Downloads/etl/")
        task = LoadDataTask(path)
        result = task.execute(default_connection)
        print(result)
    finally:
        default_connection.close()