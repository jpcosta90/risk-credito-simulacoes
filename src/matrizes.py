# Converted from matrizes.ipynb
# --- Cell 1 ---
import psycopg2 as pg
import pandas as pd
import pandas.io.sql as psql
import numpy as np
connection = pg.connect("host=localhost dbname=Simulacred user=postgres password=12345678")
# --- Cell 2 ---
bins = pd.IntervalIndex.from_tuples([(0, 30), (31, 60), (61, 90), (91, 120),
                                     (121, 150), (151, 180), (181, 210),
                                     (211, 240), (241, 270), (271, 300),
                                     (301, 330), (331, 360), (361, np.inf)], closed='both')
# --- Cell 3 ---
i = 0

zero = {'ref': [i] * 13, 
    'contrato': ['00000000000'] * 13, 
    'class_atraso_0':  range(30, 400, 30)
   }
zero = pd.DataFrame(zero)
zero['class_atraso_1'] = pd.cut(zero['class_atraso_0'], bins)
zero['class_atraso_0'] = pd.cut(zero['class_atraso_0'], bins)
query = 'SELECT * FROM jpcosta.operacoes where ref = ' + str(i)
mes0 = psql.read_sql(query, connection)[['ref', 'contrato', 'atraso']]
query = 'SELECT * FROM jpcosta.operacoes where ref = ' + str(i + 1)
mes1 = psql.read_sql(query, connection)[['contrato', 'atraso']]
mes0['class_atraso_0'] = pd.cut(mes0['atraso'], bins)
mes1['class_atraso_1'] = pd.cut(mes1['atraso'], bins)

mes0['class_atraso_0'] = pd.cut(mes0['atraso'], bins)
mes1['class_atraso_1'] = pd.cut(mes1['atraso'], bins)

migracao = zero.append(mes0[['ref', 'contrato', 'class_atraso_0']].merge(mes1[['contrato', 'class_atraso_1']], on=('contrato'), how = 'left'))

cross = pd.crosstab([migracao.ref, migracao.class_atraso_0], migracao.class_atraso_1, normalize='index')

len(np.array(cross))


# --- Cell 4 ---


#b = psql.read_sql('SELECT min(ref) as n FROM jpcosta.operacoes where atraso > 360', connection).n[0] + 1

n = psql.read_sql('SELECT max(ref) as n FROM jpcosta.operacoes', connection).n[0]

a = []

for i in range(12, n):
    
    zero = {'ref': [i] * 13, 
        'contrato': ['00000000000'] * 13, 
        'class_atraso_0':  range(30, 400, 30)
       }

    zero = pd.DataFrame(zero)

    zero['class_atraso_1'] = pd.cut(zero['class_atraso_0'], bins)
    zero['class_atraso_0'] = pd.cut(zero['class_atraso_0'], bins)

    query = 'SELECT * FROM jpcosta.operacoes where ref = ' + str(i)

    mes0 = psql.read_sql(query, connection)[['ref', 'contrato', 'atraso']]

    query = 'SELECT * FROM jpcosta.operacoes where ref = ' + str(i + 1)

    mes1 = psql.read_sql(query, connection)[['contrato', 'atraso']]

    mes0['class_atraso_0'] = pd.cut(mes0['atraso'], bins)
    mes1['class_atraso_1'] = pd.cut(mes1['atraso'], bins)

    migracao = zero.append(mes0[['ref', 'contrato', 'class_atraso_0']].merge(mes1[['contrato', 'class_atraso_1']], on=('contrato'), how = 'left'))

    l = np.array(pd.crosstab([migracao.ref, migracao.class_atraso_0], migracao.class_atraso_1, normalize='index'))

    a.append(l)
    #matriz = np.concatenate((matriz, np.array(a)), axis=1)
    #m = m.append(a)
c = pd.crosstab([migracao.ref, migracao.class_atraso_0], migracao.class_atraso_1, normalize='index').columns
# --- Cell 5 ---
pd.DataFrame(a[1] - a[0], columns = c).set_index(c)
