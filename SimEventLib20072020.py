"""
This file contain fucntions for making one simulation (A sequence of Uptime, Cm and PM).
Currently two type sof components are implemented.

1. Series/Single component

2. Reduncant component with delayed repair policy. THat is repair is initiated 
when both the components have failed. 

3. Redundant independent components

"""

def SingleComp(CMleft,CMmode, CMright, PMleft,PMmode, PMright, WeibullShape, WeibullScale, SimPeriod, PMinterval, PMtolerance):
    import numpy as np
    
    
    PMat = np.array(np.arange(PMinterval, SimPeriod + 3*PMinterval, PMinterval))
    PMcounter = 0
    NextPMat = PMat[PMcounter]
    
    SimEvent = np.array([[np.around(WeibullScale*np.random.weibull(WeibullShape)), 1, 0]])
    SimEvent[0, 2] = SimEvent[0,0]
    SimClock = np.array(SimEvent[0, 2])
        
    if SimClock >= SimPeriod and NextPMat < SimPeriod: #that if we get a very long lifetime we will not enter the loop
        SimClock = NextPMat
    elif SimClock >= SimPeriod and NextPMat > SimPeriod:#that is a corrective maintenance policy
        SimClock = SimPeriod
        SimEvent[0, 0] = SimPeriod
        SimEvent[0, 2] = SimPeriod
        
    while SimClock < SimPeriod:
            
        CurrentEvent = SimEvent[SimEvent.shape[0] - 1]
            
        if CurrentEvent[1] == 1: #Next event is then PM or CM
            if SimClock >= NextPMat: #that is enforce PM
                SimClock = NextPMat
                if SimEvent.shape[0] - 2 < 0:#That is if we have only one row
                    SimEvent[SimEvent.shape[0] - 1, 0] = NextPMat
                    SimEvent[SimEvent.shape[0] - 1, 2] = NextPMat
                    
                else: #That is when any other time during simulation
                    SimEvent[SimEvent.shape[0] - 1, 0] = abs(SimClock - SimEvent[SimEvent.shape[0] - 2, 2])
                    SimEvent[SimEvent.shape[0] - 1, 2] = NextPMat
                    #ABOVE LINES HAVE NO USE, are there due to earlier version
                #schedule the NextEvent which is a PM
                NextEvent = np.array([[np.around(np.random.triangular(PMleft,PMmode, PMright)), 3, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
                PMcounter = PMcounter + 1
                NextPMat = PMat[PMcounter]
            else:#do the CM   
                NextEvent = np.array([[np.around(np.random.triangular(CMleft,CMmode, CMright)), 2, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
            #update the SimClock
            SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
            SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
            
        elif CurrentEvent[1] == 2: #Next event is PM or Uptime
            if SimClock + PMtolerance > NextPMat:#Then we skip that PM
                PMcounter = PMcounter + 1
                NextPMat = PMat[PMcounter]
                NextEvent = np.array([[np.around(WeibullScale*np.random.weibull(WeibullShape)), 1, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
            else:#CM is followed by PM
                NextEvent = np.array([[np.around(WeibullScale*np.random.weibull(WeibullShape)), 1, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
            #update the simulation clock
            SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
            SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
            if SimClock >= NextPMat: #Ajust the SimClock again because if a very big number is generated
                SimClock = NextPMat
                SimEvent[SimEvent.shape[0] - 1, 0] = abs(SimClock - SimEvent[SimEvent.shape[0] - 2, 2])
                SimEvent[SimEvent.shape[0] - 1, 2] = NextPMat
                #schedule the NextEvent which is a PM
                NextEvent = np.array([[np.around(np.random.triangular(PMleft,PMmode, PMright)), 3, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
                PMcounter = PMcounter + 1
                NextPMat = PMat[PMcounter]
                SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
                SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
            
        else: #That is when the CurrentEvent is PM. Always will be followed by Uptime
            NextEvent = np.array([[np.around(WeibullScale*np.random.weibull(WeibullShape)), 1, 0]])
            SimEvent = np.append(SimEvent, NextEvent, axis = 0)
            #update the simulation clock
            SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
            SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
            if SimClock >= NextPMat: #Ajust the SimClock again because if a very big number is generated
                SimClock = NextPMat
                SimEvent[SimEvent.shape[0] - 1, 0] = abs(SimClock - SimEvent[SimEvent.shape[0] - 2, 2])
                SimEvent[SimEvent.shape[0] - 1, 2] = NextPMat
                #schedule the NextEvent which is a PM
                NextEvent = np.array([[np.around(np.random.triangular(PMleft,PMmode, PMright)), 3, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
                PMcounter = PMcounter + 1
                NextPMat = PMat[PMcounter]
                SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
                SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
                
    #Adjustment for the last element of the array otherwise estimates will be biased            
    if SimEvent.shape[0] > 1:
        if SimEvent[SimEvent.shape[0] - 2, 2] == SimPeriod:
            SimEvent = np.delete(SimEvent, SimEvent.shape[0] - 1, 0)
        
        elif SimEvent[SimEvent.shape[0] - 2, 2] > SimPeriod:
            SimEvent = np.delete(SimEvent, SimEvent.shape[0] - 1, 0)
            SimEvent[SimEvent.shape[0] - 1, 0] = SimPeriod - SimEvent[(SimEvent.shape[0] - 2), 2]
            SimEvent[SimEvent.shape[0] - 1, 2] = SimPeriod
        else:
            SimEvent[SimEvent.shape[0] - 1, 0] = SimPeriod - SimEvent[SimEvent.shape[0] - 2, 2]
            SimEvent[SimEvent.shape[0] - 1, 2] = SimPeriod

    
#    SimEvent = np.delete(SimEvent, 2, 1)
    SingleComp = SimEvent.astype(int)
    return SingleComp

def RedComp_DelayedRep(CMleft,CMmode, CMright, PMleft,PMmode, PMright, WeibullShape, WeibullScale, SimPeriod, PMinterval, PMtolerance):
    import numpy as np
    
    
    PMat = np.array(np.arange(PMinterval, SimPeriod + 3*PMinterval, PMinterval))
    PMcounter = 0
    NextPMat = PMat[PMcounter]
    
    maxLifetime = np.amax((np.array([[np.around(WeibullScale*np.random.weibull(WeibullShape)),
                    np.around(WeibullScale*np.random.weibull(WeibullShape))]])))
    SimEvent = np.array([[maxLifetime, 1, 0]])
    SimEvent[0, 2] = SimEvent[0,0]
    SimClock = np.array(SimEvent[0, 2])
        
    if SimClock >= SimPeriod and NextPMat < SimPeriod: #that is if we get a very long lifetime we will not enter the loop
        SimClock = NextPMat
    elif SimClock >= SimPeriod and NextPMat > SimPeriod:#that is a corrective maintenance policy
        SimClock = SimPeriod
        SimEvent[0, 0] = SimPeriod
        SimEvent[0, 2] = SimPeriod
        
    while SimClock < SimPeriod:
            
        CurrentEvent = SimEvent[SimEvent.shape[0] - 1]
            
        if CurrentEvent[1] == 1: #Next event is then PM or CM
            if SimClock >= NextPMat: #that is enforce PM
                SimClock = NextPMat
                if SimEvent.shape[0] - 2 < 0:#That if we have only one row
                    SimEvent[SimEvent.shape[0] - 1, 0] = NextPMat
                    SimEvent[SimEvent.shape[0] - 1, 2] = NextPMat
                else: #That is when any other time during simulation
                    SimEvent[SimEvent.shape[0] - 1, 0] = abs(SimClock - SimEvent[SimEvent.shape[0] - 2, 2])
                    SimEvent[SimEvent.shape[0] - 1, 2] = NextPMat
                    #ABOVE LINES HAVE NO USE, are there due to earlier version
                #schedule the NextEvent which is a PM
                NextEvent = np.array([[np.around(np.random.triangular(PMleft,PMmode, PMright)), 3, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
                PMcounter = PMcounter + 1
                NextPMat = PMat[PMcounter]
            else:#do the CM   
                NextEvent = np.array([[np.around(np.random.triangular(CMleft,CMmode, CMright)), 2, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
            #update the SimClock
            SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
            SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
            
        elif CurrentEvent[1] == 2: #Next event is PM or Uptime
            if SimClock + PMtolerance > NextPMat:#Then we skip that PM
                PMcounter = PMcounter + 1
                NextPMat = PMat[PMcounter]
                maxLifetime = np.amax((np.array([[np.around(WeibullScale*np.random.weibull(WeibullShape)),
                                                  np.around(WeibullScale*np.random.weibull(WeibullShape))]])))
                NextEvent = np.array([[maxLifetime, 1, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
                #print('SimClock + PMtolerance > NextPMat')
            else:
                maxLifetime = np.amax((np.array([[np.around(WeibullScale*np.random.weibull(WeibullShape)),
                np.around(WeibullScale*np.random.weibull(WeibullShape))]])))
                NextEvent = np.array([[maxLifetime, 1, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
                #print('UPTIME followed by CM')
            #update the simulation clock
            SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
            SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
            if SimClock >= NextPMat:
                SimClock = NextPMat
                SimEvent[SimEvent.shape[0] - 1, 0] = abs(SimClock - SimEvent[SimEvent.shape[0] - 2, 2])
                SimEvent[SimEvent.shape[0] - 1, 2] = NextPMat
                #schedule the NextEvent which is a PM
                NextEvent = np.array([[np.around(np.random.triangular(PMleft,PMmode, PMright)), 3, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
                PMcounter = PMcounter + 1
                NextPMat = PMat[PMcounter]
                SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
                SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
            
        else: #That is when the CurrentEvent is PM. Always will be followed by Uptime
            maxLifetime = np.amax((np.array([[np.around(WeibullScale*np.random.weibull(WeibullShape)),
                    np.around(WeibullScale*np.random.weibull(WeibullShape))]])))
            NextEvent = np.array([[maxLifetime, 1, 0]])
            SimEvent = np.append(SimEvent, NextEvent, axis = 0)
            #update the simulation clock
            SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
            SimClock = SimEvent[SimEvent.shape[0] - 1, 2]
            if SimClock >= NextPMat:
                SimClock = NextPMat
                SimEvent[SimEvent.shape[0] - 1, 0] = abs(SimClock - SimEvent[SimEvent.shape[0] - 2, 2])
                SimEvent[SimEvent.shape[0] - 1, 2] = NextPMat
                #schedule the NextEvent which is a PM
                NextEvent = np.array([[np.around(np.random.triangular(PMleft,PMmode, PMright)), 3, 0]])
                SimEvent = np.append(SimEvent, NextEvent, axis = 0)
                PMcounter = PMcounter + 1
                NextPMat = PMat[PMcounter]
                SimEvent[SimEvent.shape[0] - 1, 2] = np.sum(SimEvent, axis = 0)[0]
                SimClock = SimEvent[SimEvent.shape[0] - 1, 2]    
        
        #Adjustment for the last element of the array otherwise estimates will be biased            
    if SimEvent.shape[0] > 1:
        if SimEvent[SimEvent.shape[0] - 2, 2] == SimPeriod:
            SimEvent = np.delete(SimEvent, SimEvent.shape[0] - 1, 0)
        
        elif SimEvent[SimEvent.shape[0] - 2, 2] > SimPeriod:
            SimEvent = np.delete(SimEvent, SimEvent.shape[0] - 1, 0)
            SimEvent[SimEvent.shape[0] - 1, 0] = SimPeriod - SimEvent[(SimEvent.shape[0] - 2), 2]
        
        else:
            SimEvent[SimEvent.shape[0] - 1, 0] = SimPeriod - SimEvent[SimEvent.shape[0] - 2, 2]

    
#    SimEvent = np.delete(SimEvent, 2, 1)
    RedComp_DelayedRep = SimEvent.astype(int)
    return RedComp_DelayedRep

def RedComp_Indep(CMleft,CMmode, CMright, PMleft,PMmode, PMright, WeibullShape, WeibullScale, SimPeriod, PMinterval, PMtolerance):
    
    from SimEventLib20072020 import SingleComp as SingleComp
    import numpy as np
    
    #First make a Status indicator of comps and system
    Comp1_SimEvent = np.array(SingleComp(CMleft,CMmode, CMright, PMleft,PMmode, PMright, WeibullShape, WeibullScale, SimPeriod, PMinterval, PMtolerance))
    Comp2_SimEvent = np.array(SingleComp(CMleft,CMmode, CMright, PMleft,PMmode, PMright, WeibullShape, WeibullScale, SimPeriod, PMinterval, PMtolerance))

    StatusIndicator1 = [np.full((i[0],1), i[1]) for i in Comp1_SimEvent[:,0:2]]
    StatusIndicator1 = np.array([item for sublist in StatusIndicator1 for item in sublist])

    StatusIndicator2 = [np.full((i[0],1), i[1]) for i in Comp2_SimEvent[:,0:2]]
    StatusIndicator2 = np.array([item for sublist in StatusIndicator2 for item in sublist])    
    
    StatusIndicator = np.concatenate((StatusIndicator1, StatusIndicator2), axis = 1)
    temp = [int(str(i[0]) + str(i[1])) for i in StatusIndicator]
    StatusIndicator = np.column_stack((StatusIndicator, temp))
    
    #packing the StatusIndicator       
    Sys_SimEvent = np.array([[0, 11, 0]])
    Counter = 0

    for i in range(1, StatusIndicator.shape[0]):
        if StatusIndicator[i, 2] == StatusIndicator[i-1, 2]:
            Sys_SimEvent[Counter,0] = Sys_SimEvent[Counter,0] + 1
        else:
            Counter = Counter + 1
            Sys_SimEvent = np.append(Sys_SimEvent, np.array([[1, StatusIndicator[i, 2], 0]]) , axis=0)
    
    #calculating the SimClock column           
    Sys_SimEvent[:, 2] = np.cumsum(Sys_SimEvent[:, 0])
    
    RedComp_Indep = Sys_SimEvent
    return RedComp_Indep