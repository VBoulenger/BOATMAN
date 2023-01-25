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
from fastapi import HTTPException
from fastapi import Request
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from geojson import FeatureCollection
from models import Port
from models import Tile
from result_parser import parse_result
from sentinel_extractor import download_sentinel_data
from ship_detection import process
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from web_sockets import ConnectionManager

ws_manager = ConnectionManager()

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


def error_handler(
    geo_dict: FeatureCollection, client_id: int, start_time: date, end_time: date
):
    def logger_for_unidentified_clients(local_client_id: int, message: str):
        print(f"Error for client with ID({local_client_id}): {message}")

    try:
        detect_ships_in_area(geo_dict, start_time, end_time)
    except Exception as exception:
        ws_manager.send_text_to_client(
            client_id, str(exception), logger_for_unidentified_clients
        )
    else:
        ws_manager.send_text_to_client(
            client_id, "success", logger_for_unidentified_clients
        )
        ws_manager.broadcast("update_ships")


@app.get("/ships.geojson")
def get_ships(
    start_date: date,
    end_date: date,
    data_type: str = "geojson",
    db: Session = Depends(get_db),
):
    if end_date < start_date:
        raise HTTPException(
            status_code=406, detail="End date should be later than start date."
        )
    return crud.get_detections(db, start_date, end_date, data_type)


@app.get("/ports.geojson")
def get_ports(
    number: int = 50,
    db: Session = Depends(get_db),
):
    return crud.get_ports(db, number)


@app.post("/polygon")
async def get_polygon_data(
    background_tasks: BackgroundTasks,
    req: Request,
    start_date: date,
    end_date: date,
    client_id: int = 0,
):
    geo_dict = await req.json()
    background_tasks.add_task(error_handler, geo_dict, client_id, start_date, end_date)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Unexpected socket from client({client_id}): {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, client_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9967, log_level="info")
