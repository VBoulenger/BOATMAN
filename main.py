"""
First opening of Sentinel-1 SAR data
"""

import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import geopandas as gpd

from tqdm.contrib import itertools

from snappy import ProductIO, GPF, HashMap
import jpy

def plot_band(product, band, vmin, vmax, clip_factor):

    band = product.getBand(band)
    w = int(band.getRasterWidth() / clip_factor)
    h = int(band.getRasterHeight() / clip_factor)
    print(w, h)
    for i, j in itertools.product(range(clip_factor), range(clip_factor)):
        band_data = np.zeros(w * h, np.float32)
        band.readPixels(i * w, j * h, w, h, band_data)

        band_data.shape = h, w
        plt.imsave("Test/Image{}.{}.png".format(j, i), band_data, cmap='gray', vmin=vmin, vmax=vmax)


def show_product_information(product):
    width = product.getSceneRasterWidth()
    print("Width: {} px".format(width))
    height = product.getSceneRasterHeight()
    print("Height: {} px".format(height))
    name = product.getName()
    print("Name: {}".format(name))
    band_names = product.getBandNames()
    print("Band names: {}".format(", ".join(band_names)))


def list_params(operator_name):
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    op_spi = GPF.getDefaultInstance().getOperatorSpiRegistry().getOperatorSpi(operator_name)
    print('Op name:', op_spi.getOperatorDescriptor().getName())
    print('Op alias:', op_spi.getOperatorDescriptor().getAlias())
    param_Desc = op_spi.getOperatorDescriptor().getParameterDescriptors()
    for param in param_Desc:
        print(param.getName(), "or", param.getAlias())
        for value in param.getValueSet():
            print(value)
        print('________________')


# Set Path to Input Satellite Data
path = "/home/vincent/Documents/PMI/Data/Singapour/S1A_IW_GRDH_1SDV_20220930T224817_20220930T224842_045240_056864_E2A7.zip"

# Read File
input_product = ProductIO.readProduct(path)

# Get info
show_product_information(input_product)

# Subsetting
parameters = HashMap()
parameters.put('copyMetadata', True)
parameters.put('region', '{x},{y},{width},{height}'.format(
    x=1200, y=1100, width=3000, height=3000)
)
subset_product = GPF.createProduct('Subset', parameters, input_product)


# Applying orbit corrections

parameters = HashMap() #TODO: check parameter

GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
parameters.put('polyDegree', '3')
parameters.put('continueOnFail', 'False')

product = GPF.createProduct('Apply-Orbit-File', parameters, subset_product)

# Calibration

parameters = HashMap()
parameters.put('outputSigmaBand', True)
parameters.put('sourceBands', 'Intensity_VV')
parameters.put('selectedPolarisations', "VV")
parameters.put('outputImageScaleInDb', False)
product = GPF.createProduct("Calibration", parameters, product)

# Thermal Noise Removal

parameters = HashMap()
parameters.put('removeThermalNoise', True)
product = GPF.createProduct('ThermalNoiseRemoval', parameters, product)

# Speckle Filtering

parameters = HashMap()
parameters.put('filter', 'Lee')
parameters.put('filterSizeX', '5')
parameters.put('filtersizeY', '5')
speckle_product = GPF.createProduct('Speckle-Filter', parameters, product)


# Terrain Corrections
# TODO: Is it needed for ship detections ? Probably not but better check that
# Also create a problem => no TiePointGrid after applying corrections

# parameters = HashMap()
# parameters.put('demName', 'SRTM 3Sec')
# parameters.put('nodataValueAtSea', False)

# product = GPF.createProduct('Terrain-Correction', parameters, product)

# TODO: GRD corrections not needed ?

# Land Sea Mask
# TODO: import our own masks ? => better results

parameters = HashMap()
parameters.put('shorelineExtension', '15')
product = GPF.createProduct('Land-Sea-Mask', parameters, speckle_product)


# Adaptive thresholding

parameters = HashMap()
parameters.put('targetWindownSizeInMeter', '30') # Must be larger than spatial resolution, also give
# minimum size of target to detect
parameters.put('guardWindowSizeInMeter', '500') # maximum size of target
parameters.put('backgroundWindowSizeInMeter', '800') # he background window size in metres; larger
# than the guard window size to ensure accurate calculation of the background statistics
parameters.put('pfa', '12.5') # Positive number for parameter x
# TODO: litterature on CFAR ? => better parameters (especially PFA ?)

thresholded_product = GPF.createProduct('Adaptivethresholding', parameters, product)

# Object Discrimination
# This step is used to filter out false targets based on minimum and maximum size limits

parameters = HashMap()
parameters.put('minTargetSizeInMeter', '30')
parameters.put('maxTargetSizeInMeter', '500')

detection_applied_product = GPF.createProduct('Object-Discrimination', parameters, thresholded_product)

