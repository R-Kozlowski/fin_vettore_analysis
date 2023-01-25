import os, bs4, time, send2trash, csv, smtplib, threading, requests, __future__
import pandas as pd
import numpy as np
import pandas_ta as ta
import urllib.request
from lxml import html
from datetime import datetime, date, time, timezone


#creating charts
import plotly.graph_objects as go
#from mpl_finance import candlestick_ohlc
import matplotlib.pyplot as plt

#linear regression calculation
from sklearn.linear_model import LinearRegression
from scipy.stats import linregress

#sending html attachment
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import email

#open check list txt file for user-program communication
check_list = open("F:\\PROGRAMOWANIE\\PYTHON\\AUTOMAT FOREX\\main_check_list.txt", 'w')

open_csv = open("F:\\PROGRAMOWANIE\\PYTHON\\AUTOMAT FOREX\\open_csv_status.txt", 'w')
open_csv.write('')
open_csv.close()

#open files direction
os.chdir("C:\\Users\\radek\\Downloads")

#finding exact file
for file in os.listdir('.'):
    if file.startswith('EURUSD_Candlestick_1_m_BID'):
        plik = file
        break

print(plik)

#send2trash.send2trash(plik)

check_list.write(str(plik) + ' - open\n')

#disable error for pandas - "SettingWithCopyWarning"
pd.options.mode.chained_assignment = None

table = pd.read_csv(plik, sep=',', decimal='.')


#building main dataframe
table = pd.DataFrame(table, columns=['Gmt time','Weekday','Day','Time',
                                    'Open','High','Low','Close','Volume',
                                    'Resistance','Support','Long Range Resistance','Long Range Support',
                                    'Candle','RSI','MACD','Signal line (MACD)','Buy_Signal_Price','Sell_Signal_Price',
                                    'lin_sup_5','slope_lin_sup_5','lin_sup_10','slope_lin_sup_10','lin_sup_15','slope_lin_sup_15',
                                     'lin_sup_25','slope_lin_sup_25','lin_sup_50','slope_lin_sup_50','lin_sup_75','slope_lin_sup_75',
                                     'lin_sup_100','slope_lin_sup_100',
                                    'lin_res_5','slope_lin_res_5','lin_res_10','slope_lin_res_10','lin_res_15','slope_lin_res_15',
                                     'lin_res_25','slope_lin_res_25','lin_res_50','slope_lin_res_50','lin_res_75','slope_lin_res_75',
                                     'lin_res_100','slope_lin_res_100',
                                     'adj_lr_sup_2','slope_adj_lr_sup_2','adj_lr_sup_5','slope_adj_lr_sup_5','adj_lr_sup_10','slope_adj_lr_sup_10',
                                     'adj_lr_sup_15','slope_adj_lr_sup_15','adj_lr_sup_20','slope_adj_lr_sup_20',
                                     'adj_lr_res_2','slope_adj_lr_res_2','adj_lr_res_5','slope_adj_lr_res_5','adj_lr_res_10','slope_adj_lr_res_10',
                                     'adj_lr_res_15','slope_adj_lr_res_15','adj_lr_res_20','slope_adj_lr_res_20',                                     
                                     'lr_sup_2','slope_lr_sup_2','lr_sup_5','slope_lr_sup_5','lr_sup_10','slope_lr_sup_10','lr_sup_15','slope_lr_sup_15','lr_sup_20','slope_lr_sup_20',
                                     'lr_res_2','slope_lr_res_2','lr_res_5','slope_lr_res_5','lr_res_10','slope_lr_res_10','lr_res_15','slope_lr_res_15','lr_res_20','slope_lr_res_20',
                                     'const_lr_sup_2','slope_const_lr_sup_2','const_lr_sup_5','slope_const_lr_sup_5','const_lr_sup_10',
                                     'slope_const_lr_sup_10','const_lr_sup_15','slope_const_lr_sup_15','const_lr_sup_20','slope_const_lr_sup_20',
                                     'const_lr_res_2','slope_const_lr_res_2','const_lr_res_5','slope_const_lr_res_5','const_lr_res_10',
                                     'slope_const_lr_res_10','const_lr_res_15','slope_const_lr_res_15','const_lr_res_20','slope_const_lr_res_20',
                                    'Signal','Price Action','Remarks'])
table["Weekday"] = pd.to_numeric(table["Weekday"], errors='coerce').fillna(0)
table["Day"] = pd.to_numeric(table["Day"], errors='coerce').fillna(0)
table["Time"] = pd.to_numeric(table["Time"], errors='coerce').fillna(0)
table["Candle"] = pd.to_numeric(table["Candle"], errors='coerce').fillna(0)
table["RSI"] = pd.to_numeric(table["RSI"], errors='coerce').fillna(0)
table["MACD"] = pd.to_numeric(table["MACD"], errors='coerce').fillna(0)
table["Resistance Top"] = pd.to_numeric(table["Resistance Top"], errors='coerce').fillna(0)
table["Support Top"] = pd.to_numeric(table["Support Top"], errors='coerce').fillna(0)
table["Signal"] = pd.to_numeric(table["Signal"], errors='coerce').fillna(0)
table["Price Action"] = pd.to_numeric(table["Price Action"], errors='coerce').fillna(0)
table["Remarks"] = pd.to_numeric(table["Remarks"], errors='coerce').fillna(0)

#delete GMT if this is the local time
#table['Local time'] = table['Local time'].map(lambda x: x.rstrip('GMT+0100'))

#changing first column to date format
table['Gmt time'] = pd.to_datetime(table['Gmt time'], format="%d.%m.%Y %H:%M:%S.000")

#fillin up Weekday column for day of the week from first column
table["Weekday"] = pd.to_datetime(table["Gmt time"]).dt.dayofweek
table = table.loc[table["Weekday"] !=5] #wyrzucam soboty

#separate date from first column
table['Day'] = [datetime.date(d) for d in table['Gmt time']]

#separate time from first column
table['Time'] = [datetime.time(d) for d in table['Gmt time']]

#delete the row for every time grater than 22:00 every Friday and lower than 22:00 for every Sunday
for time in table.index:
    czas = table['Time'][time].strftime('%H:%M')
    if czas > '22:00' and table['Weekday'][time] == 4 or czas < '22:00' and table['Weekday'][time] == 6:
        table = table.drop([time])

table.reset_index() #reindex df after delete the rows


check_list.write('change date values - ok.\n')

#come back to the main direction and saving there my file
os.chdir("F:\\PROGRAMOWANIE\\PYTHON\\AUTOMAT FOREX\\DATA")

table.to_excel("analiza_giełdowa.xlsx", sheet_name="Sheet1")





#NEW DATAFRAME FOR EVERY PERIOD OF TIME
#=============================================#


#creating table for eveery period of time
time_frame_list = [5,15,60] #list of periods


