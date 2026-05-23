# Converted from Analise_final_simulacao-checkpoint.ipynb
# --- Cell 1 ---
import psycopg2 as pg
import pandas as pd
import math
import numpy as np
import pandas.io.sql as psql
# --- Cell 2 ---
connection = pg.connect("host=localhost dbname=Simulacred user=postgres password=12345678")
# --- Cell 3 ---
#connection.close()
# --- Cell 4 ---
#carteira
agg = psql.read_sql('SELECT * FROM jpcosta.perda_obs_atr', connection)

#Série de TD
serie_pd_2 = psql.read_sql('SELECT * FROM jpcosta.calculo_pd_2', connection)

#serie de LGD
lgd_i = psql.read_sql('SELECT * FROM jpcosta.calculo_lgd60', connection)

# --- Cell 5 ---
df1 = serie_pd_2[['ref', 'porte', 'modalidade', 'qtd', 'qtd_inad']].groupby(['ref', 'porte', 'modalidade']).sum().reset_index()

probd = df1['qtd_inad']/df1['qtd']

df1['pd'] = probd
# --- Cell 6 ---
pd_model = df1[(df1['ref'] > 0) & ((df1['ref'] < 48))].drop('ref', axis=1).groupby(['porte', 'modalidade'])\
# %magic:             .mean().reset_index().drop(['qtd', 'qtd_inad'], axis=1)
pd_model
# --- Cell 7 ---
pd_monit = df1[df1['ref'].between(72, 84)].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean().reset_index()
pd_monit = pd_monit.rename(columns={'pd': 'pd_monit'}).drop(['qtd', 'qtd_inad'], axis=1)
pd_monit
# --- Cell 8 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
df  = df1.groupby(['modalidade', 'ref']).mean()

# this is to plot the kde
sns.lineplot(data=df, x='ref', y = 'pd',  hue='modalidade')

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 9 ---
lgd = lgd_i[lgd_i.ref > 0].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean('lgd').reset_index()
lgd
# --- Cell 10 ---
ecl = pd_model.merge(lgd, on=['porte', 'modalidade'], how='left').fillna(0.500)
ecl['ecl'] = ecl['pd'] * ecl['lgd']
ecl = ecl.merge(pd_monit, on=['porte', 'modalidade'], how='left')
ecl['ecl2'] = ecl['pd_monit'] * ecl['lgd']

ecl
# --- Cell 11 ---
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
# --- Cell 12 ---
df2 = agg[['ref', 'nivel_risco', 'porte', 'qtd','modalidade', 'estagio', 'saldo', 'saldo_inad', 'perda_att']]\
# %magic:         .groupby(['ref', 'nivel_risco', 'porte', 'modalidade', 'estagio']).sum().reset_index()

df2['prov'] = df2['nivel_risco'].map(dict_prov)*df2['saldo']

df2 = df2.merge(ecl, how='left', on=['porte', 'modalidade'])

df2
# --- Cell 13 ---
prob = []

for i in range(len(df2)):
    if df2.estagio[i] == 1:
        prob.append(df2.pd[i])
    elif df2.estagio[i] == 2:
        
        b = (0.11852 - 0.05478*math.log(max(0.003, df2.pd[i])))**2
        m = (1 + (3 - 2.5) * b)/(1 - (1.5) * b)
        
        prob.append(df2.pd[i]*m)
        
    else:
        prob.append(1.00)

df2['pd'] = prob

df2['ecl'] = df2['pd'] * df2['lgd'] * df2['saldo']
#agg['ecl2'] = agg['pd_monit'] * agg['lgd'] * agg['saldo']
# --- Cell 14 ---
hst = df2[df2['nivel_risco'] != 'HH'][['ref', 'saldo', 'saldo_inad', 'prov', 'ecl', 'ecl2', 'perda_att']].groupby(['ref']).sum(['prov', 'saldo', 'ecl', 'perda_att'])
# --- Cell 15 ---
hst['iprov'] = hst['prov']/hst['saldo']
hst['inad90'] = hst['saldo_inad']/hst['saldo']
hst['iPE'] = hst['ecl']/hst['saldo']
hst['perda_obs'] = hst['perda_att']/hst['saldo']
hst['dif'] = hst['iPE'] - hst['iprov']
# --- Cell 16 ---
import seaborn as sns
import matplotlib.pyplot as plt
sns.color_palette("ch:s=.25,rot=-.25", as_cmap=True)
#sns.set_style()
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
df  = hst[['iPE','iprov','inad90', 'perda_obs']]#[60:n-82]

