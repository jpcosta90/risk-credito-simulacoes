# Converted from Analise_final_simulacao.ipynb
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
#carteira
agg = psql.read_sql('SELECT * FROM jpcosta.perda_obs_atr', connection)
# --- Cell 5 ---
#Série de TD
serie_pd_2 = psql.read_sql('SELECT * FROM jpcosta.calculo_pd_2', connection)
# --- Cell 6 ---
#serie de LGD
lgd_i = psql.read_sql('SELECT * FROM jpcosta.calculo_lgd60', connection)
# --- Cell 7 ---
df1 = serie_pd_2[['ref', 'porte', 'modalidade', 'qtd', 'qtd_inad']].groupby(['ref', 'porte', 'modalidade']).sum().reset_index()

probd = df1['qtd_inad']/df1['qtd']

df1['pd'] = probd
# --- Cell 8 ---
pd_model = df1[(df1['ref'] > 0) & ((df1['ref'] < 48))].drop('ref', axis=1).groupby(['porte', 'modalidade'])\
# %magic:             .mean().reset_index().drop(['qtd', 'qtd_inad'], axis=1)
pd_model
# --- Cell 9 ---
pd_monit = df1[df1['ref'].between(72, 84)].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean().reset_index()
pd_monit = pd_monit.rename(columns={'pd': 'pd_monit'}).drop(['qtd', 'qtd_inad'], axis=1)
pd_monit


# --- Cell 10 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

sns.set_style("white")
sns.despine(left=True)

fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
df  = df1.groupby(['modalidade', 'ref']).mean()

# this is to plot the kde
sns.lineplot(data=df.reset_index()[df.reset_index()['ref'] > 12], x='ref', y = 'pd',  hue='modalidade', linewidth=2.5)

sns.despine(offset=10, trim=False);

# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 11 ---
#serie de LGD
lgd_bst = psql.read_sql('SELECT * FROM jpcosta.calculo_lgd_bst', connection)

lgdbest = lgd_bst[lgd_bst.ref > 0].drop('ref', axis=1).groupby(['modalidade', 'fx_atraso']).mean('lgd').reset_index()
lgdbest
# --- Cell 12 ---
ecl = pd_model.merge(lgd.drop(['porte'], axis=1), on=['modalidade'], how='left').fillna(0.500)
ecl['ecl'] = ecl['pd'] * ecl['lgd']
ecl = ecl.merge(pd_monit, on=['porte', 'modalidade'], how='left')
ecl['ecl2'] = ecl['pd_monit'] * ecl['lgd']

ecl
# --- Cell 13 ---
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
# --- Cell 14 ---
df2 = agg[['ref', 'nivel_risco','fx_atraso' , 'porte', 'qtd','modalidade', 'estagio', 'saldo', 'saldo_inad', 'perda_att']]\
# %magic:         .groupby(['ref', 'nivel_risco', 'fx_atraso' ,'porte', 'modalidade', 'estagio']).sum().reset_index()

df2['prov'] = df2['nivel_risco'].map(dict_prov)*df2['saldo']

df2 = df2.merge(ecl, how='left', on=['porte', 'modalidade'])

df2
# --- Cell 15 ---
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
# --- Cell 16 ---
hst = df2[df2['nivel_risco'] != 'HH'][['ref', 'saldo', 'saldo_inad', 'prov', 'ecl', 'ecl2', 'perda_att']].groupby(['ref']).sum(['prov', 'saldo', 'ecl', 'perda_att'])
# --- Cell 17 ---
hst['iprov'] = hst['prov']/hst['saldo']
hst['inad90'] = hst['saldo_inad']/hst['saldo']
hst['iPE'] = hst['ecl']/hst['saldo']
hst['perda_obs'] = hst['perda_att']/hst['saldo']
hst['dif'] = hst['iPE'] - hst['iprov']
# --- Cell 18 ---
import seaborn as sns
import matplotlib.pyplot as plt
sns.color_palette("ch:s=.25,rot=-.25", as_cmap=True)

sns.set_style("white")
sns.set_context("paper")


#sns.set_style()
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
df  = hst[['iPE','iprov','inad90', 'perda_obs']]#[60:n-82]

