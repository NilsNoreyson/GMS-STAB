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
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append(r'C:\Users\peters\Desktop\winpython\projects\sensorData')

from calib_fit_testing import *

import parseExperimentalData as EDF

import plotDataSets as EDFPLOT
from plotDataSets import *

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

from remove_over_value import *


def loadAllSensorDataFromFolders(folders):
    sensorData=[]
    for i,folder in enumerate(folders):
        sensorFullData=EDF.loadSensorData(folder)
        sensorData.append(sensorFullData)
        print folder
    return sensorData





def combineAllDataAndSave(sensorData,topFolder):
    allSensorData={}
    for experiment in sensorData:
        for k,v in experiment.iteritems():
            if allSensorData.has_key(k):
                allSensorData[k]=pd.concat([allSensorData[k],v],join='outer')
            else:
                allSensorData[k]=v
    
    f=open(os.path.join(topFolder,'allSensorPickle.pkl'),'wb')
    pickle.dump(allSensorData,f)
    f.close()
    
    f=open(os.path.join(topFolder,'allExpsPickle.pkl'),'wb')
    pickle.dump(sensorData,f)
    f.close()
    return allSensorData
    
def loadAllDataFromPickle(topFolder):
    f=open(os.path.join(topFolder,'allSensorPickle.pkl'),'rb')
    sensorData=pickle.load(f)
    f.close()

    f=open(os.path.join(topFolder,'allExpsPickle.pkl'),'rb')
    expData=pickle.load(f)
    f.close()

    return sensorData,expData

def getFolders():   
    if os.name=="nt":
        topFolder=r'B:\python\GMS-PANDAS\measurements'
        #topFolder=r'J:\Steinbeis-Auftragsabwicklung\STZ_Mitarbeiter\20016\Messungen\GMS-Stabilization\measurements'
    elif os.name=="posix":
        topFolder='/mnt/groups/Steinbeis-Auftragsabwicklung/STZ_Mitarbeiter/20016/Messungen/GMS-Stabilization/Setup@Ate/Measurements'
    
    
    folders=[ '2014_04_16_2014_05_21',
              '2014_05_21',
              '2014_06_18'
            ]
    
    folders=[os.path.join(topFolder,folder) for folder in folders]
    return topFolder, folders


def mergeAndPickle(topFolder,folders):
    expData= loadAllSensorDataFromFolders(folders)
    allData=combineAllDataAndSave(expData,topFolder)
    return True
    


def loadData():    
    topFolder,folders=getFolders()
    
     
    print '...loading'
    sensorData,expData=loadAllDataFromPickle(topFolder)

    return sensorData,expData,topFolder
    
def plotAllExperiments(expData,topFolder,plotValues='r_min',accTime=False,plotHumid=True,plotRef=False,yLim=None):
    for i,e in enumerate(expData):
        fig=EDFPLOT.plotAllMin(e,allData=False,plotValues=plotValues,startTime=None,unit='h',plotRef=plotRef,plotHumid=plotHumid,dF=None,accTime=accTime,plotSymbol="o",yLim=yLim)

        t_start=e['REF'].index[0]
        t_stop=e['REF'].index[-1]
        dateString="%s--%s"%(t_start.strftime("%Y-%m-%d"),t_stop.strftime("%Y-%m-%d"))

        fig.savefig(os.path.join(topFolder,"%s_dry_%s.png"%(dateString,plotValues)))
    
        fig=EDFPLOT.plotRef(e,timeScale='d',startTime=None)


        fig.savefig(os.path.join(topFolder,"%s_REF.png"%dateString))
        fig.tight_layout()
        
    
def plotAllRef(sensorData,topFolder):
    fig=EDFPLOT.plotRef(sensorData,timeScale='d',startTime=None)
    fig.savefig(os.path.join(topFolder,"totalREf.png"))
    
def plotOneSensor(sensorData,sensorName,topFolder):
    fig,axe=subplots()
    EDFPLOT.plotMinPulses(sensorData,sensorName,axe,allData=False,dF=None,unit='h',startTime=None,plotRef=False,accTime=False,plotSymbol="d")
    EDFPLOT.formatFigForDates(fig)
    fig.tight_layout()
    fig.savefig(os.path.join(topFolder,"%s.png"%sensorName))




if __name__=='__main__':
    folders=getFolders()
    mergeAndPickle(*folders)
    rcParams['figure.figsize'] = 30, 20
    sensorData,expData,topFolder=loadData()
    fitFuncs=fitData.getDefaultFitFunctions()
    sensorData,expData=fitData.setCalcConcs(sensorData,expData,*fitFuncs,startPoint=2,nrOfPoints=5)
    
    
    
    pngFolder=folders[0]
    
    fig=EDFPLOT.plotRef(sensorData,timeScale='h')
    fig.savefig(os.path.join(pngFolder,'ref.png'))
        
        
    fig=EDFPLOT.plotAllMin(sensorData,allData=False,startTime=None,unit='h',plotRef=False,plotHumid=True,dF=None,accTime=False,plotSymbol="o",shrinkData=10)
    name='overview_all'
    name=name+".png"
    fig.savefig(os.path.join(pngFolder,name))

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
##    plotAllRef(sensorData,topFolder)
##    plotOneSensor(sensorData,sensorName='AA026_37',topFolder=topFolder)
##    plotAllExperiments(expData,topFolder,plotValues='calcConc',plotRef=False)
##    plotAllExperiments(expData,topFolder,plotValues='calcConc',plotRef=True,yLim=(0,450))
##    plotAllExperiments(expData,topFolder,plotValues='r_min',plotRef=False)
##    plotAllExperiments(expData,topFolder,plotValues='r_min',plotRef=True)
