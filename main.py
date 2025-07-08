from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
import pandas as pd
from io import StringIO, BytesIO
from contextlib import asynccontextmanager
from database import engine, get_session
from sqlmodel import SQLModel, Session, select
from models import Document

@asynccontextmanager
async def lifespan(app: FastAPI):
  SQLModel.metadata.create_all(engine)
  yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

@app.post('/upload-csv')
async def upload_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    contents = file.file.read()
    data = BytesIO(contents)
    df = pd.read_csv(data)
    data.close()
    file.file.close()
    document = Document(name=file.filename)
    session.add(document)
    session.commit()
    session.refresh(document)
    
    return {"filename": file.filename}
  
@app.get('/documents')
def get_documents(session: Session = Depends(get_session)):
  documents = session.exec(select(Document)).all()
  return documents