# this is to plot the kde
sns.lineplot(data=df[:120], x='ref', y = 'iPE', label='iPE', linewidth=2.5)
sns.lineplot(data=df[:120], x='ref', y = 'iprov', label='iProv', linewidth=2.5)
sns.lineplot(data=df[:120], x='ref', y = 'inad90', label='NPL', linewidth=2.5)
#sns.lineplot(data=df[:120], x='ref', y = 'perda_obs', label='PO')

sns.despine(offset=20, trim=False);

ax.axvline(72, ls='--', c='red')

# beautifying the labels
plt.xlabel('Período')
plt.ylabel('')
plt.show()
# --- Cell 19 ---
n = agg.ref.max()
# --- Cell 20 ---
df3 = df1.sort_values(['porte', 'modalidade', 'ref']).merge(pd_monit[['porte', 'modalidade', 'pd_monit']], how='left', on=['modalidade', 'porte'])
df3 = df3.merge(pd_model[['porte', 'modalidade', 'pd']].rename(columns={'pd':'pd_model'}), how='left', on=['modalidade', 'porte'])

df3['td'] = df3.groupby(['porte','modalidade'])['pd'].shift(12)
df3['PD_12'] = df3.groupby(['porte','modalidade']).rolling(window=12)['td'].mean().reset_index()['td']
df3['PD_24'] = df3.groupby(['porte','modalidade']).rolling(window=24)['td'].mean().reset_index()['td']
df3['PD_36'] = df3.groupby(['porte','modalidade']).rolling(window=36)['td'].mean().reset_index()['td']
df3['PD_48'] = df3.groupby(['porte','modalidade']).rolling(window=48)['td'].mean().reset_index()['td']
# --- Cell 21 ---
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

# --- Cell 22 ---
hst2 = agg2[agg2['nivel_risco'] != 'HH'][['ref', 'saldo', 'saldo_inad', 'prov', 'ecl', 'ecl2','ecl3', 'ecl4','ecl5', 'ecl6', 'ecl7', 'perda_att']].groupby(['ref']).sum(['prov', 'saldo', 'ecl', 'perda_att'])
# --- Cell 23 ---
hst2['iprov'] = hst2['prov']/hst2['saldo']
hst2['inad90'] = hst2['saldo_inad']/hst['saldo']
hst2['iPE1'] = hst2['ecl']/hst['saldo']
hst2['iPE2'] = hst2['ecl2']/hst['saldo']
hst2['perda_obs'] = hst2['perda_att']/hst2['saldo']
#hst2['dif'] = hst2['iPE'] - hst2['iprov']
# --- Cell 24 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
#ax2 = ax1.twinx() 
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

plt.ticklabel_format(style='plain', axis='y')

ax1.axvline(72, ls='--', c='grey')
ax1.axvline(96, ls='--', c='grey')


# beautifying the labels
plt.xlabel('Período')
plt.ylabel('')
plt.show()
# --- Cell 25 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
#ax2 = ax1.twinx() 
# this is to plot the kde
sns.lineplot(data=hst2, x='ref', y = 'ecl', linestyle='dotted', color='grey', ax = ax1, label='ECL')
sns.lineplot(data=hst2, x='ref', y = 'ecl2', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst2, x='ref', y = 'prov', color='black', ax = ax1, label='PCLD 2682')
sns.lineplot(data=hst2, x='ref', y = 'ecl3',  ax = ax1, label='ECL PD')
sns.lineplot(data=hst2, x='ref', y = 'ecl4',  ax = ax1, label='ECL PD$_{mm}$')
#sns.lineplot(data=df1[60:148][df1['ref_r'].between(60, 148, inclusive='both')], x='ref_r', y = 'pd', ax = ax2)

#sns.lineplot(data=hst2[60:156], x='ref', y = 'ecl3', linestyle='dashed', color='orange', ax = ax1)
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl4', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl5', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl6', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl7', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'prov', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'perda_att', linestyle='dashed')

plt.ticklabel_format(style='plain', axis='y')
ax1.axvline(72, ls='--', c='grey')
ax1.axvline(96, ls='--', c='grey')


# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('')
plt.show()
# --- Cell 26 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
#ax2 = ax1.twinx() 
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
plt.ylabel('R$')
plt.show()
# --- Cell 27 ---
serie_pd_2
# --- Cell 28 ---
#df4 = serie_pd_2.sort_values(['porte', 'modalidade', 'fx_atraso', 'ref'])
#df4['td'] = df4.groupby(['porte','modalidade', 'fx_atraso'])['pd'].shift(12)
#df4['PD_12'] = df4.groupby(['porte','modalidade', 'fx_atraso']).rolling(window=12)['td'].mean().reset_index()['td']

pool = []

for i in range(len(serie_pd_2)):
    if serie_pd_2.fx_atraso[i] == 1:
        pool.append('0' + str(serie_pd_2.fx_atraso[i]) + '0' + '0' + str(serie_pd_2.modalidade[i]) + str(serie_pd_2.porte[i]))
    else:
        pool.append('0' + str(serie_pd_2.fx_atraso[i]) + '0' + str(serie_pd_2.modalidade[i]) + '00')

len(pool)
# --- Cell 29 ---
serie_pd_2['pool'] = pool

a = serie_pd_2[serie_pd_2['fx_atraso'] != 4]
a
# --- Cell 30 ---
pool = []

for i in range(len(agg)):
    if agg.fx_atraso[i] == 1:
        pool.append('0' + str(agg.fx_atraso[i]) + '0' + '0' + str(agg.modalidade[i]) + str(agg.porte[i]))
    else:
        pool.append('0' + str(agg.fx_atraso[i]) + '0' + str(agg.modalidade[i]) + '00')

len(pool)
# --- Cell 31 ---
agg['pool'] = pool
# --- Cell 32 ---
a = a.sort_values(['pool', 'ref'])
a['td'] =  a.groupby(['pool'])['pd'].shift(12)
a['PD_12'] = a.groupby(['pool']).rolling(window=12)['td'].mean().reset_index()['td']

a = a[['ref', 'pool', 'fx_atraso', 'qtd', 'qtd_inad']].groupby(['pool','fx_atraso', 'ref']).sum().reset_index()
p = a['qtd_inad']/a['qtd']

a['pd'] = p
a
# --- Cell 33 ---
a = a.sort_values(['pool', 'ref'])
a['td'] = a.groupby(['pool'])['pd'].shift(12)
a['PD_12'] = a.groupby(['pool']).rolling(window=12)['td'].mean().reset_index()['td']
a['PD_24'] = a.groupby(['pool']).rolling(window=24)['td'].mean().reset_index()['td']
a
# --- Cell 34 ---
l = agg[['modalidade', 'pool']].drop_duplicates().merge(lgd, how='left', on='modalidade')[['pool', 'lgd']]
l
# --- Cell 35 ---
b = agg[['ref', 'pool', 'fx_atraso', 'modalidade','nivel_risco', 'estagio', 'qtd', 'saldo', 'saldo_inad', 'perda_att']].groupby(['pool','fx_atraso', 'ref', 'nivel_risco', 'modalidade', 'estagio']).sum().reset_index()
b = b.merge(l, how='left', on = 'pool')
b
# --- Cell 36 ---
compara1 = agg2[['ref', 'fx_atraso', 'ecl3']].groupby(['ref', 'fx_atraso']).sum().reset_index()
compara1[(compara1['fx_atraso']==1) & (compara1['ref']==36)]
# --- Cell 37 ---
compara2 = agg3[['ref', 'fx_atraso', 'ecl3']].groupby(['ref', 'fx_atraso']).sum().reset_index()
compara2[(compara2['fx_atraso']==1) & (compara2['ref']==36)]
# --- Cell 38 ---
agg3 = b[(b.ref <= max(a.ref))].reset_index()
agg3
# --- Cell 39 ---
i = 23069
lgd[(lgd.modalidade == agg3.modalidade[i])]

chave_atr =  {'E' : 1,
              'F':  2,
              'G':  3,
              'H':  4,
              'HH': 4}

lgdbest[(lgdbest.modalidade == agg3.modalidade[i]) & (lgdbest.fx_atraso == chave_atr[agg3.nivel_risco[i]])]
#lgdbest[(lgdbest.modalidade == agg3.modalidade[i]) & (lgdbest.fx_atraso == chave_atr[agg3.nivel_risco[i]])]
# --- Cell 40 ---
pd_modelb = a[(a['ref'] > 0) & ((a['ref'] < 48))].drop('ref', axis=1).groupby(['pool'])\
# %magic:             .mean().reset_index().drop(['qtd', 'qtd_inad'], axis=1)
pd_modelb
# --- Cell 41 ---
pd_monitb = a[a['ref'].between(72, 84)].drop('ref', axis=1).groupby(['pool']).mean().reset_index()
pd_monitb = pd_monitb.rename(columns={'pd': 'pd_monit'}).drop(['qtd', 'qtd_inad'], axis=1)
pd_monitb
# --- Cell 42 ---
prob0, prob1, prob2, prob3, prob4, lgd_bst = [], [], [], [], [], []

