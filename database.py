import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel

load_dotenv()
DATABASEURL = os.getenv('DATABASE')
engine = create_engine(DATABASEURL, echo=True)

def init_db():
  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield session