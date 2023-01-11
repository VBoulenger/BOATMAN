from database import Base
from geojson import Feature
from geojson import Point
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)

    tile_dataset = Column(String, ForeignKey("tiles.dataset"))
    tile = relationship("Tile", back_populates="detections")

    width = Column(Float)
    length = Column(Float)

    latitude = Column(Float)
    longitude = Column(Float)

    pixel_x = Column(Integer)
    pixel_y = Column(Integer)

    def attributes_string(self):
        attributes = [
            attr
            for attr in self.__class__.__dict__.keys()
            if (
                not callable(getattr(self, attr))
                and not (attr.startswith("__") or attr.startswith("_sa_"))
            )
        ]
        attributes.remove("tile")
        return ",".join(attributes)

    def to_geojson(self):
        return Feature(
            geometry=Point((self.longitude, self.latitude)),
            properties={"id": self.id, "width": self.width, "length": self.length},
        )

    def __repr__(self):
        return (
            f"<Detection(id={self.id}, tile_dataset={self.tile_dataset},"
            f" width={self.width}, length={self.length},"
            f" latitude={self.latitude}, longitude={self.longitude},"
            f" pixel_x={self.pixel_x}, pixel_y={self.pixel_y})>"
        )

    def to_csv(self):
        fields = self.attributes_string().split(",")
        data = [str(getattr(self, field)) for field in fields]
        return ",".join(data)


class Tile(Base):
    __tablename__ = "tiles"

    detections = relationship("Detection", order_by=Detection.id, back_populates="tile")

    input_path = Column(String)
    dataset = Column(String, primary_key=True)
    descriptor = Column(String)

    orbit_type = Column(String)

    image_width = Column(Integer)
    image_height = Column(Integer)

    acquisition_time = Column(DateTime)
    esa_processed_time = Column(DateTime)
    processed_time = Column(DateTime)

    top_left_latitude = Column(Float)
    top_left_longitude = Column(Float)
    bottom_right_latitude = Column(Float)
    bottom_right_longitude = Column(Float)

    def __repr__(self):
        return (
            f"<Tile(input_path={self.input_path}, dataset={self.dataset},"
            f" descriptor={self.descriptor}, orbit_type={self.orbit_type},"
            f" image_width={self.image_width}, image_height={self.image_height},"
            f" acquisition_time={self.acquisition_time}, esa_processed_time={self.esa_processed_time},"
            f" processed_time={self.processed_time}, top_left_latitude={self.top_left_latitude},"
            f" top_left_longitude={self.top_left_longitude}, bottom_right_latitude={self.bottom_right_latitude},"
            f" bottom_right_longitude={self.bottom_right_longitude}, number_of_detections={len(self.detections)})>"
        )
