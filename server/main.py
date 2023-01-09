from datetime import date
from datetime import timedelta

import crud
import uvicorn
from database import SessionLocal
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from sentinel_extractor import download_sentinel_data
from sqlalchemy.orm import Session

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


@app.get("/ships.geojson")
def read_db(db: Session = Depends(get_db)):
    return crud.get_detections(db)


@app.post("/polygon")
async def get_polygon_data(req: Request):
    geo_dict = await req.json()
    end_req_date = date.today()
    start_req_date = end_req_date - timedelta(days=5)
    download_sentinel_data(geo_dict, start_req_date, end_req_date)
    return


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info")
