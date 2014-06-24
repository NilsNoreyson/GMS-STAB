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

import sensorMetaData

timeFormat="%d.%m.%Y %H:%M:%S"


import numpy as np  # NumPy (multidimensional arrays, linear algebra, ...)
import scipy as sp  # SciPy (signal and image processing library)

import matplotlib as mpl         # Matplotlib (2D/3D plotting library)
import matplotlib.pyplot as plt  # Matplotlib's pyplot: MATLAB-like syntax
from pylab import *              # Matplotlib's pylab interface
ion()                            # Turned on Matplotlib's interactive mode

#import guidata  # GUI generation for easy dataset editing and display

#import guiqwt                 # Efficient 2D data-plotting features
#import guiqwt.pyplot as plt_  # guiqwt's pyplot: MATLAB-like syntax
#plt_.ion()                    # Turned on guiqwt's interactive mode

sensorSheetsFolder=sensorMetaData.sensorSheetsFolder
sensorNameMeta=sensorMetaData.getSumFileEntries(sensorSheetsFolder)
sensorNameMeta=r'J:\Steinbeis-Auftragsabwicklung\STZ_Mitarbeiter\20016\SensorsAtAOAction\Sensirion_to_AOAction'

def getMetaSensorData(name):
    metaData=sensorMetaData.getSensorData(name,sensorNameMeta)
    if metaData:
        if metaData['label']:
            return "\n"+metaData['label']
        else:
            return ""
    return ""


def addUndublicatedLegend(axes,legendSize=None):
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
        
    axes[0].legend(H, L,prop=prop)


def on_ylim_changed(ax):
    ylim=ax.get_ylim()
    print ylim
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
        

def plotRef(dF,timeScale='d',startTime=None):
    
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
        t=[((ts-dFT.index[0]).total_seconds()/rescale) for ts in dFT.index]
    else:
        t=dF.index
        
    axe.plot(t,dF['Reference_Resistance'],'k',label="Resistance")
    
        
    addUndublicatedLegend([axe],legendSize=None)
    
    axe=axes[1]
    axe.set_xlabel(xLabel)
    axe.set_ylim((10,90))
    
    
    if ('Reference_relHumidity' in dF.keys()):
        axe.set_ylabel('$r.h.\/[\%]$')
        axe.plot(t,dF['Reference_relHumidity'],'b',label="Humidity")
    else:
        axe.set_ylabel('$r.h.\/[set\/\%]$')
        #humidData=dF['MFC_1_conc_set'].dropna()
        axe.plot(t,dF['MFC_1_conc_set'],'b',label="Humidity")
        #axe.redraw_in_frame()

    Temp=False
    if ('Reference_Temperature' in dF.keys()):
        temp=True
        axe2=axe.twinx()    
        axe2.plot(t,dF['Reference_Temperature'],'r',label="Temperature")
        axe2.set_ylabel('$Temp.\/[^\circ C]$')
        

    
    if Temp:
        addUndublicatedLegend([axe,axe2],legendSize=None)
    else:
        addUndublicatedLegend([axe],legendSize=None)
    
    fig.tight_layout()
    
    for ax in fig.axes:
        ax.callbacks.connect('xlim_changed', on_xlim_changed)
    formatFigForDates(fig)
    return fig
    
def openEDF(fileName):
    headerSize=0
    header={}
    f=open(fileName,"r")
    
    for i in range(10):
        line=f.readline().strip()
        if len(line.split("\t"))>1:
            break
        else:
            line=line.split("=")
            header=dict(header.items()+{line[0]:line[1]}.items())
    f.close()

    return header,i

def loadFlowEDF(totalPath,cleanRHandT=True):
    
    header,startRow=openEDF(totalPath)
    dF=pd.read_csv(totalPath,header=[startRow,startRow+1],sep="\t",index_col=0)
    dF.header=header
    
    colNames=[k[1] for k in dF.keys()]
    dF.metaData={k[1]:k[0] for k in dF.keys()}
    
    if ('Reference' in colNames):
        idx=list(colNames).index('Reference')
        colNames[idx]='Reference_Resistance'
    
    dF.columns=colNames
    
    if cleanRHandT and ('Reference_Temperature' in dF.keys()):
        dF['Reference_Temperature'][dF['Reference_Temperature']<0]=None
        dF['Reference_Temperature'].ffill()
        dF['Reference_relHumidity'][dF['Reference_relHumidity']<1]=None
        dF['Reference_relHumidity'].ffill()

    #remove the col with no values (ie non used power supplies)
    #dF=dF.dropna(axis=1)
    
    return dF

