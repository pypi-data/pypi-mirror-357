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
from skimage.segmentation import find_boundaries
from skimage import segmentation,morphology,measure
import xarray as xr

from IPython import get_ipython
if get_ipython().__class__.__name__=='ZMQInteractiveShell':
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

def mean_grain(self,dilate=True,var_grain='grainId'):
    '''
    Compute the mean orientation inside each grain.

    :param dilate: remove grain boundaries by dilation (default True)
    :type dilate: bool

    :param var_grain: name of the variable containing grain labels (default 'grainId')
    :type var_grain: str

    :return: map of mean orientations (azimuth, colatitude) per grain
    :rtype: xr.DataArray with shape (m, n, 2)
'''
    allv=[]
    # number of grain
    nb_grain=int(np.nanmax(self._obj[var_grain]))
    res=np.array(self._obj.orientation)
    res[:,:,:]=np.nan
    # loop on all the grain
    for i in tqdm(range(nb_grain+1)):
        sg=self._obj.where(self._obj[var_grain]==i,drop=True)
        if np.sum(~np.isnan(np.array(sg.orientation)))!=0:
            eval,evec=sg.orientation.uvecs.OT2nd()
            mori=evec[:,0]
            if mori[2]<0:
                mori=-mori

            col=np.arccos(mori[2])
            azi=np.arctan2(mori[1],mori[0])
        else:
            col=np.nan
            azi=np.nan
        
        mm=np.array(self._obj.grainId)==i
        if dilate:
            mm=skimage.morphology.binary_dilation(mm)
            
            
        id1,id2=np.where(mm==True)
        res[id1,id2,0]=azi
        res[id1,id2,1]=col
        
    res=xr.DataArray(res,dims=[self._obj.orientation.coords.dims[0],self._obj.orientation.coords.dims[1],'uvecs'])
    return res

def area_grain(self,var_grain='grainId',drop=None):
    '''
    Compute the grain area of each grain.

    :param var_grain: name of the variable containing grain labels (default 'grainId')
    :type var_grain: str

    :param drop: list of grain IDs to exclude from the result (default None)
    :type drop: list[int] or None

    :return: 1D array of grain areas with coordinates labeled by grain ID
    :rtype: xr.DataArray
    '''
    unique, counts = np.unique(self._obj[var_grain],return_counts=True)
    da=xr.DataArray(counts*self._obj.step_size**2,dims=['Id'])
    da['Id']=unique

    return da.sel(Id=~da['Id'].isin(drop))


# ------------------------------------------------

def dist2GB(self):
    '''
    Compute the distance to the closest grain boundary for each pixel

    Return : 
        - xr.DataArray : (m,n) map of distance to closest grain boundary
    '''
    dist2gb=scipy.ndimage.morphology.distance_transform_edt(np.abs(1-self._obj.micro))

    return xr.DataArray(dist2gb,dims=self._obj.micro.coords.dims)

# ---------------------------------------------------

def dist2TJ_micro(self):
    '''
    Compute the distance to the closest triple join for each pixel using micro structure

    Return : 
        - xr.DataArray : (m,n) map of distance to closest triple join
    '''
    mconv=np.ones([3,3])
    mconv[1,1]=2
    tj=(scipy.signal.convolve2d(self._obj.micro,mconv,mode='same')>4)
    dist2tj=scipy.ndimage.morphology.distance_transform_edt(np.abs(1-tj))

    return xr.DataArray(dist2tj,dims=self._obj.micro.coords.dims)

# ---------------------------------------------------

def closest_outG_value(self,xada):
    '''
    Compute for each pixel the value of the closest grain for the variable given in xada

    :param xada: map of values of same dimensions y and x
    :type xada: xr.DataArray 

    Return : 
        - xr.DataArray : (m,n,1 or 2) map of value from the closest grain 
    '''

    res=np.array(xada.copy())

    cval=0
    if cval in xada:
        while cval in xada:
            cval=cval-1
            print(cval)

    for i in tqdm(np.unique(self._obj.grainId)):
        a=xada.where(self._obj.grainId!=i)
        b=np.array(a)
        ba=np.array(a)
        b[np.isnan(b)]=cval
        ba[np.isnan(ba)]=cval

        footprint=np.ones((3,3))
        footprint[0,0]=0
        footprint[0,2]=0
        footprint[2,0]=0
        footprint[2,2]=0

        while np.sum(b==cval)!=0:
            if len(xada.shape)==2:
                c=scipy.ndimage.morphology.grey_dilation(b,footprint=footprint,cval=cval)
                id=np.where(ba==cval)
                ba[id]=c[id]
                b=ba.copy()
            elif len(xada.shape)==3:
                for j in range(xada.shape[2]):
                    c=scipy.ndimage.morphology.grey_dilation(b[:,:,j],footprint=footprint,cval=cval)
                    id1,id2=np.where(ba[:,:,j]==cval)
                    ba[id1,id2,j]=c[id1,id2]
                b=ba.copy()    

        if len(xada.shape)==2:
            id=np.where(self._obj.grainId==i)
            res[id]=b[id]
        elif len(xada.shape)==3:
            id1,id2,=np.where(self._obj.grainId==i)
            res[id1,id2,:]=b[id1,id2,:]

    res=xr.DataArray(res,dims=xada.coords.dims)
    
    return res

