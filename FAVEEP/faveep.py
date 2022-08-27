# ================================================================================
# Description:  This code calculates the Entry, Exit price for an investible 
#               stock with strong fundamentals.
# Important:    The program works best for stocks with more than 10 years of data. 
#               Output won't be accurate if its less than 10 years.
# Author:       Premkrishnan BNV (myfinancee@gmail.com)
# Date:         August/2022
# ================================================================================
# WARNING:  I AM NOT A PROFESSIONAL. THIS IS AN ATTEMPT TO LEARN AND MASTER PYTHON
#           BY CREATING REAL WORLD APPLICATIONS. IT COMES WITH NO GUARANTEE.
#           YOU WILL BE RESPONSIBLE FOR YOUR LOSSES.
#---------------------------------------------------------------------------------
# Python tips: https://jovian.ai/aakashns/python-web-scraping-and-rest-api
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
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import yfinance as yf
from yahoo_fin import stock_info
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
score_earnings = 0      #
score_net_margin = 0    #
score_roe = 0           #
score_qoe = 0           #
score_capexocf = 0         #
score_fcf = 0           #
score_d2e = 0           #
score_int_cov = 0       #


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
    get_values_no_brackets(div_tags, years, reg_exp_yr, outfilename, 'Years')
    
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
    #plt.show()
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
        if list2[i]:
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
        if list1[i]:
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
        if list2[i]:
            divide = list1[i] / list2[i]
            debttoquity.append(round(divide, 2))
            outfilename.write(str(round(divide, 2)))
            outfilename.write("\t")              
        else:
            next
        i += 1
    outfilename.write("\n")

    # ********************************************************************************
    # CALCULATE SCORES
    # ********************************************************************************
    # check if Net Margin (%) >= 15? 
    i = len(netprofitmargin) - 1                                    # point i to the last element in list
    avg_nm = 0
    tot_nm = 0
    # Iterate till 1st element and keep on decrementing i
    while i >= 13:                                                  # iterate over the list in reverse using while loop
        nm_val = re.sub("\%","",netprofitmargin[i]) 
        tot_nm += float(nm_val)
        i -= 1
    avg_nm = round(tot_nm/3)
    if avg_nm >= 15:
        score_net_margin = 1
    else:
        score_net_margin = 0

    # check if Return On Equity (%) >= 15? 
    i = len(returnonequity) - 1                                    # point i to the last element in list
    avg_roe = 0
    tot_roe = 0
    # Iterate till 1st element and keep on decrementing i
    while i >= 13:                                                  # iterate over the list in reverse using while loop
        roe_val = re.sub("\%","",returnonequity[i]) 
        tot_roe += float(roe_val)
        i -= 1
    avg_roe = round(tot_roe/3)
    if avg_roe >= 15:
        score_roe = 1
    else:
        score_roe = 0

    # check if Quaity Of Earnings >= 1.2? 
    i = len(quaityofearnings) - 1                                    # point i to the last element in list
    avg_qoe = 0
    tot_qoe = 0
    # Iterate till 1st element and keep on decrementing i
    while i >= 13:                                                  # iterate over the list in reverse using while loop
        tot_qoe += float(quaityofearnings[i])
        i -= 1
    avg_qoe = (tot_qoe/3)
    
    if avg_qoe >= 1.2:
        score_qoe = 1
    else:
        score_qoe = 0

    # check if CAPEX/OCF <= 0.5? 
    i = len(capexocf) - 1                                    # point i to the last element in list
    avg_co = 0
    tot_co = 0
    # Iterate till 1st element and keep on decrementing i
    while i >= 13:                                                  # iterate over the list in reverse using while loop
        tot_co += float(capexocf[i])
        i -= 1
    avg_co = (tot_co/3)
    
    if avg_co <= 0.5:
        score_capexocf = 1
    else:
        score_capexocf = 0

    # check if Free Cash Flow is positive? 
    i = len(freecashflow) - 1                                    # point i to the last element in list
    avg_fcf = 0
    tot_fcf = 0
    # Iterate till 1st element and keep on decrementing i
    while i >= 13:                                                  # iterate over the list in reverse using while loop
        tot_fcf += float(freecashflow[i])
        i -= 1
    avg_fcf = (tot_fcf/3)
    
    if avg_fcf > 0:
        score_fcf = 1
    else:
        score_fcf = 0

    # check if Debt To Equity <= 0.5? 
    i = len(debttoquity) - 1                                    # point i to the last element in list
    avg_de = 0
    tot_de = 0
    # Iterate till 1st element and keep on decrementing i
    while i >= 13:                                                  # iterate over the list in reverse using while loop
        tot_de += float(debttoquity[i])
        i -= 1
    avg_de = (tot_de/3)
    
    if avg_de <= 0.5:
        score_d2e = 1
    elif avg_de > 0.5:
        int_cov = input("Enter the interest coverage: ")
        if int(int_cov) >= 4:
            score_d2e = 1
        else:
            score_d2e = 0

    # CAGR value calculation
    #i = len(years) - 1                                    # point i to the last element in list
    #avg_de = 0
    #tot_de = 0
    # Iterate till 1st element and keep on decrementing i
    #while i >= 13:                                                  # iterate over the list in reverse using while loop
    #    tot_de += float(debttoquity[i])
    #    i -= 1
    #avg_de = (tot_de/3)    
    start_year = len(years) - 1
    end_year = len(years) - 3
    start_val = float(netincome[start_year])
    end_val = float(netincome[end_year])

    cagr = ( ( (start_val/end_val) ** (1/2) ) - 1 ) * 100
    
    #print("CAGR: {:.2f}%".format(cagr))
    #print("Increasing earning score: ", score_earnings)
    #print("Net margin score: ", score_net_margin)
    #print("Return on equity score: ", score_roe)
    #print("Quality of earning score: ", score_qoe)
    #print("CAPEX/OCF score: ", score_capexocf)
    #print("Free cash flow csore: ", score_fcf)
    #print("Debt to equity score: ", score_d2e)
    
    checklist_score = int(score_earnings) + int(score_net_margin) + int(score_roe) + int(score_qoe) + int(score_capexocf) + int(score_fcf) + int(score_d2e)
    return(checklist_score, cagr)

    # ********************************************************************************
    # CALCULATE SCORES - end
    # ********************************************************************************

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
    return(avg_pe_ratio)

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
#debtToEquity = desc.info["debtToEquity"]          # get the actual stock name
current_price = stock_info.get_live_price(ticker)