def loadDataEDF(totalPath):

    header,startRow=openEDF(totalPath)
    dF=pd.read_csv(totalPath,header=[startRow,startRow+1],sep="\t",index_col=0)
    dF.header=header
    
    colNames=[k[1] for k in dF.keys()]
    dF.metaData={k[1]:k[0] for k in dF.keys()}
    
        
    dF.columns=colNames
    
    return dF


#Data+timeDiff


def combineDF(dF_Flow,dF_Data,dropNaN=False):
    #combine both dF
    
    
    #Shift the difference in start-timings back
    #not needed since timestamps are used now
    #fS=time.strptime(dF_Flow.header['Date'],timeFormat)
    #dS=time.strptime(dF_Data.header['Date'],timeFormat)
    #timeDiff=time.mktime(dS)-time.mktime(fS)
    #dF_Data.index=[t+timeDiff for t in dF_Data.index]
    
    dF=dF_Flow.join(dF_Data,how='outer')
    


    
    dF_Data_combined=dF
    
    #Since the freq. of the Flow-Prot. is higer fill up the values for the Sensor-Data
    for k in dF_Flow.keys():
        dF_Data_combined[k]=dF_Data_combined[k].ffill()
    
    if dropNaN:
        #The timestamps of the SensorsData should now be filled with data. Drop the lines with not full Datasets
        dF_small=dF_Data_combined.dropna()
        

    
    return dF_Data_combined
    

    

    


def findHeatingPulse(dataFrame,voltChannel=0,startI=None,lookFW_days=2,threshold=0.01):
    chName='Voltage_Channel_%i_actual'%voltChannel
    if startI:    
        startTime=dF.index[startI]
    else:
        startTime=dataFrame.index[0]
    heatingPulses=[]
    start=[]
    stop=[]
    duration=[]
    multiFactor=6
    print voltChannel
    while True:
        #startIndex=dataFrame[chName][startIndex:startIndex+(3600*multiFactor)][dataFrame[chName]>0].index[0]
        data=dataFrame[chName][startTime:startTime+datetime.timedelta(days=lookFW_days)].dropna()
        
        startData=data[data>threshold]
        
        if len(startData)==0:
            break
        else:
            startTime=startData.index[0]
        

        
        stopData=data[startTime+datetime.timedelta(seconds=2):startTime+datetime.timedelta(days=lookFW_days)]
        stopData=stopData[stopData<threshold]
        
        if len(stopData)==0:
            break
        else:
            stopTime=stopData.index[0]
            
        heatingDuration=(stopTime-startTime).total_seconds()
    

        try:
            if startTime<pulses[-1][0]:
                break
        except:
            pass

        start.append(startTime)
        stop.append(stopTime)
        duration.append(heatingDuration)
        
        heatingPulses.append({'pulse':(startTime,stopTime),'duration':heatingDuration})

        startTime=stopTime
    
    dF_heatingPulses=pd.DataFrame(data={'stop':stop,'duration':duration,'start':start},index=start)
    return dF_heatingPulses
    


def printKeys(dF):
    for i,k in enumerate(dF.keys()):
        print i,k

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

def getMinUnderExposures(dataFrame,minValue=False):
    
   
    minPoints={}


    pulseDatabyName={}
    
    for sensor in dataFrame.sensorData:
        minPoints[sensor]={50:{"t":[],"r":[],"t_min":[],"r_min":[]},
                            150:{"t":[],"r":[],"t_min":[],"r_min":[]},
                            "pre":{"t":[],"r":[]},
                            "heatingPeriode":[]
                            }
    
    for sensor in dataFrame.sensorData:
        sensorNr=dataFrame.sensorData.get_loc(sensor)
                
        pulseData=dataFrame.pulsesByPos[sensorNr]


        

        heaterNumber=dF.heaterOfPosition[sensorNr]

        pulseData['conc']=None
        pulseData['t_pre']=None
        pulseData['r_pre']=None
        pulseData['r_min']=None
        pulseData['t_min']=None
        pulseData['r']=None
        pulseData['t']=None 
        pulseData['ref_pre']=None
        pulseData['ref_min']=None
        pulseData['ref']=None

