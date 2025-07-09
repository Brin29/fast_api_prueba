from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, UploadFile, File, Form
import pandas as pd
import numpy as np
import joblib
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from io import BytesIO
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

model = keras.models.load_model("modelo_lstm_multi_output.h5")
scaler: MinMaxScaler = joblib.load("minmax_scaler.pkl")

df = pd.read_csv("./content/dataset.csv")
df.set_index("Fecha", inplace=True)
df.sort_index(inplace=True)

window_size = 2
predict_years = 11

scaled_values = scaler.transform(df)
scaled_df = pd.DataFrame(scaled_values, columns=df.columns, index=df.index)
last_sequence = scaled_df.iloc[-window_size:].values
last_sequence = np.expand_dims(last_sequence, axis=0)

@app.post('/upload-csv')
async def upload_csv(degree: str = Form(...), file: UploadFile = File(...), session: Session = Depends(get_session)):
  contents =  file.file.read()
  data = BytesIO(contents)
  df = pd.read_csv(data)
  data.close()
  file.file.close()
  document = Document(name=file.filename, degree=degree)
  session.add(document)
  session.commit()
  session.refresh(document)
  
  return {"filename": file.filename}
  
@app.get("/predict")
def get_predictions():
  predicted_scaled = model.predict(last_sequence)
  predicted_scaled = predicted_scaled.reshape(predict_years, scaled_df.shape[1])
  predicted = scaler.inverse_transform(predicted_scaled)
  
  last_year = int(df.index[-1])
  future_years = [last_year + i for i in range(1, predict_years + 1)]
  
  result = []
  for i, year in enumerate(future_years):
    result.append({
      "year": year,
      "values": {
        col: float(predicted[i][j]) for j, col in enumerate(df.columns)
      }
    })
    
  return {"predictions": result}
  
@app.get('/documents')
def get_documents(session: Session = Depends(get_session)):
  documents = session.exec(select(Document)).all()
  return documents