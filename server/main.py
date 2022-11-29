from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

import models
import crud
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/test.geojson")
async def get_geosjon():
    with open("../output_data/Singapour/ship_detections_gdf.geojson") as f:
        data = json.load(f)
    return data


@app.get("/test_db")
def read_db(db: Session = Depends(get_db)):
    return crud.get_detections(db)