# this is to plot the kde
sns.lineplot(data=df[:100], x='ref', y = 'iPE', label='iPE', linewidth=2.5)
sns.lineplot(data=df[:100], x='ref', y = 'iprov', label='iProv', linewidth=2.5)
sns.lineplot(data=df[:100], x='ref', y = 'inad90', label='Inad90', linewidth=2.5)
#sns.lineplot(data=df[:50], x='ref', y = 'perda_obs', label='PO')

ax.axvline(72, ls='--', c='red')

# beautifying the labels
plt.xlabel('Data de Referência')
plt.ylabel('')
plt.show()
# --- Cell 17 ---
n = agg.ref.max() - 1
# --- Cell 18 ---
df3 = df1.sort_values(['porte', 'modalidade', 'ref']).merge(pd_monit[['porte', 'modalidade', 'pd_monit']], how='left', on=['modalidade', 'porte'])
df3 = df3.merge(pd_model[['porte', 'modalidade', 'pd']].rename(columns={'pd':'pd_model'}), how='left', on=['modalidade', 'porte'])

df3['td'] = df3.groupby(['porte','modalidade'])['pd'].shift(12)
df3['PD_12'] = df3.groupby(['porte','modalidade']).rolling(window=12)['td'].mean().reset_index()['td']
df3['PD_24'] = df3.groupby(['porte','modalidade']).rolling(window=24)['td'].mean().reset_index()['td']
df3['PD_36'] = df3.groupby(['porte','modalidade']).rolling(window=36)['td'].mean().reset_index()['td']
df3['PD_48'] = df3.groupby(['porte','modalidade']).rolling(window=48)['td'].mean().reset_index()['td']
# --- Cell 19 ---
prob, prob0, prob1, prob2, prob3, prob4, prob5 = [], [], [], [], [], [], []

agg2 = df2[df2.ref <= max(df3.ref)]

for i in range(len(agg2)):
    p  = df3[(df3.ref == agg2.ref[i]) & (df3.modalidade == agg2.modalidade[i]) & (df3.porte == agg2.porte[i])].pd_model.values[0]
    p0 = df3[(df3.ref == agg2.ref[i]) & (df3.modalidade == agg2.modalidade[i]) & (df3.porte == agg2.porte[i])].td.values[0]
    p1 = df3[(df3.ref == agg2.ref[i]) & (df3.modalidade == agg2.modalidade[i]) & (df3.porte == agg2.porte[i])].PD_12.values[0]
    p2 = df3[(df3.ref == agg2.ref[i]) & (df3.modalidade == agg2.modalidade[i]) & (df3.porte == agg2.porte[i])].PD_24.values[0]
    p3 = df3[(df3.ref == agg2.ref[i]) & (df3.modalidade == agg2.modalidade[i]) & (df3.porte == agg2.porte[i])].PD_36.values[0]
    p4 = df3[(df3.ref == agg2.ref[i]) & (df3.modalidade == agg2.modalidade[i]) & (df3.porte == agg2.porte[i])].PD_48.values[0]
    p5 = df3[(df3.ref == agg2.ref[i]) & (df3.modalidade == agg2.modalidade[i]) & (df3.porte == agg2.porte[i])].pd_monit.values[0]
  
    if agg2.estagio[i] == 1:
        prob.append(p)
        prob0.append(p0)
        prob1.append(p1)
        prob2.append(p2)
        prob3.append(p3)
        prob4.append(p4)
        prob5.append(p5)       
        
    elif agg2.estagio[i] == 2:
        
        b = (0.11852 - 0.05478*math.log(max(0.003, p)))**2          
        b0 = (0.11852 - 0.05478*math.log(max(0.003, p0)))**2     
        b1 = (0.11852 - 0.05478*math.log(max(0.003, p1)))**2
        b2 = (0.11852 - 0.05478*math.log(max(0.003, p2)))**2
        b3 = (0.11852 - 0.05478*math.log(max(0.003, p3)))**2
        b4 = (0.11852 - 0.05478*math.log(max(0.003, p4)))**2
        b5 = (0.11852 - 0.05478*math.log(max(0.003, p5)))**2
        
        m = (1 + (3 - 2.5) * b)/(1 - (1.5) * b)         
        m0 = (1 + (3 - 2.5) * b0)/(1 - (1.5) * b0)      
        m1 = (1 + (3 - 2.5) * b1)/(1 - (1.5) * b1)
        m2 = (1 + (3 - 2.5) * b2)/(1 - (1.5) * b2)
        m3 = (1 + (3 - 2.5) * b3)/(1 - (1.5) * b3)
        m4 = (1 + (3 - 2.5) * b4)/(1 - (1.5) * b4)
        m5 = (1 + (3 - 2.5) * b5)/(1 - (1.5) * b5)
        
        prob.append(p*m)        
        prob0.append(p0*m0)        
        prob1.append(p1*m1)
        prob2.append(p2*m2)
        prob3.append(p3*m3)
        prob4.append(p4*m4)
        prob5.append(p5*m5)
        
    else:
        
        prob.append(1.00)       
        prob0.append(1.00)
        prob1.append(1.00)
        prob2.append(1.00)
        prob3.append(1.00)  
        prob4.append(1.00)
        prob5.append(1.00)

