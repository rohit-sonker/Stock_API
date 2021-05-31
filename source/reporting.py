import pandas as pd
from pandas_datareader import data as web
import os
import numpy as np
from tqdm import tqdm

import sys
# sys.path.append("../")
sys.path.insert(1, '../')



from Technical_Indicators_master.indicator.indicators import EMA,RSI

def print_report(list_of_dict):
    for results in list_of_dict:
        # further reports
        print("******************************************************\n")
        print("\t\t",results['stock'])
        print("Latest date in data = ",results['latest_date'])
        print("Last Close = ",results['last_close'])
        print("Latest diff values in EMA7 (recent first) = ",results['current_lagdiff_EMA7'])
        print("Latest RSI = ",results['RSIs'][0])

        if(any(results['RSIs']>78.0)):
            print("!! WARN !! RSI Value crossed 78, watch for sell")
        elif(any(results['RSIs']<22.0)):
            print("!!WARN !! RSI Value below, watchout for buy")

        if(any(results['ema_7_21']<0)):
            print("!! WARN !! EMA 7 is below EMA 21, watch for sell")
        else:
            print("EMA7 is above EMA21")

        if(any(results['ema_21_50']<0)):
            print("!! WARN !! EMA 21 is below EMA 50, watch for sell !!!")
        else:
            print("EMA21 is above EMA50")
        print("\n")
        
        
if __name__ == "__main__":
    
    #set start date and path to portfolio as args
    
    start_date = "01-01-2020"
    
    path_to_portfolio = "../data/portfolio.txt"
    
    with open(path_to_portfolio,'r') as f:
        portfolio = f.read().splitlines() 
    
    portfolio = [x + '.NS' for x in portfolio]
    print("Stocks in portfolio = ", len(portfolio))
    
    all_results = []

    for stock in tqdm(portfolio):

        df = web.DataReader(stock, data_source='yahoo', start=start_date)
        df.reset_index(level=0, inplace=True)

        #metrics

        df = EMA(df, base = "Close", target = "EMA21", period = 21)
        df = EMA(df, base = "Close", target = "EMA7", period = 7)
        df = EMA(df, base = "Close", target = "EMA50", period = 50)
        df = RSI(df, base="Close", period=14)

        df2 = df.reindex(index=df.index[::-1])
        df2.reset_index(inplace = True)

        df2['difference_close'] = df2['Close'] - df2['Close'].shift(-1)
        df2['difference_EMA7'] = df2['EMA7'] - df2['EMA7'].shift(-1)

        results = {}
        results['stock'] = stock
        results['latest_date'] = df2.Date[0]
        results['last_close'] = np.round(df2.Close[0],2)
        results['current_lagdiff_close'] = np.round(df2.head(5).difference_close.values,2)
        results['current_lagdiff_EMA7'] = np.round(df2.head(5).difference_EMA7.values,2)
        results['RSIs'] = np.round(df2.head(5).RSI_14.values,2)
        results['ema_7_21'] = np.round(df2.head(5).EMA7 - df2.head(5).EMA21)
        results['ema_21_50'] = np.round(df2.head(5).EMA21 - df2.head(5).EMA50)

        #add to file
        all_results.append(results)
    
    
    #print report
    print_report(all_results)