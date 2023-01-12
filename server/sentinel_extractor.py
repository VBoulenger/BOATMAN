"""
This module handles everything related to the download of files from the Copernicus Open Access Hub.
"""
from datetime import date

from geojson import FeatureCollection
from sentinelsat import geojson_to_wkt
from sentinelsat import SentinelAPI


def download_sentinel_data(
    request_geojson: FeatureCollection,
    start_date: date,
    end_date: date,
    directory_path: str = "Data/",
    platformname: str = "Sentinel-1",
    producttype: str = "GRD",
):
    """
    This function download data from the Copernicus Open Access Hub based on a geojson.
    The geojson specifies the region of interest in which data is queried.

    Note that you need to put your login credentials in a file to use this code, see the README
    for more information.

    Parameters
    ----------
    request_geojson: FeatureCollection
        Geojson object containing polygon in which data in queried.
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

    assert start_date <= end_date

    api = SentinelAPI(None, None)
    footprint = geojson_to_wkt(request_geojson)

    products = api.query(
        footprint,
        date=(start_date, end_date),
        platformname=platformname,
        producttype=producttype,
    )

    if len(products) == 0:
        print("Unable to find a corresponding product, returning")
        return

    # Usually, products are added to the OrderedDict in antichronological order,
    # it means that popping the first entered item should return us the last product.
    latest_product_id = products.popitem(last=False)[0]
    api.download_all([latest_product_id], directory_path=directory_path)
