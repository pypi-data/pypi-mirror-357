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


def fliplr(self):
    '''
    Geometric transformation

    Flip left right the data and rotate the orientation  
    May be it is more a routation around the 0y axis of 180 degree

    Return :
        - xarray.Dataset : fliped dataset
    '''
    ori = np.array(self._obj.orientation)
    ori[:, :, 0] = np.mod(2*np.pi-ori[:, :, 0], 2*np.pi)
    ori = np.fliplr(ori)

    qua = np.fliplr(self._obj.quality)
    mi = np.fliplr(self._obj.micro)

    ds = xr.Dataset(
        {
            "orientation": (["y", "x", "uvecs"], ori),
            "quality": (["y", "x"], qua),
            "micro": (["y", "x"], mi),
            "grainId": (["y", "x"], skimage.morphology.label(mi, connectivity=1, background=1)),

        },
        coords={
            "x": np.array(self._obj.x),
            "y": np.array(self._obj.y),
        },
    )

    ds.attrs["date"] = self._obj.attrs['date']
    ds.attrs["unit"] = self._obj.attrs['unit']
    ds.attrs["step_size"] = self._obj.attrs['step_size']
    ds.attrs["path_dat"] = self._obj.attrs['path_dat']

    return ds

# ----------------------------------------


def rot180(self):
    '''
    Geometric transformantion

    Rotate 180 degre around Oz the data and rotate the orientation 

    Return :
        - xarray.Dataset : rotated dataset
    '''

    ori = np.array(self._obj.orientation)
    ori[:, :, 0] = np.mod(np.pi+ori[:, :, 0], 2*np.pi)
    ori = np.flipud(np.fliplr(ori))

    qua = np.flipud(np.fliplr(self._obj.quality))
    mi = np.flipud(np.fliplr(self._obj.micro))

    ds = xr.Dataset(
        {
            "orientation": (["y", "x", "uvecs"], ori),
            "quality": (["y", "x"], qua),
            "micro": (["y", "x"], mi),
            "grainId": (["y", "x"], skimage.morphology.label(mi, connectivity=1, background=1)),

        },
        coords={
            "x": np.array(self._obj.x),
            "y": np.array(self._obj.y),
        },
    )

    ds.attrs["date"] = self._obj.attrs['date']
    ds.attrs["unit"] = self._obj.attrs['unit']
    ds.attrs["step_size"] = self._obj.attrs['step_size']
    ds.attrs["path_dat"] = self._obj.attrs['path_dat']

    return ds

# --------------------------------------


def rot90c(self):
    '''
    Geometric transformation

    Rotate 90 degre in clockwise direction 

    Return :
        - xarray.Dataset : rotated dataset
    '''
    ori = np.array(self._obj.orientation)
    ori[:, :, 0] = np.mod(-np.pi/2+ori[:, :, 0], 2*np.pi)
    ori = np.fliplr(np.transpose(ori, [1, 0, 2]))

    qua = np.fliplr(np.transpose(np.array(self._obj.quality)))
    mi = np.fliplr(np.transpose(np.array(self._obj.micro)))

    ds = xr.Dataset(
        {
            "orientation": (["y", "x", "uvecs"], ori),
            "quality": (["y", "x"], qua),
            "micro": (["y", "x"], mi),
            "grainId": (["y", "x"], skimage.morphology.label(mi, connectivity=1, background=1)),

        },
        coords={
            "x": np.max(np.array(self._obj.y))-np.array(self._obj.y),
            "y": np.max(np.array(self._obj.x))-np.array(self._obj.x),
        },
    )

    ds.attrs["date"] = self._obj.attrs['date']
    ds.attrs["unit"] = self._obj.attrs['unit']
    ds.attrs["step_size"] = self._obj.attrs['step_size']
    ds.attrs["path_dat"] = self._obj.attrs['path_dat']

    return ds

# --------------------------------------------


def crop(self, lim, rebuild_gId=True):
    '''
    Geometric transformation

    Crop dataset between limits given in parameters

    :param rebuild_gId: recompute the grainID
    :type rebuild_gId: bool
    :param lim:
    :type lim: np.array

    Return:
        - xarray.Dataset : croped dataset
    '''
    ds = self._obj.where((self._obj.x > np.min(lim[0])) * (self._obj.x < np.max(lim[0])) * (
        self._obj.y > np.min(lim[1]))*(self._obj.y < np.max(lim[1])), drop=True)

    if rebuild_gId:
        ds.grainId.data = skimage.morphology.label(
            ds.micro, connectivity=1, background=1)

    return ds

# ----------------------------------------------


def resize(self, res):
    '''
    Geometric transformation

    Resize the dataset

    :param res: resolution factor
    :type res: float

    Return: 
        - xarray.Dataset : resized dataset
    '''

    zoom = self._obj.step_size/res
    k = True
    for name in self._obj.data_vars:
        if len(self._obj.get(name).shape) == 2:
            tmp = scipy.ndimage.interpolation.zoom(
                self._obj.get(name), zoom, order=0, mode='nearest')
            tmp = np.flipud(tmp)
        elif len(self._obj.get(name).shape) == 3:
            tmp = []
            for i in range(self._obj.get(name).shape[-1]):
                tmp.append(scipy.ndimage.interpolation.zoom(
                    self._obj.get(name)[:, :, i], zoom, order=0, mode='nearest'))
            tmp = np.dstack(np.fliplr(tmp))

        if k:
            nself = xr.Dataset()
            nself.attrs = self._obj.attrs
            nself.attrs['step_size'] = res
            ss = tmp.shape
            idx = np.linspace(0, ss[1]-1, ss[1])*res
            idy = np.linspace(0, ss[0]-1, ss[0])*res
            nself.coords['x'] = idx
            nself.coords['y'] = idy
            k = False

        nself[name] = xr.DataArray(tmp, dims=self._obj.get(name).dims)

    return nself

# -----------------------------------------------------
def downscale(self,n):
    '''
    Downscale the data in order to keep one value for each n x n boxes.
    
    :param n:
    :type n: int
    '''
    ww=np.zeros([n,n])
    ww[0,0]=1

    weights = xr.DataArray(ww, dims=["x_window", "y_window"])

    aec=self._obj.coarsen(x=n,y=n,boundary='trim').construct(
        x=("xn", "x_window"),
        y=("yn", "y_window")
    )

    ds_n=(aec*weights).sum(["x_window", "y_window"])
    ds_n=ds_n.rename({'xn': 'x','yn': 'y'})
    ds_n.attrs=self._obj.attrs
    ds_n['x']=ds_n.x*ds_n.attrs['step_size']*n
    ds_n['y']=(ds_n.y[-1]-ds_n.y)*ds_n.attrs['step_size']*n
    ds_n.attrs['step_size']=ds_n.attrs['step_size']*n
    
    return ds_n
# -----------------------------------------------------

xr.Dataset.aita.downscale = downscale
xr.Dataset.aita.fliplr = fliplr
xr.Dataset.aita.rot180 = rot180
xr.Dataset.aita.rot90c = rot90c
xr.Dataset.aita.crop = crop
xr.Dataset.aita.resize = resize