for time_shape in time_frame_list:
    table_min = pd.DataFrame(columns=['Gmt time','Weekday','Day','Time',
                                    'Open','High','Low','Close','Volume',
                                    'Resistance','Support','Long Range Resistance','Long Range Support',
                                    'Candle','RSI','MACD','Signal line (MACD)','Buy_Signal_Price','Sell_Signal_Price',
                                    'lin_sup_5','slope_lin_sup_5','lin_sup_10','slope_lin_sup_10','lin_sup_15','slope_lin_sup_15',
                                     'lin_sup_25','slope_lin_sup_25','lin_sup_50','slope_lin_sup_50','lin_sup_75','slope_lin_sup_75',
                                     'lin_sup_100','slope_lin_sup_100',
                                    'lin_res_5','slope_lin_res_5','lin_res_10','slope_lin_res_10','lin_res_15','slope_lin_res_15',
                                     'lin_res_25','slope_lin_res_25','lin_res_50','slope_lin_res_50','lin_res_75','slope_lin_res_75',
                                     'lin_res_100','slope_lin_res_100',
                                     'adj_lr_sup_2','slope_adj_lr_sup_2','adj_lr_sup_5','slope_adj_lr_sup_5','adj_lr_sup_10','slope_adj_lr_sup_10',
                                     'adj_lr_sup_15','slope_adj_lr_sup_15','adj_lr_sup_20','slope_adj_lr_sup_20',
                                     'adj_lr_res_2','slope_adj_lr_res_2','adj_lr_res_5','slope_adj_lr_res_5','adj_lr_res_10','slope_adj_lr_res_10',
                                     'adj_lr_res_15','slope_adj_lr_res_15','adj_lr_res_20','slope_adj_lr_res_20',                                     
                                     'lr_sup_2','slope_lr_sup_2','lr_sup_5','slope_lr_sup_5','lr_sup_10','slope_lr_sup_10','lr_sup_15','slope_lr_sup_15','lr_sup_20','slope_lr_sup_20',
                                     'lr_res_2','slope_lr_res_2','lr_res_5','slope_lr_res_5','lr_res_10','slope_lr_res_10','lr_res_15','slope_lr_res_15','lr_res_20','slope_lr_res_20',
                                     'const_lr_sup_2','slope_const_lr_sup_2','const_lr_sup_5','slope_const_lr_sup_5','const_lr_sup_10',
                                     'slope_const_lr_sup_10','const_lr_sup_15','slope_const_lr_sup_15','const_lr_sup_20','slope_const_lr_sup_20',
                                     'const_lr_res_2','slope_const_lr_res_2','const_lr_res_5','slope_const_lr_res_5','const_lr_res_10',
                                     'slope_const_lr_res_10','const_lr_res_15','slope_const_lr_res_15','const_lr_res_20','slope_const_lr_res_20',
                                    'Signal','Price Action','Remarks'])
    position = 0
    for row in table.index:
        try:
            temporary_df = table.copy().iloc[position:position+time_shape] #I specify a temporary dataframe from the original in the range of 5 min
            temporary_df.at[temporary_df.index[-1], 'Open'] = temporary_df['Open'].head(1) #opening price from the first line
            temporary_df.at[temporary_df.index[-1], 'High'] = temporary_df['High'].max() #maximum price from all rows
            temporary_df.at[temporary_df.index[-1], 'Low'] = temporary_df['Low'].min() #minimum price from all rows
            temporary_df.at[temporary_df.index[-1], 'Volume'] = temporary_df['Volume'].sum() #total volume from all rows
            temporary_df.at[temporary_df.index[-1], 'Time'] = temporary_df['Time'].iloc[0]
            #temporary_df['Volume'][4:] = temporary_df['Volume'].sum() #total volume from all rows
                
            table_min = pd.concat([table_min,temporary_df.tail(1)]) #merge tables to add a new row to table_5min
            position += time_shape
        except:
            break
    print(time_shape)
    #save each time interval in a separate file
    table_min.to_excel("analiza_giełdowa_"+ str(time_shape) +"min.xlsx", sheet_name="Sheet1")


check_list.write('create 5, 15, 60 min periods files - ok.\n')


#create a separate analysis for daily excel
days = table['Day'].loc[~table.duplicated(['Day'])] #I create a dataframe with individual days
days.reset_index() #resetuję nr wierszy
table_day = pd.DataFrame(columns=['Gmt time','Weekday','Day','Time',
                                    'Open','High','Low','Close','Volume',
                                    'Resistance','Support','Long Range Resistance','Long Range Support',
                                    'Candle','RSI','MACD','Signal line (MACD)','Buy_Signal_Price','Sell_Signal_Price',
                                    'lin_sup_5','slope_lin_sup_5','lin_sup_10','slope_lin_sup_10','lin_sup_15','slope_lin_sup_15',
                                     'lin_sup_25','slope_lin_sup_25','lin_sup_50','slope_lin_sup_50','lin_sup_75','slope_lin_sup_75',
                                     'lin_sup_100','slope_lin_sup_100',
                                    'lin_res_5','slope_lin_res_5','lin_res_10','slope_lin_res_10','lin_res_15','slope_lin_res_15',
                                     'lin_res_25','slope_lin_res_25','lin_res_50','slope_lin_res_50','lin_res_75','slope_lin_res_75',
                                     'lin_res_100','slope_lin_res_100',
                                     'adj_lr_sup_2','slope_adj_lr_sup_2','adj_lr_sup_5','slope_adj_lr_sup_5','adj_lr_sup_10','slope_adj_lr_sup_10',
                                     'adj_lr_sup_15','slope_adj_lr_sup_15','adj_lr_sup_20','slope_adj_lr_sup_20',
                                     'adj_lr_res_2','slope_adj_lr_res_2','adj_lr_res_5','slope_adj_lr_res_5','adj_lr_res_10','slope_adj_lr_res_10',
                                     'adj_lr_res_15','slope_adj_lr_res_15','adj_lr_res_20','slope_adj_lr_res_20',                                     
                                     'lr_sup_2','slope_lr_sup_2','lr_sup_5','slope_lr_sup_5','lr_sup_10','slope_lr_sup_10','lr_sup_15','slope_lr_sup_15','lr_sup_20','slope_lr_sup_20',
                                     'lr_res_2','slope_lr_res_2','lr_res_5','slope_lr_res_5','lr_res_10','slope_lr_res_10','lr_res_15','slope_lr_res_15','lr_res_20','slope_lr_res_20',
                                     'const_lr_sup_2','slope_const_lr_sup_2','const_lr_sup_5','slope_const_lr_sup_5','const_lr_sup_10',
                                     'slope_const_lr_sup_10','const_lr_sup_15','slope_const_lr_sup_15','const_lr_sup_20','slope_const_lr_sup_20',
                                     'const_lr_res_2','slope_const_lr_res_2','const_lr_res_5','slope_const_lr_res_5','const_lr_res_10',
                                     'slope_const_lr_res_10','const_lr_res_15','slope_const_lr_res_15','const_lr_res_20','slope_const_lr_res_20',
                                    'Signal','Price Action','Remarks'])

for day in days.index:
    temporary_df = table.copy().loc[table['Day'] == days[day]]
    temporary_df.at[temporary_df.index[-1], 'Open'] = temporary_df['Open'].head(1) #opening price from the first line
    temporary_df.at[temporary_df.index[-1], 'High'] = temporary_df['High'].max() #maximum price from all rows
    temporary_df.at[temporary_df.index[-1], 'Low'] = temporary_df['Low'].min() #minimum price from all rows
    temporary_df.at[temporary_df.index[-1], 'Volume'] = temporary_df['Volume'].sum() #total volume from all rows

    table_day = pd.concat([table_day,temporary_df.tail(1)]) #merge tables to add a new row to table_min

table_day = table_day.loc[table_day["Weekday"] !=0] #delete Sundays because they have weak performance of data
table_day.to_excel("analiza_giełdowa_dzienny.xlsx", sheet_name="Sheet1")

check_list.write('create daily period file - ok.\n')



#table.to_excel("analiza_giełdowa_2.xlsx", sheet_name="Sheet1")



#CALCULATIONS
#=============================================#

#add a description of the candle on the rise or fall for the RSI
table.loc[table['Open'] > table['Close'], 'Candle'] = 'falling'
table.loc[table['Open'] < table['Close'], 'Candle'] = 'growth'
table.loc[table['Open'] == table['Close'], 'Candle'] = 'no change'


#code below doesn't work because it finds vertices incorrectly
###looking for tops and bottoms
###'Resistance Top','Support Top'
##for i in table.index:
##    if table.loc[i]['Weekday'] >= 0: #delete Sundays
##        try: #try option to don't show an error with the first two lines
##            if table.loc[i-2]['Candle'] == 'falling' and (table.loc[i-2]['Open'] - table.loc[i-2]['Close']) > 0.00005:
##                if table.loc[i-1]['Candle'] == 'falling'  and (table.loc[i-1]['Open'] - table.loc[i-1]['Close']) > 0.00005:
##                    if table.loc[i+1]['Candle'] == 'growth' and (table.loc[i+1]['Close'] - table.loc[i+1]['Open']) > 0.00005:
##                        if table.loc[i+2]['Candle'] == 'growth' and (table.loc[i+2]['Close'] - table.loc[i+2]['Open']) > 0.00005:
##                            table.at[i, 'Support Top'] = table.loc[i-2:i+2]['Low'].min()
##                            print(table.loc[i-2:i+2]['Day'])
##                            print(table.loc[i-2:i+2]['Time'])
##                            print(table.loc[i]['Support Top'])
##                            
##            elif table.loc[i-2]['Candle'] == 'growth' and (table.loc[i-2]['Close'] - table.loc[i-2]['Open']) > 0.00005:
##                if table.loc[i-1]['Candle'] == 'growth' and (table.loc[i-1]['Close'] - table.loc[i-1]['Open']) > 0.00005:
##                    if table.loc[i+1]['Candle'] == 'falling' and (table.loc[i+1]['Open'] - table.loc[i+1]['Close']) > 0.00005:
##                        if table.loc[i+2]['Candle'] == 'falling' and (table.loc[i+2]['Open'] - table.loc[i+2]['Close']) > 0.00005:
##                            table.at[i, 'Resistance Top'] = table.loc[i-2:i+2]['High'].max()
##                            print(table.loc[i-2:i+2]['Day'])
##                            print(table.loc[i-2:i+2]['Time'])
##                            print(table.loc[i]['Resistance Top'])
##        except:
##            next




