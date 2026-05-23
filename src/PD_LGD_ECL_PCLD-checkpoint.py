# Converted from PD_LGD_ECL_PCLD-checkpoint.ipynb
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
probd.columns
# --- Cell 6 ---
probd = serie_pd[['ref', 'porte', 'modalidade', 'pd']]
# --- Cell 7 ---
pd_model = probd[(probd['ref'] > 0) & ((probd['ref'] < 48))].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean().reset_index()
pd_model
# --- Cell 8 ---
pd_monit = probd[probd['ref'].between(36, 60)].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean().reset_index()
pd_monit = pd_monit.rename(columns={'pd': 'pd_monit'})
pd_monit
# --- Cell 9 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
df  = probd.groupby(['modalidade', 'ref']).mean()

# this is to plot the kde
sns.lineplot(data=df, x='ref', y = 'pd',  hue='modalidade')

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 10 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

# data to create an example data frame
df  = probd.groupby(['porte', 'ref']).mean()

# this is to plot the kde
sns.lineplot(data=df, x='ref', y = 'pd',  hue='porte')

# beautifying the labels
plt.xlabel('value')
plt.ylabel('density')
plt.show()
# --- Cell 11 ---
#probd[(probd.modalidade == 2) & (probd.porte == 6)][['ref', 'pd']].plot(x = 'ref')
# --- Cell 12 ---
lgd_i = psql.read_sql('SELECT * FROM jpcosta.calculo_lgd60', connection)

lgd = lgd_i[lgd_i.ref > 0].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean('lgd').reset_index()
lgd
# --- Cell 13 ---
ecl = pd_model.merge(lgd, on=['porte', 'modalidade'], how='left').fillna(0.500)
ecl['ecl'] = ecl['pd'] * ecl['lgd']
ecl = ecl.merge(pd_monit, on=['porte', 'modalidade'], how='left')
ecl['ecl2'] = ecl['pd_monit'] * ecl['lgd']

ecl
# --- Cell 14 ---
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
# --- Cell 15 ---
pd.options.display.float_format = '{:2}'.format

agg = psql.read_sql('SELECT * FROM jpcosta.perda_obs', connection)

agg['prov'] = agg['nivel_risco'].map(dict_prov)*agg['saldo']
# --- Cell 16 ---
agg = agg.merge(ecl, how='left', on=['porte', 'modalidade'])
# --- Cell 17 ---
prob = []

for i in range(len(agg)):
    if agg.estagio[i] == 1:
        prob.append(agg.pd[i])
    elif agg.estagio[i] == 2:
        
        b = (0.11852 - 0.05478*math.log(max(0.003, agg.pd[i])))**2
        m = (1 + (3 - 2.5) * b)/(1 - (1.5) * b)
        
        prob.append(agg.pd[i]*m)
        
    else:
        prob.append(1.00)

agg['pd'] = prob

agg['ecl'] = agg['pd'] * agg['lgd'] * agg['saldo']
agg['ecl2'] = agg['pd_monit'] * agg['lgd'] * agg['saldo']
# --- Cell 18 ---
hst = agg[agg['nivel_risco'] != 'HH'][['ref', 'saldo', 'saldo_inad', 'prov', 'ecl', 'ecl2', 'perda_att']].groupby(['ref']).sum(['prov', 'saldo', 'ecl', 'perda_att'])
# --- Cell 19 ---
hst['iprov'] = hst['prov']/hst['saldo']
hst['inad90'] = hst['saldo_inad']/hst['saldo']
hst['iPE'] = hst['ecl']/hst['saldo']
hst['perda_obs'] = hst['perda_att']/hst['saldo']
hst['dif'] = hst['iPE'] - hst['iprov']
# --- Cell 20 ---
hst[['iPE','iprov','inad90', 'perda_obs', 'dif']]
# --- Cell 21 ---
pd.options.display.float_format = '{:2}'.format

agg = psql.read_sql('SELECT * FROM jpcosta.perda_obs', connection)

agg['prov'] = agg['nivel_risco'].map(dict_prov)*agg['saldo']
# --- Cell 22 ---
n = agg.ref.max() - 1
# --- Cell 23 ---
n
# --- Cell 24 ---
#agg['media'] = agg['saldo']/agg['qtd']

a = agg[(agg['nivel_risco'] != 'HH') & (agg.saldo > 0) & (agg.ref == n)].groupby(['porte', 'modalidade']).sum().reset_index()

a['inad'] = a['saldo_inad']/a['saldo']
a['media'] = a['saldo']/a['qtd']

tot = a.qtd.sum()
a['perc'] = a.qtd/tot

a = a[['porte', 'modalidade', 'media', 'saldo', 'inad', 'qtd', 'perc']][a['modalidade'] == 2]

