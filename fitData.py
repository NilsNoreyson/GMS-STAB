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
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append(r'C:\Users\peters\Desktop\winpython\projects\sensorData')



import parseExperimentalData as EDF

import plotDataSets as EDFPLOT

timeFormat="%d.%m.%Y %H:%M:%S"


import numpy as np  # NumPy (multidimensional arrays, linear algebra, ...)
import scipy as sp  # SciPy (signal and image processing library)
from scipy import optimize

import matplotlib as mpl         # Matplotlib (2D/3D plotting library)
import matplotlib.pyplot as plt  # Matplotlib's pyplot: MATLAB-like syntax
from pylab import *              # Matplotlib's pylab interface


def getDefaultFitFunctions(alometric=True):
    if alometric:
        fitFunc = lambda p, x:p[0]*(x**p[1])# Target function
        anaFunc=lambda R,p:((R/p[0])**(1/p[1]))
        p0=[1e6,0.5] # Initial guess for the parameters
    else:
        fitFunc = lambda p, x:p[0]*(1+p[2]*x)**p[3]# Target function
        anaFunc=lambda R,p:(((R/p[0])**(1/p[3]))-p[1])/p[2]
    
    errFunc = lambda p, x, y: (fitFunc(p, x) - y)/y # Distance to the target function


    
    
    return fitFunc,errFunc,anaFunc,p0

def fitSensor(sensorData,fitFunc,errFunc,anaFunc,p0,sensorName='AA019_10',startPoint=5,nrOfPoints=5,zero=False):

    data=sensorData[sensorName]
    
    concData=np.array(data['conc'][data['r'].dropna().index[startPoint:startPoint+nrOfPoints]]).astype(np.float32)
    
    resData=np.array(data['r_min'][data['r'].dropna().index[startPoint:startPoint+nrOfPoints]]).astype(np.float32)

    if zero:
        zeroConc=np.zeros(len(concData))
        concData=np.append(concData,zeroConc)
        
        zeroRes=np.array(data['r_pre'][data['r'].dropna().index[startPoint:startPoint+nrOfPoints]]).astype(np.float32)
        resData=np.append(resData,zeroRes)        

    
    p, success = optimize.leastsq(errFunc, p0[:], args=(concData, resData))
    


    print p
    
    

    calFunc=lambda x:fitFunc(p,x)
    anaFunc_temp=lambda R:anaFunc(R,p)

    

    

    return concData,resData,p,calFunc,anaFunc_temp,success

def plotFitAndPoints(xData,yData,calFunc,axe,p):

    axe.plot(xData,yData,'ro',label='data')

    xFitData=np.linspace(xData.min()*0.8,xData.max()*1.3,100)

    yFitData=calFunc(xFitData)
    
    axe.plot(xFitData,yFitData,'r',label='fit')
    
    text="$%.2e*(%.2f +%.2f*x)^{%.2f}$"%(p[0],p[1],p[2],p[3])
    
    axe.text(0.5, 0.5,text, horizontalalignment='center',verticalalignment='center',transform=axe.transAxes)


def setCalcConcs(sensorData,expData,fitFunc,errFunc,anaFunc,p0,startPoint=2,nrOfPoints=5,zero=False):
    for sensorName in  sensorData.keys():
        if sensorName=='REF':
            continue    
    
        xData,yData,p,calFunc,anaFunc_temp,sucess=fitSensor(sensorData,fitFunc,errFunc,anaFunc,p0,sensorName=sensorName,startPoint=startPoint,nrOfPoints=nrOfPoints,zero=zero)
        sensorData[sensorName]['calcConc']=sensorData[sensorName]['r_min'].dropna().apply(anaFunc_temp)
        
    for i,e in enumerate(expData):
        for sensorName in  e.keys():
            if sensorName=='REF':
                continue

            xData,yData,p,calFunc,anaFunc_temp,sucess=fitSensor(expData[i],fitFunc,errFunc,anaFunc,p0,sensorName=sensorName,startPoint=startPoint,nrOfPoints=nrOfPoints)
            
            expData[i][sensorName]['calcConc']=expData[i][sensorName]['r_min'].dropna().apply(anaFunc_temp)
            
    return sensorData,expData

if __name__=="__main__":
    getDefaultFitFunctions()
    fitSensor(sensorData,fitFunc,errFunc,anaFunc,p0,sensorName='AA028_16',startPoint=5,nrOfPoints=5)
    setCalcConcs(sensorData,expData,fitFunc,errFunc,anaFunc,p0,startPoint=2,nrOfPoints=5)
    plotFitAndPoints(xData,yData,calFunc,axe,p)