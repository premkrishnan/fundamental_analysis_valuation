# ================================================================================
# Description:  This code calculates the Entry, Exit price for an investible 
#               stock with strong fundamentals.
# Important:    The program works best for stocks with more than 10 years of data. 
#               Ouput won't be accurate if its less than 10 years.
# Author:       Premkrishnan BNV (myfinancee@gmail.com)
# Date:         August/2022
# ================================================================================
#---------------------------------------------------------------------------------
# Code motivation: https://jovian.ai/aakashns/python-web-scraping-and-rest-api
#---------------------------------------------------------------------------------
# Setting up environment
# --------------------------------------------------------------------------------
# python3 -m venv scrapweb
# source scrapweb/bin/activate 
# python3 -m pip install BeautifulSoup4
# python3 -m pip install requests
# python3 -m pip install matplotlib
# --------------------------------------------------------------------------------
# Import the library
from tkinter import W
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import yfinance as yf
import os

# Variables
outfile = 'Fundamentals.txt'
counter = 0         # incremental counter for 'divs' in 'div_tags'
selected_data = {}  # dictionary to store data
years = []          # store years
revenue = []        # store revenue
fcfpershare = []   # store FCF per share
capexpershare = []  # store CAPEX per share
netincome = []      # store net income
netprofitmargin = []      # store net profit margin
longtermdebt = []   # store Long-term debt (m)
equity = []         # store Equity (m)
returnonequity = []      # store return on equity
num_shares = []     # store total number of shares (common stock)
freecashflow = []   # store calculated free cash flow values
capex = []          # store calculated CAPEX values
operatingcashflow = []  # store calculated OCF values
quaityofearnings = []   # store calculated QOE values
capexocf = []   # store calculated CAPEX/OCF ratios
debttoquity = []   # store calculated Debt-to-equity ratios

