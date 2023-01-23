import json
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
from models import Port
from models import Tile
from result_parser import parse_result
from sentinel_extractor import download_sentinel_data
from ship_detection import process
from sqlalchemy import inspect
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_ports_table():
    session = SessionLocal()

    if inspect(engine).has_table("ports") and len(session.query(Port).all()) != 0:
        return

    print("Adding ports to the database...")

    if not inspect(engine).has_table("ports"):
        Base.metadata.create_all(engine, checkfirst=True)

    with open("../Meta/ports_unique.json", "rb") as geo_f:
        geojson = json.load(geo_f)
    for feature in geojson["features"]:
        session.add(
            Port(
                locode=feature["properties"]["LOCODE"],
                country=feature["properties"]["Country"],
                name=feature["properties"]["NameWoDiac"],
                outflows=feature["properties"]["outflows"],
                latitude=feature["geometry"]["coordinates"][1],
                longitude=feature["geometry"]["coordinates"][0],
            )
        )
    session.commit()
    session.close()


# Dependency
def get_db():
    if not Path(PATH_DB).exists():
        Base.metadata.create_all(engine)
    ensure_ports_table()
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
def get_ships(
    start_date: date,
    end_date: date,
    data_type: str = "geojson",
    db: Session = Depends(get_db),
):
    assert end_date > start_date
    return crud.get_detections(db, start_date, end_date, data_type)


@app.get("/ports.geojson")
def get_ports(
    number: int = 50,
    db: Session = Depends(get_db),
):
    return crud.get_ports(db, number)


@app.post("/polygon")
async def get_polygon_data(req: Request):
    geo_dict = await req.json()
    detect_ships_in_area(geo_dict)
    return


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9967, log_level="info")
