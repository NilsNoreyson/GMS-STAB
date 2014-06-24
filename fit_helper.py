# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 16:27:29 2014

@author: peterb
"""


from scipy import optimize
from pylab import *

FIT_FUNC = lambda p, x:p[0]*(x**p[1])# Target function

ERR_FUNC = lambda p, x, y: (FIT_FUNC(p, x) - y)/y # Distance to the target function


P0=[4000,-0.3] # Initial guess for the parameters

def fitExposure(xData,yData):
    pfit, pcov,infodict,errmsg,success = optimize.leastsq(ERR_FUNC, P0[:], args=(xData, yData),full_output=True)
    

    if (len(yData) > len(P0)) and pcov is not None:
        s_sq = (ERR_FUNC(pfit, xData, yData)**2).sum()/(len(yData)-len(P0))
        pcov = pcov * s_sq
    else:
        pcov = inf

    error = []
    for i in range(len(pfit)):
        try:
            error.append( np.absolute(pcov[i][i])**0.5)
        except:
            error.append( 0.00 )

    p_err = np.array(error) 

    return pfit,p_err
    

def calibFunc(p):
    return lambda x:FIT_FUNC(p,x)
    
def anaFunc(p):
    return lambda R:(R/p[0])**(1/p[1])
    

def calc_rel_error_in_conc(p,c,R):
    calib=calibFunc(p)
    ana=anaFunc(p)
    
    rE=abs(ana(R)-c)/c
    
    return rE
    


def sensitivity(p):
    return lambda x:p[0]*p[1]*x**(p[1]-1)
        