def main(roic_resp):
    # the `doc` object contains several properties and methods for extracting information from the HTML document
    doc1 = BeautifulSoup(roic_resp.text, 'html.parser')

    # Functions accessing table vales
    # table with positive values (no margins)
    def get_values_no_brackets(dtags, list_name, regx, outfname, row_lbl):
        counter = 0
        outfname.write(row_lbl)             # print first column name to the file
        outfname.write("\t")
        for dtag in dtags:
            counter += 1
            div_text = dtag.text.strip()    # get value from the div selected
            if regx.search(div_text):
                for x in (dtags[counter]):       # len(div_tags[counter]) to know the total number of values obtained
                    if x.text:
                        valx = re.sub("\,","",x.text)
                        val = re.sub("\- \-","2010",valx)
                        list_name.append(val)      # append years to the list
                        outfname.write(val)         # write to file
                        outfname.write("\t")         
                    else:
                        val = 0
                        list_name.append(val)      # append years to the list
                        outfname.write(val)         # write to file
                        outfname.write("\t")
                list_name.pop()
                outfname.write("\n")
                return(list_name)

    # table with negative values (with margins)
    def get_values_wt_brackets(dtags, list_name, regx, outfname, row_lbl):
        counter = 0
        outfname.write(row_lbl)             # print first column name to the file
        outfname.write("\t")        
        for dtag in dtags:
            counter += 1
            div_text = dtag.text.strip()    # get value from the div selected
            if regx.search(div_text):
                for x in (dtags[counter]):       # len(div_tags[counter]) to know the total number of values obtained
                    if x.text:
                        valx = re.sub("\,","",x.text)
                        val = re.sub("\- \-","0",valx)
                        s = re.compile("\(+(.*)\)+(\%*)$")    # regex expression for checking if the value is negative ( within paranthesis'()' )
                        if s.search(val):
                            result = s.search(val)        # check if the value is negative ( within paranthesis'()' )
                            new_x = str(int(0)-float(result.group(1)))  # convert to a negative value and the convert to string for the list formatting (' ')
                            if result.group(2):
                                list_name.append(new_x + "%")      # store the modified value
                                outfname.write(val)         # write to file
                                outfname.write("\t")                                
                            else:
                                list_name.append(new_x)
                                outfname.write(val)         # write to file
                                outfname.write("\t")                                
                        else:
                            list_name.append(val)      # store the value as it is
                            outfname.write(val)         # write to file
                            outfname.write("\t")                            
                    else:
                        val = 0
                        list_name.append(val)      # append years to the list
                        outfname.write(val)         # write to file
                        outfname.write("\t")                        
                list_name.pop()
                outfname.write("\n")
                return(list_name)

    # Function for 'Common stock' (number of shares)
    def get_values_no_perc(dtags, list_name):
        counter = 0
        for dtag in dtags:
            counter += 1
            dtext = dtag.text.strip()    # get value from the div selected
            if re.search("^Retained\s+earnings$", dtext):
                for x in (dtags[counter]):
                    if x.text:
                        val = re.sub("\,","",x.text)    # remove comma (') from the text
                        list_name.append(val)      # append years to the list
                    else:
                        val = 0
                        list_name.append(val)      # append years to the list                
                return(list_name)

    # // Get 'Common stock' (number of shares) //
    # ----------------------------------------------------------------------------------------------------------------------
    # The following is a funny situation. Wanted to get "Common stock" value but somehow its not coming out correctly.
    # It worked when tried with previous label (Retained earnings) and so using below
    # Might want to check in the future. Could be the div class name that is confusing.
    # ----------------------------------------------------------------------------------------------------------------------  
    # look for divs with the following class
    matched_class_div_lbl = ['w-1/2', 'flex-col', 'truncate', 'text-sm', 'text-left']
    div_tags = doc1.find_all('div', { 'class': matched_class_div_lbl})

    # Start parsing divs returned
    get_values_no_perc(div_tags, num_shares)
    common_stock = int(num_shares[1])   # get the value
    outfilename.write("Number of shares (millions):\t")
    outfilename.write(num_shares[1])
    outfilename.write("\n")

    # --------------------------------------
    # get values directly 
    # --------------------------------------
    # look for divs with the following class
    matched_class_div_lbl = ['grid', 'grid-flow-col', '2xl:auto-cols-fr', 'w-full', 'justify-items-center', 'h-full']
    div_tags = doc1.find_all('div', { 'class': matched_class_div_lbl})

    # Years
    reg_exp_yr = re.compile("^Currency\:+\s+USD$")
    get_values_no_brackets(div_tags, years, reg_exp_yr, outfilename, 'Years')        # open in append mode)

    # Revenue
    reg_exp_rv = re.compile("^Revenue\s+\(+m\)+$")
    get_values_no_brackets(div_tags, revenue, reg_exp_rv, outfilename, 'Revenue')

    # Net profits
    reg_exp_np = re.compile("^Net\s+profit\s+\(+m\)+$")
    get_values_wt_brackets(div_tags, netincome, reg_exp_np, outfilename, 'Net profits')

    # Net profit margin
    reg_exp_npm = re.compile("^Net\s+profit\s+margin$")
    get_values_wt_brackets(div_tags, netprofitmargin, reg_exp_npm, outfilename, 'Net margin')

    # Return on equity
    reg_exp_roe = re.compile("^Return\s+on\s+equity$")
    get_values_wt_brackets(div_tags, returnonequity, reg_exp_roe, outfilename, 'Return on equity')

    # FCF per share
    reg_exp_fcfs = re.compile("^FCF\s+per\s+share$")
    get_values_wt_brackets(div_tags, fcfpershare, reg_exp_fcfs, outfilename, 'FCF per share')

    # CAPEX per share
    reg_exp_capex = re.compile("^CAPEX\s+per\s+share$")
    get_values_wt_brackets(div_tags, capexpershare, reg_exp_capex, outfilename, 'CAPEX per share')

    # Long-term debt
    reg_exp_ltd = re.compile("^Long\-+term\s+debt\s+\(+m\)+$")
    get_values_wt_brackets(div_tags, longtermdebt, reg_exp_ltd, outfilename, 'Long-term debt')

    # Equity
    reg_exp_eqty = re.compile("^Equity\s+\(+m\)+$")
    get_values_wt_brackets(div_tags, equity, reg_exp_eqty, outfilename, 'Equity')

    # ----------------------------------------------------
    # Plotting NET INCOME vs YEARs chart to see the trend 
    # convert the lists to integers and the plot
    # ----------------------------------------------------
    xpoints = list(map(int, years))         # this convert the list values into integers
    ypoints = list(map(float, netincome))
    plt.plot(xpoints, ypoints)              # plotting
    plt.show()
    score_earnings = input("Enter the score for increasing earnings (0/1): ")       # get user determined score for increasing earnings based on the plot

    # ------------------------------
    # Formulas & Calculations
    # ------------------------------
    # Functions for formulas
    def comm_stock_func(shares, temp_list, list_name, outfname, row_lbl):
        data_list = list(map(float, temp_list))
        outfname.write(row_lbl)
        outfname.write("\t")
        for x in data_list:
            result = shares * x 
            list_name.append(round(result, 2))
            outfname.write(str(round(result, 2)))
            outfname.write("\t")
        outfname.write("\n")
        return(list_name)

    # Free Cash Flow = FCF per share * Common stock
    comm_stock_func(common_stock, fcfpershare, freecashflow, outfilename, 'Free Cash Flow')

    # CAPEX = CAPEX per share * Common stock
    comm_stock_func(common_stock, capexpershare, capex, outfilename, 'CAPEX')

    # Operating Cash Flow = Free Cash Flow + CAPEX
    i = 0
    outfilename.write("Operating Cash Flow")
    outfilename.write("\t")    
    while(i<len(capex)):
        list1 = list(map(float, freecashflow))
        list2 = list(map(float, capex))
        sum = list1[i] + list2[i]
        operatingcashflow.append(round(sum, 2))
        outfilename.write(str(round(sum, 2)))
        outfilename.write("\t")
        i += 1
    outfilename.write("\n")
    

    # Quaity Of Earnings = Operating Cash Flow / Net Profit
    i = 0
    outfilename.write("Quality Of Earnings")
    outfilename.write("\t")    
    while(i<len(operatingcashflow)):
        list1 = list(map(float, operatingcashflow))
        list2 = list(map(float, netincome))
        if list2[i]>0:
            divide = list1[i] / list2[i]
            quaityofearnings.append(round(divide, 2))
            outfilename.write(str(round(divide, 2)))
            outfilename.write("\t")
        i += 1
    outfilename.write("\n")

    # CAPEX/OCF = CAPEX / Operating Cash Flow
    i = 0
    outfilename.write("CAPEX/OCF")
    outfilename.write("\t")     
    while(i<len(operatingcashflow)):
        list1 = list(map(float, operatingcashflow))
        list2 = list(map(float, capex))
        if list1[i]>0:
            divide = list2[i] / list1[i]
            capexocf.append(round(divide, 2))
            outfilename.write(str(round(divide, 2)))
            outfilename.write("\t")         
        else:
            next
        i += 1
    outfilename.write("\n")

    # Debt / Equity = Long-term debt (m) / Equity (m)
    i = 0
    outfilename.write("Debt To Equity")
    outfilename.write("\t")     
    while(i<len(equity)):
        list1 = list(map(float, longtermdebt))
        list2 = list(map(float, equity))
        if list2[i]>0:
            divide = list1[i] / list2[i]
            debttoquity.append(round(divide, 2))
            outfilename.write(str(round(divide, 2)))
            outfilename.write("\t")              
        else:
            next
        i += 1
    outfilename.write("\n")

