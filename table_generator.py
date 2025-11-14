from faker import Faker
import pandas as pd
import sqlite3
import random
from typing import Dict, List, Tuple

class DynamicTableGenerator:
    """Generate custom tables dynamically based on user specifications"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.fake = Faker()
        Faker.seed(0)
        random.seed(0)

    def create_table_from_schema(self, table_name: str, schema: Dict[str, str]) -> Tuple[bool, str]:
        """Create a new table in the database
        Args:
            table_name: Name of the table
            schema: Dict with column_name: data_type pairs
        Returns:
            (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if table already exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                conn.close()
                return False, f"❌ Table '{table_name}' already exists!"

            # Build column definitions
            cols_def = []
            for col, dtype in schema.items():
                dtype_sql = "INTEGER" if dtype.upper() == "BOOLEAN" else dtype.upper()
                cols_def.append(f'"{col}" {dtype_sql}')

            create_sql = f'CREATE TABLE "{table_name}" ({", ".join(cols_def)});'
            cursor.execute(create_sql)
            conn.commit()
            conn.close()

            return True, f"✅ Table '{table_name}' created successfully!"

        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    def generate_value(self, dtype: str, col_name: str = None):
        """Generate fake data based on data type and column name"""
        dtype = dtype.upper()

        if "INT" in dtype:
            return random.randint(1, 1000)
        if "REAL" in dtype or "FLOAT" in dtype or "DOUBLE" in dtype:
            return round(random.uniform(1, 1000), 3)
        if "DATE" in dtype:
            return self.fake.date()
        if "BOOL" in dtype or "BOOLEAN" in dtype:
            return random.choice([0, 1])

        # Heuristics for TEXT columns
        if col_name:
            lname = col_name.lower()
            if "name" in lname:
                return self.fake.name()
            if "email" in lname:
                return self.fake.email()
            if "phone" in lname or "mobile" in lname:
                return self.fake.phone_number()
            if "address" in lname:
                return self.fake.address().replace("\n", " ")
            if "city" in lname:
                return self.fake.city()
            if "country" in lname:
                return self.fake.country()
            if "desc" in lname or "text" in lname or "note" in lname:
                return self.fake.sentence(nb_words=8)

        return self.fake.word()

    def insert_data(self, table_name: str, schema: Dict[str, str], num_rows: int) -> Tuple[bool, str]:
        """Insert fake data into a table
        Args:
            table_name: Name of the table
            schema: Dict with column_name: data_type pairs
            num_rows: Number of rows to generate
        Returns:
            (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                conn.close()
                return False, f"❌ Table '{table_name}' does not exist!"

            # Generate data
            rows = []
            col_names = list(schema.keys())
            for i in range(num_rows):
                row = [self.generate_value(schema[c], c) for c in col_names]
                rows.append(tuple(row))

            # Insert data
            placeholders = ", ".join(["?"] * len(col_names))
            insert_sql = f'INSERT INTO "{table_name}" ({", ".join(["\"" + c + "\"" for c in col_names])}) VALUES ({placeholders});'
            cursor.executemany(insert_sql, rows)
            conn.commit()
            conn.close()

            return True, f"✅ Inserted {num_rows} rows into '{table_name}'!"

        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    def get_all_tables(self) -> List[str]:
        """Get list of all tables in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            return []

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """Get information about a table"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(f"PRAGMA table_info('{table_name}')", conn)
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()

print("✅ Dynamic Table Generator module created!")
