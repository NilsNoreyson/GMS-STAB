# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 08:40:53 2014

@author: peterb
"""

pulse=-3



pulse=(p.iloc[pulse].start,p.iloc[pulse].stop)
sensorName='AS-MLC-14'
pulseData=dF[sensorName].truncate(pulse[0],pulse[1]).dropna()

print(dF['MFC_4_conc_set'].truncate(pulse[0],pulse[1]).max())
print(pulseData)

def update_heaterIndex_in_meatadata(dF):
    for name in dF.posByName:
        pos=dF.posByName[name]
        heaterIndex=int(dF.heaterOfPosition[pos]['heater'])
        dF.metaData[name].update({'heaterIndex':heaterIndex})

update_heaterIndex_in_meatadata(dF)