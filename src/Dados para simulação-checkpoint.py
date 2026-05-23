# Converted from Dados para simulação-checkpoint.ipynb
# --- Cell 1 ---
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
# --- Cell 2 ---
saldo = []

for i in range(1000000):
    saldo.append(np.random.lognormal(7.0, 0.1, size=None))
    

np.mean(saldo)
# --- Cell 3 ---
connection = pg.connect("host=localhost dbname=Simulacred user=postgres password=12345678")
# --- Cell 4 ---
agg = psql.read_sql('SELECT * FROM jpcosta.perda_obs', connection)
# --- Cell 5 ---
agg
# --- Cell 6 ---
hst = agg[agg['nivel_risco'] != 'HH'][['ref', 'porte', 'modalidade', 'saldo', 'saldo_inad', 'qtd']].groupby(['ref', 'porte','modalidade']).sum(['prov', 'saldo', 'ecl', 'perda_att']).reset_index()
# --- Cell 7 ---
filtro = hst[(hst['porte']==1) & (hst['modalidade']==1)].reset_index()

filtro['media'] = hst['saldo']/hst['qtd']
# --- Cell 8 ---
filtro['media'].plot()
# --- Cell 9 ---
lista_datas = {0: 201206, 1: 201209, 2: 201212, 
               3: 201303, 4: 201306, 5: 201309, 6: 201312, 
               7: 201403, 8: 201406, 9: 201409, 10: 201412,
              11: 201503, 12: 201506, 13: 201509, 14: 201512,
              15: 201603, 16: 201606, 17: 201609, 18: 201612,
              19: 201703, 20: 201706, 21: 201709, 22: 201712,
              23: 201803, 24: 201806, 25: 201809, 26: 201812,
              27: 201903, 28: 201906, 29: 201909, 30: 201912,
              31: 202003, 32: 202006, 33: 202009, 34: 202012,
              35: 202103, 36: 202106}
# --- Cell 10 ---
diretorio = 'C:/Users/jpcos/OneDrive/Documentos/PPCA/Dissertação/Capítulo - Econometria/Dados_SCR'
# --- Cell 11 ---
for i in range(37):
    
    anomes = lista_datas[i]

    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    exec('df' + str(anomes) + ' = pd.read_csv(' + 'diretorio + "/planilha_' + str(anomes) + '.csv" , delimiter=";", decimal=",")')
    
    exec('df' + str(anomes) + ' = df' + str(anomes) + '.drop(["sr", "a_vencer_ate_90_dias", "a_vencer_de_91_ate_360_dias", "a_vencer_de_361_ate_1080_dias", "a_vencer_de_1081_ate_1800_dias", "a_vencer_de_1801_ate_5400_dias","a_vencer_acima_de_5400_dias"], axis = 1)')
    
    exec('df' + str(anomes) + ' = df' + str(anomes) + '.loc[(df' + str(anomes) + '["cliente"] == "PF") & (df' + str(anomes) + '["tcb"] == "Bancário")]')
    
    exec('for i in df' + str(anomes) + '.index:' +
        '\n\tif df' + str(anomes) + '["numero_de_operacoes"].loc[i] == "<= 15":' +
            '\tdf' + str(anomes) + '["numero_de_operacoes"].loc[i] = 7' +
        '\nelse:' +
            '\n\tdf' + str(anomes) + '["numero_de_operacoes"].loc[i] = int(df' + str(anomes) + '["numero_de_operacoes"].loc[i])')

    exec('for i in df' + str(anomes) + '.index:' +
            '\n\tif df' + str(anomes) + '["porte"].loc[i] in ["PF - Sem rendimento                          ", "PF - Até 1 salário mínimo                    ", "PF - Mais de 1 a 2 salários mínimos          "]:' +
                '\tdf' + str(anomes) + '["porte"].loc[i] = "PF - Até 2 salários mínimos                  "' +
            '\nelse:' +
                '\n\tdf' + str(anomes) + '["numero_de_operacoes"].loc[i] = int(df' + str(anomes) + '["numero_de_operacoes"].loc[i])')   
    
    exec('for i in df' + str(anomes) + '.index:' +
            '\n\tif df' + str(anomes) + '["modalidade"].loc[i] in ["PF - Cartão de crédito", "PF - Empréstimo sem consignação em folha"]:' +
                '\tdf' + str(anomes) + '["modalidade"].loc[i] = "PF - Cartão e CDC"')
    
    exec('df' + str(anomes) + '.numero_de_operacoes = df' + str(anomes) + '.numero_de_operacoes.astype(int)')
    
    exec('df' + str(anomes) + ' = df' + str(anomes) + '.groupby(by=["data_base", "porte", "modalidade"], dropna=False).sum().reset_index()')

