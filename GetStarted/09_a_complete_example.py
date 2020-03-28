# %%
"""
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/GetStarted/09_a_complete_example.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/GetStarted/09_a_complete_example.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/GetStarted/09_a_complete_example.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
</table>
"""

# %%
"""
## Install Earth Engine API and geemap
Install the [Earth Engine Python API](https://developers.google.com/earth-engine/python_install) and [geemap](https://github.com/giswqs/geemap). The **geemap** Python package is built upon the [ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) and [folium](https://github.com/python-visualization/folium) packages and implements several methods for interacting with Earth Engine data layers, such as `Map.addLayer()`, `Map.setCenter()`, and `Map.centerObject()`.
The following script checks if the geemap package has been installed. If not, it will install geemap, which automatically installs its [dependencies](https://github.com/giswqs/geemap#dependencies), including earthengine-api, folium, and ipyleaflet.

**Important note**: A key difference between folium and ipyleaflet is that ipyleaflet is built upon ipywidgets and allows bidirectional communication between the front-end and the backend enabling the use of the map to capture user input, while folium is meant for displaying static data only ([source](https://blog.jupyter.org/interactive-gis-in-jupyter-with-ipyleaflet-52f9657fa7a)). Note that [Google Colab](https://colab.research.google.com/) currently does not support ipyleaflet ([source](https://github.com/googlecolab/colabtools/issues/60#issuecomment-596225619)). Therefore, if you are using geemap with Google Colab, you should use [`import geemap.eefolium`](https://github.com/giswqs/geemap/blob/master/geemap/eefolium.py). If you are using geemap with [binder](https://mybinder.org/) or a local Jupyter notebook server, you can use [`import geemap`](https://github.com/giswqs/geemap/blob/master/geemap/geemap.py), which provides more functionalities for capturing user input (e.g., mouse-clicking and moving).
"""

# %%
# Installs geemap package
import subprocess

try:
    import geemap
except ImportError:
    print('geemap package not installed. Installing ...')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'geemap'])

# Checks whether this notebook is running on Google Colab
try:
    import google.colab
    import geemap.eefolium as emap
except:
    import geemap as emap

# Authenticates and initializes Earth Engine
import ee

try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()  

# %%
"""
## Create an interactive map 
The default basemap is `Google Satellite`. [Additional basemaps](https://github.com/giswqs/geemap/blob/master/geemap/geemap.py#L13) can be added using the `Map.add_basemap()` function. 
"""

# %%
Map = emap.Map(center=[40,-100], zoom=4)
Map.add_basemap('ROADMAP') # Add Google Map
Map

# %%
"""
## Add Earth Engine Python script 
"""

# %%
# Add Earth Engine dataset
# This function gets NDVI from a Landsat 8 image.


def addNDVI(image):
    return image.addBands(image.normalizedDifference(['B5', 'B4']))

# This function masks cloudy pixels.


def cloudMask(image):
    clouds = ee.Algorithms.Landsat.simpleCloudScore(image).select(['cloud'])
    return image.updateMask(clouds.lt(10))


# Load a Landsat collection, map the NDVI and cloud masking functions over it.
collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA') \
    .filterBounds(ee.Geometry.Point([-122.262, 37.8719])) \
    .filterDate('2014-03-01', '2014-05-31') \
    .map(addNDVI) \
    .map(cloudMask)

# Reduce the collection to the mean of each pixel and display.
meanImage = collection.reduce(ee.Reducer.mean())
vizParams = {'bands': ['B5_mean', 'B4_mean', 'B3_mean'], 'min': 0, 'max': 0.5}
Map.setCenter(-122.262, 37.8719, 10)
Map.addLayer(meanImage, vizParams, 'mean')

# Load a region in which to compute the mean and display it.
counties = ee.FeatureCollection('TIGER/2016/Counties')
santaClara = ee.Feature(counties.filter(
    ee.Filter.eq('NAME', 'Santa Clara')).first())
Map.addLayer(ee.Image().paint(santaClara, 0, 2), {
             'palette': 'yellow'}, 'Santa Clara')

# Get the mean of NDVI in the region.
mean = meanImage.select(['nd_mean']).reduceRegion(**{
    'reducer': ee.Reducer.mean(),
    'geometry': santaClara.geometry(),
    'scale': 30
})

# Print mean NDVI for the region.
print('Santa Clara spring mean NDVI:', mean.get('nd_mean').getInfo())


# %%
"""
## Display Earth Engine data layers 
"""

# %%
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
Map