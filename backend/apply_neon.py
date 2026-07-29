import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_6NLRJU8SBIuO@ep-restless-salad-aobtxx22-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(os.environ["DATABASE_URL"])

queries = [
    "ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'PRESENT'",
    "ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS marked_by INTEGER"
]

with engine.connect() as conn:
    for q in queries:
        print(f"Executing: {q}")
        conn.execute(text(q))
    conn.commit()
print("Success!")