# -----------------------------------------------------

def filter(self,val):
    '''
    Put nan value in orientation for quality below val 

    :param val: threshold value
    :type val: float
    '''
    idx,idy=np.where(self._obj.quality<val)
    
    new=np.array(self._obj.orientation)
    new[idx,idy,:]=np.nan
    self._obj.orientation[:,:,:]=new

# -----------------------------------------------------

def get_neighbours(self, id_grain):
    '''
    Search and return id's of neighbours of the given grain

    :param id_grain: id of grain
    :type id_grain: int 

    Return : 
        - np.array : list with id's of neighbours 
    '''

    cval = -1

    a = self._obj.grainId.where(self._obj.grainId != id_grain)
    b = np.array(a)
    ba = np.array(a)
    b[np.isnan(b)] = cval
    ba[np.isnan(ba)] = cval

    footprint = np.ones((3, 3))
    footprint[0, 0] = 0
    footprint[0, 2] = 0
    footprint[2, 0] = 0
    footprint[2, 2] = 0

    step = 0
    while ((np.sum(b == cval) != 0) & (step < 5)):
        c = scipy.ndimage.morphology.grey_dilation(
            b, footprint=footprint, cval=cval)
        id = np.where(ba == cval)
        ba[id] = c[id]
        b = ba.copy()
        step = step + 1

    id = np.where(self._obj.grainId == id_grain)

    neighbours = np.unique(b[id])
    neighbours = [x for x in neighbours if x != -1]

    return np.array(neighbours)


# ------------------------------------------------------------------

def TJ_map(self):
    """
    Search Triple Join map and compute coordinates and grain of each triple Join

    Return : 
        - xarray.DataArray : (nbTJ,5) , coordinates and triplet of grainId for each TJ
    """
    map = np.array(self._obj.grainId)

    x = map[0:-1, 0:-1]
    y = map[1::, 0:-1]
    z = map[0:-1, 1::]
    t = map[1::, 1::]

    tj = (((x-z) == 0).astype(np.int32)+((x-y) == 0).astype(np.int32)+((x-t) == 0).astype(np.int32) +
          ((y-t) == 0).astype(np.int32)+((y-z) == 0).astype(np.int32)+((z-t) == 0).astype(np.int32)) == 1

    c = np.full((np.shape(tj)[0], 1), False)
    r = np.full((1, np.shape(tj)[1]+1), False)

    tj = np.c_[c, tj]
    tj = np.r_[r, tj]

    coords = np.array([np.where(tj)[1]-0.5, np.where(tj)[0]-0.5]).T

    ptj = np.array([np.where(tj)[0], np.where(tj)[1]]).T

    idg = []
    grain = np.array(self._obj.grainId)
    for i, j in ptj:
        idg.append(
            np.unique([grain[i, j], grain[i, j-1], grain[i-1, j], grain[i-1, j-1]]))
    idg = np.array(idg)


    TJ = xr.DataArray(np.concatenate([coords,idg],axis=1), dims=("nbTJ","prop"))

    return TJ


# ---------------------------------------------------------

def dist2eachTJ(self):
    """
    Compute distance to each TJ for each pixel using TJ coordinates from method TJ_map

    Return : 
        - xarray.DataArray : matrix (n,m,nb_TJ) of distance to each TJ
    """
    TJ= self.TJ_map()

    s = np.shape(self._obj.grainId)

    xx, yy = np.meshgrid(np.arange(s[1]),np.arange(s[0]))
    
    dist = np.zeros(
        (s[0], s[1], np.shape(TJ)[0]))

    for k in range(np.shape(TJ)[0]):
        tj = np.array(TJ[k])
        dist[:,:,k] = np.sqrt((xx-tj[0])**2 + (yy - tj[1])**2)

    return xr.DataArray(dist,dims=("y","x","nbTJ"))


