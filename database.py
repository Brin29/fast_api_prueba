from sqlmodel import create_engine, Session

DATABASE_URL = 'mysql+pymysql://root:1234@localhost:3306/test'
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
  with Session(engine) as session:
    yield session