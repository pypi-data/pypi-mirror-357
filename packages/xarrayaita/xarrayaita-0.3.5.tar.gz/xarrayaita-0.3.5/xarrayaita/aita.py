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
if get_ipython().__class__.__name__=='ZMQInteractiveShell':
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

@xr.register_dataset_accessor("aita")

class aita(object):
    '''
    This is a classe to work on aita data in xarray environnement.
    
    .. note:: xarray does not support heritage from xr.DataArray may be the day it support it, we could move to it
    '''
    
    def __init__(self, xarray_obj):
        '''
        Constructor for aita. 
        
        The xarray_obj should contained at least :
        1. orientation : DataArray that is compatible with uvec structure
        2. quality : DataArray of dim (m,n,1)
        
        It can contained :
        1. micro : DataArray of dim (m,n,1)
        2. grainId : DataArray of dim (m,n,1)
        
        :param xarray_obj:
        :type xarray_obj: xr.Dataset
        '''
        self._obj = xarray_obj 
    pass

from . import aita_export
from . import aita_geom
from . import aita_interactive_nb
from . import aita_plot
from . import aita_processing
from . import loadData_aita