# --------------------------------------------------------

def dist2TJ_labels(self):
    """
    Calculate distance to closest TJ for each pixel using dist matrix calculated by dist2eachTJ method

    Return : 
        xarray.DataArray : map of distance to closest triple join
    """
    dist = np.array(self.dist2eachTJ())

    min_dist = xr.DataArray(np.min(dist, axis=2),dims=self._obj.grainId.coords.dims)

    return min_dist


# ---------------------------------------

def closest_outTJ_value(self, xada):
    """
    Compute values of xada for the 3 grain of the closest TJ

    :param xada: (n,m) or (n,m,2) map of values to compute
    :type xada: xarray.DataArray

    Return : 
        xarray.DataArray : (n,m,3) or (n,m,3,2), the 3 maps of values (for each grain of TJ the closest TJ)
    """

    dist = self.dist2eachTJ()

    TJ = self.TJ_map()

    min_dist = self.dist2TJ_labels()

    # calcul de l'index du TJ
    index_closest_TJ = np.zeros((np.shape(dist)[0],np.shape(dist)[1])) - 1

    for k in range(np.shape(dist)[2]) :
        index_closest_TJ[np.where(dist[:,:,k]==min_dist)] = k

    if len(xada.shape) == 2:

        res = np.array(TJ)[index_closest_TJ.astype(int)]
        res = res[:,:,2:5]

        for i in np.unique(self._obj.grainId):
            res[np.where(res==i)] = np.unique(xada.where(self._obj.grainId==i))[0] 

        return xr.DataArray(res,dims=("y","x","nTJ"))

    elif len(xada.shape) == 3:

        res = np.array(TJ)[index_closest_TJ.astype(int)]
        res2 = np.array(TJ)[index_closest_TJ.astype(int)]
        res = res[:,:,2:5]
        res2 = res2[:,:,2:5]

        mat = np.zeros((np.shape(res)[0],np.shape(res)[1],np.shape(res)[2],2))

        for i in np.unique(self._obj.grainId):
            res[np.where(res==i)] = np.unique(xada.where(self._obj.grainId==i)[:,:,0])[0] 
            res2[np.where(res2==i)] = np.unique(xada.where(self._obj.grainId==i)[:,:,1])[0] 
        
        mat[:,:,0,0] = res[:,:,0]
        mat[:,:,1,0] = res[:,:,1]
        mat[:,:,2,0] = res[:,:,2]
        mat[:,:,0,1] = res2[:,:,0]
        mat[:,:,1,1] = res2[:,:,1]
        mat[:,:,2,1] = res2[:,:,2]

        return xr.DataArray(mat,dims=("y","x","nTJ","uvecs"))    


# --------------------------------------------

def anisotropy_factors(self) :
    """
    Class function for xarray.DataSet.aita

    Compute anisotropy factors of the closest TJ 

    Factors order :
        0 : Relaive anisotropy
        1 : Fractonal anisotropy
        2 : Volume ratio anisotropy
        3 : Flatness anisotropy

    Return :
        - xarray.DataArray : (n,m,4) 

    """
    s = np.shape(self._obj.grainId)

    dist = self.dist2eachTJ()

    min_dist = self.dist2TJ_labels()

    Tj_idg = np.array(self.TJ_map()[:,2:5])

    index_closest_TJ = np.zeros((np.shape(dist)[0],np.shape(dist)[1])) - 1

    for k in range(np.shape(dist)[2]) :
        index_closest_TJ[np.where(dist[:,:,k]==min_dist)] = k

    TJ_val1 = Tj_idg.copy()
    TJ_val2 = Tj_idg.copy()

    for i in range(np.shape(Tj_idg)[0]) :
        TJ_val1[np.where(TJ_val1==i)] = np.unique(self._obj.orientation.where(self._obj.grainId==i)[:,:,0])[0]
        TJ_val2[np.where(TJ_val2==i)] = np.unique(self._obj.orientation.where(self._obj.grainId==i)[:,:,1])[0]

    mat_tj = np.zeros((np.shape(Tj_idg)[0],np.shape(Tj_idg)[1],2))

    mat_tj[:,:,0] = TJ_val1
    mat_tj[:,:,1] = TJ_val2    
    
    mat_tj = xr.DataArray(mat_tj,dims=("nbTJ","value_g","uvecs"))

    eigen_OT2 = np.zeros((np.shape(Tj_idg)[0],3))

    for i in range(np.shape(Tj_idg)[0]) :
        eigen_OT2[i] = mat_tj[i].uvecs.OT2nd()[0]

    anisotropy_fact = np.zeros((np.shape(Tj_idg)[0],4))

    i = 0
    for itj in eigen_OT2 : 
        anisotropy_fact[i,0] = np.std(itj)/np.mean(itj)
        anisotropy_fact[i,1] = np.std(itj)/np.sqrt(np.mean(itj**2))
        anisotropy_fact[i,2] = 1 - itj[0]*itj[1]*itj[2]/(np.mean(itj)**3)
        anisotropy_fact[i,3] = itj[2]/itj[1]
        i = i+1

    res = np.array(anisotropy_fact)[index_closest_TJ.astype(int)]

    return xr.DataArray(res,dims=("y","x","anisotropy_factor"))

