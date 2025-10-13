import sqlite3

db_path = 'timly.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(applications)')
columns = cursor.fetchall()

print("Columns in applications table:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Проверяем наличие нужных полей
col_names = [col[1] for col in columns]
print(f"\ncollection_id exists: {'collection_id' in col_names}")
print(f"state exists: {'state' in col_names}")

conn.close()