a#.to_csv(path_or_buf='result_sim2.csv', sep=';', index=False, encoding='latin1')
# --- Cell 25 ---
teste = agg[(agg['porte']==1) & (agg['modalidade']==1)].groupby(['ref', 'modalidade']).sum().reset_index()
teste['tx'] = teste['saldo_inad']/teste['saldo']

teste['tx'].plot()
# --- Cell 26 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
df  = hst[['iPE','iprov','inad90', 'perda_obs']]#[60:n-82]

# this is to plot the kde
sns.lineplot(data=df, x='ref', y = 'iPE', label='iPE')
sns.lineplot(data=df, x='ref', y = 'iprov', label='iProv')
sns.lineplot(data=df, x='ref', y = 'inad90', label='Inad90')
sns.lineplot(data=df, x='ref', y = 'perda_obs', label='PO')

# beautifying the labels
plt.xlabel('Data de Referência')
plt.ylabel('')
plt.show()
# --- Cell 27 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
df1  = probd.groupby(['ref']).mean().reset_index()
df1['ref_r'] = df1['ref'] + 12

# this is to plot the kde
sns.lineplot(data=df1[df1['ref'].between(60, n-82, inclusive='both')], x='ref', y = 'pd')
sns.lineplot(data=df1[df1['ref_r'].between(60, n-82, inclusive='both')], x='ref_r', y = 'pd')

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 28 ---
df1['varpd'] = ((df1['pd']/df1['pd'].shift(1))-1).rolling(window=12).mean()
df['varnpl'] = ((df['inad90']/df['inad90'].shift(1))-1).rolling(window=12).mean()
# --- Cell 29 ---
inad = agg[(agg.nivel_risco != 'HH') & (agg.ref==n)][['porte', 'modalidade','saldo']].groupby(['porte', 'modalidade']).sum()
inad['inad'] = inad['saldo_inad']/inad['saldo']

inad
# --- Cell 30 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
#df1  = probd.groupby(['ref']).mean().reset_index()
#df1['ref_r'] = df1['ref'] + 12

# this is to plot the kde
sns.lineplot(data=df1[df1['ref_r'].between(60, n-82, inclusive='both')], x='ref_r', y = 'varpd', label = '%TD')
sns.lineplot(data=df, x='ref', y = 'varnpl', label = '%NPL')

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 31 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame

# this is to plot the kde
sns.lineplot(data=hst[36:145], x='ref', y = 'ecl', color='black')
sns.lineplot(data=hst[144:n-36], x='ref', y = 'ecl', linestyle='dotted', color='grey')
sns.lineplot(data=hst[36:157], x='ref', y = 'ecl2', linestyle='dotted', color='grey')
sns.lineplot(data=hst[156:n-36], x='ref', y = 'ecl2', color='black')
#sns.lineplot(data=hst[36:157], x='ref', y = 'perda_att', color='black')

ax.axvline(144, ls='--', c='grey')
ax.axvline(156, ls='--', c='grey')
ax.axvline(121, ls='--', c='grey')

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 32 ---
probd['td'] = probd.groupby(['porte','modalidade'])['pd'].shift(12)

probd['PD_12'] = probd.groupby(['porte','modalidade']).rolling(window=12)['td'].mean().reset_index()['td']
probd['PD_24'] = probd.groupby(['porte','modalidade']).rolling(window=24)['td'].mean().reset_index()['td']
probd['PD_36'] = probd.groupby(['porte','modalidade']).rolling(window=36)['td'].mean().reset_index()['td']
probd['PD_48'] = probd.groupby(['porte','modalidade']).rolling(window=48)['td'].mean().reset_index()['td']
# --- Cell 33 ---
probd = probd.merge(pd_monit[['porte', 'modalidade', 'pd_monit']], how='left', on=['modalidade', 'porte'])
probd = probd.merge(pd_model[['porte', 'modalidade', 'pd']].rename(columns={'pd':'pd_model'}), how='left', on=['modalidade', 'porte'])
# --- Cell 34 ---
probd[(probd.ref.between(142, 158)) & (probd.modalidade == agg.modalidade[i]) & (probd.porte == agg.porte[i])]
# --- Cell 35 ---
lgd[(lgd.porte == 2) & (lgd.modalidade == 3)]
# --- Cell 36 ---
pd.set_option('display.max_columns', None)
a = agg2[(agg2['porte']==2) & (agg2['modalidade']==3) & (agg2['ref']==144) & (agg2['nivel_risco'] != 'HH')]