#TOPS AND BOTTOMS

#the idea is simple. I compare the first 2 values. Then the first with the third, then with the fourth, etc.
#until the price is less than the first. Then the program sees the top. I take the largest value.


#wykrywam punkty wierzchołków i dołków
for i in table.index:
    try:
        if table.loc[i-2]['Low']>table.loc[i]['Low'] and table.loc[i-1]['Low']>=table.loc[i]['Low'] and table.loc[i+1]['Low']>=table.loc[i]['Low'] and table.loc[i+2]['Low']>table.loc[i]['Low']:
            #to będzie mój Support
            indeks = table.loc[i-2:i+2]['Low'].idxmin()
            #jeśli następna wartość będzie taka sama to podaję następną żeby dobrze wyrysować funkcję
            if table.loc[indeks+1]['Low']==table.loc[indeks]['Low']:
                table.at[indeks+1, 'Support'] = table.loc[indeks+1]['Low']
            else:
                table.at[indeks, 'Support'] = table.loc[indeks]['Low']
        elif table.loc[i-2]['High']<table.loc[i]['High'] and table.loc[i-1]['High']<=table.loc[i]['High'] and table.loc[i+1]['High']<=table.loc[i]['High'] and table.loc[i+2]['High']<table.loc[i]['High']:
            #to będzie mój Resistance
            indeks = table.loc[i-2:i+2]['High'].idxmax()
            #jeśli następna wartość będzie taka sama to podaję następną żeby dobrze wyrysować funkcję
            if table.loc[indeks+1]['High']==table.loc[indeks]['High']:
                table.at[indeks+1, 'Resistance'] = table.loc[indeks+1]['High']
            else:
                table.at[indeks, 'Resistance'] = table.loc[indeks]['High']
    except:
        next




#V-LAMBDA CONCEPTION
#----------------------------------------#
#an innovative concept that assumes that a set of, for example, two Support and one Resistance 
#points forms a "Lambda formation", the slope of which can be measured by tilting the two Support points. 
#Such a function can be carried further and examined to see if subsequent points also resist it. 
#It gives then a solid basis for believing that it is a model trend line.

v_lambda_matrix = table[['Support','Resistance']].copy()
#v_lambda_matrix = v_lambda_matrix.dropna(how='all')
i = v_lambda_matrix.index[-1]
x3_last_position = i



#TODO
#this loop should be developed. It never leaving second while loop

while i>=0:
    i = x3_last_position
    if i < 0:
        print("mniejsze od 0")
        break
    #measure one, or the average of several right arms of the formation
    if pd.notna(v_lambda_matrix.loc[i]['Support'])==True:
        x1 = v_lambda_matrix.loc[i]['Support']
        x1_index = i
        y=1
        i=i-1
        if i < 0:
            print("mniejsze od 0")
            break
        while pd.notna(v_lambda_matrix.loc[i]['Resistance'])==False:
            print("prawa noga " + str(i))
            if pd.notna(v_lambda_matrix.loc[i]['Support'])==True:
                x1 = x1 + v_lambda_matrix.loc[i]['Support']
                y=y+1
            i=i-1
            if i < 0:
                print("mniejsze od 0")
                break
        x1=x1/y
        if i < 0:
            print("mniejsze od 0")
            break
        
        #measure one, or the average of several formation vertices and zero the y-number
        y = 0
        if pd.notna(v_lambda_matrix.loc[i]['Resistance'])==True and pd.notna(v_lambda_matrix.loc[i]['Resistance'])==True:
            x2 = v_lambda_matrix.loc[i]['Resistance']
            x3 = v_lambda_matrix.loc[i]['Support']
            x3_last_position = i
        else:
            while pd.notna(v_lambda_matrix.loc[i]['Support'])==False:
                print("wierzchołek " + str(i))
                if pd.notna(v_lambda_matrix.loc[i]['Resistance'])==True:
                    x2 = v_lambda_matrix.loc[i]['Resistance']
                    y=y+1
                i=i-1
                if i < 0:
                    print("mniejsze od 0")
                    break
            x2=x2/y
            if i < 0:
                print("mniejsze od 0")
                break

        
            #measure one, or the average of several left arms of the formation and zero the y-number
            y=0
            while pd.notna(v_lambda_matrix.loc[i]['Resistance'])==False:
                print("lewa noga " + str(i))
                if pd.notna(v_lambda_matrix.loc[i]['Support'])==True:
                    x3 = v_lambda_matrix.loc[i]['Support']
                    x3_last_position = i
                    y=y+1
                i=i-1
                if i < 0:
                    print("mniejsze od 0")
                    break
            x3=x3/y

        if x1 < x3:
            #rośnie
            table.loc[x3_last_position:x1_index,['V-Lambda']] = 1
        elif x1==x3:
            table.loc[x3_last_position:x1_index,['V-Lambda']] = 0
        elif x1 > x3:
            table.loc[x3_last_position:x1_index,['V-Lambda']] = -1
    else:
        x3_last_position = x3_last_position - 1
    x1=0; x2=0; x3=0




#LINEAR FUNCTION calculation
#----------------------------------------------#

#I have to provide 5 values:
#- x1, y1 - coordinates of the first vertex
#- x2, y2 - coordinates of the second vertex
#- x3 - line number for which I calculate where the linear function will run
#by calculating the price of y3, I can specify if the price is approaching a linear function or not
def price_from_linear_function(x1, y1, x2, y2, x3):
    print('\nLokalizacje punktów')
    print(str(x1) + ',' + str(y1))
    print(str(x2) + ',' + str(y2))
    a = (y2-y1)/(x2-x1) #calculating the slope a of a function
    b = y2-(a*x2) #calculating the b-value of the function
    y3 = (a*x3)+b
    return y3 #returns the price at the specified location
    
#counting the slope of the linear function and you need to compare this with the other line
def price_from_linear_function_check_canal(x1, y1, x2, y2):
    a = (y2-y1)/(x2-x1) #obliczam nachylenie a funkcji
    return a #zwraca nachylenie linii 


high_linear_model_price = 0
low_linear_model_price = 0
high1, high2 = table['High'].tail(5000).nlargest(2, keep = 'last') #finding the two highest, last values in a column
highest_table = table['High'].tail(500).nlargest(2, keep = 'last')
highest_index1, highest_index2 = highest_table.index #provides an index of the largest values

low1, low2 = table['Low'].tail(500).nsmallest(2, keep = 'last') #finding the two highest, last values in a column
lowest_table = table['High'].tail(500).nlargest(2, keep = 'last')
lowest_index1, lowest_index2 = highest_table.index #provides an index of the largest values

print(high1, high2)
print(low1, low2)



#first, I have to check the slope of the function. If the highest values fall then I check the maximum vertices.
#if they are growing then I measure the holes
if high1 > high2 or high1 == high2: #checking the slope of the function
    if high1 != high2: #excludes a horizontal line at the intersection of two vertices
        if highest_index1 > highest_index2:
            if highest_index1 - highest_index2 > 3: #limit of periods between which vertices can occur
                high_linear_model_price = price_from_linear_function(highest_index1, high1, highest_index2, high2, table['High'].tail(1).index)
        elif index1 < index2:
            if highest_index1 - highest_index2 < -3: #limit of periods between which vertices can occur
                high_linear_model_price = price_from_linear_function(highest_index1, high1, highest_index2, high2, table['High'].tail(1).index)
    else: #if the highest values are equal it gives the price of one of them as the price on which there is a horizontal line
        high_linear_model_price = high1