agg3 = b[(b.ref <= max(a.ref))].reset_index()

for i in range(len(agg3)):
        if agg3.estagio[i] != 3:
            if len(a[(a.ref == agg3.ref[i]) & (a.pool == agg3.pool[i])]) > 0:
                p0 = a[(a.ref == agg3.ref[i]) & (a.pool == agg3.pool[i])].td.values[0]
                p1 = a[(a.ref == agg3.ref[i]) & (a.pool == agg3.pool[i])].PD_12.values[0]           
                p2 = pd_modelb[(pd_modelb.pool == agg3.pool[i])].pd.values[0] 
                p3 = pd_monitb[(pd_monitb.pool == agg3.pool[i])].pd_monit.values[0] 
                p4 = a[(a.ref == agg3.ref[i]) & (a.pool == agg3.pool[i])].PD_24.values[0]
                
            if agg3.estagio[i] == 1:
                prob0.append(p0)
                prob1.append(p1) 
                prob2.append(p2) 
                prob3.append(p3) 
                prob4.append(p4) 
                
            elif agg3.estagio[i] == 2:

                b0 = (0.11852 - 0.05478*math.log(max(0.003, p0)))**2     
                b1 = (0.11852 - 0.05478*math.log(max(0.003, p1)))**2
                b2 = (0.11852 - 0.05478*math.log(max(0.003, p2)))**2
                b3 = (0.11852 - 0.05478*math.log(max(0.003, p3)))**2
                b4 = (0.11852 - 0.05478*math.log(max(0.003, p4)))**2
                
                m0 = (1 + (3 - 2.5) * b0)/(1 - (1.5) * b0)      
                m1 = (1 + (3 - 2.5) * b1)/(1 - (1.5) * b1)
                m2 = (1 + (3 - 2.5) * b2)/(1 - (1.5) * b2)
                m3 = (1 + (3 - 2.5) * b3)/(1 - (1.5) * b3)
                m4 = (1 + (3 - 2.5) * b4)/(1 - (1.5) * b4)
                
                prob0.append(p0*m0)        
                prob1.append(p1*m1)
                prob2.append(p2*m2)
                prob3.append(p3*m3)
                prob4.append(p4*m4)
                
            lgd_bst.append(lgd[(lgd.modalidade == agg3.modalidade[i])])
            
        else:

            prob0.append(1.00)
            prob1.append(1.00)
            prob2.append(1.00)
            prob3.append(1.00)
            prob4.append(1.00)
            
            lgd_bst.append(lgdbest[(lgdbest.modalidade == agg3.modalidade[i]) & (lgdbest.fx_atraso == chave_atr[agg3.nivel_risco[i]])])

            
agg3['td'] = prob0
agg3['pd_12'] = prob1

agg3['pd_model'] = prob2
agg3['pd_monit'] = prob3

agg3['pd_24'] = prob4

agg3['lgd_bst'] = lgd_bst


agg3['ecl']  = agg3['pd_model'] * agg3['lgd'] * agg3['saldo']
agg3['ecl2'] = agg3['pd_monit'] * agg3['lgd'] * agg3['saldo']

agg3['ecl3'] = agg3['td'] * agg3['lgd'] * agg3['saldo']
agg3['ecl4'] = agg3['pd_12'] * agg3['lgd'] * agg3['saldo']

agg3['ecl5'] = np.where(agg3['estagio'] == 3, agg3['pd_12'] * agg3['lgd_bst'] * agg3['saldo'] ,agg3['pd_12'] * agg3['lgd'] * agg3['saldo'])

agg3['ecl6'] = agg3['pd_24'] * agg3['lgd'] * agg3['saldo']
# --- Cell 43 ---
hst3 = agg3[agg3['nivel_risco'] != 'HH'][['ref', 'saldo', 'ecl','ecl2', 'ecl3', 'ecl4', 'ecl5', 'ecl6']].groupby(['ref']).sum()
hst3
# --- Cell 44 ---
df  = hst3[['ecl']]#[60:n-82]

