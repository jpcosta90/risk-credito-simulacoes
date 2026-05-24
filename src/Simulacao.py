"""Versão import-safe do módulo de simulação.
Mantém classes e funções definidas; execução pesada é feita apenas em `main()`.
"""
import numpy as np
import random
import pandas as pd
import numpy_financial as nf


class cliente:
    def __init__(self, codigo):
        self.codigo = codigo
        self.inad = max(0.06 + np.random.normal(0., 0.005), 0.003)
        self.prop = np.random.uniform(low=0.0, high=1.0, size=None)


clientes = []


class operacao:
    def __init__(self, contrato, ref, mes, dia):
        self.ref = ref
        self.valor = np.random.lognormal(6., 1.8, size=None) + 5000
        self.prazo = int(np.random.uniform(low=1, high=36, size=None))
        self.juros = 0.01
        self.parcela = nf.pmt(self.juros, self.prazo, self.valor)
        self.contrato = contrato
        # will sample `clientes` at runtime; ensure populated before instantiation
        self.cliente = random.sample(clientes, 1)[0]
        self.atraso = 0
        self.mes = mes
        self.dia = dia


def contrata(mes, ctr_dia, ref):
    operacoes = []
    for d in range(1, 31):
        q = np.random.poisson(lam=ctr_dia, size=None)
        for i in range(q):
            operacoes.append(operacao(str(mes).zfill(3) + str(d).zfill(2) + (str(i)).zfill(6), ref, mes, d))
    return operacoes


def atualiza_mes(anterior):
    atual = []
    for i in range(len(anterior)):
        atual.append(anterior[i])
        dia = 30 - anterior[i].dia
        p_atraso = np.random.binomial(size=None, n=1, p=anterior[i].cliente.inad)
        atual[i].atraso = p_atraso * anterior[i].atraso + p_atraso * dia

        if anterior[i].atraso < 30:
            p = 0.06 + 0.24 * (atual[i].atraso - 0) / 30
        elif anterior[i].atraso < 60:
            p = 0.3 + 0.3 * (atual[i].atraso - 30) / 30
        elif anterior[i].atraso < 90:
            p = 0.6 + 0.34 * (anterior[i].atraso - 60) / 30
        elif anterior[i].atraso < 120:
            p = 0.94
        elif anterior[i].atraso < 150:
            p = 0.98
        elif anterior[i].atraso < 180:
            p = 0.993
        elif anterior[i].atraso < 270:
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
        atual[i].valor = max((anterior[i].valor) * (1 + anterior[i].juros) + anterior[i].parcela * p_atraso, 0)

    atual.extend(contrata(anterior[0].mes + 1, 500, anterior[0].ref + 1))
    return atual


def main(sample_clients=1000):
    """Lightweight entrypoint: cria uma pequena carteira de clientes e salva uma amostra."""
    global clientes
    clientes = [cliente(str(i).zfill(7)) for i in range(sample_clients)]
    base0 = contrata(0, 50, 0)
    data = {'ref': [], 'cliente': [], 'contrato': [], 'prazo': [], 'valor': [], 'mes': [], 'dia': [], 'prob': [], 'atraso': []}
    df_local = pd.DataFrame(data)
    for n in range(len(base0)):
        df_local.loc[len(df_local.index)] = [base0[n].ref, base0[n].cliente.codigo, base0[n].contrato, base0[n].prazo, base0[n].valor, base0[n].mes, base0[n].dia, base0[n].cliente.inad, base0[n].atraso]
    df_local.to_csv(path_or_buf='Simulacao_mes_0_sample.csv', sep=';', header=True, decimal=',')


if __name__ == '__main__':
    main()
