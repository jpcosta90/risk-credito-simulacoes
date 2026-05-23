# Converted from Simulacao_v2.ipynb
# --- Cell 1 ---
import numpy as np
import random
import pandas as pd
import numpy_financial as npf
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
class operacao:
    def __init__(self, contrato, ref,  mes, dia):
        self.ref = ref
        self.valor = np.random.lognormal(6., 1.8, size=None) + 5000
        self.prazo = int(np.random.uniform(low=1, high=36, size=None))
        self.juros = 0.01
        self.parcela = npf.pmt(self.juros, self.prazo, self.valor)
        self.multa = 0
        self.pagamento = 0
        self.contrato = contrato
        self.cliente = random.sample(clientes, 1)[0]
        self.atraso = 0
        self.mes = mes
        self.dia = dia
# --- Cell 5 ---
def contrata(mes, ctr_dia, ref):
    
    operacoes = []

    for d in range(1, 31):
        q = np.random.poisson(lam=ctr_dia, size=None)
        
        for i in range(q):
            operacoes.append(operacao(str(mes).zfill(3) + str(d).zfill(2)+(str(i)).zfill(6), ref, mes, d))
            
    return(operacoes)
# --- Cell 6 ---
def atualiza_mes(anterior, ctr_dia=500):
    #print(len(anterior))
    atual = []

    for i in range(len(anterior)):

        atual.append(anterior[i])

        dia = 30 - anterior[i].dia
        
        #ajustar atraso para somar 30 dias se menor que 30 dia se não + 30
        
        p_atraso = np.random.binomial(size = None, n = 1, p = anterior[i].cliente.inad)
        
        atual[i].atraso = p_atraso * anterior[i].atraso + p_atraso * dia

        if anterior[i].atraso < 30:
            p = 0.06 + 0.24 * (atual[i].atraso - 0)/30
        elif anterior[i].atraso < 60:
            p = 0.3 + 0.3 * (atual[i].atraso - 30)/30
        elif anterior[i].atraso < 90:    
            p = 0.6 + 0.34 * (atual[i].atraso - 60)/30
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
        atual[i].pagamento = (-anterior[i].parcela + anterior[i].multa) * (1 - p_atraso) 
        atual[i].valor = max((anterior[i].valor) * (1 + anterior[i].juros) + ((anterior[i].parcela - atual[i].multa) * (1 - p_atraso)), 0)

        atual[i].multa = - (anterior[i].parcela * p_atraso * (1 + anterior[i].juros)) + (anterior[i].multa * p_atraso)
        
        
    atual.extend(contrata(anterior[0].mes + 1, ctr_dia, anterior[0].ref))
    
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
# --- Cell 7 ---
base0 = contrata(0, 500, 0)

data = {'ref':[], 'cliente':[], 'contrato':[], 'prazo':[], 'valor':[], 'mes':[], 'dia':[], 'prob':[],'atraso':[], 'pgto':[]}

df = pd.DataFrame(data)

for n in range(len(base0)):
    df.loc[len(df.index)] = [base0[n].ref , base0[n].cliente.codigo, base0[n].contrato, base0[n].prazo, base0[n].valor, base0[n].mes, base0[n].dia, base0[n].cliente.inad, base0[n].atraso, base0[n].pagamento]

df.to_csv(path_or_buf='Simulacao_mes_0.csv', sep=';',header=True, decimal=',', index=False)

print("Simulacao_mes_0.csv gravada com sucesso.")

for i in range(1):
    
    exec("base" + str(i+1) + "= atualiza_mes(" + "base" + str(i) + ")")
    
    data = {'ref':[], 'cliente':[], 'contrato':[], 'prazo':[], 'valor':[], 'mes':[], 'dia':[], 'prob':[],'atraso':[], 'pgto':[]}
    
    exec("df" + str(i) + "= pd.DataFrame(data)")
    
    exec("linhas = len(base" + str(i + 1) + ")")
    
    for n in range(linhas):
        exec("df" + str(i) + ".loc[len(df" + str(i) + ".index)] = [" + "base" + str(i+1) + "[n].ref , base" 
             + str(i+1) + "[n].cliente.codigo, base" + str(i+1) + "[n].contrato, base" + str(i+1) + "[n].prazo, base"+
             str(i+1) + "[n].valor, base" + str(i+1) + "[n].mes, base" + str(i+1) + "[n].dia, base" + 
             str(i+1) + "[n].cliente.inad, base" + str(i + 1) + "[n].atraso, base" + str(i+1) + "[n].pagamento]")
        
    exec("df" + str(i) + ".to_csv(path_or_buf='Simulacao_mes_" + str(i+1) + ".csv', sep=';',header=True, decimal=',', index=False)")
    print("Simulacao_mes_" + str(i + 1) + ".csv gravada com sucesso.")
# --- Cell 8 ---
base0 = contrata(0, 1, 0)
# --- Cell 9 ---
for i in range(len(base0)):
    print("ref:", base0[i].ref,
          "contrato:",  base0[i].contrato,
          "prazo:", base0[i].prazo,
          "atraso:", base0[i].atraso, 
          "pagamento:", "%6.2f"% base0[i].pagamento,
          "parcela:",  "%6.2f"% base0[i].parcela,
          "multa:",  "%6.2f"% base0[i].multa,
          "valor:" , "%6.2f"% base0[i].valor)  
# --- Cell 10 ---
base1 = atualiza_mes(base0, 1)
# --- Cell 11 ---
for i in range(len(base0)):
    print("ref:", base1[i].ref,
          "contrato:",  base1[i].contrato,
          "prazo:", base1[i].prazo,
          "atraso:", base1[i].atraso, 
          "pagamento:", "%6.2f"% base1[i].pagamento,
          "parcela:",  "%6.2f"% base1[i].parcela,
          "multa:",  "%6.2f"% base1[i].multa,
          "valor:" , "%6.2f"% base1[i].valor)   
# --- Cell 12 ---
base2 = atualiza_mes(base1)
# --- Cell 13 ---
for i in range(len(base0)):
    print("ref:", base2[i].ref,
          "contrato:",  base2[i].contrato,
          "prazo:", base2[i].prazo,
          "atraso:", base2[i].atraso, 
          "pagamento:", "%6.2f"% base2[i].pagamento,
          "parcela:",  "%6.2f"% base2[i].parcela,
          "multa:",  "%6.2f"% base2[i].multa,
          "valor:" , "%6.2f"% base2[i].valor)   
# --- Cell 14 ---
base3 = atualiza_mes(base2)
# --- Cell 15 ---
for i in range(len(base0)):
    print("ref:", base3[i].ref,
          "contrato:",  base3[i].contrato,
          "prazo:", base3[i].prazo,
          "atraso:", base3[i].atraso, 
          "pagamento:", "%6.2f"% base3[i].pagamento,
          "parcela:",  "%6.2f"% base3[i].parcela,
          "multa:",  "%6.2f"% base3[i].multa,
          "valor:" , "%6.2f"% base3[i].valor) 
