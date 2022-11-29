from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test.geojson")
async def get_geosjon():
    with open("../output_data/Singapour/ship_detections_gdf.geojson") as f:
        data = json.load(f)
    return data