a[['estagio', 'saldo', 'prov', 'ecl', 'ecl2', 'ecl3', 'ecl4', 'ecl5', 'ecl6', 'ecl7']].groupby('estagio').sum()
# --- Cell 37 ---
prob, prob0, prob1, prob2, prob3, prob4, prob5 = [], [], [], [], [], [], []

agg2 = agg[agg.ref <= max(probd.ref)]

for i in range(len(agg2)):
    p  = probd[(probd.ref == agg2.ref[i]) & (probd.modalidade == agg2.modalidade[i]) & (probd.porte == agg2.porte[i])].pd_model.values[0]
    p0 = probd[(probd.ref == agg2.ref[i]) & (probd.modalidade == agg2.modalidade[i]) & (probd.porte == agg2.porte[i])].td.values[0]
    p1 = probd[(probd.ref == agg2.ref[i]) & (probd.modalidade == agg2.modalidade[i]) & (probd.porte == agg2.porte[i])].PD_12.values[0]
    p2 = probd[(probd.ref == agg2.ref[i]) & (probd.modalidade == agg2.modalidade[i]) & (probd.porte == agg2.porte[i])].PD_24.values[0]
    p3 = probd[(probd.ref == agg2.ref[i]) & (probd.modalidade == agg2.modalidade[i]) & (probd.porte == agg2.porte[i])].PD_36.values[0]
    p4 = probd[(probd.ref == agg2.ref[i]) & (probd.modalidade == agg2.modalidade[i]) & (probd.porte == agg2.porte[i])].PD_48.values[0]
    p5 = probd[(probd.ref == agg2.ref[i]) & (probd.modalidade == agg2.modalidade[i]) & (probd.porte == agg2.porte[i])].pd_monit.values[0]
  
    if agg.estagio[i] == 1:
        prob.append(p)
        prob0.append(p0)
        prob1.append(p1)
        prob2.append(p2)
        prob3.append(p3)
        prob4.append(p4)
        prob5.append(p5)       
        
    elif agg.estagio[i] == 2:
        
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
# --- Cell 38 ---
hst2 = agg2[agg2['nivel_risco'] != 'HH'][['ref', 'saldo', 'saldo_inad', 'prov', 'ecl', 'ecl2','ecl3', 'ecl4','ecl5', 'ecl6', 'ecl7', 'perda_att']].groupby(['ref']).sum(['prov', 'saldo', 'ecl', 'perda_att'])
# --- Cell 39 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
ax2 = ax1.twinx() 
# this is to plot the kde
sns.lineplot(data=hst2[60:156], x='ref', y = 'ecl', color='black', ax = ax1)
sns.lineplot(data=hst2[155:n-36], x='ref', y = 'ecl', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst2[60:156], x='ref', y = 'ecl2', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst2[155:n-36], x='ref', y = 'ecl2', color='black', ax = ax1)
#sns.lineplot(data=hst2[60:n-36], x='ref', y = 'prov', color='black', ax = ax1)
#sns.lineplot(data=df1[60:148][df1['ref_r'].between(60, 148, inclusive='both')], x='ref_r', y = 'pd', ax = ax2)

sns.lineplot(data=hst2[60:156], x='ref', y = 'ecl3', linestyle='dashed', color='orange', ax = ax1)
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl4', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl5', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl6', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl7', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'prov', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'perda_att', linestyle='dashed')


ax1.axvline(134, ls='--', c='grey')
ax1.axvline(155, ls='--', c='grey')


# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 40 ---
choque = data=hst2[115:136][['prov','ecl','ecl3', 'ecl4']]
choque['prov2'] = choque['prov'].map('R$ {:,.2f}'.format)
choque['ecl2']  = choque['ecl'].map('R$ {:,.2f}'.format) 
choque['ecl32'] = choque['ecl3'].map('R$ {:,.2f}'.format)
choque['ecl42'] = choque['ecl4'].map('R$ {:,.2f}'.format)

choque['var_prov'] = (choque['prov'] - choque[choque.index == 115].prov.values[0])/choque[choque.index == 115].prov.values[0]
choque['var_ecl'] = (choque['ecl'] - choque[choque.index == 115].ecl.values[0])/choque[choque.index == 115].ecl.values[0]
choque['var_ecl3'] = (choque['ecl3'] - choque[choque.index == 115].ecl3.values[0])/choque[choque.index == 115].ecl3.values[0]
choque['var_ecl4'] = (choque['ecl4'] - choque[choque.index == 115].ecl4.values[0])/choque[choque.index == 115].ecl4.values[0]

choque[['var_prov','var_ecl','var_ecl3', 'var_ecl4']]
# --- Cell 41 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame

# this is to plot the kde
sns.lineplot(data=choque, x='ref', y = 'var_prov', label='Provisão')
sns.lineplot(data=choque, x='ref', y = 'var_ecl', label='ECL')
sns.lineplot(data=choque, x='ref', y = 'var_ecl3', label='ECL TD')
sns.lineplot(data=choque, x='ref', y = 'var_ecl4', label='ECL MA 12')



