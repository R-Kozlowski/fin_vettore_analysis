#! python3
#download data file from Dukascopy.com


import os, bs4, time, send2trash
from selenium import webdriver
import __future__
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



#opening browser
url = 'https://www.dukascopy.com/swiss/pl/marketwatch/historical/'
browser = webdriver.Chrome()
browser.get(url)
browser.implicitly_wait(10)



#choosing currency
WebDriverWait(browser, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'//*[@id="main-center-col"]/div/p[3]/iframe')))
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":g6"]'))).click()


#choosing time interval (minutes)
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/div[2]/div/div/div/div[1]/div[2]/div'))).click()
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":2"]'))).click()


#choosing date
#from
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/div[2]/div/div/div/div[3]/div/div'))).click()
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[10]/table/thead/tr/td[1]/button[1]'))).click()
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":l"]'))).click()
#to
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/div[2]/div/div/div/div[4]/div/div'))).click()
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":2w"]'))).click()

#confirm download button
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/div[2]/div/div/div/div[9]/div'))).click()



#logging
login = browser.find_element_by_xpath('/html/body/div[9]/div[5]/div/div/div[2]/div[3]/div[1]/div/div[4]/div[1]/div/div/input')
login.send_keys('email')
password = browser.find_element_by_xpath('/html/body/div[9]/div[5]/div/div/div[2]/div[3]/div[1]/div/div[4]/div[2]/div/div/input')
password.send_keys('password')
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/div[5]/div/div/div[2]/div[3]/div[1]/div/div[4]/div[4]/div[1]'))).click()


#saving the file
WebDriverWait(browser, 200).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/div[1]/div[5]/div/div[2]/div[1]/div'))).click()


time.sleep(10)


browser.close()
