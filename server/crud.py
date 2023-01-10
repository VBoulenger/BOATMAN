"""
Reusable functions to interact with the data in the database.
Note that pydantic models should be defined and used if the goal is to modify
the database (only reading for now).
"""
import datetime

from geojson import FeatureCollection
from models import Detection
from sqlalchemy.orm import Session


def get_detections(db: Session, start_date: datetime.date, end_date: datetime.date):
    dets_db = db.query(Detection).all()
    dets_geojson = [det.to_geojson() for det in dets_db]
    return FeatureCollection(dets_geojson)
