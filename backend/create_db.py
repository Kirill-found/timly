"""
Создаёт базу данных с правильной схемой
"""
from app.database import engine, Base
from app.models import User, Vacancy, Application, AnalysisResult, SyncJob

print("Dropping existing tables...")
Base.metadata.drop_all(bind=engine)

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database created successfully!")

# Проверяем что поля действительно созданы
import sqlite3
conn = sqlite3.connect('timly.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(applications)')
columns = cursor.fetchall()

print("\nColumns in applications table:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

col_names = [col[1] for col in columns]
print(f"\ncollection_id exists: {'collection_id' in col_names}")
print(f"state exists: {'state' in col_names}")

conn.close()
