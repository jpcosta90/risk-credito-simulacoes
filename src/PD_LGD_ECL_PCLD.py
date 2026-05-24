"""Módulo PD/LGD/ECL — versão import-safe.
Coloque visualizações e execuções pesadas no bloco `if __name__ == '__main__'`.
"""
import psycopg2 as pg
import pandas as pd
import math
import numpy as np
import pandas.io.sql as psql

connection = None

def _run_pd_lgd_demo():
    conn = None
    try:
        conn = pg.connect("host=localhost dbname=Simulacred user=postgres password=12345678")
    except Exception:
        import sqlite3
        try:
            conn = sqlite3.connect('data/simulacred.db')
        except Exception:
            conn = None

    if conn is None:
        print('No DB connection available for PD/LGD demo; skipping.')
        return

    def _r(table):
        try:
            return psql.read_sql(f'SELECT * FROM jpcosta.{table}', conn)
        except Exception:
            try:
                return psql.read_sql(f'SELECT * FROM {table}', conn)
            except Exception:
                return pd.DataFrame()

    serie_pd = _r('calculo_pd')
    serie_pd_2 = _r('calculo_pd_2')

    req1 = {'ref', 'porte', 'modalidade', 'qtd', 'qtd_inad'}
    if not req1.issubset(set(serie_pd_2.columns)):
        print('PD/LGD demo: calculo_pd_2 missing required columns; skipping.')
        return

    df1 = serie_pd_2[['ref', 'porte', 'modalidade', 'qtd', 'qtd_inad']].groupby(['ref', 'porte', 'modalidade']).sum().reset_index()
    df1['pd'] = df1['qtd_inad']/df1['qtd']

    req2 = {'ref', 'porte', 'modalidade', 'pd'}
    if not req2.issubset(set(serie_pd.columns)):
        print('PD/LGD demo: calculo_pd missing required columns; skipping.')
        return

    probd = serie_pd[['ref', 'porte', 'modalidade', 'pd']]
    pd_model = probd[(probd['ref'] > 0) & ((probd['ref'] < 48))].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean().reset_index()
    pd_monit = probd[probd['ref'].between(72, 84)].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean().reset_index()
    pd_monit = pd_monit.rename(columns={'pd': 'pd_monit'})
    print('PD/LGD demo loaded; pd_model shape:', pd_model.shape)

if __name__ == '__main__':
    _run_pd_lgd_demo()
