import json
from datetime import date
from datetime import timedelta
from pathlib import Path
from threading import Lock

import crud
import uvicorn
from database import Base
from database import engine
from database import PATH_DB
from database import SessionLocal
from fastapi import BackgroundTasks
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


db_creation_lock = Lock()


def get_db():
    global db_creation_lock
    with db_creation_lock:
        if not Path(PATH_DB).exists():
            Base.metadata.create_all(engine)
        ensure_ports_table()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def detect_ships_in_area(
    geo_dict: FeatureCollection,
    start_time: date = date.today() - timedelta(days=5),
    end_time: date = date.today(),
):

    downloaded_file = download_sentinel_data(geo_dict, start_time, end_time)

    if downloaded_file is None:
        raise FileNotFoundError("Error while downloading the file.")

    process(downloaded_file)
    db_result = parse_result(downloaded_file)

    session = next(get_db())

    if (
        session.query(Tile.dataset).filter_by(dataset=db_result.dataset).scalar()
        is not None
    ):
        raise ValueError("Product already exists in database.")
    else:
        session.add(db_result)
        session.commit()

    crud.remove_duplicates(session)


def error_handler(geo_dict: FeatureCollection, start_time: date, end_time: date):
    try:
        detect_ships_in_area(geo_dict, start_time, end_time)
    except Exception as exception:
        print(exception)


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
async def get_polygon_data(
    background_tasks: BackgroundTasks, req: Request, start_date: date, end_date: date
):
    geo_dict = await req.json()
    background_tasks.add_task(error_handler, geo_dict, start_date, end_date)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9967, log_level="info")
