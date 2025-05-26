import os
from sqlalchemy import create_engine
from models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@localhost:5432/tienda_cartas")

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_db()