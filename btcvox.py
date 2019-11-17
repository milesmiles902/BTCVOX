#File System
import os
#Dataframes
import pandas as pd
#Array
import numpy as np
#Date Information
import datetime
from datetime import timedelta
#Times
from time import sleep
#CSV
import csv

#Get Dates
dates = pd.read_csv("Dates", sep='\t', index_col=0)
#Get Weekly Dates
weekly = dates.values[0][0]
print weekly
#Min Put/Call Difference
min_dif = []
strike = []
def calculate_sigma(folder, sub):
    global min_dif
    global strike
    #Grab last and second to last sorted date files in folder: 1 is last, 2 is second to last
    files = sorted(os.listdir(str(folder)))[len(os.listdir(str(folder)))-sub]    
    name = folder + "/" + files  
    df = pd.read_csv(name, sep='\t',index_col=0) 

    ###Error Checking:
    #print "DateFrame is: " + str(df)

    tot = []
    df_c_d = []
    df_p_d = []
    #Get (Ks/K*K)*Q(Ki)
    for ind in range(2, df.shape[0]-1):
        #Get mid-Call/Put value at each strike price
        #Df = Call_B, Call_A, Put_B, Put_A 
        idx = ind-2
        df_c_d = np.append(df_c_d, (abs(df.iloc[idx, 0]-df.iloc[idx, 1])/2)+df.iloc[idx,0])
        df_p_d = np.append(df_p_d, (abs(df.iloc[idx, 2]-df.iloc[idx, 3])/2)+df.iloc[idx,2])
        #Mid-point for each Bid Ask
        q = abs(df_c_d[idx]-df_p_d[idx])/2+min(df_c_d[idx], df_p_d[idx])
        #Sliding del_K window: (ind+1 - ind-1)/2 /(K*K) = (k+1 - k-1)/2 /(K*K)
        del_K = (((df.index.values[ind+1]-df.index.values[ind-1])/2))/(df.index.values[ind]*df.index.values[ind])
        #DelK/K*K*Q
        tot.append(del_K*q)
        
        ###Error Checking:
        #print "Mid Point - Q for row " + str(idx+1) + " is: " + str(q)
        #print "Del K / K*K for row " + str(idx+1) + " is: " + str(del_K)
   
    #Find smallest abs(call-put) - Record Strike - F
    min_dif.append(np.amin(abs(np.subtract(df_c_d, df_p_d))))
    strike.append(df.index.values[np.where(min_dif[sub-1] == abs(np.subtract(df_c_d, df_p_d)))][0])

    ###Error Checking:
    #print "Calls: " + str(df_c_d)
    #print "Puts:" + str(df_p_d)
    #print "Difference: " + str(np.subtract(df_c_d, df_p_d))
    #print "Minimum Absolute Difference: " + str(min_dif)
    #print "Index that the minimum difference is the same: " + str(min_dif[sub-1] == abs(np.subtract(df_c_d, df_p_d)))
    #print "Strike prices : " + str(df.index.values)
    
    return sum(tot)

def time(folder,sub):
    now = datetime.datetime.now()
    cur_day = ((24-now.hour-sub)*60*60)+((60-now.minute-1)*60)+(60-now.second)
    set_day = ((int(folder[:2])-now.day)*24*60*60-cur_day)
    return float(cur_day+set_day)/(365*24*60*60)         

def f(sub):
    return float(strike[sub-1] + min_dif[sub-1])

def n_t(folder, sub):
    files = sorted(os.listdir(str(folder)))[len(os.listdir(str(folder)))-sub]
    min_till = 60 - int(files[11:13])
    hour_till = 24-int(files[14:16])
    return float((int(folder[:2])-hour_till)*60+min_till*60)

def get_values():    
    #Next Term Options
    sigma_2 = calculate_sigma(weekly, 1)
    time_2 = time(weekly, 1)
    f_2 = f(1)
    var_2 = (2/time_2)*sigma_2-(1/time_2)*((f_2/strike[0])-1)*((f_2/strike[0])-1)

    ###Error Checking:
    #print "Next Term-" 
    #print "Next term Sigma: " + str(sigma_2)
    #print "Next term T(sec - not min): " + str(time_2)
    #print "Next term F: " + str(f_2)
    #print "Next Term variance: " + str(var_2)

    #Near Term Options
    sigma_1 = calculate_sigma(weekly, 2)
    time_1 = time(weekly, 2)
    f_1 = f(2)
    var_1 = (2/time_1)*sigma_1-(1/time_1)*((f_1/strike[1])-1)*((f_1/strike[1])-1)

    ###Error Checking:
    #print "Near Term-"         
    #print "Near term Sigma: " + str(sigma_1)
    #print "Near term T(sec - not min): " + str(time_1)
    #print "Near term F: " + str(f_1)
    #print "Near Term variance:  " + str(var_1)

    n2 = n_t(weekly,1)
    n1 = n_t(weekly,2)
    n30 = 30*24*60
    n365 = 365*n30

    #Error Checking:
    #print "N2 for Next Term: " + str(n2)
    #print "N1 for Near Term: " + str(n1)
    #print "N30: " + str(n30)
    #print "N365: " + str(n365)

    VOX = 100*((time_1*sigma_1*((n2-n30)/(n2-n1))+time_2*sigma_2*((n30-n1)/(n2-n1)))*n365/n30*1000)**(1/2.0)
    print "The VOX is: " + str(VOX)
    
    #with open('VOX/VOX.csv','a') as fd:
    #    fd.write([str(datetime.datetime.now()), str(VOX)])
    #fd.close()

    global min_dif 
    global strike 
    min_dif = []
    strike = []
while(True):
    get_values()
    sleep(2*60*60)

