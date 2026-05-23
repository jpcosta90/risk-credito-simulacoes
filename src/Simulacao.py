# Converted from Simulacao.ipynb
# --- Cell 1 ---
import numpy as np
import random
import pandas as pd
# --- Cell 2 ---
class cliente:
    def __init__(self, codigo):
        self.codigo = codigo
        self.inad = max(0.06 + np.random.normal(0., 0.005),0.003)
        self.prop = np.random.uniform(low=0.0, high=1.0, size=None)
# --- Cell 3 ---
clientes = []

for i in range(1000000):
    clientes.append(cliente(str(i).zfill(7)))
# --- Cell 4 ---
clientes[0].codigo
# --- Cell 5 ---
class operacao:
    def __init__(self, contrato, ref,  mes, dia):
        self.ref = ref
        self.valor = np.random.lognormal(6., 1.8, size=None) + 5000
        self.prazo = int(np.random.uniform(low=1, high=36, size=None))
        self.juros = 0.01
        self.parcela = np.pmt(self.juros, self.prazo, self.valor)
        self.contrato = contrato
        self.cliente = random.sample(clientes, 1)[0]
        self.atraso = 0
        self.mes = mes
        self.dia = dia
# --- Cell 6 ---
def contrata(mes, ctr_dia, ref):
    
    operacoes = []

    for d in range(1, 31):
        q = np.random.poisson(lam=ctr_dia, size=None)
        
        for i in range(q):
            operacoes.append(operacao(str(mes).zfill(3) + str(d).zfill(2)+(str(i)).zfill(6), ref, mes, d))
            
    return(operacoes)
# --- Cell 7 ---
mes0 = contrata(0, 500, 0)
# --- Cell 8 ---
print("Quantidade de Operações:", len(mes0))
# --- Cell 9 ---
mes0[3].valor
# --- Cell 10 ---
data = {'ref':[], 'cliente':[], 'contrato':[], 'prazo':[], 'valor':[], 'mes':[], 'dia':[], 'prob':[],'atraso':[]}
 
df = pd.DataFrame(data)

for n in range(len(mes0)):
    df.loc[len(df.index)] = [mes0[n].ref , mes0[n].cliente.codigo, mes0[n].contrato, mes0[n].prazo, mes0[n].valor, mes0[n].mes, mes0[n].dia, mes0[n].cliente.inad, mes0[n].atraso]

df.head()
# --- Cell 11 ---
df.to_csv(path_or_buf='Mes0.csv', sep=';',header=True, decimal=',')
# --- Cell 12 ---
#atualizar mês: ref, atraso, prazo e saldo
for atraso in range(5):

    if atraso < 30:
        p = 0.06 + 0.24 * (atraso - 0)/30
    elif atraso < 60:
        p = 0.3 + 0.3 * (atraso - 30)/30
    elif atraso < 90:    
        p = 0.6 + 0.34 * (atraso - 60)/30
    elif atraso < 120:
        p = 0.94
    elif atraso < 150:
        p = 0.98
    elif atraso < 180:
        p = 0.993  
    elif atraso < 270:
        p = 0.995
    elif atraso < 300:
        p = 0.997
    elif atraso < 330:
        p = 0.999  
    elif atraso < 360:
        p = 0.9995
    else:
        p = 1
    
    print("Atraso:", atraso, "Probabilidade:", p)
# --- Cell 13 ---
print('Máximo:', max(df['prob']), '\nMínimo:', min(df['prob']))
# --- Cell 14 ---
i = 10
mes0[i].prazo
# --- Cell 15 ---
def atualiza_mes(anterior):
    #print(len(anterior))
    atual = []

    for i in range(len(anterior)):

        atual.append(anterior[i])

        dia = 30 - anterior[i].dia
        
        p_atraso = np.random.binomial(size = None, n = 1, p = anterior[i].cliente.inad)
        
        atual[i].atraso = p_atraso * anterior[i].atraso + p_atraso * dia

        if anterior[i].atraso < 30:
            p = 0.06 + 0.24 * (atual[i].atraso - 0)/30
        elif anterior[i].atraso < 60:
            p = 0.3 + 0.3 * (atual[i].atraso - 30)/30
        elif anterior[i].atraso < 90:    
            p = 0.6 + 0.34 * (mes1[i].atraso - 60)/30
        elif anterior[i].atraso < 120:
            p = 0.94
        elif anterior[i].atraso < 150:
            p = 0.98
        elif anterior[i].atraso < 180:
            p = 0.993  
        elif anterior[0].atraso < 270:
            p = 0.995
        elif anterior[i].atraso < 300:
            p = 0.997
        elif anterior[i].atraso < 330:
            p = 0.999  
        elif anterior[i].atraso < 360:
            p = 0.9995
        else:
            p = 1

        atual[i].cliente.inad = p
        atual[i].prazo = anterior[i].prazo - 1
        atual[i].ref = anterior[i].ref + 1
        atual[i].valor = max((anterior[i].valor) * (1 + anterior[i].juros) + anterior[i].parcela*p_atraso, 0)
        
    atual.extend(contrata(anterior[0].mes + 1, 500, anterior[0].ref + 1))
    
    return(atual)

        ## Incluir probabilidade de inadimplência em 1 mês ok
        ## atualizar dias de atraso ok
        ## utilizar probabilidades de recuperação e inadimplência do System Dynamics ok
        
        
        ## atualizar mes de referencia ok
        ## atualizar prazo ok
        ## atualizar liquidação ok
        ## exportar cada nova tabela
        ## criar loop