# ********************************************************************************************************************************************
# Find out AVERAGE PE RATIO for the last 3 YEARS
# ********************************************************************************************************************************************
def pe_ratio(macro_resp):
    # the `doc` object contains several properties and methods for extracting information from the HTML document
    doc2 = BeautifulSoup(macro_resp.text, 'html.parser')
    # look for table with the following class - considering only the PE ratio table
    tbl_tags = doc2.find_all('table', class_='table')
    pe_ratios = []
    sum = 0
    avg_pe_ratio = 0
    outfilename.write("Avg. PE Ratio")
    outfilename.write("\t")     
    for tbltag in tbl_tags[0]:
        #counter += 1
        tbl_text = tbltag.text.strip()    # get value from the div selected
        if tbl_text:
            if not re.search("PE Ratio Historical Data", tbl_text) and not re.search("Date", tbl_text):     # skipping the header
                lines = re.split("\n\n", tbl_text)                                                          # split lines
                i = 2                                                                                       # skipping first two rows
                years_lmt = 12+i                                                                            # fetch only for last 3 years (assuming 4Q per year)
                while i<years_lmt:
                    rows = re.split("\n", lines[i])
                    sum += float(rows[3])
                    avg_pe_ratio = sum/12                                                                   # calculate average
                    outfilename.write(str(round(avg_pe_ratio)))
                    outfilename.write("\t")                       
                    i += 1
    outfilename.write("\n")

