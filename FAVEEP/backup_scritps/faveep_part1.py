#---------------------------------------------------------------------------
# Code idea: https://jovian.ai/aakashns/python-web-scraping-and-rest-api
#---------------------------------------------------------------------------
# Setting up environment
# --------------------------------------------------------------------------
# python3 -m venv scrapweb
# source scrapweb/bin/activate 
# python3 -m pip install BeautifulSoup4
# python3 -m pip install requests
# python3 -m pip install matplotlib
# --------------------------------------------------------------------------
# Import the library
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt

print("# ****************************************************************************************************************************************************#")
print("# Important:\n# -------------------- \n# The program is written to work best for stocks that has more than 10 years of data. Ouput won't be predicted if its less than 10 years.")
print("# ****************************************************************************************************************************************************#\n")
ticker = input("Enter ticker symbol: ")      # get user input (ticker symbol)

# Variables
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

# URLs
url_roic = 'https://roic.ai/company/' + ticker
url_wsj = 'https://www.wsj.com/market-data/quotes/' + ticker + '/financials'

# download web page using the requests.get function.
response = requests.get(url_roic)
# if the request was successful, response.status_code is set to a value between 200 and 299
#print(response.status_code)

# the `doc` object contains several properties and methods for extracting information from the HTML document
doc = BeautifulSoup(response.text, 'html.parser')

# Functions accessing table vales
def get_values_no_brackets(dtags, list_name, regx):
    counter = 0
    for dtag in dtags:
        counter += 1
        div_text = dtag.text.strip()    # get value from the div selected
        if regx.search(div_text):
            for x in (dtags[counter]):       # len(div_tags[counter]) to know the total number of values obtained
                if x.text:
                    valx = re.sub("\,","",x.text)
                    val = re.sub("\- \-","2010",valx)
                    list_name.append(val)      # append years to the list
                else:
                    val = 0
                    list_name.append(val)      # append years to the list
            list_name.pop()
            return(list_name)

def get_values_wt_brackets(dtags, list_name, regx):
    counter = 0
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
                        else:
                            list_name.append(new_x)
                    else:
                        list_name.append(val)      # store the value as it is
                else:
                    val = 0
                    list_name.append(val)      # append years to the list
            list_name.pop()
            return(list_name)

# --------------------------------------
# get values directly 
# --------------------------------------
# look for divs with the following class
matched_class_div_lbl = ['grid', 'grid-flow-col', '2xl:auto-cols-fr', 'w-full', 'justify-items-center', 'h-full']
div_tags = doc.find_all('div', { 'class': matched_class_div_lbl})

# Years
reg_exp_yr = re.compile("^Currency\:+\s+USD$")
get_values_no_brackets(div_tags, years, reg_exp_yr)

# Revenue
reg_exp_rv = re.compile("^Revenue\s+\(+m\)+$")
get_values_no_brackets(div_tags, revenue, reg_exp_rv)

# FCF per share
reg_exp_fcfs = re.compile("^FCF\s+per\s+share$")
get_values_wt_brackets(div_tags, fcfpershare, reg_exp_fcfs)

# CAPEX per share
reg_exp_capex = re.compile("^CAPEX\s+per\s+share$")
get_values_wt_brackets(div_tags, capexpershare, reg_exp_capex)

# Net profits
reg_exp_np = re.compile("^Net\s+profit\s+\(+m\)+$")
get_values_wt_brackets(div_tags, netincome, reg_exp_np)

# Net profit margin
reg_exp_npm = re.compile("^Net\s+profit\s+margin$")
get_values_wt_brackets(div_tags, netprofitmargin, reg_exp_npm)

# Long-term debt
reg_exp_ltd = re.compile("^Long\-+term\s+debt\s+\(+m\)+$")
get_values_wt_brackets(div_tags, longtermdebt, reg_exp_ltd)

# Equity
reg_exp_eqty = re.compile("^Equity\s+\(+m\)+$")
get_values_wt_brackets(div_tags, equity, reg_exp_eqty)

# Return on equity
reg_exp_roe = re.compile("^Return\s+on\s+equity$")
get_values_wt_brackets(div_tags, returnonequity, reg_exp_roe)

# Print output
print(years)
print(revenue)
print(fcfpershare)
print(capexpershare)
print(netincome)
print(netprofitmargin)
print(longtermdebt)
print(equity)
print(returnonequity)

# ----------------------------------------------------
# Plotting NET INCOME vs YEARs chart to see the trend 
# convert the lists to integers and the plot
# ----------------------------------------------------
xpoints = list(map(int, years))         # this convert the list values into integers
ypoints = list(map(float, netincome))
plt.plot(xpoints, ypoints)              # plotting
plt.show()

# Function for 'Common stock'
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

# // Common stock (number of shares) //
# ----------------------------------------------------------------------------------------------------------------------
# The following is a funny situation. Wanted to get "Common stock" value but somehow its not coming out correctly.
# It worked when tried with previous label (Retained earnings) and so using below
# Might want to check in the future. Could be the div class name that is confusing.
# ----------------------------------------------------------------------------------------------------------------------  
# look for divs with the following class
matched_class_div_lbl = ['w-1/2', 'flex-col', 'truncate', 'text-sm', 'text-left']
div_tags = doc.find_all('div', { 'class': matched_class_div_lbl})

# Start parsing divs returned
get_values_no_perc(div_tags, num_shares)
common_stock = int(num_shares[1])   # get the value

# Functions for formulas
def comm_stock_func(shares, temp_list, list_name):
    data_list = list(map(float, temp_list))
    for x in data_list:
        result = shares * x 
        list_name.append(round(result, 2))
    return(list_name)

# ------------------------------
# Formulas & Calculations
# ------------------------------
# Free Cash Flow = FCF per share * Common stock
comm_stock_func(common_stock, fcfpershare, freecashflow)
print(freecashflow)

# CAPEX = CAPEX per share * Common stock
comm_stock_func(common_stock, capexpershare, capex)
print(capex)

# Operating Cash Flow = Free Cash Flow + CAPEX
i = 0
while(i<len(capex)):
    list1 = list(map(float, freecashflow))
    list2 = list(map(float, capex))
    sum = list1[i] + list2[i]
    operatingcashflow.append(round(sum, 2))
    i += 1
print(operatingcashflow)

# Quaity Of Earnings = Operating Cash Flow / Net Profit
i = 0
while(i<len(operatingcashflow)):
    list1 = list(map(float, operatingcashflow))
    list2 = list(map(float, netincome))
    if list2[i]>0:
        divide = list1[i] / list2[i]
        quaityofearnings.append(round(divide, 2))
    #else:
        #next
    i += 1
print(quaityofearnings)

# CAPEX/OCF = CAPEX / Operating Cash Flow
i = 0
while(i<len(operatingcashflow)):
    list1 = list(map(float, operatingcashflow))
    list2 = list(map(float, capex))
    if list1[i]>0:
        divide = list2[i] / list1[i]
        capexocf.append(round(divide, 2))
    else:
        next
    i += 1
print(capexocf)

# Debt / Equity = Long-term debt (m) / Equity (m)
i = 0
while(i<len(equity)):
    list1 = list(map(float, longtermdebt))
    list2 = list(map(float, equity))
    if list2[i]>0:
        divide = list1[i] / list2[i]
        debttoquity.append(round(divide, 2))
    else:
        next
    i += 1
print(debttoquity)