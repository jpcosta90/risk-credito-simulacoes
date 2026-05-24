# Converted from Simulacao_choque.ipynb
# --- Cell 1 ---
import numpy as np
import random
import pandas as pd
import numpy_financial as npf

import os
import psycopg2
import psycopg2.extras as ext
import datetime
# --- Cell 2 ---
''''
chave_prob = {1 : 0.015,
             2:  0.010,
             3:  0.008,
             4:  0.006,
             5:  0.002,
             6:  0.0000}
'''''
chave_prob = {1 : 1.400,
              2:  1.300,
              3:  1.100,
              4:  1.000,
              5:  0.900,
              6:  0.500}   
    
chave_valr = {1 : 4.75,
             2:  4.00,
             3:  3.36,
             4:  2.44,
             5:  1.68,
             6:  1.00}
# --- Cell 3 ---
class cliente:
    def __init__(self, codigo):
        self.codigo = codigo
 #       self.inad = max(0.02 + np.random.normal(0., 0.005),0.003)
        self.porte = int(np.where(np.random.multinomial(1, [0.419, 0.156, 0.167, 0.146, 0.072, 0.041], size=1) == 1)[1][0] + 1)
        self.inad = max(0.025 + np.random.normal(0., 0.005),0.0003) * chave_prob[self.porte]
        self.mtlp = chave_valr[self.porte]
# --- Cell 4 ---
clientes = []
 
# --- Cell 5 ---
chave_mdld_prob = {1 : 0.040,
                  2:  0.020,
                  3:  0.010,
                  4:  0.005}

chave_mdld_valor = {1 : 7500,
                    2:  2376,
                    3:  20106,
                    4:  127205}

chave_prazo =      {1 : 0,
                    2:  0,
                    3:  0,
                    4:  5}

chave_prt_inad =      {1 : 2.00,
                       2:  1.20,
                       3:  0.40,
                       4:  0.15}
# --- Cell 6 ---
class operacao:
    def __init__(self, contrato, ref,  mes, dia):
        self.ref = ref
        self.cliente = random.sample(clientes, 1)[0]
        self.modalidade = int(np.where(np.random.multinomial(1, [0.147, 0.779, 0.050, 0.024], size=1) == 1)[1][0] + 1)
        self.valor = (np.random.lognormal(6., 1.8, size=None) + chave_mdld_valor[self.modalidade]) * self.cliente.mtlp
        self.mtpl_inad = chave_prt_inad[self.modalidade]
        self.p_inad = min(self.cliente.inad * self.mtpl_inad, 0.5)
        self.prazo = int(np.random.uniform(low=1, high=10, size=None)) * 6 * (1 + chave_prazo[self.modalidade])
        self.juros = 0.01
        self.parcela = npf.pmt(self.juros, self.prazo, self.valor)
        self.multa = 0
        self.pagamento = 0
        self.contrato = contrato
        self.atraso = 0
        self.mes = mes
        self.dia = dia
# --- Cell 7 ---
def contrata(mes, ctr_dia, ref):
    
    operacoes = []

    for d in range(1, 31):
        q = np.random.poisson(lam=ctr_dia, size=None)
        
        for i in range(q):
            operacoes.append(operacao(str(mes).zfill(3) + str(d).zfill(2)+(str(i)).zfill(6), ref, mes, d))
            
    return(operacoes)
