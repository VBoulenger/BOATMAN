"""
Reusable functions to interact with the data in the database.
Note that pydantic models should be defined and used if the goal is to modify
the database (only reading for now).
"""
import datetime
from typing import Union

from geojson import FeatureCollection
from models import Detection
from sqlalchemy.orm import Session


def get_detections(
    db: Session, start_date: datetime.date, end_date: datetime.date, data_type: str
) -> Union[str, FeatureCollection, None]:
    dets_db = db.query(Detection).all()
    if data_type == "csv":
        headers = dets_db[0].attributes_string()
        dets_csv = [det.to_csv() for det in dets_db]
        dets_csv.insert(0, headers)
        return "\n".join(dets_csv)
    if data_type == "geojson":
        dets_geojson = [det.to_geojson() for det in dets_db]
        return FeatureCollection(dets_geojson)
    return None
