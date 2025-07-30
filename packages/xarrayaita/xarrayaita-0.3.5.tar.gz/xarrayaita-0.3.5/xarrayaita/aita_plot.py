import xarray as xr
import xarrayuvecs.uvecs as xu
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import mahotas as mh
import ipywidgets as widgets
import scipy
import datetime
import skimage

from IPython import get_ipython
if get_ipython().__class__.__name__ == 'ZMQInteractiveShell':
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

def plotBoundary(self,dilatation=0,**kwargs):
    '''
    Plot the grains boundries
    
    :param dilatation: number of iteration to perform dilation on boundaries
    :type dilatation: int
    '''
    mi=self._obj.micro
    
    if dilatation>0:
        mi=xr.DataArray(scipy.ndimage.binary_dilation(mi, iterations=dilatation),dims=self._obj.micro.dims)
    mi.coords['x']=self._obj.x
    mi.coords['y']=self._obj.y
    mi=mi.where(mi==True)
    mi.plot(add_colorbar=False,**kwargs)  

# -----------------------------------

xr.Dataset.aita.plotBoundary = plotBoundary