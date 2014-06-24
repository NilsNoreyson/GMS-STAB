# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 10:53:07 2014

@author: peterb
"""

#from plotDataSets import *

fig,axes=subplots(3,2,figsize=(20,30))
for i in [0,1,2]:
    axe_ac=axes[i][0]
    axe_set=axes[i][1]

    shrink=10
    
    power_actual=dF['Voltage_Channel_%i_actual'%i].dropna()[::shrink]
    power_set=dF['Voltage_Channel_%i_set'%i].dropna()[::shrink]
    
    axe_ac.plot(power_actual.index,power_actual)    
    axe_set.plot(power_set.index,power_set)
    axe_ac.callbacks.connect('xlim_changed', on_xlim_changed)
    axe_set.callbacks.connect('ylim_changed', on_ylim_changed)
    axe_ac.set_title("Actual\n"+getNamesWithHeaterIndex(i))
    axe_set.set_title("SET")


def getNamesWithHeaterIndex(index):
    sensornames=[]

    names=sensorFullData.keys()
    names=[n for n in names if not('Ref' in n) and not('REF' in n)]
    for name in names:
        if dF.metaData[name]['heaterIndex']==index:
            sensornames.append(name)
    return ",".join(sensornames)
            
print getNamesWithHeaterIndex(2)

    
formatFigForDates(fig)    
    