"""
First opening of Sentinel-1 SAR data
"""

import numpy as np
import matplotlib.pyplot as plt

from snappy import ProductIO, GPF, HashMap


def plot_band(product, band, vmin, vmax, clip_factor):

    band = product.getBand(band)
    w = int(band.getRasterWidth() / clip_factor)
    h = int(band.getRasterHeight() / clip_factor)
    print(w, h)
    for i in range(clip_factor):
        for j in range(clip_factor):
            print(i)
            band_data = np.zeros(w * h, np.float32)
            band.readPixels(i * w, j * h, w, h, band_data)

            band_data.shape = h, w
            plt.imsave("Test/Image{}.{}.png".format(j, i), band_data, cmap='gray', vmin=vmin, vmax=vmax, dpi=150)

    return



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

apply_orbit_file = GPF.createProduct('Apply-Orbit-File', parameters, product)

# Clipping

#TODO: Remove all lands cover from images => less memory and processing

plot_band(product, "Intensity_VV", 0, 100000, 5)
