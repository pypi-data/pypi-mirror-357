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


def interactive_crop(self,rebuild_gId=True):
    '''
    out=data.aita.interactive_crop()
    
    :param rebuild_gId: recompute the grainID
    :type rebuild_gId: bool

    This function can be use to crop within a jupyter notebook
    It will crop the data and export the value of the crop in out.pos
    '''
    
    def onselect(eclick, erelease):
        "eclick and erelease are matplotlib events at press and release."
        print('startposition: (%f, %f)' % (eclick.xdata, eclick.ydata))
        print('endposition  : (%f, %f)' % (erelease.xdata, erelease.ydata))
        print('used button  : ', eclick.button)

    def toggle_selector(event):
        print('Key pressed.')
        if event.key in ['Q', 'q'] and toggle_selector.RS.active:
            print('RectangleSelector deactivated.')
            toggle_selector.RS.set_active(False)
        if event.key in ['A', 'a'] and not toggle_selector.RS.active:
            print('RectangleSelector activated.')
            toggle_selector.RS.set_active(True)

    print('1. click and drag the mouse on the figure to selecte the area')
    print('2. you can draw the rectangle using the button "Draw area"')
    print('3. if you are unhappy with the selection restart to 1.')
    print('4. if you are happy with the selection click on "Export crop" (only the last rectangle is taken into account)')

    
    fig,ax=plt.subplots()
    ml=np.max(np.array([len(self._obj.x),len(self._obj.y)]))
    fig.set_figheight(len(self._obj.y)/ml*15)
    fig.set_figwidth(len(self._obj.x)/ml*15)
    tmp=self._obj.copy()
    tmp['colormap']=self._obj.orientation.uvecs.calc_colormap()
    tmp.colormap.plot.imshow()
    toggle_selector.RS = matplotlib.widgets.RectangleSelector(ax, onselect, interactive=True)
    fig.canvas.mpl_connect('key_press_event', toggle_selector)


    buttonCrop = widgets.Button(description='Export crop')
    buttonDraw = widgets.Button(description='Draw area')
    
    def draw_area(_):
        x=list(toggle_selector.RS.corners[0])
        x.append(x[0])
        y=list(toggle_selector.RS.corners[1])
        y.append(y[0])
        plt.plot(x,y,'-k')

    def get_data(_):
        x=list(toggle_selector.RS.corners[0])
        x.append(x[0])
        y=list(toggle_selector.RS.corners[1])
        y.append(y[0])
        # what happens when we press the button
        out=self.crop(lim=toggle_selector.RS.corners,rebuild_gId=rebuild_gId)
        plt.plot(x,y,'-b')
        get_data.ds=out
        get_data.crop=toggle_selector.RS.corners
        
        return get_data
        
        


    # linking button and function together using a button's method
    buttonDraw.on_click(draw_area)
    buttonCrop.on_click(get_data)
    # displaying button and its output together
    display(buttonDraw,buttonCrop)

    return get_data

# --------------------------------------

def interactive_misorientation_profile(self,res=0,degre=True):
    '''
    Interactive misorientation profile for jupyter notebook
    
    :param res: step size of the profil
    :type res: float
    :param degre: return mis2o and mis2p in degre overwise in radian (default: true)
    :type degre: bool
    '''
    fig,ax=plt.subplots()
    ml=np.max(np.array([len(self._obj.x),len(self._obj.y)]))
    fig.set_figheight(len(self._obj.y)/ml*15)
    fig.set_figwidth(len(self._obj.x)/ml*15)
    tmp=self._obj.copy()
    tmp['colormap']=tmp.orientation.uvecs.calc_colormap()
    tmp.colormap.plot.imshow()
    ax.axis('equal')

    pos = []
    def onclick(event):
        pos.append([event.xdata,event.ydata])
        if len(pos)==1:
            plt.plot(pos[0][0],pos[0][1],'sk')
        else:
            pos_mis=np.array(pos[-2::])
            plt.plot(pos[-2][0],pos[-2][1],'sk')
            plt.plot(pos[-1][0],pos[-1][1],'ok')
            plt.plot(pos_mis[:,0],pos_mis[:,1],'-k')


    fig.canvas.mpl_connect('button_press_event', onclick)

    buttonShow = widgets.Button(description='Show line')
    buttonExtract = widgets.Button(description='Extract profile')


    def extract_data(_):
        pos_mis=np.array(pos[-2::])
        ll=((pos_mis[1,1]-pos_mis[1,0])**2+(pos_mis[0,1]-pos_mis[0,0])**2)**0.5
        if res==0:
            rr=np.array(np.abs(self._obj.x[1]-self._obj.x[0]))
        else:
            rr=res
        nb=int(ll/rr)
        
        xx=np.linspace(pos_mis[0,0],pos_mis[1,0],nb)
        yy=np.linspace(pos_mis[0,1],pos_mis[1,1],nb)
        ds=self._obj.orientation.uvecs.misorientation_profile(xx,yy,degre=degre)
        ds.attrs["start"]=pos_mis[0,:]
        ds.attrs["end"]=pos_mis[1,:]
        ds.attrs["step_size"]=rr
        ds.attrs["unit"]=self._obj.unit

        extract_data.ds=ds
        

        return extract_data


    # linking button and function together using a button's method
    buttonExtract.on_click(extract_data)

    # displaying button and its output together
    display(buttonExtract)

    return extract_data

