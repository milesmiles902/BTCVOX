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

def record():
    global count
    global dates
    for d in dates:
        options_date = extract(exp_dat, d, u'instrumentName')
        options = extract(options_date, "0-P", u'instrumentName')
        options.extend(extract(options_date, "0-C", u'instrumentName'))
        df = store_options(options, d)
        df = store_bids_asks(options,df, d)
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

while True:
    date = extract_dates(exp_dat)
    check_dates(date)
    record()
    sleep(2*60*60)