elif low1 < low2 or low1 == low2: #if the function is increasing
    if low1 != low2: #detects the horizontal line at the intersection of two vertices
        if lowest_index1 > lowest_index2:
            if lowest_index1 - lowest_index2 > 3: #limit of the periods between which the holes may occur
                low_linear_model_price = price_from_linear_function(lowest_index1, lo1, lowest_index2, low2, table['High'].tail(1).index)
        elif lowest_index1 < lowest_index2:
            if lowest_index1 - lowest_index2 < -3: #limit on the periods between which the holes may occur
                low_linear_model_price = price_from_linear_function(lowest_index1, low1, lowest_index2, low2, table['High'].tail(1).index)
    else: #if the highest values are equal it gives the price of one of them as the price on which the horizontal line is
        low_linear_model_price = low1


print('high_linear_model_price - ' + str(high_linear_model_price) + '\n')
print('low_linear_model_price - ' + str(low_linear_model_price) + '\n')





#new model of LINEAR REGRESSION calculation
#-----------------------------------------------------------#
#the idea is to create linear regression predicted price for each row. This line should be adjusted to the largest/smallest 
#tops on the chart to show the trend on the chart, give the user information that last close price is close to this trend and predict future price.
#Anyhow it should give the user crucial information to help him in making investing decisions.


#calculations for SUPPORT/RESISTANCE
table = table.reset_index()

#giving a list for periods of times
list_of_ranges = [5,10,15,25,50,75,100]

for range in list_of_ranges:

    #calculation for Support points
    support_table = table[['Support']].copy().dropna(subset=['Support']).reset_index()
    support_table = support_table.tail(range)

    #adjusting linear function to 2 points
    while len(support_table)>2:
        slope, intercept, r_value, p_value, std_err = linregress(x=support_table['index'], y=support_table['Support'])
        support_table = support_table.loc[support_table['Support'] < slope * support_table['index'] + intercept]
    print('Support dla ' + str(range) + ' okresów:\n')
    print(support_table)
    print('---------------------')
    
    #giving ranges for the result table to exclude wrong data
    if not len(support_table) < 2:
        #reading position of the last, oldest index from where I can draw the funkction 
        indeks = support_table.iloc[0][0].astype(np.int64)
        slope, intercept, r_value, p_value, std_err = linregress(x=support_table['index'], y=support_table['Support'])
        #I calculate the prices on each line based on the calculated function
        table.iloc[indeks:, table.columns.get_loc('lin_sup_'+str(range))] = slope * table.iloc[indeks:, table.columns.get_loc('index')] + intercept
        #I give the slope of the function for later commentary on whether the trend is downward/upward
        table.iloc[indeks:, table.columns.get_loc('slope_lin_sup_'+str(range))] = format(slope, '.10f')

    #calculations for Resistance points
    resistance_table = table[['Resistance']].copy().dropna(subset=['Resistance']).reset_index()
    resistance_table = resistance_table.tail(range).copy()

    #adjusting 2 largest values
    while len(resistance_table)>2:
        slope, intercept, r_value, p_value, std_err = linregress(x=resistance_table['index'], y=resistance_table['Resistance'])
        resistance_table = resistance_table.loc[resistance_table['Resistance'] > slope * resistance_table['index'] + intercept]
    print('Resistance dla ' + str(range) + ' okresów:\n')
    print(resistance_table)
    print('---------------------')
    
    #limitation to the resulting table because sometimes it gives one row that causes errors and will overwrite the slope with an incorrect value
    if not len(resistance_table) < 2:
        #taking the index of the oldest position from which I will draw the function
        indeks = resistance_table.iloc[0][0].astype(np.int64)
        #I determine the function and complete the master table on the basis of the obtained slope and intercept values   
        slope, intercept, r_value, p_value, std_err = linregress(x=resistance_table['index'], y=resistance_table['Resistance'])
        #I calculate the prices on each line based on the calculated function
        table.iloc[indeks:, table.columns.get_loc('lin_res_'+str(range))] = slope * table.iloc[indeks:, table.columns.get_loc('index')] + intercept
        #I give the slope of the function for later commentary on whether the trend is downward/upward
        table.iloc[indeks:, table.columns.get_loc('slope_lin_res_'+str(range))] = format(slope, '.10f')




#calculations for LONG RANGE SUPPORT/RESISTANCE

#giving a new list of periods I will look at from the end of the table. Range smaller because the points are rarer
list_of_ranges = [2,10,20]

for range in list_of_ranges:
    #Support
    support_table = table[['Long Range Support']].copy().dropna(subset=['Long Range Support']).reset_index()
    support_table = support_table.tail(range)

    #leaving the 2 smallest prices in the table to match the function
    support_table = support_table.loc[support_table['Long Range Support'].nsmallest(2).index]

    #I take the index of the oldest position from which I will draw the function
    indeks = support_table.iloc[0][0].astype(np.int64)
    
    slope, intercept, r_value, p_value, std_err = linregress(x=support_table['index'], y=support_table['Long Range Support'])
    table.iloc[indeks:, table.columns.get_loc('lr_sup_'+str(range))] = slope * table.iloc[indeks:, table.columns.get_loc('index')] + intercept
    table.iloc[indeks:, table.columns.get_loc('slope_lr_sup_'+str(range))] = format(slope, '.10f')

    #Resistance
    resistance_table = table[['Long Range Resistance']].copy().dropna(subset=['Long Range Resistance']).reset_index()
    resistance_table = resistance_table.tail(range)

    #leaving the 2 largest prices in the table to match the function
    resistance_table = resistance_table.loc[resistance_table['Long Range Resistance'].nlargest(2).index]
    
    #I take the index of the oldest position from which I will draw the function
    indeks = resistance_table.iloc[0][0].astype(np.int64)

    #I determine the function and complete the master table on the basis of the obtained slope and intercept values  
    slope, intercept, r_value, p_value, std_err = linregress(x=resistance_table['index'], y=resistance_table['Long Range Resistance'])
    table.iloc[indeks:, table.columns.get_loc('lr_res_'+str(range))] = slope * table.iloc[indeks:, table.columns.get_loc('index')] + intercept
    table.iloc[indeks:, table.columns.get_loc('slope_lr_res_'+str(range))] = format(slope, '.10f')






#calculations for LONG RANGE SUPPORT/RESISTANCE with a fixed first hole/top
#the principle here is to see if the price is approaching a trend line, or if the price has recently pierced such a trend line!!!

#I give a new list of periods with which I will look from the end of the table to the past. The first position 2 for the last two positions
list_of_ranges = [2,5,10,15,20]

for range in list_of_ranges:
    
    #SUPPORT
    support_table = table[['Long Range Support']].copy().dropna(subset=['Long Range Support']).reset_index()
    support_table = support_table.tail(range)
    
    #RESISTANCE
    resistance_table = table[['Long Range Resistance']].copy().dropna(subset=['Long Range Resistance']).reset_index()
    resistance_table = resistance_table.tail(range)
    
    #first scenario if the range includes only 2 values
    if range == 2:
        
        #SUPPORT
        indeks = support_table.iloc[0][0].astype(np.int64)
        #I determine the function and complete the master table on the basis of the obtained slope and intercept values  
        slope, intercept, r_value, p_value, std_err = linregress(x=support_table['index'], y=support_table['Long Range Support'])
        table.iloc[indeks:, table.columns.get_loc('const_lr_sup_'+str(range))] = slope * table.iloc[indeks:, table.columns.get_loc('index')] + intercept
        table.iloc[indeks:, table.columns.get_loc('slope_const_lr_sup_'+str(range))] = format(slope, '.10f')

        #RESISTANCE
        indeks = resistance_table.iloc[0][0].astype(np.int64)
        #I determine the function and complete the master table on the basis of the obtained slope and intercept values    
        slope, intercept, r_value, p_value, std_err = linregress(x=resistance_table['index'], y=resistance_table['Long Range Resistance'])
        table.iloc[indeks:, table.columns.get_loc('const_lr_res_'+str(range))] = slope * table.iloc[indeks:, table.columns.get_loc('index')] + intercept
        table.iloc[indeks:, table.columns.get_loc('slope_const_lr_res_'+str(range))] = format(slope, '.10f')

    #if the table has more than 2 values
    else:

        #SUPPORT
        #selecting the last row and then create a table without the last row
        last_row = support_table.tail(1)
        support_table = support_table.iloc[:-1]
        #I leave the line with the smallest value
        support_table = support_table.loc[support_table['Long Range Support'].nsmallest(1).index]
        #merge the received row with the last row downloaded earlier to last_row
        support_table = pd.concat([support_table,last_row])
        print('\nponiżej połączone Long Range Support z wartością stałą w okresie - '+ str(range))
        print(support_table)
        #taking the index from which I will feed the data for the linear function to the last line
        indeks = support_table.iloc[0][0].astype(np.int64)
        #calculate the parameters of a linear function
        slope, intercept, r_value, p_value, std_err = linregress(x=support_table['index'], y=support_table['Long Range Support'])
        table.iloc[indeks:, table.columns.get_loc('const_lr_sup_'+str(range))] = slope * table.iloc[indeks:, table.columns.get_loc('index')] + intercept
        table.iloc[indeks:, table.columns.get_loc('slope_const_lr_sup_'+str(range))] = format(slope, '.10f')

        #RESISTANCE
        #selecting the last row and then create a table without the last row
        last_row = resistance_table.tail(1)
        resistance_table = resistance_table.iloc[:-1]
        #leaving the line with the smallest value
        resistance_table = resistance_table.loc[resistance_table['Long Range Resistance'].nlargest(1).index]
        #merge the received row with the last row downloaded earlier to last_row
        resistance_table = pd.concat([resistance_table,last_row])
        print('\nponiżej połączone Long Range Resistance z wartością stałą w okresie - '+ str(range))
        print(resistance_table)
        #taking the index from which I will feed the data for the linear function to the last line
        indeks = resistance_table.iloc[0][0].astype(np.int64)
        #calculate the parameters of a linear function
        slope, intercept, r_value, p_value, std_err = linregress(x=resistance_table['index'], y=resistance_table['Long Range Resistance'])
        table.iloc[indeks:, table.columns.get_loc('const_lr_res_'+str(range))] = slope * table.iloc[indeks:, table.columns.get_loc('index')] + intercept
        table.iloc[indeks:, table.columns.get_loc('slope_const_lr_res_'+str(range))] = format(slope, '.10f')


