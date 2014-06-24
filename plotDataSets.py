# -*- coding: utf-8 -*-
"""
Created on Tue Jan 07 12:54:34 2014

@author: peters
"""

import time
import datetime
startT=datetime.datetime.now()


import pandas as pd
import os
import numpy as np
import pickle

import Tkinter
import tkMessageBox
import tkFileDialog 

#for reading the excel file
import xlrd


import sys

import sensorMetaData as Meta
sensorSheetsFolder=Meta.getSensorSheetsFolder()
sensorMetaData=Meta.updateSummary(sensorSheetsFolder)
import mergeAllFolder as Merge
from parseExperimentalData import *


timeFormat="%d.%m.%Y %H:%M:%S"


import numpy as np  # NumPy (multidimensional arrays, linear algebra, ...)
import scipy as sp  # SciPy (signal and image processing library)


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import matplotlib as mpl         # Matplotlib (2D/3D plotting library)
mpl.use('Agg')
matplotlib.use('Agg')


from pylab import *              # Matplotlib's pylab interface
ion()                            # Turned on Matplotlib's interactive mode



#import guidata  # GUI generation for easy dataset editing and display

#import guiqwt                 # Efficient 2D data-plotting features
#import guiqwt.pyplot as plt_  # guiqwt's pyplot: MATLAB-like syntax
#plt_.ion()                    # Turned on guiqwt's interactive mode



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


def on_ylim_changed(ax):
    ylim=ax.get_ylim()
    for a in ax.figure.axes:
        try:
            rescale=a.y_rescale_on_changed
        except:
            rescale=True
        if rescale:
            # shortcuts: last avoids n**2 behavior when each axis fires event
            if a is ax or len(a.lines) == 0 or getattr(a, 'ylim', None) == ylim:
                continue
    
    
            # TODO: update limits from Patches, Texts, Collections, ...
    
            # x axis: emit=False avoids infinite loop
            a.set_ylim(ylim, emit=False)
            a.ylim=ylim
            #a.redraw_in_frame()

def on_xlim_changed(ax):
    xlim = ax.get_xlim()
    ylim=ax.get_ylim()

    for a in ax.figure.axes:
        # shortcuts: last avoids n**2 behavior when each axis fires event
        if a is ax or len(a.lines) == 0 or getattr(a, 'xlim', None) == xlim:
            continue

        #ylim = np.inf, -np.inf
        
        for l in a.lines:
            pass
            #x, y = l.get_data()
            # faster, but assumes that x is sorted
            #start, stop = np.searchsorted(x, xlim)
            #yc = y[max(start-1,0):(stop+1)]
            #ylim = min(ylim[0], np.nanmin(yc)), max(ylim[1], np.nanmax(yc))

        # TODO: update limits from Patches, Texts, Collections, ...

        # x axis: emit=False avoids infinite loop
        a.set_xlim(xlim, emit=False)

        # y axis: set dataLim, make sure that autoscale in 'y' is on 
        #corners = (xlim[0], ylim[0]), (xlim[1], ylim[1])
#        #print ylim        
#        #a.set_ylim(ylim,emit=False)
#        #a.ylim=ylim
        #a.dataLim.update_from_data_xy(corners, ignore=True, updatex=False)
        #a.autoscale(enable=True, axis='y')
        # cache xlim to mark 'a' as treated
        a.xlim = xlim
        



