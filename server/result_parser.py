"""
A function to parse `gpt` results.
Result files are simple CSV with boat positions.
"""
import csv
import xml.etree.ElementTree as ElementTree
from datetime import datetime
from pathlib import Path
from typing import List
from typing import Optional

from locale_helper import locale_context
from models import Detection
from models import Tile


def parse_ship_positions(input_data: Path):
    expected_result_path = (
        input_data.with_suffix(".data") / "vector_data/ShipDetections.csv"
    )

    if not expected_result_path.exists():
        raise FileNotFoundError(f"Unable to open: {expected_result_path}")

    positions: List[Detection] = []

    with open(expected_result_path, newline="") as csvfile:
        filtered_file = filter(lambda row: row[0] != "#", csvfile)

        reader = csv.DictReader(filtered_file, delimiter="\t")

        for row in reader:
            positions.append(
                Detection(
                    pixel_x=int(row["Detected_x:Integer"]),
                    pixel_y=int(row["Detected_y:Integer"]),
                    latitude=float(row["Detected_lat:Double"]),
                    longitude=float(row["Detected_lon:Double"]),
                    width=float(row["Detected_width:Double"]),
                    length=float(row["Detected_length:Double"]),
                )
            )
    return positions


def parse_metadata(input_data: Path):
    expected_result_path = input_data.with_suffix(".dim")

    if not expected_result_path.exists():
        raise FileNotFoundError(f"Unable to open: {expected_result_path}")

    result: Tile = Tile()

    result.input_path = str(input_data)

    first_line_time: Optional[datetime] = None
    last_line_time: Optional[datetime] = None

    positions = {
        "first_near_lat": Optional[float],
        "first_near_long": Optional[float],
        "first_far_lat": Optional[float],
        "first_far_long": Optional[float],
        "last_near_lat": Optional[float],
        "last_near_long": Optional[float],
        "last_far_lat": Optional[float],
        "last_far_long": Optional[float],
    }

    root = ElementTree.parse(expected_result_path).getroot()

    # FIXME: Somehow we are still changing something here, abbreviated
    #  months will loose their final points after this
    with locale_context("C"):
        for type_tag in root.findall("Dataset_Sources/MDElem/MDElem/MDATTR"):
            value = type_tag.get("name")
            if value == "PRODUCT":
                result.dataset = type_tag.text
            if value == "SPH_DESCRIPTOR":
                result.descriptor = type_tag.text

            if value == "PASS":
                result.orbit_type = type_tag.text

            if value == "num_output_lines":
                result.image_height = int(str(type_tag.text))
            if value == "num_samples_per_line":
                result.image_width = int(str(type_tag.text))

            if value == "first_line_time":
                # Format should match 12-OCT-2022 22:48:41.866898
                first_line_time = datetime.strptime(
                    str(type_tag.text), "%d-%b-%Y %H:%M:%S.%f"
                )
            if value == "last_line_time":
                last_line_time = datetime.strptime(
                    str(type_tag.text), "%d-%b-%Y %H:%M:%S.%f"
                )
            if value == "PROC_TIME":
                result.esa_processed_time = datetime.strptime(
                    str(type_tag.text), "%d-%b-%Y %H:%M:%S.%f"
                )

            if value in positions.keys():
                positions[str(value)] = float(str(type_tag.text))

    if first_line_time is not None and last_line_time is not None:
        delta = last_line_time - first_line_time
        result.acquisition_time = first_line_time + delta / 2
    else:
        raise ValueError("Unable to parse dates")

    result.processed_time = datetime.now()

    if result.orbit_type == "DESCENDING":
        result.top_left_latitude = positions["first_far_lat"]
        result.top_left_longitude = positions["first_near_long"]
        result.bottom_right_latitude = positions["last_near_lat"]
        result.bottom_right_longitude = positions["last_far_long"]
    else:  # "ASCENDING"
        result.top_left_latitude = positions["first_near_lat"]
        result.top_left_longitude = positions["first_far_long"]
        result.bottom_right_latitude = positions["last_far_lat"]
        result.bottom_right_longitude = positions["last_near_long"]

    return result


def parse_result(input_data: Path):
    result = parse_metadata(input_data)
    result.detections = parse_ship_positions(input_data)

    return result


if __name__ == "__main__":
    # Set Path to Input Satellite Data
    input_path = Path(
        "../Data/Singapour/S1A_IW_GRDH_1SDV_20221012T224816_20221012T224841_045415_056E4B_7DC8.zip"
    )

    test_result = parse_result(input_path)
    print(test_result)
    print("\n".join("{}: {}".format(*k) for k in enumerate(test_result.detections[:5])))
