import csv
import re
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup as bs

ticker = 'tsla'
years = 5  # note: more years into the future = less accurate
market_return = .075  # personal % amount you want back
gdp_growth = .04
fcf_growth = .025


def future_percent(value, percent_of):
    b = np.array([])
    for i in range(0, years):
        b = np.append(b, value[i] * percent_of)
    return b


def average_no_outliers(to_average, m=2.5):
    x = to_average[abs(to_average - np.mean(to_average)) < m * np.std(to_average)]
    return sum(x) / len(x)

# TODO: FIX TABLE SCRAPER


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

key_list = np.array(['Revenue', 'Cost of Revenue', 'Selling General & Admin',
                     'EBIT', 'Pretax Income', 'Income Tax', 'Depreciation & Amortization',
                     'Capital Expenditures', 'Receivables', 'Inventory', 'EBITDA',
                     'Interest Expense / Income', 'Other Long Term Assets',
                     'Accounts Payable', 'Other Current Liabilities', 'Operating Expenses',
                     'Long Term Debt', 'Cash & Cash Equivalents', 'Deferred Revenue',
                     'Current Debt'],
                    dtype=str)
data = {key: None for key in key_list}

urls = {'income annually': f"https://stockanalysis.com/stocks/{ticker}/financials/",
        'balance sheet annually': f"https://stockanalysis.com/stocks/{ticker}/financials/balance-sheet/",
        'cash flow annually': f"https://stockanalysis.com/stocks/{ticker}/financials/cash-flow-statement/"}

fin_states = list()

for key in urls.keys():
    response = requests.get(urls[key], headers=headers)
    soup = bs(response.content, 'html.parser')
    df = pd.read_html(str(soup), attrs={'id': 'financial-table'})[0]
    df.replace(',', '', regex=True, inplace=True)
    df.replace('"', '', regex=True, inplace=True)
    df.replace('-', ' ', regex=True, inplace=True)
    df = df.iloc[:, [i for i in range(0, 11)]]
    fin_states.append(df)

df = pd.concat(fin_states)
df.to_csv('test_data.csv', index=False)

