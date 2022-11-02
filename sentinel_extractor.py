"""
This module handles everything related to the download of files from the Copernicus Open Access Hub.
"""

from datetime import date
from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson


def download_sentinel_data(geojson_file: str, start_date: date, end_date: date, directory_path: str = '.', platformname: str = 'Sentinel-1', producttype: str = 'GRD'):
    """
    This function download data from the Copernicus Open Acces Hub based on a geojson.
    The geojson specifies the region of interest in which data is queried.

    Note that you need to put your login credentials in a file to use this code, see the README for more information.

    Parameters
    ----------
    geojson_file: str
        Path of the geojson file.
    start_date: :obj:`date`
        Start date at which data is queried.
    end_date: :obj:`date`
        End date at which data is queried.
    directory_path: str
        Indicates the path where the data will be downloaded (default to '.').
    platformname: str
        Indicates the platform used (default to 'Sentinel-1').
    producttype: str
        Indicates product type (default to 'GRD').
    """

    api = SentinelAPI(None, None)

    footprint = geojson_to_wkt(read_geojson(geojson_file))

    products = api.query(footprint,
                         date=(start_date, end_date),
                         platformname=platformname,
                         producttype=producttype)

    api.download_all(products, directory_path=directory_path)
