#Deribit API
from deribit_api import RestClient
client = RestClient("4M2iZZwmDDqfg", "IE37DBTQ2INOHL4GZFMOC4ZGAFKMY5BX")
#Pandaz
import pandas as pd
#Numpy
import numpy as np
#Extract strings
import string
#Timers
import datetime
from time import sleep
#File system
import os, errno
#CSV
import csv

print "************************"
print "Mama Bitcoin is: " + str(client.index()[u'btc'])
print "************************"

#Get API Data
exp_dat = client.getinstruments()

#Extract Options Title
def extract(dat, extract, tool):
    opt = []
    for each in dat:
        if (extract in each[tool]):
            opt.append(each)
    return opt

#Dataframe to Store Puts and Calls
def store_options(s_list, extract):
    ind = set()
    for each in s_list:
        if (extract in each[u'instrumentName']):
            if (each[u'strike']>750.00):
                ind.add(each[u'strike'])
    ind = sorted(ind)
    df = pd.DataFrame(columns=['Calls_B','Calls_A', 'Puts_B', 'Puts_A'], index = ind)
    return df

#Get indice in list
def safe_list_get (l, idx, default):
    try:
        return l[idx][u'price']
    except IndexError:
        try:
            return default[idx][u'price']
        except IndexError:
            return float('Inf')

def store_bids_asks(opt, df, date):
    for each in opt:
        if (date in each[u'instrumentName']):
            instrument = each[u'instrumentName']
            order = client.getorderbook(instrument)
            if (each[u'strike']>700.00):
                if (each[u'optionType'] == u'put'):
                    df.at[each[u'strike'], 'Puts_A'] = safe_list_get((order)[u'asks'],0,(order)[u'bids'])
                    df.at[each[u'strike'], 'Puts_B'] = safe_list_get((order)[u'bids'],0,(order)[u'asks'])
                if (each[u'optionType'] == u'call'):
                    df.at[each[u'strike'], 'Calls_A'] = safe_list_get((order)[u'asks'],0,(order)[u'bids'])
                    df.at[each[u'strike'], 'Calls_B'] = safe_list_get((order)[u'bids'],0,(order)[u'asks'])
    return df

def extract_dates(dat):
    dates = set()
    for each in dat:
        strg = each[u'instrumentName']
        store = strg.split("-")
        dates.add(store[1])
    dates.remove(u'PERPETUAL')
    return dates

