# Converted from Markov.ipynb
# --- Cell 1 ---
import numpy as np
import pandas as pd
from random import seed
from random import random
import matplotlib.pyplot as plt
import os
import time
# --- Cell 2 ---
mplt_prt = [2.0, 1.3, 1.0, 0.87, 0.47, 0.23]
mplt_mod = [2.9, 1.6, 1.3, 1.1]
mptl_rec = [1.0, 0.95, 0.9, 0.75]

p = 0.03
# --- Cell 3 ---
porte = 1
modalidade = 2

p0 = mplt_prt[porte - 1] * mplt_mod[modalidade - 1] * p
q0 = 1 - p0

p30 = 0.40 * mptl_rec[modalidade - 1]
p60 = 0.55 * mptl_rec[modalidade - 1]
p90 = 0.63 * mptl_rec[modalidade - 1]
p120 = 0.75 * mptl_rec[modalidade - 1]
p150 = 0.80 * mptl_rec[modalidade - 1]
p180 = 0.85
p270 = 0.90
p300 = 0.95
p330 = 0.975
p360 = 0.995
prej = 1.000


# --- Cell 4 ---
P = np.array([[q0      , p0   , 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00 ],
              [1 - p30 , 0.00, p30  , 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00 ],
              [1 - p60 , 0.00, 0.00, p60  , 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00 ],
              [1 - p90 , 0.00, 0.00, 0.00, p90 ,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00 ],
              [1 - p120, 0.00, 0.00, 0.00, 0.00, p120 , 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00 ],
              [1 - p150, 0.00, 0.00, 0.00, 0.00, 0.00, p150 , 0.00, 0.00, 0.00, 0.00, 0.00, 0.00 ],
              [1 - p180, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, p180  , 0.00, 0.00, 0.00, 0.00, 0.00 ],
              [1 - p180, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, p180  , 0.00, 0.00, 0.00, 0.00 ],
              [1 - p180, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, p180  , 0.00, 0.00, 0.00 ],
              [1 - p270, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, p270  , 0.00, 0.00 ],
              [1 - p300, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, p300  , 0.00 ],
              [1 - p330, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00  , p330 ],
              [0.00    , 0.00, 0.00, 0.00, 0.00, 0.000, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00 , 1.00]])
        
stateChangeHist= np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
# --- Cell 5 ---
np.seterr(divide='ignore', invalid='ignore')

def simulate_multinomial(vmultinomial):
  r=np.random.uniform(0.0, 1.0)
  CS=np.cumsum(vmultinomial)
  CS=np.insert(CS,0,0)
  m=(np.where(CS<r))[0]
  nextState=m[len(m)-1]
  return nextState

def run_markov_sim(reps=100, meses=60, last=60):
  lista = []
  for _ in range(reps):
    state=np.array([[1.0] + [0.0]*12])
    currentState=0
    stateHist=state
    distr_hist = [[0]*13]
    seed(4)

    for x in range(meses):
      currentRow=np.ma.masked_values((P[currentState]), 0.0)
      nextState=simulate_multinomial(currentRow)
      stateChangeHist[currentState,nextState]+=1
      state=np.array([[0]*13])
      state[0,nextState]=1.0
      stateHist=np.append(stateHist,state,axis=0)
      currentState=nextState
      totals=np.sum(stateHist,axis=0)
      gt=np.sum(totals)
      distrib=totals/gt
      distrib=np.reshape(distrib,(1, 13))
      distr_hist=np.append(distr_hist,distrib,axis=0)

    dfDistrHist = pd.DataFrame(distr_hist)
    carteira = dfDistrHist.loc[last, list(range(12))].sum()
    inad = dfDistrHist.loc[last, list(range(3,12))].sum()
    lista.append(inad/carteira)

  return np.mean(lista)

def run_single_sim(meses=60):
  state=np.array([[1.0] + [0.0]*12])
  currentState=0
  stateHist=state
  distr_hist = [[0]*13]
  seed(4)

  for x in range(meses):
    currentRow=np.ma.masked_values((P[currentState]), 0.0)
    nextState=simulate_multinomial(currentRow)
    stateChangeHist[currentState,nextState]+=1
    state=np.array([[0]*13])
    state[0,nextState]=1.0
    stateHist=np.append(stateHist,state,axis=0)
    currentState=nextState
    totals=np.sum(stateHist,axis=0)
    gt=np.sum(totals)
    distrib=totals/gt
    distrib=np.reshape(distrib,(1, 13))
    distr_hist=np.append(distr_hist,distrib,axis=0)

  return pd.DataFrame(distr_hist)
# --- Demo / CLI entrypoint ---
if __name__ == '__main__':
    dfDistrHist = run_single_sim(60)
    print('Final distribution (last row):')
    print(dfDistrHist.iloc[-1].values)
    P_hat=stateChangeHist/stateChangeHist.sum(axis=1)[:,None]
    print('Estimated transition matrix (P_hat):')
    print(P_hat)
    try:
        dfDistrHist.plot(title="Simulation History")
        plt.show()
    except Exception:
        pass

    last = 60
    carteira = dfDistrHist.loc[last, list(range(12))].sum()
    inad = dfDistrHist.loc[last, list(range(3,12))].sum()
    print('inad/carteira =', inad/carteira)
