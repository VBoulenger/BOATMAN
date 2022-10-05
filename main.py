"""
First opening of Sentinel-1 SAR data
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from tqdm.contrib import itertools

from snappy import ProductIO, GPF, HashMap


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

    return

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
path = "/home/vincent/Documents/PMI/Data/Paper/" \
    "S1A_IW_GRDH_1SDV_20210106T221634_20210106T221659_036023_04388F_3DF5.zip"

# Read File
product = ProductIO.readProduct(path)

# Get info
width = product.getSceneRasterWidth()
print("Width: {} px".format(width))
height = product.getSceneRasterHeight()
print("Height: {} px".format(height))
name = product.getBandNames()
print("Name: {}".format(name))
band_names = product.getBandNames()
print("Band names: {}".format(", ".join(band_names)))


# Applying orbit corrections

parameters = HashMap() #TODO: check parameter

GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
parameters.put('polyDegree', '3')
parameters.put('continueOnFail', 'False')

product = GPF.createProduct('Apply-Orbit-File', parameters, product)

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
product = GPF.createProduct('Speckle-Filter', parameters, product)

# Terrain Corrections

#TODO: Do not apply mask on no elevation terrain
list_params('Terrain-Correction')
parameters = HashMap()
parameters.put('demName', 'SRTM 3Sec')
parameters.put('nodataValueAtSea', False)

product = GPF.createProduct('Terrain-Correction', parameters, product)

# Remove GRD Border Noise
# TODO: Nothing to do because product is alreaady calibrated ?

# parameters = HashMap()
# product = GPF.createProduct('Remove-GRD-Border-Noise', parameters, product)

# Land Sea Mask

parameters = HashMap()
parameters.put('shorelineExtension', '15')
product = GPF.createProduct('Land-Sea-Mask', parameters, product)

write_format = 'BEAM-DIMAP' 
ProductIO.writeProduct(product , 'out/test', write_format)
