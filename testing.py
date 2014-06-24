# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 23:22:27 2014

@author: peterb
"""

#
#fig,axe=subplots()
#data=dF['AA026_04'].dropna()
#axe.plot(data.index,data)
#axe.set_yscale('log')
#axe.set_ylim(1e3,1e10)

from plotDataSets import *

for i in range(30):close()




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
            
    
    
plotXvsYAll()    