def plotAllHeatingPulses(dataFrame,sensorName,preSec=20,postSec=20,yLim=(100,1e8),xLim=None):
    fig,axes=subplots(2,1)
    axes2=[a.twinx() for a in axes]
    offset=0
    sensorPos=dataFrame.sensorData.get_loc(sensorName)
    
    heaterNumber=dF.heaterOfPosition[sensorPos]
    
    
    
    metaPlot='Voltage_Channel_%i_actual'%(heaterNumber)

    
    for i,pulseData in dataFrame.pulsesBySensor[sensorNumber].iterrows():
        p=(pulseData['start'],pulseData['stop'])
        if (dataFrame['MFC_2_conc_set'][p[0]:p[1]]>0).any():
            axe=axes[0]
            axe2=axes2[0]
        else:
            axe=axes[1]
            axe2=axes2[1]
            
        y=dataFrame[sensorName][p[0]-preSec:p[1]+postSec].dropna()
        
        
        
        if dataFrame['MFC_1_conc_set'][p[0][0]:p[1]].iloc[0]<50:
            col="r"
        else:
            col="b"
        
        
        x=np.array(y.index)-p[0]+offset
        

        
        axe.plot(x,y,col)
    
        
        if metaPlot:
        #axe2=axe.twinx()
            y=dataFrame[metaPlot][p[0]-preSec:p[1]+postSec].dropna()
            x=np.array(y.index)-p[0]+offset
            axe2.plot(x,y,'y-')
            axe2.set_ylim(dF[metaPlot].min()*0.9,dF[metaPlot].max()*1.1)
            offset=offset+p[1]+postSec-p[0]+preSec
    
    for axe in fig.axes:
        axe.set_yscale('log')
        axe.set_xlim((0,offset+300))
        axe.set_ylim(yLim)
    
        
    for ax in fig.axes:
        ax.callbacks.connect('xlim_changed', on_xlim_changed)
        ax.callbacks.connect('ylim_changed', on_ylim_changed)
        

    
    return



def plotMinPulses(sensorData,sensorName,axe,allData=False,dF=None,unit='h',plotValues='r_min',startTime=None,plotRef=False,plotHumid=False,accTime=True,plotSymbol="o",label=None,title=False,yLim=None,setYLim=True,shrinkData=100,linkYAxes=True):
    concColors={50:"g",150:"r","pre":'k','b4H':'y'}
    data=sensorData[sensorName]
    if sensorName=='Reference_Resistance':
        labelExtra='_REF'
    else:
        labelExtra=''
    if accTime:
        data['accTime']=None
        for i,r in data.iterrows():
            data['accTime'][i]=data['duration'][0:i].sum()


    if allData:
        res=dF[sensorName].dropna()[::shrinkData]
        t=res.index
        axe.plot(t,res,"y")
    
    xLabel,scale=createXLabel(startTime,unit)
    
    if plotValues=='r_min':
        tIndex='t_min'
        rIndex='r_min'
    elif plotValues=='r':
        tIndex='t'
        rIndex='r'
    elif plotValues=='calcConc':
        tIndex='t'
        rIndex='calcConc'

    if accTime:
        tIndex='accTime'
    
    
#    for conc in [50,150]:
    for conc in data['conc'].value_counts().keys():


        cData=data[data['conc']==conc]

        if len(cData):
            r=cData[rIndex].dropna()
            t=cData[tIndex].dropna()
            temp=pd.DataFrame({'r':r})
            temp=temp.set_index(t)
            r=temp['r']
            
            
            
            #t=timeStampToDuration(t,startTime,scale)
            plotColor=concColors[conc]
            axe.plot(r.index,r,'%s%s'%(plotColor,plotSymbol),label="min@exposure"+labelExtra)
    
    if not(plotValues=='calcConc'):
        #plot also the pre resistances
        preData=data[data['r_pre']>0]
        r_pre=preData['r_pre']
        if accTime:
            t_pre=preData[tIndex]
        else:
            t_pre=preData['t_pre']
        
        t_pre=timeStampToDuration(t_pre,startTime,scale)
    
        plotColor=concColors['pre']
        axe.plot(t_pre,r_pre,'%s%s'%(plotColor,plotSymbol),label="max@preheating"+labelExtra)
        axe.set_ylabel("$Resistance\/[\Omega]$")
        
        b4HData=data[data['b4r']>0].dropna()     
        b4r=b4HData['b4r']
        b4t=b4HData['b4t']
        plotColor=concColors['b4H']
        axe.plot(b4t,b4r,'%s%s'%(plotColor,plotSymbol),label="10s before heating"+labelExtra)
        
        
        if setYLim:
            axe.set_ylim((100,1e9))
        else:
            pass
        axe.set_yscale('log')
    else:
        axe.set_ylabel("$calc. conc.\/[ppm]$")
        if yLim:
            axe.set_ylim(yLim)
        else:
            axe.set_ylim((0,200))
