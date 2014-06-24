# -*- coding: utf-8 -*-
"""
Created on Tue Jan 07 12:54:34 2014

@author: peters
"""

import time
import datetime
startT=datetime.datetime.now()

import fitData
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

import parseExperimentalData as EDF
import plotDataSets as EDFPLOT
import mergeAllFolder as Merge

timeFormat="%d.%m.%Y %H:%M:%S"


import numpy as np  # NumPy (multidimensional arrays, linear algebra, ...)
import scipy as sp  # SciPy (signal and image processing library)
from scipy import optimize


import matplotlib as mpl         # Matplotlib (2D/3D plotting library)
import matplotlib.pyplot as plt  # Matplotlib's pyplot: MATLAB-like syntax
from pylab import *              # Matplotlib's pylab interface
ion()                            # Turned on Matplotlib's interactive mode

#import guidata  # GUI generation for easy dataset editing and display

#import guiqwt                 # Efficient 2D data-plotting features
#import guiqwt.pyplot as plt_  # guiqwt's pyplot: MATLAB-like syntax
#plt_.ion()                    # Turned on guiqwt's interactive mode

import multiprocessing
from multiprocessing import Process, freeze_support


for i in range(30):close()

if __name__=='__main__':
    #init variable to load the big datasets not on each run.
    #set init ro (re)load data
    #This is only helpful if working with  I(nteracive)Python

    init=True
    if init:
        sensorData,expData,topFolder=Merge.loadData()
        Merge.plotAllRef(sensorData,topFolder)
    matplotlib.rcParams['savefig.directory']=topFolder

def plotResVsConc(axe,sensorData,sensorName='AA019_10',yType='res',legend=True,excludeTimeSpans=None):

    data=sensorData[sensorName]
    resData=data['r_min']
    concData=data['conc']
    
    concs=concData.value_counts().keys()
    for conc in concs:
        c=concData[concData==conc]
        r=resData[concData==conc]
        r_stdv=r.std()
        r_mean=r.mean()
        
        axe.plot(c,r,'o',label="%0.f ppm"%conc)
        axe.errorbar(conc,r_mean,yerr=r_stdv,capsize=10,elinewidth=5)
        axe.plot(conc,r_mean,'ko',markersize=10)
        axe.set_title('%s'%sensorName)
        axe
        axe.set_yscale('log')
        axe.set_xlim((40,160))

        if yType=='res':
            axe.set_ylabel('$Resistance\/[\Omega]$')
            axe.set_ylim((1e3,1e8))
        elif yType=='calcConc':
            axe.set_ylabel('$calc. conc\/[ppm]$')
        axe.set_xlabel('$set\/concetration\/[ppm]$')
        
        if legend:
            EDFPLOT.addUndublicatedLegend([axe],legendSize=None,loc=None)

def plotSensors(sensorData):
    close()
    fig,axes=subplots(5,5,figsize=(30,30),dpi=60)
    for i,s in enumerate(sensorData.keys()[:25]):
        print s
        if s=='REF':
            continue 
        axe=fig.axes[i]
        plotResVsConc(axe,sensorData,sensorName=s,legend=False)
    fig.tight_layout()
    
    
    badStart=datetime.datetime.strptime("26.01.2014","%d.%m.%Y")
    badEnd=datetime.datetime.strptime("28.01.2014","%d.%m.%Y")
    data=sensorData['AA019_10']
    dataGood=data[data.index.indexer_between_time(badStart, badEnd,include_start=False, include_end=False)]

for i in range(30):close()
zero=False

fitFuncs=fitData.getDefaultFitFunctions(withp1=False)
sensorData,expData=fitData.setCalcConcs(sensorData,expData,*fitFuncs,startPoint=2,nrOfPoints=5,zero=zero)



fig,axes=subplots(5,5,figsize=(30,30),dpi=100)
yMax,yMin=None,None
sensorNames=[k for k in sensorData.keys() if k != 'REF' and k!='AA021_01']
for i,sensorName in  enumerate(sensorNames[:len(fig.axes)]):
    axe=fig.axes[i]
    
    
    axe.set_title("%s%s"%(sensorName,Meta.getSensorMetaDataLabel(sensorName,sensorMetaData)))
    axe.set_yscale('log')
    
    sensorData[sensorName]
    
    xData,yData,p,calFunc,anaFunc,sucess=fitData.fitSensor(sensorData,*fitFuncs,sensorName=sensorName,startPoint=2,nrOfPoints=5,zero=zero)
    
    
    if yMax and yMin:
        yMax=max((list(yData)+[yMax,yMin]))
        yMin=min((list(yData)+[yMax,yMin]))
    else:
        yMax=yData.max()
        yMin=yData.min()
   
    
    fitData.plotFitAndPoints(xData,yData,calFunc,axe,p)
    

for axe in fig.axes:
    axe.set_ylim(yMin*0.1,yMax*10)
fig.tight_layout()
fig.savefig(os.path.join(topFolder,'fitData.png'))


   

Merge.plotAllExperiments(expData,topFolder,plotValues='calcConc',plotRef=True,yLim=(0,300))

#for sensorName in  sensorNames:
#    fig,axe=subplots()
#    EDFPLOT.plotMinPulses(sensorData,sensorName,axe,allData=False,dF=None,unit='h',plotValues="calcConc",startTime=None,plotRef=False,accTime=False,plotSymbol="d")
#    humid=sensorData['REF']['rh'][::100]
#    axe2=axe.twinx()
#    axe2.plot(humid.index,humid,'b',label="background humidity")
#    axe.set_xlim((sensorData[sensorName].index[0],sensorData[sensorName].index[-1]))
#    EDFPLOT.formatFigForDates(fig)
#    fig.savefig(os.path.join(topFolder,'%s_calcConc.png'%sensorName))

