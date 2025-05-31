# db/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

def get_engine():
    return create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin_password')}@"
        f"{os.getenv('POSTGRES_HOST', 'db')}:{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'reporteria_db')}"
    )

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)