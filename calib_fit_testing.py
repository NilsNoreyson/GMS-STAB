# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 15:26:56 2014

@author: peterb
"""

from fit_helper import *
import plotDataSets as PLT
import sensorMetaData as Meta
sensorSheetsFolder=Meta.getSensorSheetsFolder()
sensorMetaData=Meta.updateSummary(sensorSheetsFolder)



from pylab import *





def addUndublicatedLegend(axes,legendSize=None,loc=None):
    handles=[]
    labels=[]
    for a in axes:
        h, l = a.get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)
        
    L=[]
    H=[]            
    for i,l in enumerate(labels):
        if l in L:
            continue
        else:
            L.append(l)
            H.append(handles[i])
    if legendSize:
        prop={'size':legendSize}
    else:
        prop=None
        
    axes[0].legend(H, L,prop=prop,loc=loc)









def calc_n_a_from_last_n(name,sensorData,n=1):
    sensorData[name]['n']=NaN
    sensorData[name]['b']=NaN
    data=sensorData[name][sensorData[name]['conc']>0]
    for i in range(len(data['r'])):
        index=data.index[i]
        if i<n:
            continue
        else:
            yData=list(data['r_min'][i-n:i+1])
            xData=list(data['conc'][i-n:i+1])
            
            
            p,pE=fitExposure(xData,yData)
            sensorData[name]['n'].ix[index]=p[1]
            sensorData[name]['b'].ix[index]=p[0]

            
            
    


def set_axe_limit(axe,name='n',legend='x'):
    limits={'n':(-1,0,'linear'),
            'b':(1e4,1e9,'log'),
            'r_pre':(1e4,1e9,'log')
            }
    if legend=='x':
        axe.set_xlim(limits[name][0],limits[name][1])
        axe.set_xscale(limits[name][2])
    if legend=='y':
        axe.set_ylim(limits[name][0],limits[name][1])
        axe.set_yscale(limits[name][2])




def plot_parameter_against(sensorData,left=None,right=None,altX=None,humid=True,link=True):
    
    names=[s for s in sensorData.keys() if not(s in ['REF','Reference_Resistance'])]
    print names
    
    if humid:
        fig, axes=subplots(5,4,figsize=(30,20))
    else:
        fig, axes=subplots(4,4,figsize=(30,20))
        
    for sensorName in names:
        
        calc_n_a_from_last_n(name=sensorName,sensorData=sensorData,n=1)
        data=sensorData[sensorName][sensorData[sensorName]['conc']>0]
        
        axe=fig.axes[data['pos'][0]]
        
        axe.set_title("%s%s"%(sensorName,Meta.getSensorMetaDataLabel(sensorName,sensorMetaData)))
    
        spacer=0.05
        fig.subplots_adjust(hspace=.5,wspace=.5,top=1-spacer,bottom=spacer,left=spacer,right=1-spacer)
        
        if altX:
            if left:
                
                x=data[altX].dropna()
                
                
                lowH_x=data[altX][data['backgroundHumidity']<50]
                highH_x=data[altX][data['backgroundHumidity']>50]
                
                colorMap={0:'g',1:'b'}                

                for c,x in enumerate([lowH_x,highH_x]):
                    c=colorMap[c]
                    
                    x=x[x<1e20]
                    
                    y=data[left][x.index]

                    x=list(x)
                    
                    axe.plot(x,y,'%so'%c,label=left)
                    axe.set_xlabel(altX)
                    axe.set_ylabel(left)

                
                set_axe_limit(axe,name=altX,legend='x')
                set_axe_limit(axe,name=left,legend='y')
                    
                
                addUndublicatedLegend([axe],legendSize=None,loc=None)  
                
                if link:
                    axe.callbacks.connect('xlim_changed', PLT.on_xlim_changed)
                    axe.callbacks.connect('ylim_changed', PLT.on_ylim_changed)
            
        else:
            axe2=axe.twinx()
            y=data[left].dropna()
            y=y[y<1e20]
            x=y.index
            
            axe.plot(x,y,'ko',label=left)
            axe.set_ylabel(left)
            axe.set_xlabel('Time')

            set_axe_limit(axe,name=left,legend='y')



            
            
            y2=data[right].dropna()
            y2=y2[y2<1e20]
            x2=y2.index
            axe2.plot(x2,y2,'bo',label=right)
            axe2.set_ylabel(right)

            set_axe_limit(axe2,name=right,legend='y')              


            addUndublicatedLegend([axe,axe2],legendSize=None,loc=None)  

            if link:        
                axe.callbacks.connect('xlim_changed', PLT.on_xlim_changed)
                axe.callbacks.connect('ylim_changed', PLT.on_ylim_changed)
            
                axe2.callbacks.connect('xlim_changed', PLT.on_xlim_changed)
                axe2.callbacks.connect('ylim_changed', PLT.on_ylim_changed)
            
                
        print sensorName


    if humid:
        for i in [0,1,2,3]:
            axe=axes[4][i]
            humidity=sensorData[sensorData.keys()[0]]['backgroundHumidity'].dropna()
            axe.plot(humidity.index,humidity,'bo')
            axe.set_ylabel('Rel. back. humidity [%]')

    if altX:
        pass
    else:
        PLT.formatFigForDates(fig)
    spacer=0.05
    #    hspace=fig.subplotpars.hspace
    fig.subplots_adjust(hspace=.5,top=1-spacer,bottom=spacer,left=spacer,right=1-spacer)

    return fig

if __name__=="__main__":

    pngFolder=folders[0]    
#    fig=plot_parameter_against(sensorData,left='n',right='r_pre',humid=True)
#    name='n_and_r_pre_vs_t'
#    name=name+".png"
#    fig.savefig(os.path.join(pngFolder,name))

    
    fig=plot_parameter_against(sensorData,left='n',right='r_pre',link=False)
    name='n_and_r_pre_vs_t'
    name=name+".png"
    fig.savefig(os.path.join(pngFolder,name))
    
    
    fig=plot_parameter_against(sensorData,left='b',right='r_pre',link=False)
    name='b_vs_r_pre'
    name=name+".png"
    fig.savefig(os.path.join(pngFolder,name))
    
    
    fig=plot_parameter_against(sensorData,left='n',altX='b',humid=False,link=False)
    name='n_vs_b'
    name=name+".png"
    fig.savefig(os.path.join(pngFolder,name))
    
    
    fig=plot_parameter_against(sensorData,left='n',altX='r_pre',humid=False,link=False)
    name='n_vs_r_pre'
    name=name+".png"
    fig.savefig(os.path.join(pngFolder,name))


    fig=plot_parameter_against(sensorData,left='b',altX='r_pre',humid=False,link=False)
    name='b_vs_r_pre_correlation'
    name=name+".png"
    fig.savefig(os.path.join(pngFolder,name))
    
    fig=plot_parameter_against(sensorData,left='n',altX='b',humid=False,link=False)
    name='n_vs_b_correlation'
    name=name+".png"
    fig.savefig(os.path.join(pngFolder,name))
#
#    
#    
#    
#
#
