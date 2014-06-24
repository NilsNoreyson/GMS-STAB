# -*- coding: utf-8 -*-
"""
Created on Tue Jan 07 12:54:34 2014

@author: peters
"""

import time
import datetime
startT=datetime.datetime.now()

import dateutil.parser
import calendar
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

from experiment_data_format.tools import str_to_timedelta, timedelta_to_str
from PandasToEDF import *

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

def createMetaData(dF):
    meta={}
    for k in dF.keys():
        
        name=k[1]

        keys=k[0].split(',')
        
        meta[name]={}
        for key in keys:
            value=key.split('=')[1]
            keyName=key.split('=')[0]
            meta[name][keyName]=value
        
        
    return meta

def loadFlowEDF(totalPath,cleanRHandT=True):
    
    header,startRow=openEDF(totalPath)
    dF=pd.read_csv(totalPath,header=[startRow,startRow+1],sep="\t",index_col=0)
    dF.header=header
    
    colNames=[k[1] for k in dF.keys()]
    dF.metaData=createMetaData(dF)
    
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
    dF.metaData=createMetaData(dF)
    
        
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

    flowMeta=dF_Flow.metaData
    dataMeta=dF_Data.metaData
    
    meta=flowMeta
    meta.update(dataMeta)


    
    dF_Data_combined=dF
    
    #Since the freq. of the Flow-Prot. is higer fill up the values for the Sensor-Data
    #for k in dF_Flow.keys():
    #    dF_Data_combined[k]=dF_Data_combined[k].ffill()
    
    if dropNaN:
        #The timestamps of the SensorsData should now be filled with data. Drop the lines with not full Datasets
        dF_small=dF_Data_combined.dropna()
        

    dF_Data_combined.metaData=meta
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
    



def getMinUnderExposures(dataFrame,minValue=False):
    
    T=10



    pulseDataByName={}
    
    sensorNames=np.append(dataFrame.sensorNames,"Reference_Resistance")

    for sensor in sensorNames:
        

                
        


        
        if sensor!='Reference_Resistance':
            sensorNr=dataFrame.posByName[sensor]
            pulseData=dataFrame.pulsesByPos[sensorNr].copy()
            heaterNumber=dataFrame.heaterOfPosition[sensorNr]['heater']
            heaterPattern=dataFrame.heaterOfPosition[sensorNr]['pattern']
        else:

            sensorNr=len(dataFrame.sensorNames)
            
            pulseData=dataFrame.pulsesByPos[0].copy()
            heaterNumber=dataFrame.heaterOfPosition[0]['heater']
            heaterPattern='conct.'

        pulseData['conc']=None
        pulseData['t_pre']=None
        pulseData['r_pre']=None
        pulseData['r_min']=None
        pulseData['t_min']=None
        pulseData['r']=None
        pulseData['t']=None

        pulseData['b4r']=None
        pulseData['b4t']=None
        
        pulseData['pos']=sensorNr
        pulseData['heaterPattern']=heaterPattern
        pulseData['backgroundHumidity']=None