#        print pulseData
        
        for i,pulse in pulseData.iterrows():
            p=(pulse['start'],pulse['stop'])
            print i
#            print pulse
#            print dataFrame['MFC_2_conc_set'][p[0]:p[1]]
            conc=dataFrame['MFC_2_conc_set'][p[0]:p[1]].max()
            if conc>0:
                
                underEthanol=dF[p[0]:p[1]][dF['MFC_2_conc_set']>0]                
                
                
                preData=dataFrame[sensor][p[0]+datetime.timedelta(seconds=2):underEthanol.index[0]+datetime.timedelta(seconds=5)]
                preMax=preData.max()
                preMaxT=preData.idxmax()
                
                sensorUnderEthanol=underEthanol[sensor]
                
                resMin=sensorUnderEthanol.min()
                tMin=sensorUnderEthanol.idxmin()
            
                res=(sensorUnderEthanol.dropna()).iloc[-1]
                t=(sensorUnderEthanol.dropna()).index[-1]
                
                #point before turning of the ethnaol gas flow
                minPoints[sensor][conc]['r'].append(res)
                minPoints[sensor][conc]['t'].append(t)
                
                #minimal resistance under the ethnao exposure
                minPoints[sensor][conc]['r_min'].append(resMin)
                minPoints[sensor][conc]['t_min'].append(tMin)
                
                minPoints[sensor]["pre"]['r'].append(preMax)
                minPoints[sensor]["pre"]['t'].append(preMaxT)
                
                minPoints[sensor]["heatingPeriode"].append((p[0],p[1]))
                
                ref_min=dataFrame['Reference_Resistance'][tMin]
                ref_pre=dataFrame['Reference_Resistance'][preMaxT]
                ref=dataFrame['Reference_Resistance'][t]
                
                pulseData['conc'][i]=conc
                pulseData['t_pre'][i]=preMaxT
                pulseData['r_pre'][i]=preMax
                pulseData['t_min'][i]=tMin
                pulseData['r_min'][i]=resMin
                pulseData['t'][i]=t       
                pulseData['r'][i]=res
                pulseData['ref_pre']=ref_pre
                pulseData['ref_min']=ref_min
                pulseData['ref']=ref


        pulseDatabyName[sensor]=pulseData

                
                 
                
    
    return minPoints,pulseDatabyName

def getPulses(dataFrame,lookFW_days=2,threshold=0.01):
    pulsesByPos={}
    pulsesByHeater={}
    
    for h in dF.heaterOfPosition:
        if pulsesByHeater.has_key(dF.heaterOfPosition[h]):
            p=pulsesByHeater[dF.heaterOfPosition[h]]
        else:
            p=findHeatingPulse(dataFrame,voltChannel=dF.heaterOfPosition[h],lookFW_days=lookFW_days,threshold=threshold)
            pulsesByHeater[dF.heaterOfPosition[h]]=p

        pulsesByPos[h]=p

    return pulsesByPos,pulsesByHeater
    

def plotMinPulses(dF,sensorName,axe,allData=False,unit='h',minValues=False,startTime=None):
    
    minExposure=dF.minExposure    
    #dF=dF[0:50000]
    
    if allData and dF:
        for p in minExposure[sensorName]["heatingPeriode"]:
            res=dF[sensorName][p[0]:p[1]].dropna()
            t=res.index
            axe.plot(t,res,"yd-")
    
    xLabel,scale=createXLabel(startTime,unit)
    
    if minValues:
        tIndex='t_min'
        rIndex='r_min'
    else:
        tIndex='t'
        rIndex='r'

    conc=150
    t=np.array(minExposure[sensorName][conc][tIndex])
    t=timeStampToDuration(t,startTime,scale)
    
    r=np.array(minExposure[sensorName][conc][rIndex])
    axe.plot(t,r,'ro-')
    
    conc=50
    t=np.array(minExposure[sensorName][conc][tIndex])
    t=timeStampToDuration(t,startTime,scale)

    r=np.array(minExposure[sensorName][conc][rIndex])
    axe.plot(t,r,'bo-')
    
    conc="pre"
    t=np.array(minExposure[sensorName][conc]['t'])
    t=timeStampToDuration(t,startTime,scale)
    
    r=np.array(minExposure[sensorName][conc]['r'])
    axe.plot(t,r,'ko-')
    

    
    
    axe.set_xlabel(xLabel)
    axe.set_ylabel("$Resistance\/[\Omega]$")
    
    axe.set_ylim((100,1e8))
    axe.set_yscale('log')
 

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
   