with open("test_data.csv", 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        for i in range(0, 20):
            if key_list[i] in row:
                str_row = '|'.join(row)
                match = re.findall(r'\d\d*', str_row)
                float_match = [float(x) for x in match]
                data[key_list[i]] = float_match

data['Working Capital'] = data['Receivables'][0] + data['Inventory'][0] + data['Other Long Term Assets'][0] -\
                          data['Accounts Payable'][0] - data['Other Current Liabilities'][0]

holder = np.array([])

# revenue % growth AVERAGE FOR PREDICTION
for i in range(0, 9):
    holder = np.append(holder, (data['Revenue'][i] - data['Revenue'][i + 1]) / data['Revenue'][i + 1])
data['P Revenue % Growth'] = average_no_outliers(holder)
holder = np.array([])

# cost % revenue
for i in range(0, 10):
    holder = np.append(holder, data['Cost of Revenue'][i] / data['Revenue'][i])
data['P Cost % Revenue'] = average_no_outliers(holder)
holder = np.array([])

# SGA % revenue
for i in range(0, 10):
    holder = np.append(holder, data['Selling General & Admin'][i] / data['Revenue'][i])
data['P SGA % Revenue'] = average_no_outliers(holder)
holder = np.array([])

# IntExp % EBITDA (MAYBE NOT FULLY ACCURATE)
for i in range(0, 10):
    holder = np.append(holder, data['Interest Expense / Income'][i] / data['EBITDA'][i])
data['P Interest Expense % EBITDA'] = average_no_outliers(holder)
holder = np.array([])

# income tax % pre-tax income
for i in range(0, 10):
    holder = np.append(holder, data['Income Tax'][i] / data['Pretax Income'][i])
data['P Income Tax % Pretax Income'] = average_no_outliers(holder)
holder = np.array([])

'''
# NOPAT
for i in range(0, 10):
    holder.append(data['EBIT'][i] / (1 - data['Income Tax % Pretax Income'][i]))
data['NOPAT'] = holder.copy()
holder.clear()
'''

# DA % revenue
for i in range(0, 10):
    holder = np.append(holder, data['Depreciation & Amortization'][i] / data['Revenue'][i])
data['P DA % Revenue'] = average_no_outliers(holder)
holder = np.array([])

# CapEx % revenue
for i in range(0, 10):
    holder = np.append(holder, data['Capital Expenditures'][i] / data['Revenue'][i])
data['P CapEx % Revenue'] = average_no_outliers(holder)
holder = np.array([])

# AR % revenue
for i in range(0, 10):
    holder = np.append(holder, data['Receivables'][i] / data['Revenue'][i])
data['P AR % Revenue'] = average_no_outliers(holder)
holder = np.array([])

# AR % revenue
for i in range(0, 10):
    holder = np.append(holder, data['Receivables'][i] / data['Revenue'][i])
data['P AR % Revenue'] = average_no_outliers(holder)
holder = np.array([])

# inventory % cost
for i in range(0, 10):
    holder = np.append(holder, data['Inventory'][i] / data['Cost of Revenue'][i])
data['P Inventory % Cost of Revenue'] = average_no_outliers(holder)
holder = np.array([])

# other assets % growth
for i in range(0, 9):
    holder = np.append(holder, data['Other Long Term Assets'][i] / data['Other Long Term Assets'][i + 1] - 1)
data['P Other Assets % Growth'] = average_no_outliers(holder)
holder = np.array([])

# accounts payable % cost
for i in range(0, 10):
    holder = np.append(holder, data['Accounts Payable'][i] / data['Cost of Revenue'][i])
data['P Accounts Payable % Cost of Revenue'] = average_no_outliers(holder)
holder = np.array([])

# other current liab % sga
for i in range(0, 10):
    holder = np.append(holder, data['Other Current Liabilities'][i] / data['Selling General & Admin'][i])
data['P Other Current Liab % SGA'] = average_no_outliers(holder)
holder = np.array([])

# operating exp % revenue
for i in range(0, 10):
    holder = np.append(holder, data['Operating Expenses'][i] / data['Revenue'][i])
data['P Operating Exp % Revenue'] = average_no_outliers(holder)
holder = np.array([])

'''             divider                    '''

projection_data = {}

# future revenue
holder = np.append(holder, data['Revenue'][0] * (1 + data['P Revenue % Growth']))
for i in range(0, years - 1):
    holder = np.append(holder, holder[i] * (1 + data['P Revenue % Growth'] + (.01 * i)))
projection_data['Future Revenue'] = holder.copy()
holder = np.array([])

# future cost
projection_data['Future Cost'] = future_percent(projection_data['Future Revenue'], data['P Cost % Revenue'])

# future sga
projection_data['Future SGA'] = future_percent(projection_data['Future Revenue'], data['P SGA % Revenue'])

# future operating expenses
projection_data['Future Operating Expenses'] = future_percent(projection_data['Future Revenue'],
                                                              data['P Operating Exp % Revenue'])

# future ebit
for i in range(0, years):
    holder = np.append(holder, projection_data['Future Revenue'][i] - (projection_data['Future Cost'][i] +
                                                                       projection_data['Future Operating Expenses'][i]))
projection_data['Future EBIT'] = holder.copy()
holder = np.array([])

# future DA
projection_data['Future DA'] = future_percent(projection_data['Future Revenue'], data['P DA % Revenue'])

# future int exp MAY BE NOT ACCURATE
for i in range(0, years):
    holder = np.append(holder, (projection_data['Future DA'][i] + projection_data['Future EBIT'][i]) *
                       data['P Interest Expense % EBITDA'])
projection_data['Future Int Exp'] = holder.copy()
holder = np.array([])

# future pre-tax income
for i in range(0, years):
    holder = np.append(holder, projection_data['Future EBIT'][i] - projection_data['Future Int Exp'][i])
projection_data['Future Pre-Tax Income'] = holder.copy()
holder = np.array([])

# future income tax
projection_data['Future Income Tax'] = future_percent(projection_data['Future Pre-Tax Income'],
                                                      data['P Income Tax % Pretax Income'])

# future NOPAT
for i in range(0, years):
    holder = np.append(holder, projection_data['Future EBIT'][i] * (1 - data['P Income Tax % Pretax Income']))
projection_data['Future NOPAT'] = holder.copy()
holder = np.array([])

# future capex
projection_data['Future CapEx'] = future_percent(projection_data['Future Revenue'], data['P CapEx % Revenue'])

# future ar
projection_data['Future AR'] = future_percent(projection_data['Future Revenue'], data['P AR % Revenue'])

# future inventory
projection_data['Future Inventory'] = future_percent(projection_data['Future Cost'],
                                                     data['P Inventory % Cost of Revenue'])

# future other assets
for i in range(0, years):
    holder = np.append(holder, data['Other Long Term Assets'][0] * (1 + data['P Other Assets % Growth']) ** (1 + i))
projection_data['Future Other Assets'] = holder.copy()
holder = np.array([])

# future accounts payable
projection_data['Future Accounts Payable'] = future_percent(projection_data['Future Cost'],
                                                            data['P Accounts Payable % Cost of Revenue'])

# future other current liabilities
projection_data['Future Other Current Liab'] = future_percent(projection_data['Future SGA'],
                                                              data['P Other Current Liab % SGA'])

# future working capital
for i in range(0, years):
    holder = np.append(holder, projection_data['Future AR'][i] + projection_data['Future Inventory'][i] +
                       projection_data['Future Other Assets'][i] - projection_data['Future Accounts Payable'][i] -
                       projection_data['Future Other Current Liab'][i])
projection_data['Future Working Capital'] = holder.copy()
holder = np.array([])

# future change in working capital
holder = np.append(holder, projection_data['Future Working Capital'][0] - data['Working Capital'])
for i in range(1, years):
    holder = np.append(holder, projection_data['Future Working Capital'][i] -
                       projection_data['Future Working Capital'][i - 1])
projection_data['Future Change in Working Capital'] = holder.copy()
holder = np.array([])

# future unlevered free cash flow
for i in range(0, years):
    holder = np.append(holder, projection_data['Future NOPAT'][i] + projection_data['Future DA'][i] -
                       projection_data['Future CapEx'][i] - projection_data['Future Change in Working Capital'][i])
projection_data['Future Unlevered Free Cash Flow'] = holder.copy()
holder = np.array([])

'''                           weighted average cost                                    '''

stock = yf.Ticker(ticker)

# market cap
price = stock.info['currentPrice']
shares_outstanding = stock.info['sharesOutstanding']
mkt_cap = price * shares_outstanding

# market val of debt
mkt_debt = data["Long Term Debt"][0] * 1000000

# cost of equity
beta = stock.info['beta']

risk_web = requests.get('https://www.cnbc.com/quotes/US10Y')
risk_web = bs(risk_web.text, "lxml")
for el in risk_web.find_all('span', {'class': 'QuoteStrip-lastPrice'}):
    risk_free = float(el.get_text().replace("%", "")) / 100

cost_equity = risk_free + (market_return - risk_free) * beta

# cost of debt
total_debt = stock.info['totalDebt']
int_exp = (-1 * stock.financials.loc["Interest Expense"].iloc[1])
cost_debt = int_exp / total_debt

# tax rate
tax_rate_web = requests.get('https://www.gurufocus.com/term/TaxRate/' + ticker + '/Tax-Rate-Percentage/')
tax_rate_web = bs(tax_rate_web.text, "lxml")
for el in tax_rate_web.find_all('font', {'style': 'font-size: 24px; font-weight: 700; color: #337ab7'}):
    holder = re.search(r'\d*.\d*%', el.get_text())
tax_rate = float(holder[0].replace('%', '')) / 100
holder = np.array([])

WACC = cost_equity * (mkt_cap / (mkt_cap + mkt_debt)) + (cost_debt * (mkt_debt / (mkt_cap + mkt_debt))) * (1 - tax_rate)

'''                                              perpetuity growth                                         '''

for i in range(0, years):
    holder = np.append(holder, 1 / ((1 + WACC) ** (i + 1)))
projection_data['Discount Factor'] = holder.copy()
holder = np.array([])

for i in range(0, years):
    holder = np.append(holder, projection_data['Future Unlevered Free Cash Flow'][i] *
                       projection_data['Discount Factor'][i])
projection_data['PV FCF'] = holder.copy()
holder = np.array([])

terminal_val = projection_data['Future Unlevered Free Cash Flow'][years - 1] * (1 + fcf_growth) / (WACC - fcf_growth)

ebitda_multiple = terminal_val / projection_data['Future Unlevered Free Cash Flow'][years - 1]

pv_terminal_val = terminal_val * projection_data['Discount Factor'][years - 1]

sum_fcf = np.sum(projection_data['PV FCF'])

implied_ev = sum_fcf + pv_terminal_val

min_int = stock.financials.loc['Minority Interest'].iloc[1]
if min_int is None:
    min_int = 0
else:
    min_int = min_int / 1000000

pref_stock_web = requests.get('https://www.gurufocus.com/term/Preferred+Stock/' + ticker + '/Preferred%252BStock/')
pref_stock_web = bs(pref_stock_web.text, "lxml")
for el in pref_stock_web.find_all('font', {'style': 'font-size: 24px; font-weight: 700; color: #337ab7'}):
    holder = re.findall(r'\$\d*.\d*', el.get_text())
pref_stock = float(holder[0].replace('$', ''))
holder = np.array([])

implied_equity_val = implied_ev - pref_stock - min_int + data['Cash & Cash Equivalents'][0] - data['Long Term Debt'][0]

implied_share_price = implied_equity_val / (shares_outstanding / 1000000)
print(implied_share_price)
