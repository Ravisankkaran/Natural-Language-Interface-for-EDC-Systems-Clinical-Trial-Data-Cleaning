import re
from typing import List, Tuple, Dict
import sqlite3
import pandas as pd
from datetime import datetime
import google.generativeai as genai

class SimpleNLtoSQL:
    """Gemini-powered NL to SQL converter for clinical trial queries"""

    def __init__(self, db_path, api_key=None):
        self.db_path = db_path
        self.api_key = api_key

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
                print("✅ Gemini API configured successfully!")
            except Exception as e:
                print(f"⚠️ Error configuring Gemini: {e}")
                self.model = None
        else:
            self.model = None

        self.schema_info = """
DATABASE SCHEMA FOR CLINICAL TRIAL:

1. patients table:
   - patient_id (TEXT PRIMARY KEY)
   - site_id (TEXT)
   - age (INTEGER)
   - gender (TEXT)
   - enrollment_date (DATE)
   - treatment_arm (TEXT)
   - status (TEXT)

2. adverse_events table:
   - event_id (INTEGER PRIMARY KEY)
   - patient_id (TEXT, FOREIGN KEY)
   - event_term (TEXT)
   - severity (TEXT)
   - event_date (DATE)
   - resolved (TEXT)

3. lab_results table:
   - lab_id (INTEGER PRIMARY KEY)
   - patient_id (TEXT, FOREIGN KEY)
   - test_name (TEXT)
   - test_value (REAL)
   - unit (TEXT)
   - test_date (DATE)
   - normal_range_low (REAL)
   - normal_range_high (REAL)

4. visits table:
   - visit_id (INTEGER PRIMARY KEY)
   - patient_id (TEXT, FOREIGN KEY)
   - visit_number (INTEGER)
   - visit_date (DATE)
   - scheduled_date (DATE)
   - visit_type (TEXT)
   - completed (TEXT)
"""

    def parse_query(self, nl_query: str) -> Tuple[str, str, str]:
        """Convert natural language to SQL using Gemini API"""
        nl_query = nl_query.strip()

        if not nl_query:
            return None, "error", "Please enter a query."

        if not self.model:
            return None, "error", "⚠️ Gemini API not configured. Please provide API key in the app."

        try:
            prompt = f"""You are a SQL expert for a clinical trial database.

{self.schema_info}

IMPORTANT RULES:
1. Generate ONLY valid SQLite syntax
2. Return ONLY the SQL query, no explanations or markdown
3. Use proper table and column names from the schema above
4. Always add LIMIT 100 to prevent large result sets
5. For "outliers" or "out of range" labs, use: test_value < normal_range_low OR test_value > normal_range_high

USER QUERY: "{nl_query}"

Generate the SQL query:"""

            response = self.model.generate_content(prompt)

            if not response or not response.text:
                return None, "error", "No response from Gemini API"

            sql_query = self._extract_sql(response.text)

            if not sql_query:
                return None, "error", "Could not extract valid SQL from response"

            is_valid, validation_msg = self._validate_sql(sql_query)

            if not is_valid:
                return None, "error", f"Invalid SQL: {validation_msg}"

            explanation = f"Natural Language: {nl_query}\n\nGenerated SQL Query:\n{sql_query}"

            return sql_query, "success", explanation

        except Exception as e:
            return None, "error", f"Error generating SQL: {str(e)}"

    def _extract_sql(self, response_text: str) -> str:
        """Extract SQL query from Gemini response"""
        response_text = response_text.strip()

        if response_text.startswith('```'):
            lines = response_text.split('\n')
            lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response_text = '\n'.join(lines)

        sql_query = response_text.strip()

        if not sql_query.upper().startswith('SELECT'):
            match = re.search(r'(SELECT\s+.+)', sql_query, re.IGNORECASE | re.DOTALL)
            if match:
                sql_query = match.group(1)

        return sql_query

    def _validate_sql(self, sql_query: str) -> Tuple[bool, str]:
        """Validate SQL query"""
        if not sql_query.upper().strip().startswith('SELECT'):
            return False, "Only SELECT queries are allowed"

        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        upper_query = sql_query.upper()
        for keyword in dangerous_keywords:
            if keyword in upper_query:
                return False, f"Query contains forbidden keyword: {keyword}"

        return True, "Valid"

    def execute_query(self, sql_query: str) -> Tuple:
        """Execute SQL query and return results"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            return df, "success"
        except Exception as e:
            return None, f"Error executing query: {str(e)}"

    def get_example_queries(self) -> List[str]:
        """Return list of example queries"""
        return [
            "Show all patients",
            "How many patients per site?",
            "List patients with severe adverse events",
            "Show patients older than 65",
            "Find lab results with outliers",
            "Count adverse events by severity"
        ]

print("✅ Gemini-powered NL-to-SQL module created!")