agg2['pd'] = prob
agg2['td'] = prob0
agg2['pd_12'] = prob1
agg2['pd_24'] = prob2
agg2['pd_36'] = prob3
agg2['pd_48'] = prob4
agg2['pd_mnt'] = prob5

agg2['ecl'] = agg2['pd'] * agg2['lgd'] * agg2['saldo']
agg2['ecl2'] = agg2['pd_mnt'] * agg2['lgd'] * agg2['saldo']
agg2['ecl3'] = agg2['td'] * agg2['lgd'] * agg2['saldo']
agg2['ecl4'] = agg2['pd_12'] * agg2['lgd'] * agg2['saldo']
agg2['ecl5'] = agg2['pd_24'] * agg2['lgd'] * agg2['saldo']
agg2['ecl6'] = agg2['pd_36'] * agg2['lgd'] * agg2['saldo']
agg2['ecl7'] = agg2['pd_48'] * agg2['lgd'] * agg2['saldo']
# --- Cell 20 ---
hst2 = agg2[agg2['nivel_risco'] != 'HH'][['ref', 'saldo', 'saldo_inad', 'prov', 'ecl', 'ecl2','ecl3', 'ecl4','ecl5', 'ecl6', 'ecl7', 'perda_att']].groupby(['ref']).sum(['prov', 'saldo', 'ecl', 'perda_att'])
# --- Cell 21 ---
hst2['iprov'] = hst2['prov']/hst2['saldo']
hst2['inad90'] = hst2['saldo_inad']/hst['saldo']
hst2['iPE1'] = hst2['ecl']/hst['saldo']
hst2['iPE2'] = hst2['ecl2']/hst['saldo']
hst2['perda_obs'] = hst2['perda_att']/hst2['saldo']
#hst2['dif'] = hst2['iPE'] - hst2['iprov']
# --- Cell 22 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
ax2 = ax1.twinx() 
# this is to plot the kde
sns.lineplot(data=hst2[0:96], x='ref', y = 'ecl', color='black', ax = ax1, label='ECL')
sns.lineplot(data=hst2[96:], x='ref', y = 'ecl', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst2[0:96], x='ref', y = 'ecl2', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst2[96:], x='ref', y = 'ecl2', color='black', ax = ax1)
sns.lineplot(data=hst2, x='ref', y = 'prov',  ax = ax1, label='PCLD 2682')
#sns.lineplot(data=df1[60:148][df1['ref_r'].between(60, 148, inclusive='both')], x='ref_r', y = 'pd', ax = ax2)