#        print pulseData
        
        for i,pulse in pulseData.iterrows():
            p=(pulse['start'],pulse['stop'])
            conc=dataFrame['MFC_4_conc_set'][p[0]:p[1]].max()
            if conc>0:
               
                
                beforeHeating=dataFrame.truncate(p[0]+datetime.timedelta(seconds=-50),p[0])
                beforeHeating=beforeHeating[sensor].dropna()
                #print beforeHeating
                b4H_t=beforeHeating.index[0]
                b4H_res=beforeHeating.iloc[0]
                print b4H_t,b4H_res
                underEthanol=dataFrame[p[0]:p[1]]
                underEthanol=underEthanol[underEthanol['MFC_4_conc_set']>0]
                
                
                #print pulse['duration']
                #print underEthanol
                ethanolStart=underEthanol.index[0]
                ethanolStopPlusDeltaT=underEthanol.index[-1]+datetime.timedelta(seconds=T)
                ethanolStop=underEthanol.index[-1]
                
                underEthanolPlusDeltaT=dataFrame[ethanolStart:ethanolStopPlusDeltaT]               
                underEthanol=dataFrame[ethanolStart:ethanolStop]
                
                if 'Reference_Temperature' in dataFrame.keys():
                    preBackHumidity=dataFrame['Reference_relHumidity'][p[0]+datetime.timedelta(seconds=-20):p[0]+datetime.timedelta(seconds=-10)].dropna().mean()
                else:
                    preBackHumidity=dataFrame['MFC_1_conc_actual'][p[0]+datetime.timedelta(seconds=-20):p[0]+datetime.timedelta(seconds=-10)].dropna().mean()
                    
                
                preData=dataFrame[sensor][p[0]+datetime.timedelta(seconds=2):ethanolStart+datetime.timedelta(seconds=5)].dropna()
                preMax=preData.max()
                preMaxT=preData.idxmax()
                
                sensorUnderEthanol=underEthanol[sensor].dropna()
                sensorUnderEthanolPlusDeltaT=underEthanolPlusDeltaT[sensor].dropna()
                
                resMin=sensorUnderEthanolPlusDeltaT.min()
                tMin=sensorUnderEthanolPlusDeltaT.idxmin()
                
                if len(sensorUnderEthanol.dropna())==0:
                    if sensor=='AS-MLC-14':
                        print sensorUnderEthanol               
                    continue
                    
                res=(sensorUnderEthanol.dropna()).iloc[-1]
                t=(sensorUnderEthanol.dropna()).index[-1]
                

                pulseData['conc'][i]=conc
                pulseData['t_pre'][i]=preMaxT
                pulseData['r_pre'][i]=preMax
                pulseData['t_min'][i]=tMin
                pulseData['r_min'][i]=resMin
                pulseData['t'][i]=t       
                pulseData['r'][i]=res
                
                pulseData['b4r'][i]=b4H_res
                pulseData['b4t'][i]=b4H_t
                
                pulseData['backgroundHumidity'][i]=preBackHumidity


        pulseDataByName[sensor]=pulseData

    if 'Reference_Temperature' in dataFrame.keys():
        pulseDataByName['REF']=pd.DataFrame(data={'res':dataFrame['Reference_Resistance'],'temp':dataFrame['Reference_Temperature'],'rh':dataFrame['Reference_relHumidity']},index=dataFrame.index)
    else:
        pulseDataByName['REF']=pd.DataFrame(data={'res':dataFrame['Reference_Resistance'],'temp':None,'rh':dataFrame['MFC_1_conc_actual']},index=dataFrame.index)

    pulseDataByName['REF'].join(pulseDataByName['Reference_Resistance'])


    
    
    return pulseDataByName

def getPulses(dataFrame,lookFW_days=14,threshold=0.01):
    pulsesByPos={}
    pulsesByHeater={}
    pulsesByName={}
    for s in dataFrame.sensorNames:
        pos=dataFrame.posByName[s]

        if pulsesByHeater.has_key(dataFrame.heaterOfPosition[pos]['heater']):
            p=pulsesByHeater[dataFrame.heaterOfPosition[pos]['heater']]
        else:
            p=findHeatingPulse(dataFrame,voltChannel=dataFrame.heaterOfPosition[pos]['heater'],lookFW_days=lookFW_days,threshold=threshold)
            pulsesByHeater[dataFrame.heaterOfPosition[pos]['heater']]=p

        pulsesByPos[pos]=p
        pulsesByName[s]=p

    return pulsesByPos,pulsesByHeater,pulsesByName

def saveDecoration(supFolder,dF):
    saveDict={}
    saveDict["pulsesByPos"]=dF.pulsesByPos
    saveDict['minExposure']=dF.minExposure
    saveDict['sensorNames']=dF.sensorNames
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
    

def getFiles(topFolder=None,folder=None):

    print folder

    supFolder=None
    
    if topFolder and os.path.exists(topFolder):
    #check if the topfolder existes. else use the current folder where the script is as start folder
        initFolder=topFolder
    
    elif folder and os.path.exists(folder):
        supFolder=folder
    else:
        initFolder=os.path.dirname(os.path.abspath(__file__))
        
    if not(supFolder):
	root=Tkinter.Tk()
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
        if (".xls" in f) and ("Flow" in f):
            xlsFileName=f
            break    
    
    flowTotalPath=os.path.join(supFolder,flowFileName)
    resTotalPath=os.path.join(supFolder,resFileName)
    xlsTotalPath=os.path.join(supFolder,xlsFileName)
    return supFolder,flowTotalPath,resTotalPath,xlsTotalPath

def getHeaterOfPosition(xlsFileName):
    workbook = xlrd.open_workbook(xlsFileName)
    worksheet = workbook.sheet_by_name('PowerSettings')
    heaterOfPosition={}
    for i in range(1,200):
        try:
            cell_value_pos = int(worksheet.cell_value(i, 0))
            cell_value_heater = worksheet.cell_value(i, 1)
            cell_value_pattern = worksheet.cell_value(i, 2)
        except:
            break
        heaterOfPosition[cell_value_pos]={'heater':cell_value_heater,'pattern':cell_value_pattern}
    return heaterOfPosition