#deleting index column
table = table.drop('index', axis=1)



#filtering wrong linear regression lines
#-------------------------------------#
#The lines based on the first vertex have the bug that they intersect other holes/vertices.
#They must be removed, so I check if whichever value intersects the graph and replace entire column with NaN value


#list of columns to check (SUPPORT)
list_of_columns = ['const_lr_sup_2','const_lr_sup_5','const_lr_sup_10','const_lr_sup_15','const_lr_sup_20']

#loop for every column
for column in list_of_columns:
    #mazzle
    muzzle = len(table[table[column] > table.Low])
    #if it has found at least one intersection it converts that column and slope to NaN
    if muzzle > 1:
        table[column] = np.nan
        table['slope_' + str(column)] = np.nan


#list of columns to check (RESISTANCE)
list_of_columns = ['const_lr_res_2','const_lr_res_5','const_lr_res_10','const_lr_res_15','const_lr_res_20']

#loop for every column
for column in list_of_columns:
    #mazzle
    muzzle = len(table[table[column] < table.High])
    #if it has found at least one intersection it converts that column and slope to NaN
    if muzzle > 1:
        table[column] = np.nan
        table['slope_' + str(column)] = np.nan





#deleting wrong linear regression lines based on last values
#------------------------------------------------------------------#

#giving list of ranges to check
list_of_ranges = [10,15,30,45,60,120,240,480]

for frame in list_of_ranges:
    if frame <= 30:
        temp_table = table.tail(5)
        list_of_columns = ['lin_sup_5','lin_sup_10','lin_sup_15']
        for column in list_of_columns:
            muzzle = len(temp_table[temp_table[column] > temp_table.Low])
            if muzzle == 5:
                table[column] = np.nan
                table['slope_' + str(column)] = np.nan                
        list_of_columns = ['lin_res_5','lin_res_10','lin_res_15']
        for column in list_of_columns:
            muzzle = len(temp_table[temp_table[column] < temp_table.High])
            if muzzle == 5:
                table[column] = np.nan
                table['slope_' + str(column)] = np.nan              
    else:
        temp_table = table.tail(10)
        list_of_columns = ['lin_sup_25','lin_sup_50','lin_sup_75','lin_sup_100',
                           'lr_sup_2','lr_sup_5','lr_sup_10','lr_sup_15','lr_sup_20',
                           'adj_lr_sup_2','adj_lr_sup_5','adj_lr_sup_10','adj_lr_sup_15','adj_lr_sup_20']
        for column in list_of_columns:
            muzzle = len(temp_table[temp_table[column] > temp_table.Low])
            if muzzle == 10:
                table[column] = np.nan
                table['slope_' + str(column)] = np.nan                
        list_of_columns = ['lin_res_25','lin_res_50','lin_res_75','lin_res_100',
                           'lr_res_2','lr_res_5','lr_res_10','lr_res_15','lr_res_20',
                           'adj_lr_res_2','adj_lr_res_5','adj_lr_res_10','adj_lr_res_15','adj_lr_res_20']
        for column in list_of_columns:
            muzzle = len(temp_table[temp_table[column] < temp_table.High])
            if muzzle == 10:
                table[column] = np.nan
                table['slope_' + str(column)] = np.nan          



#The next condition examines all the rest of the function to see if it has crossed the graph. It only checks all above the last 15 minutes


#I give the end of the table first, and then without the last 5 rows
temp_table = table.tail(500)
temp_table = temp_table.head(500-5)

#Support
list_of_columns = ['lin_sup_5','lin_sup_10','lin_sup_15','lin_sup_25','lin_sup_50','lin_sup_75','lin_sup_100',
                   'lr_sup_2','lr_sup_5','lr_sup_10','lr_sup_15','lr_sup_20',
                   'adj_lr_sup_2','adj_lr_sup_5','adj_lr_sup_10','adj_lr_sup_15','adj_lr_sup_20']
for column in list_of_columns:
    muzzle = len(temp_table[temp_table[column] > temp_table.Low])
    if muzzle > 5:
        table[column] = np.nan
        table['slope_' + str(column)] = np.nan

#Resistance
list_of_columns = ['lin_res_5','lin_res_10','lin_res_15','lin_res_25','lin_res_50','lin_res_75','lin_res_100',
                   'lr_res_2','lr_res_5','lr_res_10','lr_res_15','lr_res_20',
                   'adj_lr_res_2','adj_lr_res_5','adj_lr_res_10','adj_lr_res_15','adj_lr_res_20']
for column in list_of_columns:
    muzzle = len(temp_table[temp_table[column] < temp_table.High])
    if muzzle > 5:
        table[column] = np.nan
        table['slope_' + str(column)] = np.nan



        


#CHARTS
#---------------------------------------#
#building the chart for each period of time from the given list (list_of_ranges) based on last calculations for linear regression model


#list time ranges ((minutes)) for each chart
list_of_ranges = [25,50,100,150,200,400,1000]

