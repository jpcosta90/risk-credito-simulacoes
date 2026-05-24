"""Refatorado para evitar execução no import.
Este módulo expõe um demo leve via CLI (executado somente quando chamado como script).
"""
import psycopg2 as pg
import pandas as pd
import math
import numpy as np
import pandas.io.sql as psql

connection = None

def _run_calibragem_demo():
    # try to obtain a DB connection (Postgres preferred, else sqlite)
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
        print('No DB connection available for calibragem demo; skipping.')
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
    required = {'ref', 'porte', 'modalidade', 'pd'}
    if not required.issubset(set(serie_pd.columns)):
        print('calibragem demo: required columns missing in calculo_pd; skipping.')
        return

    probd = serie_pd[['ref', 'porte', 'modalidade', 'pd']]
    pd_model = probd[(probd['ref'] > 0) & ((probd['ref'] < 48))].drop('ref', axis=1).groupby(['porte', 'modalidade']).mean().reset_index()
    pd.options.display.float_format = '{:2}'.format
    agg = _r('perda_obs')
    if agg.empty:
        print('calibragem demo: perda_obs table missing or empty; skipping further analysis.')
        return
    n = agg.ref.max() - 1
    print('Loaded agg with max ref', n)

if __name__ == '__main__':
    _run_calibragem_demo()