df['iprov'] = hst['prov']/hst['saldo']
df['inad90'] = hst['saldo_inad']/hst['saldo']
df['iPE'] = df['ecl']/hst['saldo']

# --- Cell 45 ---
import seaborn as sns
import matplotlib.pyplot as plt
sns.color_palette("ch:s=.25,rot=-.25", as_cmap=True)

sns.set_style("white")
sns.set_context("paper")


#sns.set_style()
# %magic: %matplotlib inline
fig, ax = plt.subplots(figsize=(15,10))
# data to create an example data frame
#df  = hst3[['iPE','iprov','inad90', 'perda_obs']]#[60:n-82]

# this is to plot the kde
sns.lineplot(data=df[:72], x='ref', y = 'iPE', label='iPE', linewidth=2.5)
sns.lineplot(data=df[:72], x='ref', y = 'iprov', label='iProv', linewidth=2.5)
sns.lineplot(data=df[:72], x='ref', y = 'inad90', label='NPL', linewidth=2.5)
#sns.lineplot(data=df[:120], x='ref', y = 'perda_obs', label='PO')

sns.despine(offset=20, trim=False);

#ax.axvline(72, ls='--', c='red')

# beautifying the labels
plt.xlabel('Período')
plt.ylabel('')
plt.show()
# --- Cell 46 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

sns.set_style("white")
sns.despine(left=True)

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
#ax2 = ax1.twinx() 
# this is to plot the kde
sns.lineplot(data=hst3[0:97], x='ref', y = 'ecl', color='black', ax = ax1, label='ECL', linewidth = 2)
sns.lineplot(data=hst3[96:], x='ref', y = 'ecl', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst3[0:96], x='ref', y = 'ecl2', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst3[96:], x='ref', y = 'ecl2', color='black', ax = ax1, linewidth = 2)
sns.lineplot(data=hst2, x='ref', y = 'prov',  ax = ax1, label='PCLD 2682', linewidth = 2)
#sns.lineplot(data=df1[60:148][df1['ref_r'].between(60, 148, inclusive='both')], x='ref_r', y = 'pd', ax = ax2)

#sns.lineplot(data=hst2[60:156], x='ref', y = 'ecl3', linestyle='dashed', color='orange', ax = ax1)
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl4', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl5', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl6', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'ecl7', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'prov', linestyle='dashed', color='grey')
#sns.lineplot(data=hst2[60:], x='ref', y = 'perda_att', linestyle='dashed')

plt.ticklabel_format(style='plain', axis='y')

ax1.axvline(72, ls='--', c='grey')
ax1.axvline(96, ls='--', c='grey')

sns.despine(offset=20, trim=False);

# beautifying the labels
plt.xlabel('Período')
plt.ylabel('')
plt.show()
# --- Cell 47 ---
sum(hst3['ecl'] - hst2['ecl'])
# --- Cell 48 ---
#carteira
pda = psql.read_sql('SELECT * FROM jpcosta.prd_anual', connection)
# --- Cell 49 ---
pda_lt = psql.read_sql('SELECT * FROM jpcosta.perda_lt_12', connection)
# --- Cell 50 ---
perda_ifrs = np.where(pda_lt['estagio'] == 1, pda_lt['perda_att_1'], pda_lt['perda_att_2'])
# --- Cell 51 ---
pda_lt['perda_ifrs'] = perda_ifrs

