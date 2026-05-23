# Converted from calibragem.ipynb
# --- Cell 1 ---
import psycopg2 as pg
import pandas as pd
import math
import numpy as np
import pandas.io.sql as psql
# --- Cell 2 ---
connection = pg.connect("host=localhost dbname=Simulacred user=postgres password=12345678")
# --- Cell 3 ---
connection.close()
# --- Cell 4 ---
serie_pd = psql.read_sql('SELECT * FROM jpcosta.calculo_pd', connection)
# --- Cell 5 ---
probd = serie_pd[['ref', 'porte', 'modalidade', 'pd']]
# --- Cell 6 ---
pd_model = probd[(probd['ref'] > 0) & ((probd['ref'] < 48))].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean().reset_index()
pd_model
# --- Cell 7 ---
pd.options.display.float_format = '{:2}'.format

agg = psql.read_sql('SELECT * FROM jpcosta.perda_obs', connection)

n = agg.ref.max() - 1

n
# --- Cell 8 ---
#agg['media'] = agg['saldo']/agg['qtd']
n = 71
a = agg[(agg['nivel_risco'] != 'HH') & (agg.saldo > 0) & (agg.ref == n)].groupby(['porte', 'modalidade']).sum().reset_index()

inad = a['saldo_inad']/a['saldo']

a['inad']  = inad

a['media'] = a['saldo']/a['qtd']

tot = a.qtd.sum()
a['perc'] = a.qtd/tot

a = a[['porte', 'modalidade', 'media', 'saldo', 'inad', 'qtd', 'perc']]#[a['modalidade'] == 1]

a.to_csv(path_or_buf='result_sim2.csv', sep=';', index=False, encoding='latin1')
# --- Cell 9 ---
hst = agg[agg['nivel_risco'] != 'HH'][['ref', 'porte', 'modalidade', 'saldo', 'saldo_inad', 'qtd', 'nivel_risco']].groupby(['ref', 'porte','modalidade', 'nivel_risco']).sum().reset_index()
# --- Cell 10 ---
hst['prov'] = hst['nivel_risco'].map(dict_prov)*hst['saldo']
# --- Cell 11 ---
hst
# --- Cell 12 ---
df = hst[['ref', 'saldo','prov','saldo_inad']].groupby('ref').sum()

df['iprov'] = df['prov']/df['saldo']
df['inad90'] = df['saldo_inad']/df['saldo']
# --- Cell 13 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
#df  = hst[['ref','iprov','inad90']].groupby('ref').sum()#[60:n-82]

# this is to plot the kde
#sns.lineplot(data=df[:100], x='ref', y = 'iPE', label='iPE')
sns.lineplot(data=df, x='ref', y = 'iprov', label='iProv', linewidth=2.5)
sns.lineplot(data=df, x='ref', y = 'inad90', label='Inad90', linewidth=2.5)
#sns.lineplot(data=df[:50], x='ref', y = 'perda_obs', label='PO')

ax.axvline(72, ls='--', c='grey')
ax.axvline(96, ls='--', c='grey')

# beautifying the labels
plt.xlabel('Data de Referência')
plt.ylabel('')
plt.show()
# --- Cell 14 ---
filtro = hst[(hst['porte']==1) & (hst['modalidade']==2)].reset_index()
media = filtro['saldo']/filtro['qtd']
filtro['media'] = media
# --- Cell 15 ---
filtro['media'].plot()
# --- Cell 16 ---
b = agg[(agg['nivel_risco'] != 'HH') & (agg.saldo > 0) & (agg.ref == n)].groupby(['nivel_risco']).sum().reset_index()
# --- Cell 17 ---
b['perc_nivel'] = b['saldo']/ b['saldo'].sum()
# --- Cell 18 ---
b
# --- Cell 19 ---
dict_prov = {  'AA': 0.00,
               'A' : 0.005,
               'B':  0.01,
               'C':  0.03,
               'D':  0.10,
               'E':  0.30,
               'F':  0.50,
               'G':  0.70,
               'H':  1.00,
               'HH': 0.00}   
# --- Cell 20 ---
b['prov'] = b['nivel_risco'].map(dict_prov)*b['saldo']
# --- Cell 21 ---
b['prov'].sum()/b['saldo'].sum()
# --- Cell 22 ---
b['saldo_inad'].sum()/b['saldo'].sum()
# --- Cell 23 ---
import seaborn as sns
import matplotlib.pyplot as plt

ax = sns.barplot(x="modalidade", y="saldo", data=agg[(agg.nivel_risco != 'HH') & (agg.ref==n)])
# --- Cell 24 ---
import seaborn as sns
import matplotlib.pyplot as plt

ax = sns.barplot(x="porte", y="saldo", data=agg[(agg.nivel_risco != 'HH') & (agg.ref==n)])
