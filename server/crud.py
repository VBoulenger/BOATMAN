"""
Reusable functions to interact with the data in the database.
Note that pydantic models should be defined and used if the goal is to modify
the database (only reading for now).
"""

from sqlalchemy.orm import Session

from models import Detection


def get_detections(db: Session):
    return db.query(Detection).all()
