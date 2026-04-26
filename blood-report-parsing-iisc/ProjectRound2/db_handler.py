import sqlite3
from typing import List, Dict, Optional
import os
from datetime import datetime
import json

class DatabaseHandler:
    def __init__(self, db_path: str = 'blood_reports.db'):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the database file exists"""
        if not os.path.exists(self.db_path):
            print(f"Warning: Database file {self.db_path} not found!")

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory set to dict"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_tables(self) -> List[str]:
        """Get a list of all tables in the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [row['name'] for row in cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> List[Dict]:
        """Get the schema of a specific table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            return [dict(row) for row in cursor.fetchall()]

    def get_all_users(self) -> List[Dict]:
        """Get all users from the Users table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, name, email, role FROM Users;")
            return [dict(row) for row in cursor.fetchall()]

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get a specific user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, name, email, role FROM Users WHERE user_id = ?;", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_table_count(self, table_name: str) -> int:
        """Get the number of records in a table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
            return cursor.fetchone()['count']

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a custom SQL query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

def check_patient_reports():
    db = DatabaseHandler()
    query = """
    SELECT uploaded_at, parsed_report
    FROM Reports
    WHERE patient_id in (select patient_id FROM Patients WHERE name = ? AND user_id = ?)
    ORDER BY uploaded_at ASC;
    """
    results = db.execute_query(query, ('Yash M. Patel', 3))
    print("\n=== Patient Reports ===")
    for i, (date, report) in enumerate(results, 1):
        print(f"\nReport {i}:")
        print(f"Date: {date}")
        report_data = json.loads(report)
        print(f"Test Name: {report_data.get('test_name')}")
        print(f"Patient Info: {report_data.get('patient_info')}")

def check_patient_id():
    db = DatabaseHandler()
    # query = "SELECT patient_id, name, user_id FROM Patients WHERE name = ? AND user_id = ?"
    # results = db.execute_query(query, ('Yash M. Patel', 3))
    # print("\n=== Patient ID Check ===")
    # print("Query:", query)
    # print("Parameters: name='Yash M. Patel', user_id=3")
    # print("Results:", results)
    
    
if __name__ == "__main__":
    print("\n=== Database Tables Content ===")
    db = DatabaseHandler()
    print("\n=== All Users ===")
    all_users = db.execute_query("SELECT *  FROM Users")
    for user in all_users:
        print(user)
    print("\n=== All Patients ===")
    all_patients = db.execute_query("SELECT * FROM Patients")
    for patient in all_patients:
        print(patient)

    print("\n=== All Reports ===")
    all_reports = db.execute_query("SELECT report_id, patient_id, uploaded_at FROM Reports")
    for report in all_reports:
        print(report)

    # print("\n=== Test Prev Reports ===")
    # all_reports = db.execute_query("""SELECT uploaded_at, report_id, patient_id
    # FROM Reports
    # WHERE patient_id in (select patient_id FROM Patients WHERE name = 'Yash M. Patel' AND user_id = 1)
    # ORDER BY uploaded_at ASC;""")
    # for report in all_reports:
    #     print(report)
    
    # Execute the patient reports query
    # check_patient_reports()
    
    # Execute the patient id query
    # check_patient_id()
    
    # Get all tables
    # tables = db.get_all_tables()
    
    # Print contents of each table
    # for table in tables:
    #     if table == 'Reports': continue
    #     print(f"\n=== {table} Table ===")
    #     try:
    #         results = db.execute_query(f"SELECT * FROM {table}")
    #         for row in results:
    #             print(row)
    #     except Exception as e:
    #         print(f"Error reading {table}: {e}")