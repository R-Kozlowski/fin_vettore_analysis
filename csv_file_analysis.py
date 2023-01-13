import os, bs4, time, send2trash, csv, smtplib, threading, requests, __future__
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lxml import html
import urllib.request
from datetime import datetime, date, time, timezone
import pandas_ta as ta

#żeby wysłać załącznik html
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
table = pd.DataFrame(table, columns=['Gmt time','Weekday','Day','Time','Open','High','Low','Close','Volume','Candle','RSI','MACD','Resistance Top','Support Top', 'Signal','Price Action','Remarks'])
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
    table_min = pd.DataFrame(columns=['Gmt time','Weekday','Day','Time','Open','High','Low','Close','Volume','Candle','RSI','MACD','Resistance Top','Support Top','Signal','Price Action','Remarks'])
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
table_day = pd.DataFrame(columns=['Gmt time','Weekday','Day','Time','Open','High','Low','Close','Volume','Candle','RSI','MACD','Resistance Top','Support Top','Signal','Price Action','Remarks'])
                        
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





INDICATORS
#------------------------------------#

#all averages for closing prices
#arithmetic mean
mean = table.loc[:,"Open"].mean()
#weighted average
average = np.average(table['Open'])

#simple moving average SMA
table['SMA9'] = table['Close'].rolling(window=9).mean() #9-period

#weighted moving average WMA
weights = np.array([0.1, 0.2, 0.3, 0.4]) #weights for subsequent periods
table['WMA'] = table['Close'].rolling(4).apply(lambda x: np.sum(weights*x))

#exponential moving average EMA
table['EMA9'] = table['Close'].ewm(span=9).mean()
table['EMA12'] = table['Close'].ewm(span=12).mean()
table['EMA26'] = table['Close'].ewm(span=26).mean()

#MACD
# Calculate MACD values using the pandas_ta library
table.ta.macd(close='Close', fast=12, slow=26, signal=9, append=True)

table['MACD'] = table['EMA12'] - table['EMA26']
table['MACD'] = table['MACD'].round(6) #I round up to 6 decimal places

#RSI
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




#saving result to the file
table.to_excel("analiza_giełdowa.xlsx", sheet_name="Sheet1")


check_list.close()

open_csv = open("F:\\PROGRAMOWANIE\\PYTHON\\AUTOMAT FOREX\\open_csv_status.txt", 'w')
open_csv.write('DONE')
open_csv.close()


#TODO
#check the price channel by counting two linear functions and comparing the two slope coefficients.
#if there is a rising line then after the first apex the lowest rows are measured and the slope is compared. 