# --- Cell 16 ---
mes1 = atualiza_mes(mes0)
# --- Cell 17 ---
len(df2)
# --- Cell 18 ---
data = {'ref':[], 'cliente':[], 'contrato':[], 'prazo':[], 'valor':[], 'mes':[], 'dia':[], 'prob':[],'atraso':[]}
 
df2 = pd.DataFrame(data)

for n in range(len(mes1)):
    df2.loc[len(df2.index)] = [mes1[n].ref , mes1[n].cliente.codigo, mes1[n].contrato, mes1[n].prazo, mes1[n].valor, mes1[n].mes, mes1[n].dia, mes1[n].cliente.inad, mes1[n].atraso]

df2.head()
# --- Cell 19 ---
base0 = contrata(0, 500, 0)

data = {'ref':[], 'cliente':[], 'contrato':[], 'prazo':[], 'valor':[], 'mes':[], 'dia':[], 'prob':[],'atraso':[]}
 
df = pd.DataFrame(data)

for n in range(len(base0)):
    df.loc[len(df.index)] = [base0[n].ref , base0[n].cliente.codigo, base0[n].contrato, base0[n].prazo, base0[n].valor, base0[n].mes, base0[n].dia, base0[n].cliente.inad, base0[n].atraso]

df.to_csv(path_or_buf='Simulacao_mes_0.csv', sep=';',header=True, decimal=',')

for i in range(1):
    
    exec("base" + str(i+1) + "= atualiza_mes(" + "base" + str(i) + ")")
    
    data = {'ref':[], 'cliente':[], 'contrato':[], 'prazo':[], 'valor':[], 'mes':[], 'dia':[], 'prob':[],'atraso':[]}
    
    exec("df" + str(i) + "= pd.DataFrame(data)")
    
    exec("linhas = len(base" + str(i) + ")")
    
    for n in range(linhas):
        exec("df" + str(i) + ".loc[len(df" + str(i) + ".index)] = [" + "base" + str(i+1) + "[n].ref , base" 
             + str(i+1) + "[n].cliente.codigo, base" + str(i+1) + "[n].contrato, base" + str(i+1) + "[n].prazo, base"+
             str(i+1) + "[n].valor, base" + str(i+1) + "[n].mes, base" + str(i+1) + "[n].dia, base" + 
             str(i+1) + "[n].cliente.inad, base" + str(i + 1) + "[n].atraso]")
        
    exec("df" + str(i) + ".to_csv(path_or_buf='Simulacao_mes_" + str(i+1) + ".csv', sep=';',header=True, decimal=',')")

# --- Cell 20 ---
df2.to_csv(path_or_buf='Mes1.csv', sep=';',header=True, decimal=',')
# --- Cell 21 ---
len(df2['contrato'])
# --- Cell 22 ---
len(df2['contrato'])-len(df2['contrato'].drop_duplicates())
# --- Cell 23 ---
df2.loc[29702]
# --- Cell 24 ---
import matplotlib.pyplot as plt
count, bins, ignored = plt.hist(s, 100, density=True, align='mid')
x = np.linspace(min(bins), max(bins), 10000)
pdf = (np.exp(-(np.log(x) - mu)**2 / (2 * sigma**2))
       / (x * sigma * np.sqrt(2 * np.pi)))
plt.plot(x, pdf, linewidth=2, color='r')
plt.axis('tight')
plt.show()
# --- Cell 25 ---
print("Máximo:", s.max(), 
      "\n3rd Qrt:", np.quantile(s, 0.75),
      "\nMediana:", np.quantile(s, 0.50),
      "\n1rd Qrt:", np.quantile(s, 0.25), 
      "\nMínimo:", s.min(), "\nMédia:", 
      s.mean())