#sns.lineplot(data=hst2[60:156], x='ref', y = 'ecl3', linestyle='dashed', color='orange', ax = ax1)
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl4', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl5', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl6', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl7', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'prov', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'perda_att', linestyle='dashed')


ax1.axvline(72, ls='--', c='grey')
ax1.axvline(96, ls='--', c='grey')


# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 23 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
ax2 = ax1.twinx() 
# this is to plot the kde
sns.lineplot(data=hst2, x='ref', y = 'ecl', linestyle='dotted', color='grey', ax = ax1, label='ECL')
sns.lineplot(data=hst2, x='ref', y = 'ecl2', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst2, x='ref', y = 'prov', color='black', ax = ax1, label='PCLD 2682')
sns.lineplot(data=hst2, x='ref', y = 'ecl3',  ax = ax1, label='ECL TD')
sns.lineplot(data=hst2, x='ref', y = 'ecl4',  ax = ax1, label='ECL PD$_{mm}$')
#sns.lineplot(data=df1[60:148][df1['ref_r'].between(60, 148, inclusive='both')], x='ref_r', y = 'pd', ax = ax2)

#sns.lineplot(data=hst2[60:156], x='ref', y = 'ecl3', linestyle='dashed', color='orange', ax = ax1)
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl4', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl5', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl6', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl7', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'prov', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'perda_att', linestyle='dashed')


ax1.axvline(72, ls='--', c='grey')
ax1.axvline(96, ls='--', c='grey')


# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 24 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
ax2 = ax1.twinx() 
# this is to plot the kde
#sns.lineplot(data=hst2[65:75], x='ref', y = 'ecl', linestyle='dotted', color='grey', ax = ax1, label='ECL')
#sns.lineplot(data=hst2[65:75], x='ref', y = 'ecl2', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst2[70:80], x='ref', y = 'prov', color='black', ax = ax1, label='PCLD 2682')
sns.lineplot(data=hst2[70:80], x='ref', y = 'ecl3',  ax = ax1, label='ECL TD')
sns.lineplot(data=hst2[70:80], x='ref', y = 'ecl4',  ax = ax1, label='ECL PD$_{mm}$')
#sns.lineplot(data=hst2[70:80], x='ref', y = 'saldo_inad',  ax = ax2, label='NPL', color='green')
#sns.lineplot(data=df1[60:148][df1['ref_r'].between(60, 148, inclusive='both')], x='ref_r', y = 'pd', ax = ax2)

#sns.lineplot(data=hst2[60:156], x='ref', y = 'ecl3', linestyle='dashed', color='orange', ax = ax1)
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl4', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl5', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl6', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl7', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'prov', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'perda_att', linestyle='dashed')


ax1.axvline(72, ls='--', c='red')
#ax1.axvline(96, ls='--', c='grey')


# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 25 ---
serie_pd_2
# --- Cell 26 ---
df3 = df1.sort_values(['porte', 'modalidade', 'fx' 'ref']).merge(pd_monit[['porte', 'modalidade', 'pd_monit']], how='left', on=['modalidade', 'porte'])
df3 = df3.merge(pd_model[['porte', 'modalidade', 'pd']].rename(columns={'pd':'pd_model'}), how='left', on=['modalidade', 'porte'])

df3['td'] = df3.groupby(['porte','modalidade'])['pd'].shift(12)
df3['PD_12'] = df3.groupby(['porte','modalidade']).rolling(window=12)['td'].mean().reset_index()['td']
df3['PD_24'] = df3.groupby(['porte','modalidade']).rolling(window=24)['td'].mean().reset_index()['td']
df3['PD_36'] = df3.groupby(['porte','modalidade']).rolling(window=36)['td'].mean().reset_index()['td']
df3['PD_48'] = df3.groupby(['porte','modalidade']).rolling(window=48)['td'].mean().reset_index()['td']


# --- Cell 27 ---

# --- Cell 28 ---
a = agg.merge(lgd, how='left', on=['porte', 'modalidade']).merge(serie_pd_2.drop('qtd', axis=1), how='left', on=['ref', 'fx_atraso', 'porte', 'modalidade'])
# --- Cell 29 ---

