"""
Reusable functions to interact with the data in the database.
Note that pydantic models should be defined and used if the goal is to modify
the database (only reading for now).
"""
import datetime
from typing import Union

from geojson import FeatureCollection
from models import Detection
from models import Port
from models import Tile
from sqlalchemy import desc
from sqlalchemy.orm import Session


def get_detections(
    db: Session, start_date: datetime.date, end_date: datetime.date, data_type: str
) -> Union[str, FeatureCollection, None]:
    detections = (
        db.query(Detection)
        .join(Tile)
        .filter(Tile.acquisition_time > start_date, Tile.acquisition_time < end_date)
        .all()
    )
    if data_type == "csv":
        headers = detections[0].attributes_string()
        dets_csv = [det.to_csv() for det in detections]
        dets_csv.insert(0, headers)
        return "\n".join(dets_csv)
    if data_type == "geojson":
        dets_geojson = [det.to_geojson() for det in detections]
        return FeatureCollection(dets_geojson)
    return None


def get_ports(db: Session, number: int) -> FeatureCollection:
    ports_db = db.query(Port).order_by(desc(Port.outflows)).limit(number).all()
    ports_geojson = [port.to_geojson() for port in ports_db]
    return FeatureCollection(ports_geojson)


def remove_duplicates(db: Session):
    number_of_detections = db.query(Detection.latitude, Detection.longitude).count()

    duplicates = (
        db.query(Detection)
        .where(
            Detection.id.not_in(
                db.query(Detection.id).group_by(Detection.latitude, Detection.longitude)
            )
        )
        .all()
    )

    for duplicate in duplicates:
        db.delete(duplicate)

    db.commit()

    new_number_of_detections = db.query(Detection.latitude, Detection.longitude).count()

    print(
        f"Removed {number_of_detections - new_number_of_detections} out of {number_of_detections} detections"
    )