#ax1.axvline(134, ls='--', c='grey')
#ax1.axvline(155, ls='--', c='grey')


# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 42 ---
a = hst2[hst2.index==148][['saldo', 'ecl', 'ecl2']]

a['saldo'] = a['saldo'].map('R$ {:,.2f}'.format)
a['ecl'] = a['ecl'].map('R$ {:,.2f}'.format)
a['ecl2'] = a['ecl2'].map('R$ {:,.2f}'.format)

a
# --- Cell 43 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame

# this is to plot the kde
sns.lineplot(data=hst2[60:n-36], x='ref', y = 'ecl', linestyle='dotted', color='grey')
sns.lineplot(data=hst2[60:n-36], x='ref', y = 'ecl2', linestyle='dotted', color='grey')
sns.lineplot(data=hst2[60:], x='ref', y = 'ecl3', linestyle='dashed')
sns.lineplot(data=hst2[60:], x='ref', y = 'ecl4', linestyle='dashed')
sns.lineplot(data=hst2[60:], x='ref', y = 'ecl5', linestyle='dashed')
sns.lineplot(data=hst2[60:], x='ref', y = 'ecl6', linestyle='dashed')
sns.lineplot(data=hst2[60:], x='ref', y = 'ecl7', linestyle='dashed')
#sns.lineplot(data=hst2[60:], x='ref', y = 'prov', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'perda_att', linestyle='dashed')


ax.axvline(144, ls='--', c='grey')
ax.axvline(156, ls='--', c='grey')
ax.axvline(121, ls='--', c='grey')

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 44 ---
hst2['iprov'] = hst2['prov']/hst['saldo']
hst2['inad90'] = hst2['saldo_inad']/hst['saldo']
hst2['iPE'] = hst2['ecl']/hst['saldo']
hst2['perda_obs'] = hst2['perda_att']/hst['saldo']
hst2['dif'] = hst2['iPE'] - hst2['iprov']
# --- Cell 45 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame

# this is to plot the kde
sns.lineplot(data=hst[36:145], x='ref', y = 'ecl', color='black')
sns.lineplot(data=hst[144:n-36], x='ref', y = 'ecl', linestyle='dotted', color='grey')
sns.lineplot(data=hst[36:157], x='ref', y = 'ecl2', linestyle='dotted', color='grey')
sns.lineplot(data=hst[156:n-36], x='ref', y = 'ecl2', color='black')
#sns.lineplot(data=hst[36:157], x='ref', y = 'perda_att', color='black')

ax.axvline(144, ls='--', c='grey')
ax.axvline(156, ls='--', c='grey')
ax.axvline(121, ls='--', c='grey')

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 46 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
df1  = probd.groupby(['ref']).mean().reset_index()
df1['ref_r'] = df1['ref'] + 12

# this is to plot the kde
sns.lineplot(data=df1[df1['ref'].between(60, n-82, inclusive='both')], x='ref', y = 'pd')
sns.lineplot(data=df1[df1['ref_r'].between(60, n-82, inclusive='both')], x='ref_r', y = 'pd')
sns.lineplot(data=df, x='ref', y = 'inad90', label='PO')

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 47 ---
df1
# --- Cell 48 ---
agg[(agg.nivel_risco != 'HH') & (agg.ref==n)].saldo_inad.sum()/agg[(agg.nivel_risco != 'HH') & (agg.ref==n)].saldo.sum()
# --- Cell 49 ---
agg['Dif'] = agg['prov'] - agg['ecl']
# --- Cell 50 ---
agg[(agg.nivel_risco != 'HH') & (agg.ref==n)][['nivel_risco','saldo','saldo_inad', 'prov', 'ecl', 'Dif']].groupby('nivel_risco').sum()
# --- Cell 51 ---
inad = agg[(agg.nivel_risco != 'HH') & (agg.ref==n)][['porte', 'modalidade','saldo','saldo_inad']].groupby(['porte', 'modalidade']).sum()
inad['inad'] = inad['saldo_inad']/inad['saldo']

inad
# --- Cell 52 ---
import seaborn as sns
import matplotlib.pyplot as plt

ax = sns.barplot(x="modalidade", y="saldo", data=agg[(agg.nivel_risco != 'HH') & (agg.ref==n)])
# --- Cell 53 ---
import seaborn as sns
import matplotlib.pyplot as plt

ax = sns.barplot(x="porte", y="saldo", data=agg[(agg.nivel_risco != 'HH') & (agg.ref==n)])
# --- Cell 54 ---