def reindex(EDF):
    dateString=EDF.header['Date']
    fS=dateutil.parser.parse(dateString)
    fSn=calendar.timegm(fS.timetuple())*1e9
    
    EDF.index=pd.to_datetime((EDF.index*1e9)+fSn)
    return EDF

def printACCHeatingTime(dF):
    for i,name in enumerate(dF.sensorNames):
        totalHeatingTime=dF.pulsesByPos[i]['duration'].sum()
        print "%s -- %.2fh heatingTime"%(name,totalHeatingTime/3600.0)
        
        
def update_heaterIndex_in_meatadata(dF):
    for name in dF.posByName:
        pos=dF.posByName[name]
        heaterIndex=int(dF.heaterOfPosition[pos]['heater'])
        dF.metaData[name].update({'heaterIndex':heaterIndex})



def parseExperiment(supFolder,flowTotalPath,resTotalPath,xlsTotalPath):

    initData=True
    loadDF=False
    toEDF3_output=True

    if initData:
        
    
        #load the Flow--Data
        print 'loading'
        dF_Flow=loadFlowEDF(flowTotalPath)
        #load the Sensor-Data
        dF_Data=loadDataEDF(resTotalPath)
        
        #set the date as index instead of duration
        dF_Flow=reindex(dF_Flow)
        dF_Data=reindex(dF_Data)
        
        print 'combining'    
        dF=combineDF(dF_Flow,dF_Data,dropNaN=False)
        startTime=dF.index[0]
        dF['Duration-EDF3']=dF.index.map(lambda x:timedelta_to_str((x-startTime)))

        dF.sensorNames=dF_Data.columns
        posByName={}
        for i,n in enumerate(dF.sensorNames):
            posByName[n]=i
        dF.posByName=posByName

        #get the data from the excel file for the heater vs measuring position relation
        dF.heaterOfPosition=getHeaterOfPosition(xlsTotalPath)
        #get the pulses, where the heater is activated
        dF.pulsesByPos,dF.pulsesByHeater,dF.pulsesByName=getPulses(dF,lookFW_days=14,threshold=0.01)
        
        update_heaterIndex_in_meatadata(dF)

        print 'finding pulses'
        dF.sensorFullData=getMinUnderExposures(dF)
        print 'saving'    
        sensorDataFile=open(os.path.join(supFolder,'sensorData.pkl'),'wb')
        pickle.dump(dF.sensorFullData,sensorDataFile)
        sensorDataFile.close()
        
        
        
        #dF.metaData=dict(dF_Flow.metaData.items() + dF_Data.metaData.items())
        #
        #dF.to_pickle(os.path.join(supFolder,"dF.pkl"))
        #saveDecoration(supFolder,dF)    
        
    
    
    
    
    else:
        if loadDF:
            try:
                print "All files loaded",loaded
            except:
                supFolder,flowTotalPath,resTotalPath,xlsTotalPath=getFiles(topFolder)
                dF=pd.read_pickle(os.path.join(supFolder,"dF.pkl"))
                dF=loadDecoration(supFolder,dF)
                loaded=True
    
    if toEDF3_output:    
        dataFrame_to_EDF3(dF,topFolder=supFolder,name='GMS-Sta')    
    
    printACCHeatingTime(dF)
    return dF,dF.sensorFullData





def loadSensorData(folder):
    sensorDataFile=open(os.path.join(folder,'sensorData.pkl'),'rb')
    sensorMetaData_ByName=pickle.load(sensorDataFile)
    return sensorMetaData_ByName
    
def loadDf(supfolder):
    dF=pd.read_pickle(os.path.join(supFolder,"dF.pkl"))
    dF=loadDecoration(supFolder,dF)
    return dF
    
        
            
if __name__=="__main__":
    topFolder=r'/mnt/groups/Steinbeis-Auftragsabwicklung/STZ_Mitarbeiter/20016/Messungen/GMS-Stabilization/Setup@Ate/Measurements'
    folderNames=getFiles(topFolder=topFolder)
    dF,sensorFullData=parseExperiment(*folderNames)
    stopT=datetime.datetime.now()
    print "Duration:%.2f min."%((stopT-startT).total_seconds()/60.0)
    for k,v in sensorFullData.iteritems():
        try:
            print k,v['pos'].iloc[0]
        except:
            pass