#        axe.set_yscale('log')    

    axe.set_xlabel(xLabel)
    


    


    if title:
        if len(sensorData[sensorName]['pos'].value_counts())>1:
            axe.set_title("%s%s"%(sensorName,Meta.getSensorMetaDataLabel(sensorName,sensorMetaData)))
        else:
            pos=sensorData[sensorName]['pos'].iloc[0]
            axe.set_title("%s@Ch%i-Pos%i%s"%(sensorName,pos//6,pos%6, Meta.getSensorMetaDataLabel(sensorName,sensorMetaData)))
    
    axe.callbacks.connect('xlim_changed', on_xlim_changed)    

    if linkYAxes:
        axe.callbacks.connect('ylim_changed', on_ylim_changed)
    




def createXLabel(startTime,unit):    
    if startTime:
        if unit=='h':
            scale=3600.0
        elif unit=='s':
            scale=1.0
        elif unit=='d':
            scale=3600.0*24.0
        elif unit=='m':
            scale=60.0
    else:
        unit='TimeStamp'
        scale=1
        
    xLabel='$Time\/[%s]$'%unit
        
    return xLabel,scale
    
def plotAllMin(sensorFullData,allData=False,plotValues="r_min",startTime=None,unit='h',plotRef=False,plotHumid=False,dF=None,accTime=True,plotSymbol="o",refFreq=100,label=True,loc=0,yLim=None,setYLim=True,shrinkData=100,linkYAxes=True):
    fig,axes=subplots(4,4)
    sensorNames=[n for n in sensorFullData.keys() if n!="REF" and n!="Reference_Resistance"]

    plotByPos=True
    for sensorName in sensorNames:
        count=len(sensorFullData[sensorName]['pos'].value_counts())
        if count>1:
            plotByPos=False
            print "printByIndex"
            break
        

    for i,sensorName in enumerate(sensorNames):

        if plotByPos:
            pos=sensorFullData[sensorName]['pos'].iloc[0]
        else:
            pos=i
        axe=axes[pos//4][pos%4]

        plotMinPulses(sensorFullData,sensorName,axe,allData=allData,dF=dF,plotValues=plotValues,startTime=startTime,unit=unit,accTime=accTime,plotSymbol=plotSymbol,label="Sensor",title=True,yLim=yLim,setYLim=setYLim,shrinkData=shrinkData,linkYAxes=linkYAxes)


        if plotRef:
            plotMinPulses(sensorFullData,'Reference_Resistance',axe,allData=allData,dF=dF,plotValues=plotValues,startTime=startTime,unit=unit,accTime=accTime,plotSymbol='d',label='REF',yLim=yLim,setYLim=setYLim,shrinkData=shrinkData,linkYAxes=linkYAxes)
           
        if plotHumid:
            axe2=axe.twinx()
            humidData=sensorFullData['REF']['rh'][::refFreq].dropna()
            axe2.plot(humidData.index,humidData,'b',label='Humidity')
            axe2.callbacks.connect('xlim_changed', on_xlim_changed)
            axe2.y_rescale_on_changed=False

        if label:
            if i==0:
                if plotHumid:
                    addUndublicatedLegend([axe,axe2],legendSize=None,loc=loc)
                else:
                    addUndublicatedLegend([axe],legendSize=None,loc=loc)

    if startTime or accTime:
        pass
    else:
        formatFigForDates(fig)

   
#    iMin=dF.index.min()
#    iMax=dF.index.max()
#    iLen=datetime.timedelta(seconds=(iMax-iMin).total_seconds()*1.1)
#    iMax=iMin+iLen
#    
#    for ax in fig.axes:
#        ax.set_xlim(iMin,iMax)
        
    fig.tight_layout()
    return fig


def plotXvsYAll(xAxis='r_pre',yAxis='r_min'):
    
    rh_ranges=[(10,50),(50,80)]

    concColorMap={50:'g',
                  150:'r'}
    
    rhSymbolMap={0:'d',
                 1:'o'}
                 
    rh_label={0:'dry',
              1:'humid'}    
    
    
    
    fig,axes=subplots(4,4,figsize=(30,20))
    sensorNames=[n for n in sensorFullData.keys() if n!="REF" and n!="Reference_Resistance"]
    
    plotByPos=True
    for sensorName in sensorNames:
        count=len(sensorFullData[sensorName]['pos'].value_counts())
        if count>1:
            plotByPos=False
            print "printByIndex"
            break
        
    
    for sensorIndex,name in enumerate(sensorNames):
        
        plotByPos=True
        if plotByPos:
            pos=sensorFullData[name]['pos'].iloc[0]
        else:
            pos=sensorIndex
        axe=axes[pos//4][pos%4]
        
        plotXvsY(name,axe,xAxis='r_pre',yAxis='r_min')

        if pos==0:
                addUndublicatedLegend([axe],legendSize=None,loc=0)
        
        fig.tight_layout()


def plotXvsY(name,axe,xAxis='r_pre',yAxis='r_min'):
    

    data=sensorFullData[name].dropna()
    xAxis='r_pre'
    yAxis='r_min'
    for c in data['conc'].value_counts().index:
        concData=data[data['conc']==c]
    
        col=concColorMap[c]
        
        
        for i,rh_range in enumerate(rh_ranges):
            concRhData=concData[(concData['backgroundHumidity']<rh_range[1]) & (concData['backgroundHumidity']>rh_range[0])]
            
            
            symbol=rhSymbolMap[i]        
            
            label="%i@%s"%(c,rh_label[i])
            axe.plot(concRhData[xAxis],concRhData[yAxis],'o',color=col,marker=symbol,label=label)
    
            axe.set_xlabel('res. heated and before exposure [$\Omega$]')
            axe.set_ylabel('min. res. under exposure [$\Omega$]')
    
            axe.set_xscale('log')
            axe.set_yscale('log')
            
            axe.set_title(name)

def formatFigForDates(fig):
    for ax in fig.axes:
        xax = ax.get_xaxis()
        adf = xax.get_major_formatter()
                      
        adf.scaled[1./24/60] = '%H:%M:%S'  # set the < 1d scale to H:M        
        adf.scaled[1./24] = '%H:%M'  # set the < 1d scale to H:M
        adf.scaled[1.0] = '%d.%m' # set the > 1d < 1m scale to Y-m-d
        adf.scaled[30.] = '%m' # set the > 1m < 1Y scale to Y-m
        adf.scaled[365.] = '%Y' # set the > 1y scale to Y
    
    fig.autofmt_xdate(rotation=30)
    
def plotNicolae(dF,sensorPos):
    
    sensorData=dF.sensorData
    fig,axes=subplots(len(sensorPos),1,figsize=(20,30))
    #dF=dF[0:10000]
    
    
    for i,pos in enumerate(sensorPos):
        log=True
        yRescale=True
        yLim=(1000,1e8)
        axe=axes[i]
        axe.set_ylabel("$Resistance\/[\Omega]$")
        if type(pos)==int:
            name=sensorData[pos]
        else:
            if pos=="REF":
                name='Reference_Resistance'
            elif pos=="TEMP":
                name='Reference_Temperature' 
                log=False
                yRescale=False
                yLim=(15,30)
                axe.set_ylabel("$Temperature\/[^\circ C]$")
            elif pos=="HUM":
                name='Reference_relHumidity'
                log=False
                yRescale=False
                axe.set_ylabel("$Humidity\/[\% r.h.]$")
                yLim=(10,90)
            pos=13
        
        
        if yLim:
            axe.set_ylim(yLim)
        if log:
            axe.set_yscale("log")
        data=dF[name].dropna()
        axe.plot(data.index,data,'ro-')
        axe.y_rescale_on_changed=yRescale        
        if yRescale:
            axe.callbacks.connect('ylim_changed', on_ylim_changed)
        axe.callbacks.connect('xlim_changed', on_xlim_changed)
        
        axe.set_title("%s @ Pos.:%i"%(name,pos))
        
#    
    formatFigForDates(fig)
    fig.tight_layout()
    return fig


def plotRef(sensorFullData,timeScale='d',startTime=None,refFreq=100):
    refDF=sensorFullData['REF'][::refFreq]
    if startTime:
        if timeScale=="d":
            rescale=3600.0*24.0
            unit="days"
        elif timeScale=="h":
            rescale=3600.0
            unit="h"
        elif timeScale=="m":
            rescale=60.0
            unit="min"
        elif timeScale=="s":
            rescale=1.0
            unit="sec"

    
    fig,axes=subplots(2,1)
    
    #axe.set_xscale((0,15))
    
    axe=axes[0]
    
    axe.set_yscale('LOG')
    axe.set_ylabel('$Resistance\/[\Omega$]')
    if startTime:
        xLabel='$Duration\/[%s]$'%unit
        
    else:
        xLabel='$Time$'
        
    axe.set_xlabel(xLabel)
    if startTime:    
        t=[((ts-dFT.index[0]).total_seconds()/rescale) for ts in refDF.index]
    else:
        t=refDF.index
        
    axe.plot(t,refDF['res'],'k',label="Resistance")
    
        
    addUndublicatedLegend([axe],legendSize=None,loc=4)
    
    axe=axes[1]
    axe.set_xlabel(xLabel)
    axe.set_ylim((10,90))
    

    axe.set_ylabel('$r.h.\/[\%]$')
    axe.plot(t,refDF['rh'],'b',label="Humidity")
    

    

    if (refDF['temp']>0).any():

        axe2=axe.twinx()    
        axe2.plot(t,refDF['temp'],'r',label="Temperature")
        axe2.set_ylabel('$Temp.\/[^\circ C]$')
        
    try:
        if axe2:
            addUndublicatedLegend([axe,axe2],legendSize=None,loc=4)
    except:
        addUndublicatedLegend([axe],legendSize=None,loc=4)
    
    fig.tight_layout()
    
    for ax in fig.axes:
        ax.callbacks.connect('xlim_changed', on_xlim_changed)
    formatFigForDates(fig)
    return fig
 
def timeStampToDuration(timeStamps,startTime,scale):
    if startTime:
        duration=[((tS-startTime).total_seconds())/float(scale) for tS in timeStamps]
        return duration
    else:
        return timeStamps  



def plot4MyHolydays(dF,sensorFullData):    
        
        

        
 
        for i in range(30):close()
        
        
    
        fig=plotAllMin(sensorData,allData=False,startTime=None,unit='h',plotRef=True,plotHumid=True,dF=None,accTime=False,plotSymbol="o",shrinkData=10)
        fig.savefig(os.path.join(folderNames[0],'overview.png'))
        

        fig=plotAllMin(sensorFullData,allData=True,startTime=None,unit='h',plotRef=False,plotHumid=True,dF=dF,accTime=False,plotSymbol="o",setYLim=True,shrinkData=1)
        fig.savefig(os.path.join(folderNames[0],'overview_no_ref.png'))
        
        fig=plotAllMin(sensorFullData,allData=False,startTime=None,unit='h',plotRef=False,plotHumid=True,dF=dF,accTime=False,plotSymbol="o",setYLim=False,shrinkData=1,linkYAxes=False)
        fig.savefig(os.path.join(folderNames[0],'overview_no_ref_auto_scale.png'))
      
        fig=plotRef(sensorFullData,timeScale='h')
        fig.savefig(os.path.join(folderNames[0],'ref.png'))
   
        fig,axe=subplots()
        plotMinPulses(sensorFullData,'AA026_37',axe,allData=True,dF=dF,shrinkData=1,unit='h',plotValues="r_min",startTime=None,plotRef=False,accTime=False,plotSymbol="d")
        formatFigForDates(fig)
        fig.tight_layout()
        fig.savefig(os.path.join(folderNames[0],'AA026_37.png'))
#        
        sensorName='AS-MLC-14'        
        sensorName='AA028_14'
        fig,axe=subplots()       
        plotMinPulses(sensorFullData,sensorName,axe,allData=True,dF=dF,shrinkData=1,unit='h',plotValues="r_min",startTime=None,plotRef=False,accTime=False,plotSymbol="d")
        formatFigForDates(fig)
        fig.tight_layout()
        fig.savefig(os.path.join(folderNames[0],'%s.png'%sensorName))



if __name__=="__ma8in__":
    topFolder=r'/mnt/groups/Steinbeis-Auftragsabwicklung/STZ_Mitarbeiter/20016/Messungen/GMS-Stabilization/Setup@Ate/Measurements/2014_04_16_restarted_with_autorange/'
    #folderNames=getFiles(folder=topFolder)
    folderNames=getFiles(topFolder=topFolder)
    
    matplotlib.rcParams['savefig.directory']=topFolder
    rcParams['figure.figsize'] = 30, 20
    #rcParams['lines.markersize']=12      
    
    
    #dF,sensorFullData=parseExperiment(*folderNames)
    
    plot4MyHolydays(dF,sensorFullData)
    rh_ranges=[(10,50),(50,80)]
    concColorMap={50:'g',
                  150:'r'}
    
    rhSymbolMap={0:'d',
                 1:'o'}
                 
    rh_label={0:'dry',
              1:'humid'}   

    plotXvsYAll()    