perda_ifrs9 = pda_lt[['ref', 'perda_ifrs', 'perda_att_2']].groupby('ref').sum()#.reset_index()
perda_ifrs9
# --- Cell 52 ---
hst2['npl'] = hst2['saldo_inad']/hst2['saldo']
hst2['iprov'] = hst2['prov']/hst2['saldo']
hst2['ipo_ifrs'] = perda_ifrs9['perda_ifrs']/hst2['saldo']
hst2['pe_ifrs'] = hst2['ecl4']/hst2['saldo']
hst2['pe_ifrs_atr'] = hst3['ecl4']/hst2['saldo'] 
# --- Cell 53 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
ax2 = ax1.twinx() 
# this is to plot the kde
#sns.lineplot(data=hst2[:171], x='ref', y = 'ecl', linestyle='dotted', color='grey', ax = ax1, label='ECL')
#sns.lineplot(data=hst2[:171], x='ref', y = 'ecl2', linestyle='dotted', color='grey', ax = ax1)
sns.lineplot(data=hst2[:171], x='ref', y = 'npl',ax = ax1, label='NPL')
sns.lineplot(data=hst2[:171], x='ref', y = 'iprov', color='black', ax = ax1, label='PCLD 2682')
#sns.lineplot(data=hst2[:171], x='ref', y = 'perda_att',  ax = ax1, label='Perda Obs.')
sns.lineplot(data=hst2[:171], x='ref', y = 'ipo_ifrs',  ax = ax1, label='Perda IFRS9')
#sns.lineplot(data=pda[:171], x='ref', y = 'perda_anual',  ax = ax1, label='Perda Anualizada')
sns.lineplot(data=hst2[:171], x='ref', y = 'pe_ifrs',  ax = ax1, label='ECL PD$_{mm}$')


#sns.lineplot(data=hst2[:171], x='ref', y = 'pe_ifrs_atr',  ax = ax1, label='ECL PD$_{mm} Atraso$')

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
# --- Cell 54 ---
hst2
# --- Cell 55 ---
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
#sns.lineplot(data=hst2[65:80], x='ref', y = 'ecl3',  ax = ax1, label='ECL TD')
sns.lineplot(data=hst2[70:80], x='ref', y = 'ecl4',  ax = ax1, label='ECL PD$_{mm}$')

#sns.lineplot(data=hst3[68:80], x='ref', y = 'ecl3',  ax = ax1, label='ECL TD Atraso')
sns.lineplot(data=hst3[70:80], x='ref', y = 'ecl4',  ax = ax1, label='ECL PD$_{mm}$ Atraso')

sns.lineplot(data=hst3[70:80], x='ref', y = 'ecl3',  ax = ax1, label='ECL TD$_{Atr}$')
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
# --- Cell 56 ---
#carteira
prejuizo = psql.read_sql('SELECT * FROM jpcosta.prejuizo', connection)
# --- Cell 57 ---
prejuizo
# --- Cell 58 ---
teste = ((prejuizo['ref'] - 1) - ((prejuizo['ref'] - 1) % 3)) + 3
prejuizo['ref'] = teste
preju_tri = prejuizo[['perda_anual', 'ref']].groupby('ref').sum()
preju_tri
# --- Cell 59 ---
PCLD_2682 = hst2.reset_index()[['ref','prov']]
PCLD_2682 = PCLD_2682[PCLD_2682['ref'] % 3 == 0]
PCLD_2682['delta_pcld'] = PCLD_2682['prov'] - PCLD_2682['prov'].shift(1)
PCLD_2682 = PCLD_2682.set_index('ref')[['delta_pcld']]
PCLD_2682
# --- Cell 60 ---
pe_ifrs = hst2.reset_index()[['ref','ecl4']]
pe_ifrs = pe_ifrs[pe_ifrs['ref'] % 3 == 0]
pe_ifrs['delta_pe_ifrs9mm'] = pe_ifrs['ecl4'] - pe_ifrs['ecl4'].shift(1)
pe_ifrs = pe_ifrs.set_index('ref')[['delta_pe_ifrs9mm']]
pe_ifrs
# --- Cell 61 ---
PE_IFRS_st = np.where(hst3.reset_index()['ref'] < 96, hst3['ecl'], hst3['ecl2'])
hst3['PE_IFRS_st'] = PE_IFRS_st

pe_ifrs2 = hst3.reset_index()[['ref','PE_IFRS_st']]

pe_ifrs2 = pe_ifrs2[pe_ifrs2['ref'] % 3 == 0]
pe_ifrs2['delta_pe_ifrs9st'] = pe_ifrs2['PE_IFRS_st'] - pe_ifrs2['PE_IFRS_st'].shift(1)

pe_ifrs2 = pe_ifrs2.set_index('ref')[['delta_pe_ifrs9st']]

pe_ifrs2
# --- Cell 62 ---
pe_ifrs3 = hst3.reset_index()[['ref','ecl4']]