show_product_information(detection_applied_product)
### Retrieval of vector data from product ###

print(list(detection_applied_product.getVectorDataGroup().getNodeNames()))
print(list(detection_applied_product.getBandNames()))

# Load raster data

t_0 = time.time()

detection_applied_product.getBand('Sigma0_VV_ship_bit_msk').loadRasterData()

print('Operation took: {} seconds'.format(time.time() - t_0))

# Read vector data

# print(list(detection_applied_product.getVectorDataGroup().getNodeNames()))

# Access ship detections list

ship_detections = detection_applied_product.getVectorDataGroup().get('ShipDetections')
# print(ship_detections)
ship_detections_vector = jpy.cast(ship_detections, jpy.get_type('org.esa.snap.core.datamodel.VectorDataNode'))
# print(ship_detections_vector.getFeatureCollection())
# print(ship_detections_vector.getFeatureCollection().getCount())
# print(list(ship_detections_vector.getFeatureCollection().toArray()))

# Constructing table of detections
# TODO: test other method of creating GeoDataFrame for better performances
# https://gis.stackexchange.com/questions/345167/building-geodataframe-row-by-row


tie_point_grid_longitude = thresholded_product.getTiePointGrid('longitude')
tie_point_grid_latitude = thresholded_product.getTiePointGrid('latitude')

tmp_list = []
for simple_feat in ship_detections_vector.getFeatureCollection().toArray():
    tmp_list.append({
        'id' : simple_feat.getID(),
        'det_w' : simple_feat.getAttribute('Detected_width'),
        'det_l' : simple_feat.getAttribute('Detected_length'),
        'geometry' : Point(simple_feat.getAttribute('Detected_lon'),
                           simple_feat.getAttribute('Detected_lat'))
    })
product_crs_wkt = detection_applied_product.getSceneGeoCoding().getMapCRS().toWKT()
print(product_crs_wkt)
ship_detections_gdf = gpd.GeoDataFrame(tmp_list, crs=product_crs_wkt)

ship_detections_gdf.plot()

# Output

output_data_dir = os.path.join('output_data', 'Singapour')
os.makedirs(output_data_dir, exist_ok=True)
ship_detections_gdf.to_file(os.path.join(output_data_dir, 'ship_detections_gdf.shp'))
 
# ProductIO.writeProduct(product , 'out/singapour', 'BEAM-DIMAP')

# Visualization
# TODO: Not sure what it displays tbh

speckle_product.getBand('Sigma0_VV').loadRasterData()
product=speckle_product
band_name='Sigma0_VV'

band = product.getBand(band_name)
tpg_longitude = product.getTiePointGrid('longitude')
tpg_latitude = product.getTiePointGrid('latitude')

print('Band r esolution: {}x{}'.format(band.getRasterWidth(), band.getRasterHeight()))
print('Tie-point grid longitude: {}x{}'.format(
    tpg_longitude.getRasterWidth(), tpg_longitude.getRasterHeight()))
print('Tie-point grid latitude: {}x{}'.format(
    tpg_latitude.getRasterWidth(), tpg_latitude.getRasterHeight()))

rendered_width = 500

product=speckle_product
band_name='Sigma0_VV'
band = product.getBand(band_name)

_prefix = ''

w = band.getRasterWidth()
h = band.getRasterHeight()

band_data = np.zeros(w * h, np.float32)

rendered_height = rendered_width * h / w
nth_width = int(w/rendered_width)
nth_height = int(h/rendered_height)

band.readPixels(0, 0, w, h, band_data)
band_data.shape = h, w

band_data_subsampled = np.array(band_data[0::nth_height, 0::nth_width])
del band_data

tpg_longitude = product.getTiePointGrid('longitude')
tpg_latitude = product.getTiePointGrid('latitude')


# passing only a reference to data as parameter does not seem to work for tie-point grids, 
# the return value has to be used

tpg_longitude_data = np.zeros(w * h, np.float32) 
tpg_longitude_data = np.array(tpg_longitude.readPixels(0, 0, w, h, tpg_longitude_data))
tpg_longitude_data.shape = h, w

tpg_longitude_data_subsampled = np.array(tpg_longitude_data[0::nth_height, 0::nth_width])
del tpg_longitude_data

tpg_latitude_data = np.zeros(w * h, np.float32)
tpg_latitude_data = np.array(tpg_latitude.readPixels(0, 0, w, h, tpg_latitude_data))
tpg_latitude_data.shape = h, w

tpg_latitude_data_subsampled = np.array(tpg_latitude_data[0::nth_height, 0::nth_width])
del tpg_latitude_data

print('Non-zero values count:', np.count_nonzero(band_data_subsampled))
plt.imshow(band_data_subsampled)
plt.show()

plt.imshow(tpg_longitude_data_subsampled)
plt.show()

plt.imshow(tpg_latitude_data_subsampled)
plt.show()