def timeStampToDuration(timeStamps,startTime,scale):
    if startTime:
        duration=[((tS-startTime).total_seconds())/float(scale) for tS in timeStamps]
        return duration
    else:
        return timeStamps


def saveDecoration(supFolder,dF):
    saveDict={}
    saveDict["pulsesByPos"]=dF.pulsesByPos
    saveDict['minExposure']=dF.minExposure
    saveDict['sensorData']=dF.sensorData
    saveDict['metaData']=dF.metaData
    saveDict['heaterOfPosition']=dF.heaterOfPosition
    saveDict["pulsesByHeater"]=dF.pulsesByHeater
    with open(os.path.join(supFolder,"deco.pkl"), 'wb') as handle:
        pickle.dump(saveDict, handle)

def loadDecoration(supFolder,dF):
    with open(os.path.join(supFolder,"deco.pkl"), 'rb') as handle:
        deco = pickle.load(handle)

    for k in deco:
        setattr(dF,k,deco[k])
    return dF
     
def plotAllMin(dF,allData=False,minValues=False,startTime=None,unit='h',plotRef=False):
    fig,axes=subplots(3,4,figsize=(20,30))
        
    for i,sensorName in enumerate(dF.sensorData):
        axe=axes[i%3][i//3]
        print i%3,i//3
        plotMinPulses(dF,sensorName,axe,allData=allData,minValues=minValues,startTime=startTime,unit=unit)
        axe.set_title("%s@Ch%i-Pos%i%s"%(sensorName,i//6,i%6, getMetaSensorData(sensorName)))
        if plotRef:
            refData=dF['Reference_Resistance'].dropna()
            axe.plot(refData.index,refData)            
    for ax in fig.axes:
            ax.callbacks.connect('xlim_changed', on_xlim_changed)
            ax.callbacks.connect('ylim_changed', on_ylim_changed)
    if startTime:
        pass
    else:
        formatFigForDates(fig)
    fig.tight_layout()
    return fig




def getFiles(topFolder):
    #initialize TK framework (GUI - for file dialog) to get a save filename
    root=Tkinter.Tk()
    #root.withdraw()
    #definition
    supFolder=None
    #folder=r'C:\TEMP\2013_07_17_exchange1and2'
    initFolder=topFolder
    if not(supFolder):
        supFolder = tkFileDialog.askdirectory(parent=root,title='Which experiment should be evaluated',initialdir=initFolder,mustexist=True)
    root.destroy()
    
    flowFileName=""
    for f in os.listdir(supFolder):
        if "_flow_EDF.txt" in f:
            flowFileName=f
            break
    
    
    resFileName=""
    for f in os.listdir(supFolder):
        if "_res.txt" in f:
            resFileName=f
            break
    
    xlsFileName=""
    for f in os.listdir(supFolder):
        if ".xls" in f:
            xlsFileName=f
            break    
    
    flowTotalPath=os.path.join(supFolder,flowFileName)
    resTotalPath=os.path.join(supFolder,resFileName)
    xlsTotalPath=os.path.join(supFolder,xlsFileName)
    return supFolder,flowTotalPath,resTotalPath,xlsTotalPath


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



def getHeaterOfPosition(xlsFileName):
    workbook = xlrd.open_workbook(xlsFileName)
    worksheet = workbook.sheet_by_name('PowerSettings')
    heaterOfPosition={}
    for i in range(1,200):
        try:
            cell_value_pos = int(worksheet.cell_value(i, 0))
            cell_value_heater = worksheet.cell_value(i, 1)
        except:
            break
        heaterOfPosition[cell_value_pos]=cell_value_heater
    return heaterOfPosition
    

def reindex(EDF):
    fS=time.strptime(EDF.header['Date'],timeFormat)
    fSn=time.mktime(fS)*1e9
    EDF.index=pd.to_datetime((EDF.index*1e9)+fSn)
    return EDF


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

def printACCHeatingTime(dF):
    for i,name in enumerate(dF.sensorData):
        totalHeatingTime=dF.pulsesByPos[i]['duration'].sum()
        print "%s -- %.2fh heatingTime"%(name,totalHeatingTime/3600.0)


def loadDf(supfolder)
    dF=pd.read_pickle(os.path.join(supFolder,"dF.pkl"))
    dF=loadDecoration(supFolder,dF)
    return dF
    
topFolder=r'J:\Steinbeis-Auftragsabwicklung\STZ_Mitarbeiter\20016\Messungen\GMS-Stabilization\measurements'



initData=True
loadDF=False
doPlot=False


if initData:
    supFolder,flowTotalPath,resTotalPath,xlsTotalPath=getFiles(topFolder)
 
   #load the Flow--Data
    dF_Flow=loadFlowEDF(flowTotalPath)
    #load the Sensor-Data
    dF_Data=loadDataEDF(resTotalPath)
    
    #set the date as index instead of duration
    dF_Flow=reindex(dF_Flow)
    dF_Data=reindex(dF_Data)

    dF=combineDF(dF_Flow,dF_Data,dropNaN=False)
    
    
    #get the data from the excel file for the heater vs measuring position relation
    dF.heaterOfPosition=getHeaterOfPosition(xlsTotalPath)
    
    #get the pulses, where the heater is activated
    dF.pulsesByPos,dF.pulsesByHeater=getPulses(dF,lookFW_days=2,threshold=0.01)
    dF.sensorData=dF_Data.keys()
    dF.minExposure,sensorData=getMinUnderExposures(dF)

    sensorDataFile=open(os.path.join(supFolder,'sensorData.pkl'),'wb')
    pickle.dump(sensorData,sensorDataFile)
    sensorDataFile.close()
    
    
    dF.metaData=dict(dF_Flow.metaData.items() + dF_Data.metaData.items())
    
    
    


    dF.to_pickle(os.path.join(supFolder,"dF.pkl"))
    saveDecoration(supFolder,dF)    

    

    fig=plotRef(dF_Flow,timeScale='s')


else:
    if loadDF:
        try:
            print "All files loaded",loaded
        except:

            

            loaded=True

printACCHeatingTime(dF)


if doPlot:
   
    fig=plotRef(dF,timeScale='h')
    fig.savefig(os.path.join(supFolder,"REF.png"))
    #
#    for s in dF.sensorData[0:3]:
#        plotAllHeatingPulses(dataFrame=dF,sensorName=s)
#    #
    fig=plotAllMin(dF,allData=False,startTime=dF.index[0])
    fig.savefig(os.path.join(supFolder,"exposure_time.png"))
    
    fig=plotAllMin(dF,allData=False)
    fig.savefig(os.path.join(supFolder,"exposure_date.png"))
    
    fig=plotAllMin(dF,allData=True)
    fig.savefig(os.path.join(supFolder,"exposure_date_full.png"))


    fig=plotAllMin(dF,allData=True)
    fig.savefig(os.path.join(supFolder,"exposure_date_full.png"))
    #plotAllMin(dF,allData=True,minValues=True)


    
    plotNicolae(dF,sensorPos=[0,3,6,9,"REF"])
    

def printACCHeatingTime(dF):
    for name in dF.sensorData:
        heatings=[(hp[1]-hp[0]).total_seconds() for hp in dF.minExposure[dF.sensorData[0]]['heatingPeriode']]
        print "%s -- %.2fh heatingTime"%(name,sum(heatings)/3600.0)
        



fig=plotAllMin(dF,allData=False)
print "This took %f.1 minutes"%((datetime.datetime.now()-startT).total_seconds()/60.0)