from datetime import date
from datetime import timedelta
from pathlib import Path

import crud
import uvicorn
from database import Base
from database import engine
from database import PATH_DB
from database import SessionLocal
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from geojson import FeatureCollection
from models import Tile
from result_parser import parse_result
from sentinel_extractor import download_sentinel_data
from ship_detection import process
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
    if not Path(PATH_DB).exists():
        Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def detect_ships_in_area(geo_dict: FeatureCollection):
    end_req_date = date.today()
    start_req_date = end_req_date - timedelta(days=5)

    downloaded_file = download_sentinel_data(geo_dict, start_req_date, end_req_date)

    if downloaded_file is None:
        return

    process(downloaded_file)
    db_result = parse_result(downloaded_file)

    session = next(get_db())

    if (
        session.query(Tile.dataset).filter_by(dataset=db_result.dataset).scalar()
        is not None
    ):
        print("Product already exists in database, skipping")
    else:
        session.add(db_result)
        session.commit()


@app.get("/ships.geojson")
def read_db(db: Session = Depends(get_db)):
    return crud.get_detections(db)


@app.post("/polygon")
async def get_polygon_data(req: Request):
    geo_dict = await req.json()
    detect_ships_in_area(geo_dict)
    return


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info")