#    exec('print(df' + str(anomes) + '.columns)')
    
    exec('df' + str(anomes) + ' = df' + str(anomes) + '.sort_values("modalidade")')
    exec('df' + str(anomes) + ' = df' + str(anomes) + '.sort_values("porte")')
#    exec('df' + str(anomes) + ' = df' + str(anomes) + '.sort_values("ocupacao")')
    exec('df' + str(anomes) + ' = df' + str(anomes) + '.reset_index()')
    exec('df' + str(anomes) + ' = df' + str(anomes) + '.drop(["index"], axis = 1)')

    exec('print(len(df' + str(anomes) + '))')
# --- Cell 12 ---
completos = df201206[["data_base", "porte", "modalidade"]]

for i in range(1, 37):
    exec('completos = completos.append(df' + str(lista_datas[i]) + '[["data_base", "porte", "modalidade"]])')
# --- Cell 13 ---
lista_contagem = completos.groupby(by=["porte", "modalidade"], dropna=False).count().reset_index()
# --- Cell 14 ---
max = lista_contagem['data_base'].max()

lista_final = lista_contagem[(lista_contagem['data_base'] == max)
                            & (lista_contagem['porte'] != 'PF - Indisponível                            ')].reset_index()
# --- Cell 15 ---
chave_prt = {'PF - Até 2 salários mínimos                  ': '01',
             'PF - Mais de 2 a 3 salários mínimos          ': '02',
             'PF - Mais de 3 a 5 salários mínimos          ': '03',
             'PF - Mais de 5 a 10 salários mínimos         ': '04',
             'PF - Mais de 10 a 20 salários mínimos        ': '05',
             'PF - Acima de 20 salários mínimos            ': '06',}

chave_mdl = { 'PF - Outros créditos': '01',
              'PF - Cartão e CDC': '02',
              'PF - Veículos': '03',
              'PF - Habitacional': '04',
              'PF - Empréstimo com consignação em folha': '05',
              'PF - Rural e agroindustrial': '06'}
# --- Cell 16 ---
lista = []
for i in lista_final.index:
    lista.append(chave_prt[lista_final["porte"][i]] + chave_mdl[lista_final["modalidade"][i]])
lista_final['chave_pool'] = lista
# --- Cell 17 ---
finais = pd.merge(df201206 , lista_final.drop(["data_base", "index"], axis = 1), on=["porte", "modalidade"])

for i in range(1, 37):
    exec('finais = finais.append(pd.merge(df' + str(lista_datas[i]) + ', lista_final.drop(["data_base", "index"], axis = 1), on=["porte", "modalidade"]))')
# --- Cell 18 ---
finais = finais[finais['modalidade'] != 'PF - Rural e agroindustrial']
finais = finais[finais['modalidade'] != 'PF - Empréstimo com consignação em folha']
# --- Cell 19 ---
finais
# --- Cell 20 ---
finais['taxa_inad_90'] = finais['carteira_inadimplida_arrastada']/finais['carteira_ativa']
# --- Cell 21 ---
finais['saldo_medio'] = finais['carteira_ativa']/finais['numero_de_operacoes']
# --- Cell 22 ---
finais['taxa_inad_15'] = finais['vencido_acima_de_15_dias']/finais['carteira_ativa']
# --- Cell 23 ---
finais[finais['data_base'] == finais['data_base'].max()].to_csv(path_or_buf='dados_sim.csv', sep=';', index=False, encoding='latin1')
# --- Cell 24 ---
stats = finais[['chave_pool', 'numero_de_operacoes', 'taxa_inad_15', 'taxa_inad_90', 'saldo_medio']].groupby('chave_pool').mean()
# --- Cell 25 ---
tot = stats.numero_de_operacoes.sum()
# --- Cell 26 ---
stats['prop_pool'] = stats['numero_de_operacoes']/tot
stats
# --- Cell 27 ---
import seaborn as sns
import matplotlib.pyplot as plt

ax = sns.barplot(x="modalidade", y="numero_de_operacoes", data=finais)
# --- Cell 28 ---
ax = sns.barplot(x="modalidade", y="carteira_ativa", data=finais)
# --- Cell 29 ---
ax = sns.barplot(x="porte", y="numero_de_operacoes", data=finais)
locs, labels = plt.xticks()
plt.setp(labels, rotation=90)
# --- Cell 30 ---
ax = sns.barplot(x="porte", y="carteira_ativa", data=finais)
locs, labels = plt.xticks()
plt.setp(labels, rotation=90)
# --- Cell 31 ---
P = np.array([[0.94, 0.06, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.24, 0.0, 0.76, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.30, 0.0, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.6, 0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.94, 0.0, 0.0, 0.0, 0.0, 0.06, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.98, 0.0, 0.0, 0.0, 0.0, 0.0, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.993, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.007, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0, 0.0, 0.0, 0.0],
              [0.995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0, 0.0, 0.0],
              [0.995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0, 0.0],
              [0.997, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.003, 0.0],
              [0.999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.001],
              [0.9995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0005]])