# ------------------------------------

def interactive_segmentation(self,val_scharr_init=1.5,use_scharr_init=True,val_canny_init=1.5,use_canny_init=True,val_qua_init=60,use_qua_init=False,inc_border_init=False):
    '''
    This function allow you to performed grain segmentation on aita data.
    The intitial value of the segmenation function can be set-up initially
    
    :param val_scharr_init: scharr filter usually between 0 and 10 (default : 1.5)
    :type val_scharr_init: float
    :param use_scharr_init: use scharr filter
    :type use_scharr_init: bool
    :param val_canny_init: canny filter usually between 0 and 10 (default : 1.5)
    :type val_canny_init: float
    :param use_canny_init: use canny filter
    :type use_canny_init: bool
    :param val_qua_init: quality filter usually between 0 and 100 (default : 60)
    :type val_qua_init: int
    :param use_qua_init: use quality filter
    :type use_qua_init: bool
    :param inc_border_init: add image border to grain boundaries
    :type inc_border_init: bool
    
    .. note:: on data with holes such as snow, using quality filter is not recommended 
    '''

    
    #~~~~~~~~~~~~~~~~~~ segmentation function~~~~~~~~~~~~~~~~
    def seg_scharr(field):
        ## Commented bit are previous settings which just use raw Phi1
        ## define Scharr filter
        scharr = np.array([[-3-3j,0-10j,3-3j],[-10+0j,0+0j,10+0j],[-3+3j,0+10j,3+3j]])

        ## run edge detection.
        edge_sin = np.abs(np.real(scipy.signal.convolve2d(np.sin(field*2)+1,scharr,boundary='symm',mode='same')))

        return edge_sin


    #~~~~~~~~~~~~~~~~~~pruning function~~~~~~~~~~~~~~~~~~~~~~
    def endPoints(skel):
        endpoint1=np.array([[0, 0, 0],
                            [0, 1, 0],
                            [2, 1, 2]])

        endpoint2=np.array([[0, 0, 0],
                            [0, 1, 2],
                            [0, 2, 1]])

        endpoint3=np.array([[0, 0, 2],
                            [0, 1, 1],
                            [0, 0, 2]])

        endpoint4=np.array([[0, 2, 1],
                            [0, 1, 2],
                            [0, 0, 0]])

        endpoint5=np.array([[2, 1, 2],
                            [0, 1, 0],
                            [0, 0, 0]])

        endpoint6=np.array([[1, 2, 0],
                            [2, 1, 0],
                            [0, 0, 0]])

        endpoint7=np.array([[2, 0, 0],
                            [1, 1, 0],
                            [2, 0, 0]])

        endpoint8=np.array([[0, 0, 0],
                            [2, 1, 0],
                            [1, 2, 0]])

        ep1=mh.morph.hitmiss(skel,endpoint1)
        ep2=mh.morph.hitmiss(skel,endpoint2)
        ep3=mh.morph.hitmiss(skel,endpoint3)
        ep4=mh.morph.hitmiss(skel,endpoint4)
        ep5=mh.morph.hitmiss(skel,endpoint5)
        ep6=mh.morph.hitmiss(skel,endpoint6)
        ep7=mh.morph.hitmiss(skel,endpoint7)
        ep8=mh.morph.hitmiss(skel,endpoint8)
        ep = ep1+ep2+ep3+ep4+ep5+ep6+ep7+ep8
        return ep

    def pruning(skeleton, size):
        '''remove iteratively end points "size" 
            times from the skeletonget_ipython().__class__.__name__
        '''
        for i in range(0, size):
            endpoints = endPoints(skeleton)
            endpoints = np.logical_not(endpoints)
            skeleton = np.logical_and(skeleton,endpoints)
        return skeleton
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #plot image
    ds = self._obj.copy()
    
    data_img_semi=np.array(ds.orientation.uvecs.calc_colormap(semi=True))
    data_img=np.array(ds.orientation.uvecs.calc_colormap(semi=True))
        
    
    ob=np.array(ds.orientation.uvecs.bunge_euler())
    phi1=ob[:,:,0]
    phi=ob[:,:,1]
    qua=np.array(ds.quality)

    def calcGB(val_scharr,use_scharr,val_canny,use_canny,val_qua,use_qua,dilate,CM,CW,inc_border):         
        micro=[]
        IMdata=[]
        if CW=='semi color wheel' or CW=='both color wheel':
            IMdata.append(data_img_semi)
            
        if CW=='full color wheel' or CW=='both color wheel':
            IMdata.append(data_img)
        
            
        if use_canny:
            for im in IMdata:
                edges1 = skimage.feature.canny(im[:,:,0],sigma=val_canny)
                edges2 = skimage.feature.canny(im[:,:,1],sigma=val_canny)
                edges3 = skimage.feature.canny(im[:,:,2],sigma=val_canny)
                micro.append((edges1+edges2+edges3)>0.5)
            
        if use_scharr:
            seg1=seg_scharr(phi1)
            seg2=seg_scharr(phi)
            micro.append((seg1+seg2)>val_scharr)
            
        if use_qua:
            micro.append(qua<val_qua)
            
        
        
        Edge_detect=np.zeros(micro[0].shape)
        for m in micro:
            Edge_detect+=m/len(micro)
        
        if inc_border:
            Edge_detect[0,:]=1
            Edge_detect[-1,:]=1
            Edge_detect[:,0]=1
            Edge_detect[:,-1]=1

        microCL=skimage.morphology.area_closing(Edge_detect)
        # skeleton
        skeleton = skimage.morphology.skeletonize(microCL,method='lee')
        # prunnig
        skeleton=pruning(skeleton,100)
        # remove dot 
        mat1=np.array([[-1,-1,-1],[-1,1,-1],[-1,-1,-1]])
        skeleton[scipy.signal.convolve2d(skeleton,mat1,mode='same',boundary='fill')==1]=0

        #remove small grain
        #skeleton2=skeleton
        #for i in range(small_grain):
        #    skeleton2=skimage.morphology.dilation(skeleton2)
        #    skeleton2=pruning(skeleton2,100)
            
        #TrueMicro=skimage.morphology.skeletonize(skeleton2)
        
        TrueMicro=skeleton
        if inc_border:
            TrueMicro[0,:]=1
            TrueMicro[-1,:]=1
            TrueMicro[:,0]=1
            TrueMicro[:,-1]=1

                
        dTrueMicro=TrueMicro
        
        for i in range(dilate):
            dTrueMicro=skimage.morphology.dilation(dTrueMicro) 
        
        
        #fig,ax=plt.subplots()
                
        
        if CM=='semi color wheel':
            plt.imshow(data_img_semi)
            plt.imshow(dTrueMicro,alpha=dTrueMicro.astype(float),cmap=cm.gray)
        elif CM=='full color wheel':
            plt.imshow(data_img)
            plt.imshow(dTrueMicro,alpha=dTrueMicro.astype(float),cmap=cm.gray)
        elif CM=='none':
            plt.imshow(dTrueMicro,cmap=cm.gray)
            
        #toggle_selector.RS = matplotlib.widgets.RectangleSelector(ax, onselect, drawtype='box')
        #fig.canvas.mpl_connect('key_press_event', toggle_selector)
        
        return TrueMicro
            
    
            
    def export_micro(_):
        TrueMicro=calcGB(val_scharr.get_interact_value(),use_scharr.get_interact_value(),val_canny.get_interact_value(),use_canny.get_interact_value(),val_qua.get_interact_value(),use_qua.get_interact_value(),dilate.get_interact_value(),CM.get_interact_value(),CW.get_interact_value(),inc_border.get_interact_value())
        # create microstructure
        ds['micro']=xr.DataArray(TrueMicro,dims=[self._obj.orientation.coords.dims[0],self._obj.orientation.coords.dims[1]])
        ds['grainId']=xr.DataArray(skimage.morphology.label(TrueMicro, connectivity=1, background=1),dims=[self._obj.orientation.coords.dims[0],self._obj.orientation.coords.dims[1]])
        
        export_micro.ds=ds
        
        export_micro.val_scharr=val_scharr.get_interact_value()
        export_micro.use_scharr=use_scharr.get_interact_value()
        export_micro.val_canny=val_canny.get_interact_value()
        export_micro.use_canny=use_canny.get_interact_value()
        export_micro.img_canny=CW.get_interact_value()
        export_micro.val_quality=val_qua.get_interact_value()
        export_micro.use_quality=use_qua.get_interact_value()
        export_micro.include_border=inc_border.get_interact_value()
        
        return export_micro
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~ interactive plot~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    val_scharr=widgets.FloatSlider(value=val_scharr_init,min=0,max=10.0,step=0.1,description='Scharr filter:',disabled=False,continuous_update=False,orientation='horizontal',readout=True,readout_format='.1f')
    use_scharr=widgets.Checkbox(value=use_scharr_init,description='Use scharr filter',disabled=False)

    val_canny=widgets.FloatSlider(value=val_canny_init,min=0,max=10.0,step=0.1,description='Canny filter:',disabled=False,continuous_update=False,orientation='horizontal',readout=True,readout_format='.1f')
    use_canny=widgets.Checkbox(value=use_canny_init,description='Use canny filter',disabled=False)
    
    val_qua=widgets.FloatSlider(value=val_qua_init,min=0,max=100,step=1,description='Quatlity filter:',disabled=False,continuous_update=False,orientation='horizontal',readout=True,readout_format='.1f')
    use_qua=widgets.Checkbox(value=use_qua_init,description='Use Quality filter',disabled=False)
    
    inc_border=widgets.Checkbox(value=inc_border_init,description='Include border as grain boundaries',disabled=False)

    
    #small_grain=widgets.IntSlider(value=0,min=0,max=5,step=1,description='Remove small grain:',disabled=False,continuous_update=False,orientation='horizontal',readout=True,readout_format='d')

    dilate=widgets.IntSlider(value=0,min=0,max=10,step=1,description='Dilate GB:',disabled=False,continuous_update=False,orientation='horizontal',readout=True,readout_format='d')
    CM=widgets.Dropdown(value='semi color wheel', options=['semi color wheel', 'full color wheel', 'none'], description='Plot colormap')
    CW=widgets.Dropdown(value='semi color wheel', options=['semi color wheel', 'full color wheel', 'both color wheel'], description='Segmentation colormap')
    buttonExport = widgets.Button(description='Export AITA')

    
    ui_scharr=widgets.HBox([val_scharr,use_scharr])
    ui_canny=widgets.HBox([val_canny,use_canny,CW])
    ui_quality=widgets.HBox([val_qua,use_qua])

    ui=widgets.VBox([ui_scharr,ui_canny,ui_quality,inc_border,dilate,CM,buttonExport])
    out = widgets.interactive_output(calcGB,{'val_scharr': val_scharr,'use_scharr':use_scharr,'val_canny':val_canny,'use_canny':use_canny,'val_qua':val_qua,'use_qua':use_qua,'dilate': dilate,'CM': CM,'CW': CW,'inc_border': inc_border})
    display(ui,out)

    buttonExport.on_click(export_micro)
    return export_micro

# ----------------------------------------------

xr.Dataset.aita.interactive_crop = interactive_crop
xr.Dataset.aita.interactive_misorientation_profile = interactive_misorientation_profile
xr.Dataset.aita.interactive_segmentation = interactive_segmentation