import pandas as pd
import numpy as np 
from matplotlib import pyplot as plt 
import yfinance as yf 
from datetime import datetime as dt 
data= pd.read_excel(r'C:\Users\rmnma\OneDrive\Bureau\essaie extraction python.xlsx')
pd.read_excel(r'C:\Users\rmnma\OneDrive\Bureau\essaie extraction python.xlsx')

data = data.iloc[0:51]
data = data.dropna(how='all', axis=1)

tickers = data['Ticker'].tolist()


# Entreprises long et short
n = int(len(data) * 0.3) 
shorts = data.tail(n)['Ticker'].values
longs = data.head(n)['Ticker'].values

print(f"entreprise long : {longs}")
print(f"entreprise short : {shorts}")

tickers = ['^STOXX50E'] +[i for i in tickers ]
nb_val = len(tickers)

#print("Tickers: ", tickers)

def get_data(tickers):
   df = yf.download(tickers, start = "2018-01-01", end = '2024-23-10')['Adj Close']
   return df 

df = get_data(tickers)
df = df[tickers]


log_returns = np.log(df/df.shift(1)).dropna()

def calc_beta(df):
    np_array = df.values
    m= np_array[:,0] 
    beta =[]

    for ind, col in enumerate(df):
        if ind > 0 : 
            s = np_array[:,ind]
            covariance = np.cov(s,m)
            beta.append(covariance[0,1]/covariance[1,1])
            
    return pd.Series(beta,  df.columns[1:],name= 'Beta')


beta = calc_beta(log_returns)

# Séparation des Betas en deux listes en fonctions des composants Long et Short
beta_long = beta[longs]
beta_short= beta[shorts]

#Valeurs absolues des Betas 
abs_beta_long = np.abs(beta_long)
abs_beta_short = np.abs(beta_short)

#Calcul n°9 du mémoire 
weight_long = np.round(abs_beta_long/abs_beta_long.sum(),5)
#Calcul n°10 du mémoire 
weight_short =  np.round(abs_beta_short/abs_beta_short.sum()*-1,5)


beta_weighted_long = beta_long * weight_long
beta_weighted_short = beta_short * weight_short
beta_net = np.sum(beta_weighted_long) + np.sum(beta_weighted_short)

pf_long = pd.DataFrame({
    'stocks long ': longs,
    'beta long ': beta_long,
    'weight long' : weight_long,
    'Beta weighted long' : beta_weighted_long, 
    '       ' : '          '
})

pf_short = pd.DataFrame({
    'stocks short' : shorts,
    'beta short' : beta_short, 
    'weight short ' : weight_short,
    'beta weighted short': beta_weighted_short 
    
})

pf_long = pf_long.reset_index(drop=True)
pf_short = pf_short.reset_index(drop=True)

portfolio = pd.merge(pf_long, pf_short, on=pf_long.index)
portfolio.loc['total',['weight long', 'Beta weighted long', 'weight short ', 'beta weighted short']] = \
    portfolio[['weight long','Beta weighted long','weight short ', 'beta weighted short']].sum()

total_value = np.round(portfolio.loc[portfolio.index[-1], ['Beta weighted long', 'beta weighted short']].sum(),4)
portfolio.loc['total', 'Total beta portefeuille'] = total_value
portfolio['Total beta portefeuille'] = portfolio['Total beta portefeuille'].apply(lambda x: '{:^10}'.format(x) if isinstance(x, (int, float)) else x)

portfolio.drop(portfolio.columns[0], axis=1)