pe_ifrs3 = pe_ifrs3[pe_ifrs3['ref'] % 3 == 0]
pe_ifrs3['delta_pe_ifrs9atr'] = pe_ifrs3['ecl4'] - pe_ifrs3['ecl4'].shift(1)
pe_ifrs3 = pe_ifrs3.set_index('ref')

pe_ifrs3 = pe_ifrs3[['delta_pe_ifrs9atr']]

pe_ifrs3
# --- Cell 63 ---
PE_IFRS_st = np.where(hst2.reset_index()['ref'] < 96, hst2['ecl'], hst2['ecl2'])
hst2['PE_IFRS_st'] = PE_IFRS_st

pe_ifrs4 = hst2.reset_index()[['ref','PE_IFRS_st']]

pe_ifrs4 = pe_ifrs4[pe_ifrs4['ref'] % 3 == 0]
pe_ifrs4['delta_pe_ifrs9st2'] = pe_ifrs4['PE_IFRS_st'] - pe_ifrs4['PE_IFRS_st'].shift(1)

pe_ifrs4 = pe_ifrs4.set_index('ref')[['delta_pe_ifrs9st2']]

pe_ifrs4
# --- Cell 64 ---
pe_ifrs6 = hst3.reset_index()[['ref','ecl3']]

pe_ifrs6 = pe_ifrs6[pe_ifrs6['ref'] % 3 == 0]
pe_ifrs6['delta_pe_ifrs9atr_td'] = pe_ifrs6['ecl3'] - pe_ifrs6['ecl3'].shift(1)
pe_ifrs6 = pe_ifrs6.set_index('ref')

pe_ifrs6 = pe_ifrs6[['delta_pe_ifrs9atr_td']]

pe_ifrs6
# --- Cell 65 ---
pe_ifrs7 = hst3.reset_index()[['ref','ecl6']]

pe_ifrs7 = pe_ifrs7[pe_ifrs7['ref'] % 3 == 0]
pe_ifrs7['delta_pe_ifrs924'] = pe_ifrs7['ecl6'] - pe_ifrs7['ecl6'].shift(1)
pe_ifrs7 = pe_ifrs7.set_index('ref')

pe_ifrs7 = pe_ifrs7[['delta_pe_ifrs924']]

pe_ifrs7
# --- Cell 66 ---
base_desp = PCLD_2682.join(pe_ifrs2).join(pe_ifrs).join(pe_ifrs3).join(pe_ifrs4).join(pe_ifrs6).join(pe_ifrs7).join(preju_tri)
base_desp = base_desp.fillna(0)
base_desp
# --- Cell 67 ---
base_desp['d_2682'] = base_desp['perda_anual'] + base_desp['delta_pcld']
base_desp['d_ifrs'] = base_desp['perda_anual'] + base_desp['delta_pe_ifrs9st']
base_desp['d_ifrsmm'] = base_desp['perda_anual'] + base_desp['delta_pe_ifrs9mm']
base_desp['d_ifrsatr'] = base_desp['perda_anual'] + base_desp['delta_pe_ifrs9atr']
base_desp['d_ifrs2'] = base_desp['perda_anual'] + base_desp['delta_pe_ifrs9st2']
base_desp['d_ifrs_td'] = base_desp['perda_anual'] + base_desp['delta_pe_ifrs9atr_td']
base_desp['d_ifrs_24'] = base_desp['perda_anual'] + base_desp['delta_pe_ifrs924']

base_desp
# --- Cell 68 ---
base_desp_2 = base_desp.join(hst2[['saldo']])
base_desp_2['d_2682'] = base_desp_2['d_2682']/base_desp_2['saldo']
base_desp_2['d_ifrs'] = base_desp_2['d_ifrs']/base_desp_2['saldo']
base_desp_2['d_ifrs2'] = base_desp_2['d_ifrs2']/base_desp_2['saldo']
base_desp_2['d_ifrsmm'] = base_desp_2['d_ifrsmm']/base_desp_2['saldo']
base_desp_2['d_ifrsatr'] = base_desp_2['d_ifrsatr']/base_desp_2['saldo']
base_desp_2['d_ifrs_td'] = base_desp_2['d_ifrs_td']/base_desp_2['saldo']
base_desp_2['d_ifrs_24'] = base_desp_2['d_ifrs_24']/base_desp_2['saldo']
# --- Cell 69 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

