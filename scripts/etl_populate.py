"""ETL helpers to populate DB from simulation CSVs and compute derived tables.

Usage (dry-run, only parse files):
  python etl_populate.py

To actually insert into DB (be careful):
  python etl_populate.py --apply --db-host localhost --db-port 5432 --db-user postgres --db-password 12345678 --db-name Simulacred

The derived table calculations are heuristic approximations based on available columns in the simulation CSVs.
Review and adjust formulas as needed.
"""
from pathlib import Path
import argparse
import pandas as pd
import glob
import math
import sqlite3
import os


def find_simulation_csvs(root: Path):
    patterns = [str(root / 'scripts' / 'Simulacao_mes_*.csv'), str(root / 'scripts' / 'Mes*.csv'), str(root / 'data' / '*.csv')]
    files = []
    for pat in patterns:
        files += glob.glob(pat)
    # dedupe and return as Path
    return [Path(x) for x in sorted(set(files))]


def read_sim_csv(p: Path) -> pd.DataFrame:
    # files use ';' separator and comma decimal
    try:
        df = pd.read_csv(p, sep=';', decimal=',', dtype=str)
    except Exception:
        # fallback plain read
        df = pd.read_csv(p)

    # normalize column names
    df.columns = [c.strip() for c in df.columns]

    # try converting known numeric columns
    for col in ['ref', 'prazo', 'valor', 'mes', 'dia', 'prob', 'atraso', 'pgto']:
        if col in df.columns:
            # replace comma decimal inside strings
            df[col] = df[col].astype(str).str.replace(',', '.').str.replace(';', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def insert_operacoes(conn, df: pd.DataFrame):
    # columns to insert if present
    cols = ['ref', 'cliente', 'contrato', 'prazo', 'valor', 'mes', 'dia', 'prob', 'atraso', 'pgto']
    present = [c for c in cols if c in df.columns]
    records = df[present].where(pd.notnull(df[present]), None).to_dict('records')

    # assume psycopg2 connection
    try:
        import psycopg2.extras as extras
        with conn.cursor() as cur:
            extras.execute_values(cur,
                                  sql= 'INSERT INTO jpcosta.operacoes (' + ','.join(present) + ') VALUES %s',
                                  argslist=[tuple(r[c] for c in present) for r in records],
                                  template=None,
                                  page_size=1000)
        conn.commit()
        return
    except Exception:
        # fallback to sqlite-style executemany (no schema prefix)
        cur = conn.cursor()
        table_cols = present
        placeholders = ','.join(['?'] * len(table_cols))
        sql_ins = 'INSERT INTO operacoes (' + ','.join(table_cols) + ') VALUES (' + placeholders + ')'
        argslist = []
        for r in records:
            tup = []
            for c in table_cols:
                v = r.get(c)
                if pd.isna(v):
                    tup.append(None)
                else:
                    tup.append(v)
            argslist.append(tuple(tup))
        cur.executemany(sql_ins, argslist)
        conn.commit()


def compute_and_insert_derived(conn, df_all: pd.DataFrame):
    # Heuristic derived calculations
    # perda_att = sum(valor - pgto) per ref
    grp = df_all.groupby('ref', dropna=False)
    perda_att = grp.apply(lambda g: g['valor'].fillna(0) - g['pgto'].fillna(0)).groupby(level=0).sum()
    saldo = grp['valor'].sum()
    perda_obs = (perda_att / saldo).fillna(0)

    # calculo_pd: fraction with atraso > 0
    pd_frac = grp.apply(lambda g: (g['atraso'].fillna(0) > 0).sum() / max(1, len(g)))

    # Prepare inserts
    perda_obs_df = pd.DataFrame({
        'ref': perda_obs.index.astype('Int64'),
        'perda_obs': perda_obs.values,
        'perda_att': perda_att.values,
        'saldo': saldo.values
    })

    calculo_pd_df = pd.DataFrame({
        'ref': pd_frac.index.astype('Int64'),
        'pd': pd_frac.values
    })

    # insert into respective tables
    try:
        import psycopg2.extras as extras
        with conn.cursor() as cur:
            # insert perda_obs
            extras.execute_values(cur,
                                  sql='INSERT INTO jpcosta.perda_obs (ref, perda_obs, perda_att, saldo) VALUES %s',
                                  argslist=[(int(row['ref']) if not pd.isna(row['ref']) else None, float(row['perda_obs']), float(row['perda_att']), float(row['saldo'])) for _, row in perda_obs_df.iterrows()],
                                  page_size=1000)

            # insert calculo_pd
            extras.execute_values(cur,
                                  sql='INSERT INTO jpcosta.calculo_pd (ref, pd) VALUES %s',
                                  argslist=[(int(row['ref']) if not pd.isna(row['ref']) else None, float(row['pd'])) for _, row in calculo_pd_df.iterrows()],
                                  page_size=1000)

        conn.commit()
        return
    except Exception:
        # sqlite fallback: insert into tables without schema prefix
        cur = conn.cursor()
        perda_args = []
        for _, row in perda_obs_df.iterrows():
            ref = int(row['ref']) if not pd.isna(row['ref']) else None
            perda_args.append((ref, float(row['perda_obs']), float(row['perda_att']), float(row['saldo'])))
        cur.executemany('INSERT INTO perda_obs (ref, perda_obs, perda_att, saldo) VALUES (?,?,?,?)', perda_args)

        pd_args = []
        for _, row in calculo_pd_df.iterrows():
            ref = int(row['ref']) if not pd.isna(row['ref']) else None
            pd_args.append((ref, float(row['pd'])))
        cur.executemany('INSERT INTO calculo_pd (ref, pd) VALUES (?,?)', pd_args)

        conn.commit()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true', help='Actually write to DB')
    p.add_argument('--db-host', default='localhost')
    p.add_argument('--db-port', default=5432, type=int)
    p.add_argument('--db-user', default='postgres')
    p.add_argument('--db-password', default='12345678')
    p.add_argument('--db-name', default='Simulacred')
    p.add_argument('--sqlite-file', default=None, help='Path to sqlite DB file to use/create')
    args = p.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    csvs = find_simulation_csvs(repo_root)
    if not csvs:
        print('Nenhum CSV de simulação encontrado (Simulacao_mes_*.csv ou Mes*.csv). Rode as simulações primeiro.')
        return

    print(f'Encontrados {len(csvs)} CSV(s). Lendo e parseando...')
    dfs = []
    for pth in csvs:
        df = read_sim_csv(Path(pth))
        print(f' - {pth.name}: {len(df)} linhas, colunas: {list(df.columns)}')
        dfs.append(df)

    df_all = pd.concat(dfs, ignore_index=True, sort=False)

    if not args.apply:
        print('Dry run: não serão feitas gravações no DB. Use --apply para inserir.')
        print('Resumo das colunas combinadas:', list(df_all.columns))
        return
    # connect to DB: prefer sqlite-file if provided
    if args.sqlite_file:
        sqlite_path = Path(args.sqlite_file)
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(sqlite_path))
        try:
            print('Inserindo registros em operacoes (sqlite)...')
            insert_operacoes(conn, df_all)

            print('Calculando e inserindo tabelas derivadas (perda_obs, calculo_pd) ...')
            compute_and_insert_derived(conn, df_all)
        finally:
            conn.close()
        return

    # fallback to postgres
    import psycopg2
    conn = psycopg2.connect(host=args.db_host, port=args.db_port, dbname=args.db_name, user=args.db_user, password=args.db_password)
    try:
        # Insert operacoes
        print('Inserindo registros em jpcosta.operacoes...')
        insert_operacoes(conn, df_all)

        # compute derived and insert
        print('Calculando e inserindo tabelas derivadas (perda_obs, calculo_pd) ...')
        compute_and_insert_derived(conn, df_all)

    finally:
        conn.close()


if __name__ == '__main__':
    main()