# ********************************************************************************************************************************************
# MAIN STARTS
# ********************************************************************************************************************************************
ticker = input("Enter ticker symbol: ")     # get user input (ticker symbol)
desc = yf.Ticker(ticker)                    # get stock details from yahoo finance
long_name = desc.info["longName"]          # get the actual stock name
short_name = re.split("\s", long_name)        # split by \s and get the first name of the stock
company = re.sub("\,","",short_name[0]) 
symbol = desc.info["symbol"]          # get the actual stock name
sector = desc.info["sector"]          # get the actual stock name
industry = desc.info["industry"]          # get the actual stock name
exchange = desc.info["exchange"]          # get the actual stock name
debtToEquity = desc.info["debtToEquity"]          # get the actual stock name

print("----------------------------------------------------------------")
print(" STOCK DETAILS:")
print("----------------------------------------------------------------")
print(" Ticker:\t\t", symbol)
print(" Company name:\t\t", company.upper())
print(" Sector:\t\t", sector)
print(" Industry:\t\t", industry)
print(" Exchange:\t\t", exchange)
print(" DebtToEquity:\t\t", debtToEquity)
print("----------------------------------------------------------------")
user_response = input("Enter 'yes' = looks alright, enter the 'company name' otherwise: ")     # get user response (yes/no)

# URLs
roic = 'https://roic.ai/company/' + ticker
macro = 'https://www.macrotrends.net/stocks/charts/' + ticker.upper()

if user_response.lower() == 'yes':                                  # if everything looks okay then go ahead
    company_name = company.lower()
    response1 = requests.get(roic)                                  # download web page using the requests.get function.
    if 200 <= response1.status_code <= 299:
        # create 'Fundamentals.txt' file if doesn't exists, delete if it already exists
        if os.path.exists(outfile):
            os.remove(outfile)
            outfilename = open(outfile, "a")        # open in append mode
        else:
            outfilename = open(outfile, "a")        # open in append mode

        # calculate all other values except PE ratio
        main(response1)                                             

        #URL
        macro = macro + '/' + company_name + '/pe-ratio'            # ticker and company name needs to be 'converted' based on 'case'
        response2 = requests.get(macro)
        if 200 <= response2.status_code <= 299:
            pe_ratio(response2)                                         # calculate PE ratio 
        else:
            print("Could not calculate PE Ratio. Connection error: ", response2.status_code)
    else:
        print("ROIC Connection error: ", response1.status_code)
else:                                                               # if there is a change in the company name
    company_name = user_response.lower()
    response1 = requests.get(roic)        
    if 200 <= response1.status_code <= 299:
        # create 'Fundamentals.txt' file if doesn't exists, delete if it already exists
        if os.path.exists(outfile):
            os.remove(outfile)
            outfilename = open(outfile, "a")        # open in append mode
        else:
            outfilename = open(outfile, "a")        # open in append mode

        # calculate all other values except PE ratio
        main(response1)                                             # calculate all other values except PE ratio

        #URL
        macro = macro + '/' + company_name + '/pe-ratio'            # ticker and company name needs to be 'converted' based on 'case'
        response2 = requests.get(macro)
        if 200 <= response2.status_code <= 299:
            pe_ratio(response2)                                         # calculate PE ratio 
        else:
            print("Could not calculate PE Ratio. Connection error: ", response2.status_code)    
    else:
        print("ROIC Connection error: ", response1.status_code)   
