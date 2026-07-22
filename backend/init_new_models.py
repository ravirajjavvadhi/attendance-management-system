import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import Base, engine
# Import all models to ensure they are registered with Base
from app.models.erp_academic import *
from app.models.profiles import *
from app.models.user import *

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    init_db()