for i in list_of_ranges:

    #creating temporary table with last rows (fresh data). Period is given from the list as "i"
    temp_table = table.tail(i).copy()
    
    #creating the chart
    figure = go.Figure()
    
    #adding columns for candlestick chart (x - date time index)
    figure.add_trace(go.Candlestick(x=temp_table.index,low=temp_table['Low'],high=temp_table['High'],close=temp_table['Close'],open=temp_table['Open'],increasing_line_color='orange',decreasing_line_color='black'))

    #depending on the given range of minutes, I combine certain indicators on one chart
    if i == 25 or i == 50:
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_5'],mode='lines', line=dict(color='blue', width=1),name='Linear Regresion (5 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_5'],mode='lines', line=dict(color='red', width=1),name='Linear Regresion (5 supports)',showlegend=True))
    elif i == 100:
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_5'],mode='lines', line=dict(color='blue', width=1),name='Linear Regresion (5 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_5'],mode='lines', line=dict(color='red', width=1),name='Linear Regresion (5 supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_10'],mode='lines', line=dict(color='blue', width=2),name='Linear Regresion (10 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_10'],mode='lines', line=dict(color='red', width=2),name='Linear Regresion (10 supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_res_2'],mode='lines', line=dict(color='royalblue', width=3),name='Linear Regresion (2 adj lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_sup_2'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (2 adj lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_res_2'],mode='lines', line=dict(color='royalblue', width=3),name='Linear Regresion (2 lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_sup_2'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (2 lr supports)',showlegend=True))        
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_res_2'],mode='lines', line=dict(color='royalblue', width=3),name='Linear Regresion (2 const lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_sup_2'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (2 const lr supports)',showlegend=True))
        try:
            figure.add_hrect(y0=temp_table['Long Range Resistance'].max()-0.00004, y1=temp_table['Long Range Resistance'].max()+0.00004, line_width=0, fillcolor="orange", opacity=0.2)
            figure.add_hrect(y0=temp_table['Long Range Support'].min()-0.00004, y1=temp_table['Long Range Support'].min()+0.00004, line_width=0, fillcolor="orange", opacity=0.2)
        except:
            continue
    elif i == 150:
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_10'],mode='lines', line=dict(color='blue', width=1),name='Linear Regresion (10 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_10'],mode='lines', line=dict(color='red', width=1),name='Linear Regresion (10 supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_15'],mode='lines', line=dict(color='blue', width=2),name='Linear Regresion (15 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_15'],mode='lines', line=dict(color='red', width=2),name='Linear Regresion (15 supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_res_2'],mode='lines', line=dict(color='royalblue', width=3),name='Linear Regresion (2 adj lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_sup_2'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (2 adj lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_res_2'],mode='lines', line=dict(color='royalblue', width=3),name='Linear Regresion (2 lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_sup_2'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (2 lr supports)',showlegend=True))        
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_res_2'],mode='lines', line=dict(color='royalblue', width=3),name='Linear Regresion (2 const lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_sup_2'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (2 const lr supports)',showlegend=True))
        try:
            figure.add_hrect(y0=temp_table['Long Range Resistance'].max()-0.00004, y1=temp_table['Long Range Resistance'].max()+0.00004, line_width=0, fillcolor="orange", opacity=0.2)
            figure.add_hrect(y0=temp_table['Long Range Support'].min()-0.00004, y1=temp_table['Long Range Support'].min()+0.00004, line_width=0, fillcolor="orange", opacity=0.2)
        except:
            continue
    elif i == 200 or i == 400:
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_25'],mode='lines', line=dict(color='blue', width=1),name='Linear Regresion (25 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_25'],mode='lines', line=dict(color='red', width=1),name='Linear Regresion (25 supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_50'],mode='lines', line=dict(color='blue', width=1),name='Linear Regresion (50 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_50'],mode='lines', line=dict(color='red', width=1),name='Linear Regresion (50 supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_res_2'],mode='lines', line=dict(color='green', width=2),name='Linear Regresion (2 adj lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_sup_2'],mode='lines', line=dict(color='firebrick', width=2),name='Linear Regresion (2 adjlr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_res_5'],mode='lines', line=dict(color='green', width=2),name='Linear Regresion (5 adj lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_sup_5'],mode='lines', line=dict(color='firebrick', width=2),name='Linear Regresion (5 adj lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_res_2'],mode='lines', line=dict(color='green', width=3),name='Linear Regresion (2 lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_sup_2'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (2 lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_res_5'],mode='lines', line=dict(color='green', width=3),name='Linear Regresion (5 lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_sup_5'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (5 lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_res_2'],mode='lines', line=dict(color='green', width=4),name='Linear Regresion (2 const lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_sup_2'],mode='lines', line=dict(color='firebrick', width=4),name='Linear Regresion (2 const lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_res_5'],mode='lines', line=dict(color='green', width=4),name='Linear Regresion (5 const lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_sup_5'],mode='lines', line=dict(color='firebrick', width=4),name='Linear Regresion (5 const lr supports)',showlegend=True))
        try:
            figure.add_hrect(y0=temp_table['Long Range Resistance'].max()-0.00004, y1=temp_table['Long Range Resistance'].max()+0.00004, line_width=0, fillcolor="orange", opacity=0.2)
            figure.add_hrect(y0=temp_table['Long Range Support'].min()-0.00004, y1=temp_table['Long Range Support'].min()+0.00004, line_width=0, fillcolor="orange", opacity=0.2)
        except:
            continue
    elif i == 1000:
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_75'],mode='lines', line=dict(color='blue', width=1),name='Linear Regresion (75 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_75'],mode='lines', line=dict(color='red', width=1),name='Linear Regresion (75 supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_res_100'],mode='lines', line=dict(color='blue', width=1),name='Linear Regresion (100 resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lin_sup_100'],mode='lines', line=dict(color='red', width=1),name='Linear Regresion (100 supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_res_10'],mode='lines', line=dict(color='green', width=1),name='Linear Regresion (10 adj lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_sup_10'],mode='lines', line=dict(color='firebrick', width=2),name='Linear Regresion (10 adjlr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_res_15'],mode='lines', line=dict(color='green', width=2),name='Linear Regresion (15 adj lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['adj_lr_sup_15'],mode='lines', line=dict(color='firebrick', width=2),name='Linear Regresion (15 adj lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_res_10'],mode='lines', line=dict(color='green', width=3),name='Linear Regresion (10 lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_sup_10'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (10 lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_res_15'],mode='lines', line=dict(color='green', width=3),name='Linear Regresion (15 lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['lr_sup_15'],mode='lines', line=dict(color='firebrick', width=3),name='Linear Regresion (15 lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_res_10'],mode='lines', line=dict(color='green', width=4),name='Linear Regresion (10 const lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_sup_10'],mode='lines', line=dict(color='firebrick', width=4),name='Linear Regresion (10 const lr supports)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_res_15'],mode='lines', line=dict(color='green', width=4),name='Linear Regresion (15 const lr resistances)',showlegend=True))
        figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['const_lr_sup_15'],mode='lines', line=dict(color='firebrick', width=4),name='Linear Regresion (15 const lr supports)',showlegend=True))
        try:
            figure.add_hrect(y0=temp_table['Long Range Resistance'].max()-0.00005, y1=temp_table['Long Range Resistance'].max()+0.00005, line_width=0, fillcolor="orange", opacity=0.3)
            figure.add_hrect(y0=temp_table['Long Range Support'].min()-0.00005, y1=temp_table['Long Range Support'].min()+0.00005, line_width=0, fillcolor="orange", opacity=0.3)
        except:
            continue
    #add Support and Resistance points on the chart
    figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['Support'],mode='markers',showlegend=True))
    figure.add_trace(go.Scatter(x=temp_table.index,y=temp_table['Resistance'],mode='markers',showlegend=True))
    #specify axis titles and exclude from showing an additional chart under the graph
    figure.update_layout(title='EUR/USD price (last ' + str(i) + ' minutes)',yaxis_title='Price',xaxis_title='Date',xaxis_rangeslider_visible=False)
    figure.show()
    
    
    
    
   
#second method with matplotlib library
#zastosowałem 2 różne sposoby. Pierwszy to tworzę oddzielnie wykres świecowy i MACD.
#drugi sposób to łączę je w jeden plik jpg


#resetuję index żeby nie wysypało wykresu
table = table.reset_index()


#1. sposób
#podaję listę zakresów. Do 300 ponieważ powyżej nic nie widać
list_of_ranges = [25,50,100,150,200,300]

#wyznaczam listę z nazwami obrazów wykresów
list_of_img = []


for i in list_of_ranges:
    #tworzę tymczasową tabelę dla wykresów
    temp_table = table.tail(i).copy()

    #określam rozmiar wykresu
    plt.figure(figsize=(14.2, 5.5))

    #w zależności od zakresów dokładam konkretne linie trendu
    if i < 100:
        #tworzę słownik dla każdej wartości (każda kolumna ma 2 wartości)
        slownik = {('lin_sup_5'):(1,'red'), ('lin_res_5'):(1,'blue'),
                   ('adj_lr_res_2'):(2,'red'), ('adj_lr_sup_2'):(2,'blue'),
                   ('lr_res_2'):(2,'red'), ('lr_sup_2'):(2,'blue'),
                   ('const_lr_res_2'):(2,'red'), ('const_lr_sup_2'):(2,'blue')}
        #pętla po wszystkich elementach słownika
        for column,(ii,jj) in slownik.items():
            plt.scatter(temp_table.index, temp_table[column], s=ii, color=jj, linewidths=0)
            plt.plot(temp_table[column], label=column)
            
    elif i == 100:
        #tworzę słownik dla każdej wartości (każda kolumna ma 2 wartości)
        slownik = {('lin_sup_10'):(1,'red'), ('lin_res_10'):(1,'blue'),
                   ('lin_sup_15'):(2,'brown'), ('lin_res_15'):(2,'green'),
                   ('adj_lr_res_2'):(3,'red'), ('adj_lr_sup_2'):(3,'blue'),
                   ('lr_res_2'):(3,'red'), ('lr_sup_2'):(3,'blue'),
                   ('const_lr_res_2'):(3,'red'), ('const_lr_sup_2'):(3,'blue')}
        #pętla po wszystkich elementach słownika
        for column,(ii,jj) in slownik.items():
            plt.scatter(temp_table.index, temp_table[column], s=ii, color=jj, linewidths=0)
            plt.plot(temp_table[column], label=column)
            
    elif i == 150 or i == 200:
        #tworzę słownik dla każdej wartości (każda kolumna ma 2 wartości)
        slownik = {('lin_sup_15'):(1,'red'), ('lin_res_15'):(1,'blue'),
                   ('lin_sup_25'):(2,'brown'), ('lin_res_25'):(2,'green'),
                   ('adj_lr_res_2'):(3,'red'), ('adj_lr_sup_2'):(3,'blue'),
                   ('adj_lr_res_5'):(4,'red'), ('adj_lr_sup_5'):(4,'blue'),
                   ('lr_res_2'):(3,'red'), ('lr_sup_2'):(3,'blue'),
                   ('lr_res_5'):(4,'red'), ('lr_sup_5'):(4,'blue'),                   
                   ('const_lr_res_2'):(3,'red'), ('const_lr_sup_2'):(3,'blue'),
                   ('const_lr_res_5'):(4,'red'), ('const_lr_sup_5'):(4,'blue')}
        #pętla po wszystkich elementach słownika
        for column,(ii,jj) in slownik.items():
            plt.scatter(temp_table.index, temp_table[column], s=ii, color=jj, linewidths=0)
            plt.plot(temp_table[column], label=column)      

    elif i > 200:
        #tworzę słownik dla każdej wartości (każda kolumna ma 2 wartości)
        slownik = {('lin_sup_25'):(1,'red'), ('lin_res_25'):(1,'blue'),
                   ('lin_sup_50'):(2,'brown'), ('lin_res_50'):(2,'green'),
                   ('adj_lr_res_2'):(3,'red'), ('adj_lr_sup_2'):(3,'blue'),
                   ('adj_lr_res_5'):(4,'red'), ('adj_lr_sup_5'):(4,'blue'),
                   ('lr_res_2'):(3,'red'), ('lr_sup_2'):(3,'blue'),
                   ('lr_res_5'):(4,'red'), ('lr_sup_5'):(4,'blue'),
                   ('const_lr_res_2'):(3,'red'), ('const_lr_sup_2'):(3,'blue'),
                   ('const_lr_res_5'):(4,'red'), ('const_lr_sup_5'):(4,'blue')}
        #pętla po wszystkich elementach słownika
        for column,(ii,jj) in slownik.items():
            plt.scatter(temp_table.index, temp_table[column], s=ii, color=jj, linewidths=0)
            plt.plot(temp_table[column], label=column)

    #rysuję wykres świecowy
    up = temp_table[temp_table.Close >= temp_table.Open]
    down = temp_table[temp_table.Close < temp_table.Open]
    width = 0.9
    width2 = .07
    col1 = 'black'
    col2 = 'steelblue'
    plt.bar(up.index, up.Close-up.Open, width, bottom=up.Open, color=col1)
    plt.bar(up.index, up.High-up.Close, width2, bottom=up.Close, color=col1)
    plt.bar(up.index, up.Low-up.Open, width2, bottom=up.Open, color=col1)
    plt.bar(down.index, down.Close-down.Open, width, bottom=down.Open, color=col2)
    plt.bar(down.index, down.High-down.Open, width2, bottom=down.Open, color=col2)
    plt.bar(down.index, down.Low-down.Close, width2, bottom=down.Close, color=col2)

    #zmieniam ustawienie tekstu opisu osi x
    plt.xticks(rotation=30, ha='right')
    #generuję plik jpg
    plt.savefig("fin_vettore"+str(i)+".jpg")



    #MACD
    #obliczenie short EMA
    shortEMA = temp_table.Close.ewm(span=12, adjust=False).mean()
    #obliczenie long EMA
    longEMA = temp_table.Close.ewm(span=26, adjust=False).mean()
    #obliczenie linii MACD
    MACD = shortEMA - longEMA
    #obliczenie linii sygnału
    signal = MACD.ewm(span=9, adjust=False).mean()

    #budowanie wyrkesu
    #określam ten sam rozmiar co wykresu świecowego żeby zmieśły się jeden pod drugim
    plt.figure(figsize=(14.2, 5.5))
    plt.plot(temp_table.index, MACD, label='MACD', color='black', alpha=0.75) #alpha oznacza przymglenie linii
    plt.plot(temp_table.index, signal, label='Signal line', color='blue', alpha=0.35) #alpha oznacza przymglenie linii
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.savefig("MACD "+str(i)+".jpg")




    #2. sposób
    fig, axs = plt.subplots(3, 1, figsize=(14.2, 8),gridspec_kw={'height_ratios': [4, 1, 1]})

    
    #based on given period of time I'm building one chart with 3 inter-charts (candles, MACD, RSI)
    if i < 100:
        #I create a dictionary for each value (each column has 2 values)
        slownik = {('lin_sup_5'):(1,'red'), ('lin_res_5'):(1,'blue'),
                   ('adj_lr_res_2'):(2,'red'), ('adj_lr_sup_2'):(2,'blue'),
                   ('lr_res_2'):(2,'red'), ('lr_sup_2'):(2,'blue'),
                   ('const_lr_res_2'):(2,'red'), ('const_lr_sup_2'):(2,'blue')}
        #lopp on every value in the dictionary
        for column,(ii,jj) in slownik.items():
            axs[0].scatter(temp_table.index, temp_table[column], s=ii, color=jj, linewidths=0)
            axs[0].plot(temp_table[column], label=column, alpha=0.55)
            
    elif i == 100:
        #I create a dictionary for each value (each column has 2 values)
        slownik = {('lin_sup_10'):(1,'red'), ('lin_res_10'):(1,'blue'),
                   ('lin_sup_15'):(2,'brown'), ('lin_res_15'):(2,'green'),
                   ('adj_lr_res_2'):(3,'red'), ('adj_lr_sup_2'):(3,'blue'),
                   ('lr_res_2'):(3,'red'), ('lr_sup_2'):(3,'blue'),
                   ('const_lr_res_2'):(3,'red'), ('const_lr_sup_2'):(3,'blue')}
        #lopp on every value in the dictionary
        for column,(ii,jj) in slownik.items():
            axs[0].scatter(temp_table.index, temp_table[column], s=ii, color=jj, linewidths=0)
            axs[0].plot(temp_table[column], label=column, alpha=0.55)
            
    elif i == 150 or i == 200:
        #I create a dictionary for each value (each column has 2 values)
        slownik = {('lin_sup_15'):(1,'red'), ('lin_res_15'):(1,'blue'),
                   ('lin_sup_25'):(2,'brown'), ('lin_res_25'):(2,'green'),
                   ('adj_lr_res_2'):(3,'red'), ('adj_lr_sup_2'):(3,'blue'),
                   ('adj_lr_res_5'):(4,'red'), ('adj_lr_sup_5'):(4,'blue'),
                   ('lr_res_2'):(3,'red'), ('lr_sup_2'):(3,'blue'),
                   ('lr_res_5'):(4,'red'), ('lr_sup_5'):(4,'blue'),                   
                   ('const_lr_res_2'):(3,'red'), ('const_lr_sup_2'):(3,'blue'),
                   ('const_lr_res_5'):(4,'red'), ('const_lr_sup_5'):(4,'blue')}
        #lopp on every value in the dictionary
        for column,(ii,jj) in slownik.items():
            axs[0].scatter(temp_table.index, temp_table[column], s=ii, color=jj, linewidths=0)
            axs[0].plot(temp_table[column], label=column, alpha=0.55)      

    elif i > 200:
        #I create a dictionary for each value (each column has 2 values)
        slownik = {('lin_sup_25'):(1,'red'), ('lin_res_25'):(1,'blue'),
                   ('lin_sup_50'):(2,'brown'), ('lin_res_50'):(2,'green'),
                   ('adj_lr_res_2'):(3,'red'), ('adj_lr_sup_2'):(3,'blue'),
                   ('adj_lr_res_5'):(4,'red'), ('adj_lr_sup_5'):(4,'blue'),
                   ('lr_res_2'):(3,'red'), ('lr_sup_2'):(3,'blue'),
                   ('lr_res_5'):(4,'red'), ('lr_sup_5'):(4,'blue'),
                   ('const_lr_res_2'):(3,'red'), ('const_lr_sup_2'):(3,'blue'),
                   ('const_lr_res_5'):(4,'red'), ('const_lr_sup_5'):(4,'blue')}
        #lopp on every value in the dictionary
        for column,(ii,jj) in slownik.items():
            axs[0].scatter(temp_table.index, temp_table[column], s=ii, color=jj, linewidths=0)
            axs[0].plot(temp_table[column], label=column, alpha=0.55)

    #creating candlestick chart
    up = temp_table[temp_table.Close >= temp_table.Open]
    down = temp_table[temp_table.Close < temp_table.Open]
    width = 0.9
    width2 = 0.15
    col1 = 'black'
    col2 = 'steelblue'
    axs[0].bar(up.index, up.Close-up.Open, width, bottom=up.Open, color=col1)
    axs[0].bar(up.index, up.High-up.Close, width2, bottom=up.Close, color=col1)
    axs[0].bar(up.index, up.Low-up.Open, width2, bottom=up.Open, color=col1)
    axs[0].bar(down.index, down.Close-down.Open, width, bottom=down.Open, color=col2)
    axs[0].bar(down.index, down.High-down.Open, width2, bottom=down.Open, color=col2)
    axs[0].bar(down.index, down.Low-down.Close, width2, bottom=down.Close, color=col2)
    for indeks in temp_table.index:
        axs[0].axvline(indeks,0,linewidth=0.1,zorder=0, clip_on=False)
    axs[0].set_title('EUR/USD (last ' + str(i) + ' minutes)')

    
    #MACD
    #short EMA
    shortEMA = temp_table.Close.ewm(span=12, adjust=False).mean()
    #long EMA
    longEMA = temp_table.Close.ewm(span=26, adjust=False).mean()
    #MACD line
    MACD = shortEMA - longEMA
    #signal line
    signal = MACD.ewm(span=9, adjust=False).mean()
    
    #creating the MACD chart
    axs[1].plot(temp_table['Gmt time'], MACD, label='MACD', color='black', alpha=0.75) #alpha oznacza przymglenie linii
    axs[1].plot(temp_table['Gmt time'], signal, label='Signal line', color='blue', alpha=0.35) #alpha oznacza przymglenie linii
    #axs[1].set_xticklabels(temp_table['Gmt time'],rotation=45)


    #RSI
    axs[2].plot(temp_table['Gmt time'], temp_table['RSI'], label='RSI', color='orange', alpha=0.55) #alpha oznacza przymglenie linii
    axs[2].axhline(0, linestyle='--', linewidth=0.1, color='white')
    axs[2].axhline(30, linestyle='--', linewidth=0.5, color='grey')
    axs[2].axhline(70, linestyle='--', linewidth=0.5, color='grey')
    axs[2].axhline(100, linestyle='--', linewidth=0.1, color='white')
    
    fig.tight_layout()
    plt.savefig("Candle + MACD "+str(i)+".jpg")

    #saving jpg file with the chart
    list_of_img.append("Candle + MACD "+str(i)+".jpg")






    






INDICATORS
#=======================================#

#all averages based on closing prices
#arithmetic mean
mean = table.loc[:,"Open"].mean()
#weighted average
average = np.average(table['Open'])

#simple moving average SMA
#----------------------------------------#
table['SMA9'] = table['Close'].rolling(window=9).mean() #9-period

#weighted moving average WMA
#----------------------------------------#
weights = np.array([0.1, 0.2, 0.3, 0.4]) #weights for subsequent periods
table['WMA'] = table['Close'].rolling(4).apply(lambda x: np.sum(weights*x))

#exponential moving average EMA
#----------------------------------------#
table['EMA9'] = table['Close'].ewm(span=9).mean()
table['EMA12'] = table['Close'].ewm(span=12).mean()
table['EMA26'] = table['Close'].ewm(span=26).mean()


#MACD
#----------------------------------------#
# Calculate MACD values using the pandas_ta library and saving them on the table
table.ta.macd(close='Close', fast=12, slow=26, signal=9, append=True)
table['MACD'] = table['EMA12'] - table['EMA26']
table['MACD'] = table['MACD'].round(6) #I round up to 6 decimal places

#preparing data for the chart
#short EMA calculation
shortEMA = table.Close.ewm(span=12, adjust=False).mean()
#long EMA calculation
longEMA = table.Close.ewm(span=26, adjust=False).mean()
#calculating MACD line
MACD = shortEMA - longEMA
#calculating signal line
signal = MACD.ewm(span=9, adjust=False).mean()

#creating the chart
plt.figure(figsize=(12.2, 4.5))
plt.plot(table.index, MACD, label='MACD', color='red', alpha=0.35) #alpha=0.35 oznacza przymglenie linii
plt.plot(table.index, signal, label='Signal line', color='blue', alpha=0.35) #alpha=0.35 oznacza przymglenie linii
plt.xticks(rotation=45)
plt.legend(loc='upper left')
plt.show()


#RSI
#----------------------------------------#
#(RSI = 100-(100/(1+RS)), where RS=a/b - ab are moving average from n periods of time)
table_rsi = table[['Close', 'Candle']].copy() #I create a new table under calculations
table_rsi.loc[table_rsi['Candle'] == 'falling', 'loss'] = table_rsi['Close'] #I'm only completing closures on dips
table_rsi.loc[table_rsi['Candle'] == 'growth', 'gain'] = table_rsi['Close'] #I'm only completing closures on increases
table_rsi['gain'] = pd.to_numeric(table_rsi["gain"], errors='coerce').fillna(0)
table_rsi['loss'] = pd.to_numeric(table_rsi["loss"], errors='coerce').fillna(0)
table_rsi['avg_gain'] = 0 #create the avg_gain column
table_rsi['avg_loss'] = 0 #create the avg_loss column
table_rsi['avg_gain'] = table_rsi['gain'].rolling(window=9).mean() #calculate a moving average
table_rsi['avg_loss'] = table_rsi['loss'].rolling(window=9).mean() #calculate a moving average
table_rsi['rs'] = table_rsi['avg_gain'] / table_rsi['avg_loss'] #RS calculation

table['RSI'] = 100 - (100 / (1 + table_rsi['rs'])) #calculate the RSI and paste into the main table





#PDF
#--------------------------------------#
#creating PDF file which can be send via email

W=210
H=297
pdf = FPDF() #domyślnie A4
pdf.add_page()
pdf.image('tło.png', 0, 0, W, H) #background
pdf.image('pasek kolor.png', 0, 12.5, 105, 15)
pdf.image('strona 1.png', 105, H-12, W-50, H)
pdf.dashed_line(10, H-20, W-10, H-20, 0.1, 0)
pdf.set_font("Courier", size = 20)
pdf.cell(200, 20, txt = "ANALIZA FIN-VETTORE", ln = 1, align = 'A') #title
pdf.set_font("Courier", size = 12)
pdf.cell(100, 10, txt = "Computer Science",ln = 3, align = 'A')

#adding the page for the charts
pdf.add_page()
pdf.image('tło.png', 0, 0, W, H) #background
pdf.image('pasek kolor.png', 0, 12.5, 105, 15)
pdf.image('strona 2.png', 105, H-12, W-50, H)
pdf.dashed_line(10, H-20, W-10, H-20, 0.1, 0)
pdf.set_font("Courier", size = 20)
pdf.cell(200, 20, txt = "DATA VISUALIZATION", ln = 1, align = 'A')
pdf.set_font("Courier", size = 12)

#setting minimum position for the charts
yy = 50

#loop for every jpg file with the chart
for i, img in enumerate(list_of_img):
    if i % 2 == 0:
        pdf.image(img, 10, yy, 92.5, 70)
    else:
        pdf.image(img, 105, yy, 92.5, 70)
        yy = yy + 70 + 5
    
#saving PDF file
pdf.output("FIN-VETTORE analysis.pdf")




#CLOSING THE PROGRAM
#=======================================#

#saving result to the file
table.to_excel("analiza_giełdowa.xlsx", sheet_name="Sheet1")

check_list.close()

open_csv = open("F:\\PROGRAMOWANIE\\PYTHON\\AUTOMAT FOREX\\open_csv_status.txt", 'w')
open_csv.write('DONE')
open_csv.close()




#=================================================================#
#TODO
#check the price channel by counting two linear functions and comparing the two slope coefficients.
#if there is a rising line then after the first apex the lowest rows are measured and the slope is compared. 



