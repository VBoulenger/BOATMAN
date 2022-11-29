from fastapi import FastAPI
import json

app = FastAPI()


@app.get("/test.geojson")
async def get_geosjon():
    with open("../output_data/Singapour/ship_detections_gdf.geojson") as f:
        data = json.load(f)
    return data