def quick_segmentation(self, n_seg_list=np.arange(500, 1500, 25),
                       boundary_threshold=8,
                       min_grain_area=200,
                       min_boundary_length=20):
    '''
    Image segmentation

    Performs quick and robust grain boundary segmentation based on multiple SLIC runs
    and morphology post-processing.

    :param n_seg_list: List of SLIC segment counts to use for ensemble segmentation
    :type n_seg_list: np.ndarray
    :param boundary_threshold: Minimum number of times a boundary must be detected to be considered reliable
    :type boundary_threshold: int
    :param min_grain_area: Minimum grain area (in pixels) to retain a grain
    :type min_grain_area: int
    :param min_boundary_length: Minimum boundary length (in pixels) to retain a boundary
    :type min_boundary_length: int

    :return: Binary grain boundary mask as xarray.DataArray with coordinates
    :rtype: xarray.DataArray
    :return: Labelled grain as xarray.DataArray with coordinates
    :rtype: xarray.DataArray
    '''

    # Compute orientation-based colormap
    orientation_map = self._obj.orientation.uvecs.calc_colormap(semi=True).values
    boundary_votes = np.zeros(orientation_map.shape[:2])

    # Ensemble segmentation using multiple SLIC configurations
    for n_segments in tqdm(n_seg_list):
        labels = segmentation.slic(orientation_map, compactness=0.1,
                                   n_segments=n_segments, start_label=1)
        slic_boundaries = segmentation.find_boundaries(labels, mode='outer')
        dilated_boundaries = morphology.dilation(morphology.dilation(slic_boundaries))
        boundary_votes += dilated_boundaries

    # Threshold boundaries based on frequency
    reliable_boundaries = boundary_votes > boundary_threshold
    grain_mask = ~morphology.skeletonize(reliable_boundaries)

    # Label grains and remove small ones
    grain_labels = morphology.label(grain_mask, connectivity=1)
    for region in measure.regionprops(grain_labels):
        if region.area < min_grain_area:
            grain_labels[grain_labels == region.label] = 0
    grain_labels = morphology.label(grain_labels > 0, connectivity=1)

    # Extract grain boundaries and clean small fragments
    grain_boundaries = segmentation.find_boundaries(morphology.dilation(grain_labels), mode='outer')
    boundary_labels = morphology.label(grain_boundaries, connectivity=2)
    for region in measure.regionprops(boundary_labels):
        if region.area < min_boundary_length:
            boundary_labels[boundary_labels == region.label] = 0

    # Convert to xarray.DataArray with coordinates
    cleaned_boundaries = xr.DataArray(boundary_labels > 0, dims=['y', 'x'])
    cleaned_boundaries['x'] = self._obj.x
    cleaned_boundaries['y'] = self._obj.y

    grain_labels = xr.DataArray(morphology.label(~cleaned_boundaries.values, connectivity=1), dims=['y', 'x'])
    grain_labels['x'] = self._obj.x
    grain_labels['y'] = self._obj.y

    return cleaned_boundaries,grain_labels


# --------------------------------------------------

xr.Dataset.aita.mean_grain= mean_grain
xr.Dataset.aita.area_grain= area_grain
xr.Dataset.aita.dist2GB = dist2GB
xr.Dataset.aita.dist2TJ_micro = dist2TJ_micro
xr.Dataset.aita.closest_outG_value = closest_outG_value
xr.Dataset.aita.filter = filter
xr.Dataset.aita.get_neighbours = get_neighbours
xr.Dataset.aita.TJ_map = TJ_map
xr.Dataset.aita.dist2eachTJ = dist2eachTJ
xr.Dataset.aita.dist2TJ_labels = dist2TJ_labels
xr.Dataset.aita.closest_outTJ_value = closest_outTJ_value
xr.Dataset.aita.anisotropy_factors = anisotropy_factors  
xr.Dataset.aita.quick_segmentation = quick_segmentation