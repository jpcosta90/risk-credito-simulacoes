"""
Lightweight, import-safe version of Analise_final_simulacao.

This module provides `_run_analise_demo()` which attempts to connect to
Postgres and falls back to the local SQLite database `data/simulacred.db`.
It performs a few small queries and returns the loaded DataFrames so callers
can run analysis or plotting interactively.
"""

import sqlite3
import psycopg2 as pg
import pandas as pd
import pandas.io.sql as psql
from typing import Dict


def _get_connection():
    try:
        return pg.connect("host=localhost dbname=Simulacred user=postgres password=12345678")
    except Exception:
        try:
            return sqlite3.connect('data/simulacred.db')
        except Exception:
            return None


def _run_analise_demo() -> Dict[str, pd.DataFrame]:
    conn = _get_connection()
    if conn is None:
        print('No DB connection available for Analise demo; skipping.')
        return {}

    try:
        agg = psql.read_sql('SELECT * FROM jpcosta.perda_obs_atr', conn)
    except Exception:
        agg = pd.DataFrame()

    try:
        serie_pd_2 = psql.read_sql('SELECT * FROM jpcosta.calculo_pd_2', conn)
    except Exception:
        serie_pd_2 = pd.DataFrame()

    try:
        lgd = psql.read_sql('SELECT * FROM jpcosta.calculo_lgd60', conn)
    except Exception:
        lgd = pd.DataFrame()

    # small derived example
    if not serie_pd_2.empty:
        df1 = serie_pd_2[['ref', 'porte', 'modalidade', 'qtd', 'qtd_inad']].groupby(['ref', 'porte', 'modalidade']).sum().reset_index()
        df1['pd'] = df1['qtd_inad'] / df1['qtd'].replace(0, 1)
        print('Analise demo: df1 shape', df1.shape)
    else:
        df1 = pd.DataFrame()

    result = {'agg': agg, 'serie_pd_2': serie_pd_2, 'lgd': lgd, 'df1': df1}
    return result


if __name__ == '__main__':
    _run_analise_demo()
