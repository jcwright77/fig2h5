def fig2h5(name,fig,md,info=True,**args):
    import matplotlib.pyplot as plt
    import numpy as np
    import h5py
    
    axhdl=fig.axes
    
    #logic to get axis if just list of one axis [as returned by fig.get_axes() ]
    if str(type(axhdl))=="<class 'list'>":
        if len(axhdl)==1:
            axhdl=axhdl[0]
    
    hf = h5py.File(name+'.h5', 'a')

    hf.attrs.update(md)
    
    grp1 = hf.create_group("data")
    if info : print('group', grp1.name)

    if str(type(axhdl))=="<class 'matplotlib.axes._subplots.AxesSubplot'>":
        AxesSubplot2h5(grp1, fig, axhdl, info, **args )
    
    elif str(type(axhdl))=="<class 'numpy.ndarray'>" or str(type(axhdl))=="<class 'list'>":
        if info: print('fig2h5 subfigure call') 
        Subfigures2h5(grp1, fig, axhdl, info, **args)
        
    elif str(type(axhdl))=="<class 'matplotlib.axes._subplots.Axes3DSubplot'>":
        Axes3DSubplot2h5(grp1, fig, axhdl, info, **args)
        
    
    hf.close()
    
    

def AxesSubplot2h5(topgrp,fig,axhdl,info,**args):
    """
    Handler for one dim plots possibly with multiple lines and 
    redirection for histograms
    """ 

    grp1 = topgrp.create_group("plot")
    if len(axhdl.containers)!=0:
        print('fig2h5 histogram call') 
        AxesHistogram2h5(grp1,fig,axhdl,info, **args)
        return
    
    if info : print('group', grp1.name)
    grp1.attrs['plotposition']=np.array(axhdl.get_position())
    grp1.attrs['title']=axhdl.title.get_text()
    grp1.attrs['xlabel']=axhdl.xaxis.label.get_text()
    grp1.attrs['ylabel']=axhdl.yaxis.label.get_text()

    nplots=len(axhdl.lines)
    for i in range(nplots):
        if info: print('AxesSubplot2h5 loop: nlines, index', nplots, i)
        l1=axhdl.lines[i]
        dset = grp1.create_dataset('linex'+str(i+1), 
                                  data=l1.get_xdata())
        dset = grp1.create_dataset('liney'+str(i+1), 
                                  data=l1.get_ydata())
        dset.attrs['linecolor']=l1.get_color()
        dset.attrs['linewidth']=l1.get_linewidth()
        dset.attrs['markertype']=l1.get_marker()
        dset.attrs['markercolor']=l1.get_markerfacecolor()



def Subfigures2h5(topgrp,fig,axhdl,info,**args):
    """
    Handler for plots with multiple panels (subfigures).
    """ 
    
    nplots=np.array(axhdl).size
    grp0 = topgrp.create_group("plotgrid"+str(nplots))
    if info : print('group', grp0.name)

    maintitle=fig._suptitle
    if maintitle: 
        grp0.attrs['title']=maintitle.get_text()
    
    if info: print('subfig nplots',nplots)
    for ix in range(nplots):
        grp1 = grp0.create_group("plot"+str(ix+1)+'of'+str(nplots) )
        if info : print('group', grp1.name)
        ax=np.array(axhdl).flatten()[ix]
        if info : print('Subfigures',ix+1,'ax type', str(type(ax)))
        if str(type(ax))=="<class 'matplotlib.axes._subplots.AxesSubplot'>":
            AxesSubplot2h5(grp1, fig, ax, info, **args)
        elif str(type(ax))=="<class 'numpy.ndarray'>" or str(type(axhdl))=="<class 'list'>":
            AxesHistogram2h5(grp1, fig, ax, info, **args)
            
            
    

def Axes3DSubplot2h5(topgrp,fig,axhdl,info,**args):
    """
    Handler for three dim plots possibly with multiple lines
    """ 
    grp1 = topgrp.create_group("plot")
    if info : print('group', grp1.name)
    grp1.attrs['plotposition']=np.array(axhdl.get_position())
    grp1.attrs['title']=axhdl.title.get_text()
    grp1.attrs['xlabel']=axhdl.xaxis.label.get_text()
    grp1.attrs['ylabel']=axhdl.yaxis.label.get_text()

    d = ax.collections
    nplots=len(d)
    if info: print('Axes3DSubplot2h5', nplots)
    for i in range(nplots):
        if info: print('Axes3DSubplot2h5', nplots, i)
        dset = grp1.create_dataset('points3d'+str(i+1), 
                                  data=np.array(d[i]._offsets3d).T)
        dset.attrs['markercolor']=d[i].get_facecolor()[-1][0:3]

        

def AxesHistogram2h5(topgrp,fig,axhdl,info,**args):
    """
    Handler for histograms
    """ 
    import numpy as np
    
    grp1 = topgrp.create_group("plot")
    if info : print('group', grp1.name)
    grp1.attrs['plotposition']=np.array(axhdl.get_position())
    grp1.attrs['title']=axhdl.title.get_text()
    grp1.attrs['xlabel']=axhdl.xaxis.label.get_text()
    grp1.attrs['ylabel']=axhdl.yaxis.label.get_text()

    d = axhdl.containers #https://matplotlib.org/3.1.1/api/container_api.html
    #https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.Rectangle.html#matplotlib.patches.Rectangle

    nsets=len(d)
    if info: print('Axes3DSubplot2h5', nsets)
    for i in range(nsets):
        if info: print('Axes3DSubplot2h5 nsets', nsets, i)
        rsw=[] ; rsxy=[] ; rsdv=[] 
        for j,rect in enumerate(d[i].get_children()):
            if info: print('Axes3DSubplot2h5 rect', j)
            rsxy.append( rect.xy )
            rsw.append(  rect.get_width()  )
            rsdv.append( rect.get_height() ) #datavalues[j])
        dset = grp1.create_dataset('bins_xy'+str(i+1), data=np.array(rsxy) )
        dset = grp1.create_dataset('bins_width'+str(i+1), data=np.array(rsw) )
        dset = grp1.create_dataset('bins_height'+str(i+1), data=np.array(rsdv) )
        dset.attrs['markercolor']=rect.get_facecolor()[0:3]
        if 'rawdata' in args:
            rd = args['rawdata']
            dset = grp1.create_dataset('rawdata'+str(i+1), data=rd)
       
