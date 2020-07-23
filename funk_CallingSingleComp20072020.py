# -*- coding: utf-8 -*-
"""
This file calls SimEvent fucntion and replicates simulations
"""


def funk_CallingSingleComp20072020(CMleft = 520, CMmode=720, CMright = 920, PMleft=96,PMmode=120, PMright=168, WeibullShape = 1.5,
                                 WeibullScale = 21900, SimPeriod = 87600,  PMinterval = 8760*2, 
                                 PMtolerance = 720, NumSimulations = 1000):


    from SimEventLib20072020 import SingleComp as SingleComp
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt    
    import seaborn as sns
    
    
    SimMatrix = np.array(SingleComp(CMleft,CMmode, CMright, PMleft,PMmode, PMright, WeibullShape, WeibullScale, SimPeriod, PMinterval, PMtolerance))
    
    SimNum = np.full((SimMatrix.shape[0],1),1)
    SimMatrix = np.append(SimMatrix, SimNum, axis = 1)
    
    for i in range(0, NumSimulations - 1):
        Simulation = SingleComp(CMleft,CMmode, CMright, PMleft,PMmode, PMright, WeibullShape, 
                    WeibullScale, SimPeriod, PMinterval, PMtolerance)
        SimNum =np.full((Simulation.shape[0], 1), i+2)
        Simulation = np.append(Simulation, SimNum, axis = 1)
        SimMatrix = np.append(SimMatrix, Simulation, axis = 0)
    
    SimMatrix = SimMatrix.astype(float)
     
    SimMatrix[:,0] = (SimMatrix[:,0])/24;
    SimMatrix[:,2] = (SimMatrix[:,2])/24;     
    
    df = pd.DataFrame(SimMatrix, columns = ['Duration', 'Event', 'SimClock', 'SimKey'])
    
    df_agg = pd.DataFrame(pd.pivot_table(df, index = 'SimKey',values = 'Duration', columns = 'Event', 
                   aggfunc = {'sum', 'count'}))
    
    df_agg.fillna(value = 0, inplace = True)
    
    if PMinterval < SimPeriod:# This because if PMinterval> SimPeriod then we will have no PM and error will occur
        df_agg.columns = ['UptimeCount', 'CMcount', 'PMcount', 'UptimeSum', 'CMSum', 'PMSum']
        
        df_agg['Downtime'] = df_agg['CMSum'] + df_agg['PMSum']
        df_agg['Replacements'] = df_agg['CMcount'] + df_agg['PMcount']
        df_agg['MTBF'] = df_agg['UptimeSum'] / df_agg['CMcount']
        df_agg.loc[:,'MTBF'].replace(np.inf, df_agg.loc[:,'UptimeSum'], inplace=True)
        
        df_agg['MTTR'] =  df_agg['Downtime']  / (df_agg['CMcount'] + df_agg['PMcount'])
        df_agg['Availability'] = df_agg['MTBF'] / (df_agg['MTBF'] + df_agg['MTTR'])
        
        
        f, axes = plt.subplots(2, 3, figsize=(12, 7), sharex=False)
        sns.despine(left=True)
        
        sns.distplot(df_agg['CMcount'],kde=False, color="m", ax=axes[0, 0])
        sns.distplot(df_agg['PMcount'], kde=False, color="crimson", ax=axes[0, 1])
        sns.distplot(df_agg['Replacements'], kde=False, color="r", ax=axes[0, 2])
        sns.distplot(df_agg['CMSum'], kde=False, color="y", ax=axes[1, 0])
        sns.distplot(df_agg['MTBF'], kde=False, color="b", ax=axes[1, 1])
        sns.distplot(df_agg['Availability'], kde=False, color="black", ax=axes[1, 2])
        
        f.suptitle('Simulation Plots (in days)', fontsize=16)
    
    else:
        df_agg.columns = ['UptimeCount', 'CMcount', 'UptimeSum', 'CMSum']
        
        df_agg['Downtime'] = df_agg['CMSum']
        df_agg['MTBF'] = df_agg['UptimeSum'] / (df_agg['CMcount'])
        df_agg.loc[:,'MTBF'].replace(np.inf, df_agg.loc[:,'UptimeSum'], inplace=True)
        
        df_agg['MTTR'] =  df_agg['Downtime']  / (df_agg['CMcount'])
        df_agg['Availability'] = df_agg['MTBF'] / (df_agg['MTBF'] + df_agg['MTTR'])
        

        f, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=False)
        sns.despine(left=True)
        
        sns.distplot(df_agg['CMcount'],kde=False, color="m", ax=axes[0, 0])
        sns.distplot(df_agg['MTBF'], kde=False, color="r", ax=axes[0, 1])
        sns.distplot(df_agg['CMSum'], kde=False, color="y", ax=axes[1, 0])
        sns.distplot(df_agg['Availability'], kde=False, color="black", ax=axes[1, 1])
        
        f.suptitle('Simulation Plots (in days)', fontsize=16)
        
    Summary = df_agg.describe()
    print(Summary)



#Roug work
#C:\Users\hamma\Documents\Python Scripts

#summary.to_excel("Results.xlsx", sheet_name='Test1')

#with pd.ExcelWriter('Results.xlsx', mode='a') as writer:  
#    summary.to_excel(writer, sheet_name='Sheet_name_3', engine ='xlsxwriter')