#Operations of Extracting Data
def mkdir(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            #raise
            return

#Operations of Extracting Data
first = True
dates = extract_dates(exp_dat)

def get_options(d):
    #global count
    options_date = extract(exp_dat, d, u'instrumentName')
    options = extract(options_date, "0-P", u'instrumentName')
    options.extend(extract(options_date, "0-C", u'instrumentName'))
    df = store_options(options, d)
    df = store_bids_asks(options,df, d)
    return df

def record(d):
        df.columns.name = client.index()[u'btc']
        print datetime.datetime.now()
        print df
        dat = datetime.datetime.now()
        name = str(d) + "/" + str(dat) + ".csv"
        mkdir(d)
        df.to_csv(name, sep='\t', encoding='utf-8')

def check_dates(date_check):
    global first
    global dates
    df = pd.DataFrame()
    df = df.append(list(date_check))
    if (first):
        df.to_csv("Dates", sep='\t', encoding='utf-8')
        first = False
    date = extract_dates(exp_dat)
    if (date_check != dates):
        df.to_csv("Dates", sep='\t', encoding='utf-8')
        dates = date_check
    else:
        return

#Get Weekly Dates
weekly = list(dates)[1]
#Min Put/Call Difference
min_dif = []
strike = []
def calculate_sigma(data, sub):
    global min_dif
    global strike
    #Get stored values

    #Grab last and second to last sorted date files in folder: 1 is last, 2 is second to last
    #files = sorted(os.listdir(str(folder)))[len(os.listdir(str(folder)))-sub]    
    #name = folder + "/" + files  
    #df = pd.read_csv(name, sep='\t',index_col=0) 
    df = data
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

def time(d):
    now = datetime.datetime.now()
    cur_day = ((24-now.hour)*60*60)+((60-now.minute-1)*60)+(60-now.second)
    set_day = ((int(d)-now.day)*24*60*60-cur_day)
    return float(cur_day+set_day)/(365*24*60*60)         

def f(sub):
    return float(strike[sub-1] + min_dif[sub-1])

def n_t(d, sub):
    #files = sorted(os.listdir(str(folder)))[len(os.listdir(str(folder)))-sub]
    now = datetime.datetime.now()
    min_till = 60 - int(now.minute)-sub
    hour_till = 24-int(now.hour)
    return float((int(d)-hour_till)*60+min_till*60)

def get_values(cur, prev, d):    
    #Next Term Options
    sigma_2 = calculate_sigma(cur, 0)
    time_2 = time(d)
    f_2 = f(1)
    var_2 = (2/time_2)*sigma_2-(1/time_2)*((f_2/strike[0])-1)*((f_2/strike[0])-1)

    ###Error Checking:
    #print "Next Term-" 
    #print "Next term Sigma: " + str(sigma_2)
    #print "Next term T(sec - not min): " + str(time_2)
    #print "Next term F: " + str(f_2)
    #print "Next Term variance: " + str(var_2)

    #Near Term Options
    sigma_1 = calculate_sigma(prev, 2)
    time_1 = time(prev)
    f_1 = f(2)
    var_1 = (2/time_1)*sigma_1-(1/time_1)*((f_1/strike[1])-1)*((f_1/strike[1])-1)

    ###Error Checking:
    #print "Near Term-"         
    #print "Near term Sigma: " + str(sigma_1)
    #print "Near term T(sec - not min): " + str(time_1)
    #print "Near term F: " + str(f_1)
    #print "Near Term variance:  " + str(var_1)

    n2 = n_t(d,0)
    n1 = n_t(d,5)
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

min_dif = []
strike = []
check = False
current = []
previous = []

while True:
    global dates
    global check
    global current
    global previous
    date = extract_dates(exp_dat)
    check_dates(date)
    current = get_options(list(dates)[1])
    print((list(dates)[1]).encode("utf-8")[:2])
    #print(current)
    if(check):
        get_values(current, previous, (list(dates)[1]).encode("utf-8")[:2])
        #record(d)
    previous = current
    check = True
    sleep(5*60)

#Deribit API
from deribit_api import RestClient
client = RestClient("4M2iZZwmDDqfg", "IE37DBTQ2INOHL4GZFMOC4ZGAFKMY5BX")
#Pandaz
import pandas as pd
#Numpy
import numpy as np
#Extract strings
import string
#Timers
import datetime
from time import sleep
#File system
import os, errno
#CSV
import csv

print "************************"
print "Mama Bitcoin is: " + str(client.index()[u'btc'])
print "************************"

#Get API Data
exp_dat = client.getinstruments()

#Extract Options Title
def extract(dat, extract, tool):
    opt = []
    for each in dat:
        if (extract in each[tool]):
            opt.append(each)
    return opt

#Dataframe to Store Puts and Calls
def store_options(s_list, extract):
    ind = set()
    for each in s_list:
        if (extract in each[u'instrumentName']):
            if (each[u'strike']>750.00):
                ind.add(each[u'strike'])
    ind = sorted(ind)
    df = pd.DataFrame(columns=['Calls_B','Calls_A', 'Puts_B', 'Puts_A'], index = ind)
    return df

#Get indice in list
def safe_list_get (l, idx, default):
    try:
        return l[idx][u'price']
    except IndexError:
        try:
            return default[idx][u'price']
        except IndexError:
            return float('Inf')

def store_bids_asks(opt, df, date):
    for each in opt:
        if (date in each[u'instrumentName']):
            instrument = each[u'instrumentName']
            order = client.getorderbook(instrument)
            if (each[u'strike']>700.00):
                if (each[u'optionType'] == u'put'):
                    df.at[each[u'strike'], 'Puts_A'] = safe_list_get((order)[u'asks'],0,(order)[u'bids'])
                    df.at[each[u'strike'], 'Puts_B'] = safe_list_get((order)[u'bids'],0,(order)[u'asks'])
                if (each[u'optionType'] == u'call'):
                    df.at[each[u'strike'], 'Calls_A'] = safe_list_get((order)[u'asks'],0,(order)[u'bids'])
                    df.at[each[u'strike'], 'Calls_B'] = safe_list_get((order)[u'bids'],0,(order)[u'asks'])
    return df

def extract_dates(dat):
    date = set()
    for each in dat:
        strg = each[u'instrumentName']
        store = strg.split("-")
        date.add(store[1])
    date.remove(u'PERPETUAL')
    return date

#Operations of Extracting Data
def mkdir(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            #raise
            return

#Operations of Extracting Data
first = True
dates = extract_dates(exp_dat)

def get_options(d):
    #global count
    options_date = extract(exp_dat, d, u'instrumentName')
    options = extract(options_date, "0-P", u'instrumentName')
    options.extend(extract(options_date, "0-C", u'instrumentName'))
    df = store_options(options, d)
    df = store_bids_asks(options,df, d)
    return df

#Get Weekly Dates
#Min Put/Call Difference
min_dif = []
strike = []
def calculate_sigma(data, sub):
    global min_dif
    global strike
    #Get stored values

    #Grab last and second to last sorted date files in folder: 1 is last, 2 is second to last
    #files = sorted(os.listdir(str(folder)))[len(os.listdir(str(folder)))-sub]    
    #name = folder + "/" + files  
    #df = pd.read_csv(name, sep='\t',index_col=0) 
    df = data
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
    
    return sum(tot)

def time(d):
    now = datetime.datetime.now()
    cur_day = ((24-now.hour)*60*60)+((60-now.minute-1)*60)+(60-now.second)
    set_day = ((d-now.day)*24*60*60-cur_day)
    return float((cur_day+set_day)/(24*60*60))         

def f(sub):
    return float(strike[sub-1] + min_dif[sub-1])

def n_t(d, sub):
    #files = sorted(os.listdir(str(folder)))[len(os.listdir(str(folder)))-sub]
    now = datetime.datetime.now()
    min_till = 60 - int(now.minute)-sub
    hour_till = 24-int(now.hour)
    return float((d-hour_till)*60+min_till*60)

def get_values(cur, prev, d):    
    #Next Term Options
    sigma_2 = calculate_sigma(cur, 0)
    time_2 = time(d)
    f_2 = f(1)
    var_2 = (2/time_2)*sigma_2-(1/time_2)*((f_2/strike[0])-1)*((f_2/strike[0])-1)

    ###Error Checking:
    #print "Next Term-"         
    #print "Next term Sigma: " + str(sigma_2)
    #print "Next term T(sec - not min): " + str(time_2)
    #print "Next term F: " + str(f_2)
    #print "Next Term variance:  " + str(var_2)
    
    #Near Term Options
    sigma_1 = calculate_sigma(prev, 0)
    time_1 = time(d)
    f_1 = f(2)
    var_1 = (2/time_1)*sigma_1-(1/time_1)*((f_1/strike[1])-1)*((f_1/strike[1])-1)

    ###Error Checking:
    #print "Near Term-"         
    #print "Near term Sigma: " + str(sigma_1)
    #print "Near term T(sec - not min): " + str(time_1)
    #print "Near term F: " + str(f_1)
    #print "Near Term variance:  " + str(var_1)

    n2 = n_t(d,0)
    n1 = n_t(d,5)
    n30 = 30*24*60
    n365 = 365*n30
    
    #Error Checking:
    #print "N2 for Next Term: " + str(n2)
    #print "N1 for Near Term: " + str(n1)
    #print "N30: " + str(n30)
    #print "N365: " + str(n365)

    VOX = 100*((time_1*sigma_1*((n2-n30)/(n2-n1))+time_2*sigma_2*((n30-n1)/(n2-n1)))*n365/n30)**(1/2.0)
    print "The VOX is: " + str(VOX)

min_dif = []
strike = []
global check
check = False
global current
current = []
global previous
previous = []

while True:
    current = get_options(list(dates)[1])
    
    #Modify 1 to 0-5 for different option settlement dates 1==September
    date_cur = (list(dates)[1].encode("utf-8"))[:2]        
    weekly = int(date_cur)
    if(check):

        #Modify 1 to 0-5 different option settlement dates 1==September
        print (list(dates)[1].encode("utf-8"))
        get_values(current, previous, weekly)
        #record(d)
    previous = current
    check = True
    sleep(5*60)

