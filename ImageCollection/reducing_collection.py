# %%
"""
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/ImageCollection/reducing_collection.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/ImageCollection/reducing_collection.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/ImageCollection/reducing_collection.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
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
def addTime(image):
    return image.addBands(image.metadata('system:time_start').divide(1000 * 60 * 60 * 24 * 365))

# Load a Landsat 8 collection for a single path-row.
collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA') \
    .filter(ee.Filter.eq('WRS_PATH', 44)) \
    .filter(ee.Filter.eq('WRS_ROW', 34)) \
    .filterDate('2014-01-01', '2015-01-01')

# Compute a median image and display.
median = collection.median()
Map.setCenter(-122.3578, 37.7726, 12)
Map.addLayer(median, {'bands': ['B4', 'B3', 'B2'], 'max': 0.3}, 'median')


# Reduce the collection with a median reducer.
median = collection.reduce(ee.Reducer.median())

# Display the median image.
Map.addLayer(median,
             {'bands': ['B4_median', 'B3_median', 'B2_median'], 'max': 0.3},
             'also median')


# # This function adds a band representing the image timestamp.
# addTime = function(image) {
#   return image.addBands(image.metadata('system:time_start')
#     # Convert milliseconds from epoch to years to aid in
#     # interpretation of the following trend calculation. \
#     .divide(1000 * 60 * 60 * 24 * 365))
# }

# Load a MODIS collection, filter to several years of 16 day mosaics,
# and map the time band function over it.
collection = ee.ImageCollection('MODIS/006/MYD13A1') \
  .filterDate('2004-01-01', '2010-10-31') \
  .map(addTime)

# Select the bands to model with the independent variable first.
trend = collection.select(['system:time_start', 'EVI']) \
  .reduce(ee.Reducer.linearFit())

# Display the trend with increasing slopes in green, decreasing in red.
Map.setCenter(-96.943, 39.436, 5)
Map.addLayer(
    trend,
    {'min': 0, 'max': [-100, 100, 10000], 'bands': ['scale', 'scale', 'offset']},
    'EVI trend')



# %%
"""
## Display Earth Engine data layers 
"""

# %%
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
Map