sns.set_style("white")
sns.despine(left=True)

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
#ax2 = ax1.twinx() 
# this is to plot the kde

sns.lineplot(data=base_desp_2[12:], x='ref', y = 'd_2682', ax = ax1, label='PCLD 2682')

sns.lineplot(data=base_desp_2[12:], x='ref', y = 'd_ifrs',  ax = ax1, color='blue', label='ECL$_{atr}$', linewidth=2.5)

sns.lineplot(data=base_desp_2[12:], x='ref', y = 'd_ifrs2',  ax = ax1, label='ECL$_{st}$', linewidth=2.5)
#sns.lineplot(data=base_desp[12:], x='ref', y = 'd_ifrsmm',  ax = ax1, label='ECL$_{mm}$')

#sns.lineplot(data=base_desp[12:], x='ref', y = 'd_ifrsatr',  ax = ax1, label='ECL$_{atr}$')

#sns.lineplot(data=base_desp[12:], x='ref', y = 'd_ifrs_td',  ax = ax1, label='ECL$_TD{atr}$')

#sns.lineplot(data=base_desp[15:], x='ref', y = 'd_ifrslgd',  ax = ax1, label='ECL$_{lgd}$')

ax1.axvline(72, ls='--', c='grey')
ax1.axvline(96, ls='--', c='grey')

sns.despine(offset=20, trim=False);

# beautifying the labels
plt.xlabel('Período')
plt.ylabel('Despesa de Provisão')

plt.show()
# --- Cell 70 ---
import seaborn as sns
import matplotlib.pyplot as plt
# %magic: %matplotlib inline

sns.set_style("white")
sns.despine(left=True)

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
#ax2 = ax1.twinx() 
# this is to plot the kde

sns.lineplot(data=base_desp_2[15:], x='ref', y = 'd_2682', ax = ax1, label='PCLD 2682')

#sns.lineplot(data=base_desp[12:], x='ref', y = 'd_ifrs',  ax = ax1, label='ECL$_{st}$')

#sns.lineplot(data=base_desp_2[12:], x='ref', y = 'd_ifrsmm',  ax = ax1, label='ECL$_{mm}$')

sns.lineplot(data=base_desp_2[15:], x='ref', y = 'd_ifrs_td',  ax = ax1, label='ECL$_{TD}$', linewidth=2.5)

sns.lineplot(data=base_desp_2[15:], x='ref', y = 'd_ifrsatr',  ax = ax1, label='ECL$_{mm12}$', linewidth=2.5)

sns.lineplot(data=base_desp_2[15:], x='ref', y = 'd_ifrs_24',  ax = ax1, label='ECL$_{mm24}$', linewidth=2.5)

#sns.lineplot(data=base_desp[15:], x='ref', y = 'd_ifrslgd',  ax = ax1, label='ECL$_{lgd}$')

ax1.axvline(72, ls='--', c='grey')
ax1.axvline(96, ls='--', c='grey')

sns.despine(offset=20, trim=False);

# beautifying the labels
plt.xlabel('Período')
plt.ylabel('Despesa de Provisão')

plt.show()
# --- Cell 71 ---
print(base_desp_2['d_ifrs_td'].var()/base_desp_2['d_ifrs_td'].mean())
print(base_desp_2['d_ifrsatr'].var()/base_desp_2['d_ifrsatr'].mean())
print(base_desp_2['d_ifrs_24'].var()/base_desp_2['d_ifrs_td'].mean())

# --- Cell 72 ---
import seaborn as sns
import matplotlib.pyplot as plt

plt.ticklabel_format(style='plain', axis='y',useOffset=False)

# %magic: %matplotlib inline

fig, ax1 = plt.subplots(figsize=(15,10))
# data to create an example data frame
ax2 = ax1.twinx() 
# this is to plot the kde

sns.lineplot(data=hst2, x='ref', y = 'saldo', ax = ax1, label='Saldo Contábil')

ax1.axvline(72, ls='--', c='red')
ax1.axvline(96, ls='--', c='grey')


# beautifying the labels
plt.xlabel('Safra')
plt.ylabel('TD')
plt.show()
# --- Cell 73 ---
hst2[96:97][['saldo']]
# --- Cell 74 ---
base_desp[base_desp.index == 96][['d_ifrs']]
