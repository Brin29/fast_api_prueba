from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select
from contextlib import asynccontextmanager
from io import BytesIO
import pandas as pd

from database import engine, get_session
from models import Document
from ml.predictor import predict_future
from ml.preprocessing import clean_and_prepare

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
async def upload_csv(degree: str = Form(...), file: UploadFile = File(...), session: Session = Depends(get_session)):
    contents = await file.read()
    document = Document(
      name=file.filename,
      degree=degree,
      content=contents
    )
    
    session.add(document)
    session.commit()
    session.refresh(document)
    
    return {
      "id": document.id,
      "filename": file.filename, 
      "content": contents
    }
  
@app.get('/predict/{document_id}')
async def predict_csv(document_id: int, session: Session = Depends(get_session)):
  document = session.get(Document, document_id)
  if not document:
    raise HTTPException(status_code=404, detail="Document not found")
  
  try:
    df = pd.read_csv(BytesIO(document.content))
    df = clean_and_prepare(df)
    
    predictions = predict_future(df)
    
    return {
    "id": document_id,
    "content": document.content,
    "predictions": predictions
  }
  
  except Exception as e:
    raise HTTPException(status_code=400, detail=f"Error al predecir: {str(e)}")