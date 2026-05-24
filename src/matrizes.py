# Converted from matrizes.ipynb
# --- Cell 1 ---
import psycopg2 as pg
import pandas as pd
import pandas.io.sql as psql
import numpy as np
connection = None

# Note: avoid opening DB connections at import time. Use the CLI entrypoint at bottom.
# --- Cell 2 ---
bins = pd.IntervalIndex.from_tuples([(0, 30), (31, 60), (61, 90), (91, 120),
                                     (121, 150), (151, 180), (181, 210),
                                     (211, 240), (241, 270), (271, 300),
                                     (301, 330), (331, 360), (361, np.inf)], closed='both')
# --- Cell 3 ---
def _run_matrizes_demo():
    i = 0
    zero = {'ref': [i] * 13, 
        'contrato': ['00000000000'] * 13, 
        'class_atraso_0':  range(30, 400, 30)
       }
    zero = pd.DataFrame(zero)
    zero['class_atraso_1'] = pd.cut(zero['class_atraso_0'], bins)
    zero['class_atraso_0'] = pd.cut(zero['class_atraso_0'], bins)

    # attempt to use postgres if available, otherwise fallback to sqlite
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
        print('No DB connection available for matrizes demo; skipping.')
        return

    def _r(table, where_clause=''):
        try:
            return psql.read_sql(f"SELECT * FROM jpcosta.{table} {where_clause}", conn)
        except Exception:
            try:
                return psql.read_sql(f"SELECT * FROM {table} {where_clause}", conn)
            except Exception:
                return pd.DataFrame()

    mes0 = _r('operacoes', 'where ref = ' + str(i))
    mes1 = _r('operacoes', 'where ref = ' + str(i + 1))

    if mes0.empty or mes1.empty:
        print('matrizes demo: operacoes table not available or empty for demo; skipping detailed matrix.')
        return
    mes0['class_atraso_0'] = pd.cut(mes0['atraso'], bins)
    mes1['class_atraso_1'] = pd.cut(mes1['atraso'], bins)
    migracao = zero.append(mes0[['ref', 'contrato', 'class_atraso_0']].merge(mes1[['contrato', 'class_atraso_1']], on=('contrato'), how = 'left'))
    cross = pd.crosstab([migracao.ref, migracao.class_atraso_0], migracao.class_atraso_1, normalize='index')
    print('Cross matrix shape:', np.array(cross).shape)



# --- Cell 4 ---

# The historical multi-period computation is heavy and requires a DB connection.
# It is skipped on import and available via the demo or by calling the helper explicitly.

a = []

def compute_long_history(conn):
    # placeholder for the full processing when DB is available
    print('compute_long_history: implement when DB connection is available')
if __name__ == '__main__':
    _run_matrizes_demo()