# --- Cell 32 ---
np.transpose(P)
# --- Cell 33 ---
import numpy as np
import pandas as pd
from random import seed
from random import random
import matplotlib.pyplot as plt
P = np.array([[0.94, 0.06, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.24, 0.0, 0.76, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.30, 0.0, 0.0, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.6, 0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.94, 0.0, 0.0, 0.0, 0.0, 0.06, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.98, 0.0, 0.0, 0.0, 0.0, 0.0, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.993, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.007, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0, 0.0, 0.0, 0.0],
              [0.995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.005, 0.0, 0.0, 0.0],
              [0.997, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.003, 0.0, 0.0],
              [0.999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.001, 0.0],
              [0.9995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0005]])

stateChangeHist= np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])

state=np.array([[1.00, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
currentState=0
stateHist=state
dfStateHist=pd.DataFrame(state)
distr_hist = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

seed(4)

# Simulate from multinomial distribution
def simulate_multinomial(vmultinomial):
    r=np.random.uniform(0.0, 1.0)
    CS=np.cumsum(vmultinomial)
    CS=np.insert(CS,0,0)
    m=(np.where(CS<r))[0]
    nextState=m[len(m)-1]
    return nextState

for x in range(1000000):
    currentRow=np.ma.masked_values((P[currentState]), 0.0)
    nextState=simulate_multinomial(currentRow)
  # Keep track of state changes
    stateChangeHist[currentState,nextState]+=1
  # Keep track of the state vector itself
    state=np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
    state[0, nextState]=1.0
  # Keep track of state history
    stateHist=np.append(stateHist,state,axis=0)
    currentState=nextState
  # calculate the actual distribution over the 3 states so far
    totals=np.sum(stateHist,axis=0)
    gt=np.sum(totals)
    distrib=totals/gt
    distrib=np.reshape(distrib,(1, 14))
    distr_hist=np.append(distr_hist,distrib,axis=0)
                       
                       
print(distrib)
P_hat=stateChangeHist/stateChangeHist.sum(axis=1)[:,None]
# Check estimated state transition probabilities based on history so far:
print(P_hat)
dfDistrHist = pd.DataFrame(distr_hist)
# Plot the distribution as the simulation progresses over time
dfDistrHist.plot(title="Simulation History")
plt.show()
# --- Cell 34 ---
P_hat
# --- Cell 35 ---
import numpy as np
import pandas as pd
from random import seed
from random import random
import matplotlib.pyplot as plt
P = np.array([[0.2, 0.7, 0.1],
              [0.9, 0.0, 0.1],
              [0.2, 0.8, 0.0]])
stateChangeHist= np.array([[0.0,  0.0,  0.0],
                          [0.0, 0.0,  0.0],
                          [0.0, 0.0,  0.0]])
state=np.array([[1.0, 0.0, 0.0]])
currentState=0
stateHist=state
dfStateHist=pd.DataFrame(state)
distr_hist = [[0,0,0]]
seed(4)
# Simulate from multinomial distribution
def simulate_multinomial(vmultinomial):
    r=np.random.uniform(0.0, 1.0)
    CS=np.cumsum(vmultinomial)
    CS=np.insert(CS,0,0)
    m=(np.where(CS<r))[0]
    nextState=m[len(m)-1]
    return nextState
for x in range(1000):
    currentRow=np.ma.masked_values((P[currentState]), 0.0)
    nextState=simulate_multinomial(currentRow)
  # Keep track of state changes
    stateChangeHist[currentState,nextState]+=1
  # Keep track of the state vector itself
    state=np.array([[0,0,0]])
    state[0,nextState]=1.0
  # Keep track of state history
    stateHist=np.append(stateHist,state,axis=0)
    currentState=nextState
  # calculate the actual distribution over the 3 states so far
    totals=np.sum(stateHist,axis=0)
    gt=np.sum(totals)
    distrib=totals/gt
    distrib=np.reshape(distrib,(1,3))
    distr_hist=np.append(distr_hist,distrib,axis=0)
print(distrib)
P_hat=stateChangeHist/stateChangeHist.sum(axis=1)[:,None]
# Check estimated state transition probabilities based on history so far:
print(P_hat)
dfDistrHist = pd.DataFrame(distr_hist)
# Plot the distribution as the simulation progresses over time
dfDistrHist.plot(title="Simulation History")
plt.show()
