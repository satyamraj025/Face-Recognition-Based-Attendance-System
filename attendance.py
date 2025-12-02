import sqlite3
from tabulate import tabulate  # optional, for nice formatting

# Enter the name of your attendance database file
db_filename = ("attendance_mca_priyagupta""_2025-11-07.db")

# Connect to the database
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# Fetch all records
cursor.execute("SELECT * FROM attendance")
records = cursor.fetchall()

# Print table headers
headers = ["ID", "Name", "Time", "Course", "Teacher", "Date"]

print(tabulate(records, headers=headers, tablefmt="grid"))

conn.close()
