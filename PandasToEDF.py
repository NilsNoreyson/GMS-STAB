# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 11:18:17 2014

@author: peterb
"""
import os
from experiment_data_format.tools import str_to_timedelta, timedelta_to_str


from datetime import timedelta
from experiment_data_format.experimentdata import ExperimentData


def metaData_to_str(metaData):
    strings=[]
    for k in metaData.keys():
        strings.append('%s=%s'%(k,metaData[k]))
    return ','.join(strings)
    
def createRelevantDF(dF):
    importantNames=[u'Duration-EDF3',
     u'Reference_Resistance',
     u'Reference_Temperature',
     u'Reference_relHumidity',

     u'MFC_0_set',
     u'MFC_1_set',
     u'MFC_2_set',
     u'MFC_3_set',
     u'MFC_4_set',
     
     u'Voltage_Channel_0_actual',
     u'Current_Channel_0_actual',
     u'Voltage_Channel_0_set',
     u'Current_Channel_0_set',
     
     u'Voltage_Channel_1_actual',
     u'Current_Channel_1_actual',
     u'Voltage_Channel_1_set',
     u'Current_Channel_1_set',
     
     u'Voltage_Channel_2_actual',
     u'Current_Channel_2_actual',
     u'Voltage_Channel_2_set',
     u'Current_Channel_2_set',
     
     u'Voltage_Channel_3_actual',
     u'Current_Channel_3_actual',
     u'Voltage_Channel_3_set',
     u'Current_Channel_3_set',
     
     u'AA028_14',
     u'AA028_16',
     u'AA026_02',
     u'AA026_04',
     u'AA031_047',
     u'AA031_048',
     u'AA026_30',
     u'AA026_31',
     u'AA031_31',
     u'AA031_32',
     u'AA031_17',
     u'AA031_18',
     u'AA026_37',
     u'AA026_38',
     u'AS-MLC-13',
     u'AS-MLC-14']

     
    return importantNames
    



def dataFrame_to_EDF3(dF,topFolder='./',name='GMS-STab'):
    firstT=dF.index[0].strftime('%Y.%m.%d')
    lastT=dF.index[-1].strftime('%Y.%m.%d')
    
    
    directory=os.path.join(topFolder,'%s_%s_to_%s_EDF3'%(name,firstT,lastT))
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    firstT=dF.index[0].strftime('%Y.%m.%d')
    lastT=dF.index[-1].strftime('%Y.%m.%d')
    
    fileName="%s_%s_to_%s.edf"%(name,firstT,lastT)
    fileName=os.path.join(directory,fileName)
        
    
    importantNames=createRelevantDF(dF)
    startTime=dF.index[0] 
    edf = ExperimentData(columns=0)
    header=edf.header
    header['Date']=str(startTime)
    
    f=open(fileName,'w')
    
    for k in header.keys():
        headerString="%s=%s\n"%(k,header[k])
        f.write(headerString)
    
    
    
    metaArray=[metaData_to_str(dF.metaData[m]) for m in importantNames]
    metaHeaderString='\t'.join(metaArray)
    metaHeaderString+="\n"
    
    f.write(metaHeaderString)
    
    
    dFSmall=dF.iloc[0:]
    dFSmall.to_csv(f,sep='\t',na_rep='None',index=False,cols=importantNames)
    f.close()
    edf = ExperimentData.read(fileName)

    
    
if __name__ == '__main__':
    dataFrame_to_EDF3(dF,topFolder='./',name='GMS-Sta')    
        