print("----------------------------------------------------------------")
print(" STOCK DETAILS:")
print("----------------------------------------------------------------")
print(" Ticker:\t\t", symbol)
print(" Company name:\t\t", company.upper())
print(" Current price: \t\t{:.2f}".format(current_price))
print(" Sector:\t\t", sector)
print(" Industry:\t\t", industry)
print(" Exchange:\t\t", exchange)
#print(" DebtToEquity:\t\t", debtToEquity)
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
        (final_checklist_score, cagr_val) = main(response1)

        #URL
        macro = macro + '/' + company_name + '/pe-ratio'            # ticker and company name needs to be 'converted' based on 'case'
        response2 = requests.get(macro)
        if 200 <= response2.status_code <= 299:
            pe_ratio_avg = pe_ratio(response2)                                     # calculate PE ratio

            # Find expected forward earnings from Zacks (https://www.zacks.com/stock/quote/{ticker}/)
            #est_url = 'https://www.zacks.com/stock/quote/'  + ticker.upper()
            #print("Enter the Current Yr Est (ctrl + click the link)", est_url)
            current_yr_est = input("Enter the Current Yr Est: ")
            intrinsic_price = float(current_yr_est) * float(pe_ratio_avg)
            
            # calculate entry price
            if final_checklist_score == 7:
                safety_margin = 0.9
            elif final_checklist_score == 6:
                safety_margin = 0.8
            elif final_checklist_score == 5:
                safety_margin = 0.7
            else:
                safety_margin = 0
            entry_price = safety_margin * intrinsic_price

            # calculate exit price
            exit_price = intrinsic_price * (1 + (cagr_val/100))

            print("\n----------------------------------------------------------------")
            print(" STOCK VALUATION RESULTS")
            print("----------------------------------------------------------------\n")
            print("Intrinsic price: \t\t{:.2f}".format(intrinsic_price))
            print("Entry price: \t\t{:.2f}".format(entry_price))
            print("Exit price: \t\t{:.2f}".format(exit_price))

            # difference betweeen current price and entry price
            perc_difference = ((current_price - entry_price) / entry_price) * 100
            print("% Difference between current price & entry price: \t\t{:.2f}%".format(perc_difference))

            # under/over valuation
            if entry_price < current_price:
                print("The stock is currently 'OVERVALUED'\n")
            elif entry_price > current_price:
                print("The stock is currently 'UNDERVALUED'\n")

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

# END