# --- Cell 8 ---
def atualiza_mes(anterior, ctr_dia=50):
    #print(len(anterior))
    atual = []

    for i in range(len(anterior)):

        atual.append(anterior[i])

        dia = 30 - anterior[i].dia
        
        #ajustar atraso para somar 30 dias se menor que 30 dia se não + 30
        
        p_atraso = np.random.binomial(size = None, n = 1, p = min(anterior[i].p_inad, 0.99999))
        
        atual[i].atraso = p_atraso * anterior[i].atraso + p_atraso * dia
        
        if anterior[i].atraso == 0:
            p = anterior[i].p_inad
        elif anterior[i].atraso < 30:
            p = 0.15 + 0.40 * (atual[i].atraso - 0)/30
        elif anterior[i].atraso < 60:
            p = 0.55 + 0.20 * (atual[i].atraso - 30)/30
        elif anterior[i].atraso < 90:    
            p = 0.75 + 0.05 * (atual[i].atraso - 60)/30
        elif anterior[i].atraso < 120:
            p = 0.85
        elif anterior[i].atraso < 150:
            p = 0.90
        elif anterior[i].atraso < 180:
            p = 0.95  
        elif anterior[i].atraso < 270:
            p = 0.98
        elif anterior[i].atraso < 300:
            p = 0.99
        elif anterior[i].atraso < 330:
            p = 0.995  
        elif anterior[i].atraso < 360:
            p = 0.999
        else:
            p = 0.99999

        atual[i].cliente.inad = anterior[i].cliente.inad * (p/anterior[i].p_inad)
        atual[i].p_inad = p
        atual[i].prazo = anterior[i].prazo - 1
        atual[i].ref = anterior[i].ref + 1
        atual[i].pagamento = (-anterior[i].parcela + anterior[i].multa) * (1 - p_atraso) 
        atual[i].valor = max((anterior[i].valor) * (1 + anterior[i].juros) + ((anterior[i].parcela - atual[i].multa) * (1 - p_atraso)), 0)

        atual[i].multa = - (anterior[i].parcela * p_atraso * (1 + anterior[i].juros)) + (anterior[i].multa * p_atraso)
        
        
    atual.extend(contrata(anterior[i].mes + 1, ctr_dia, anterior[i].ref))
    
    return(atual)

        ## Incluir probabilidade de inadimplência em 1 mês ok
        ## atualizar dias de atraso ok
        ## utilizar probabilidades de recuperação e inadimplência do System Dynamics ok
        
        
        ## atualizar mes de referencia ok
        ## atualizar prazo ok
        ## atualizar liquidação ok
        ## exportar cada nova tabela ok
        ## criar loop ok
        ## atualizar probabilidades na base de clientes ok
if __name__ == '__main__':
    # Lightweight demo: create a small sample and write to CSV instead of bulk DB insert
    sample_clients = 1000
    clientes = [cliente(str(i).zfill(7)) for i in range(sample_clients)]
    nmes = 12
    ctr_dia = 50
    now = datetime.datetime.now()
    print ("Início do processamento base 0 :", now.strftime("%Y-%m-%d %H:%M:%S"))
    base0 = contrata(0, ctr_dia, 0)
    data = {'ref':[], 'cliente':[], 'contrato':[], 'prazo':[], 'valor':[], 'mes':[], 'dia':[], 'prob_opr':[], 'prob_cli':[], 'atraso':[], 'pgto':[]}
    df_local = pd.DataFrame(data)
    for n in range(len(base0)):
        df_local.loc[len(df_local.index)] = [base0[n].ref, base0[n].cliente.codigo, base0[n].contrato, base0[n].prazo, base0[n].valor, base0[n].mes, base0[n].dia, base0[n].p_inad, base0[n].cliente.inad, base0[n].atraso, base0[n].pagamento]

    df_local.to_csv(path_or_buf='Simulacao_choque_mes_0_sample.csv', sep=';',header=True, decimal=',')
    now = datetime.datetime.now()
    print ("Fim do processamento base 0    :", now.strftime("%Y-%m-%d %H:%M:%S"))
    values = [base0[n].ref , base0[n].cliente.codigo, base0[n].cliente.porte, base0[n].contrato, base0[n].modalidade, base0[n].prazo, base0[n].valor, base0[n].mes, base0[n].dia, base0[n].p_inad, base0[n].cliente.inad, base0[n].atraso, base0[n].pagamento]

