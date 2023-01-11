# fin_vettore_analysis
Advanced tool for multi-calculation analysis of forex data


The idea of this concept is to build advanced prices calculation tool which will be able to analyze more than 9000 rows with 17 columns of data. 

Few steps should be presented in 2 different files:
1. first file:
  - automatically open the browser and go to the special site where program has the possibility to download excel file with the data;
  - save the file in the exact direction;
  - initialization of the second file;
2. second file:
  - the first step is to change the one-minute data into 5-minute, 15-minute, 60-minute and daily data and save these data to new excel files.
  - the next step is to analyze the price of the currency pair (for example, EUR/USD) from each period in the created files.
  - the last task will be to send to email or save the results of the analysis. 

All the final data should be given in as the chart, table with the moment of entry into the market (with stop loss and take profit price), the investment risk for this operation etc.
The entire program should be compiled to the exe file and run by Windows periodically with a 1-minute interval.
