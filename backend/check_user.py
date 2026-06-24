import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT email, role FROM users WHERE email='javvadhiraviraj@gmail.com'")).fetchall()
    print("User result:", result)
