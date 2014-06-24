# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 16:25:13 2014

@author: peterb
"""

import pandas as pd

def removeOverValue(sensorData,overValue=1e20):
    for s in sensorData.keys():
        
        for k in  sensorData[s].keys():
            
            try:
                
                sensorData[s][k][sensorData[s][k]>1e20]=NaN
                print s
                if ((sensorData[s][k]>1e20).any()):
                    print s
                    print "over"
            except:
                pass
    return sensorData