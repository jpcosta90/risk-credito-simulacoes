"""Script to create database and user if needed.

Usage:
  python init_db.py --host localhost --port 5432 --admin-user postgres --admin-password 12345678

Defaults match the docker-compose created instance.
"""
import argparse
from pathlib import Path
import sqlite3
import re
try:
    import psycopg2
    from psycopg2 import sql
except Exception:
    psycopg2 = None


def ensure_role(conn, role, password):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role,))
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(sql.Identifier(role)), [password])
            print(f"Created role {role}")
        else:
            print(f"Role {role} already exists")


def ensure_database(conn, dbname, owner=None):
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (dbname,))
        if not cur.fetchone():
            if owner:
                cur.execute(sql.SQL("CREATE DATABASE {} OWNER {};").format(sql.Identifier(dbname), sql.Identifier(owner)))
            else:
                cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(dbname)))
            print(f"Created database {dbname}")
        else:
            print(f"Database {dbname} already exists")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='localhost')
    p.add_argument('--port', default=5432, type=int)
    p.add_argument('--admin-user', default='postgres')
    p.add_argument('--admin-password', default='12345678')
    p.add_argument('--dbname', default='Simulacred')
    p.add_argument('--new-user', default='jpcosta')
    p.add_argument('--new-password', default='12345678')
    p.add_argument('--apply-schema', action='store_true', help='Apply SQL schema file to the created database')
    p.add_argument('--schema-file', default='../docker/postgres/initdb.d/schema.sql', help='Path to SQL schema file (relative to scripts/)')
    p.add_argument('--sqlite-file', default=None, help='Path to sqlite DB file to create/use (if provided, uses sqlite)')
    args = p.parse_args()
    # If sqlite-file given, create sqlite DB and apply schema translated to sqlite
    if args.sqlite_file:
        sqlite_path = Path(args.sqlite_file)
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        schema_path = Path(__file__).resolve().parent.joinpath(args.schema_file).resolve()
        try:
            sql_text = schema_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Failed to read schema file {schema_path}: {e}")
            return

        # Translate postgres-ish schema into sqlite-friendly SQL
        txt = sql_text
        # remove CREATE SCHEMA lines
        txt = re.sub(r"CREATE\s+SCHEMA.*?;\s*", "", txt, flags=re.IGNORECASE | re.DOTALL)
        # remove schema prefixes like jpcosta.
        txt = re.sub(r"\b[\w]+\.", "", txt)
        # id BIGSERIAL PRIMARY KEY -> id INTEGER PRIMARY KEY AUTOINCREMENT
        txt = re.sub(r"\bid\s+BIGSERIAL\s+PRIMARY\s+KEY\b", "id INTEGER PRIMARY KEY AUTOINCREMENT", txt, flags=re.IGNORECASE)
        # types
        txt = re.sub(r"\bBIGINT\b", "INTEGER", txt, flags=re.IGNORECASE)
        txt = re.sub(r"\bNUMERIC\b", "REAL", txt, flags=re.IGNORECASE)
        txt = re.sub(r"\bDOUBLE\s+PRECISION\b", "REAL", txt, flags=re.IGNORECASE)
        txt = re.sub(r"TIMESTAMP\s+WITH\s+TIME\s+ZONE\s+DEFAULT\s+now\(\)", "DATETIME DEFAULT CURRENT_TIMESTAMP", txt, flags=re.IGNORECASE)
        # remove OWNER/OWNER clauses (basic)
        txt = re.sub(r"OWNER\s*=\s*\w+", "", txt, flags=re.IGNORECASE)

        try:
            conn = sqlite3.connect(str(sqlite_path))
            conn.executescript(txt)
            conn.commit()
            conn.close()
            print(f"Created sqlite DB and applied translated schema to {sqlite_path}")
        except Exception as e:
            print(f"Failed to apply sqlite schema: {e}")
        return

    # Otherwise fallback to Postgres behavior
    if psycopg2 is None:
        print('psycopg2 is not available; cannot initialize Postgres. Use --sqlite-file to create a sqlite DB instead.')
        return

    conn = psycopg2.connect(host=args.host, port=args.port, dbname='postgres', user=args.admin_user, password=args.admin_password)
    conn.autocommit = True
    try:
        ensure_role(conn, args.new_user, args.new_password)
        ensure_database(conn, args.dbname, owner=args.new_user)
    finally:
        conn.close()

    if args.apply_schema:
        # apply schema SQL to the target database
        schema_path = Path(__file__).resolve().parent.joinpath(args.schema_file).resolve()
        try:
            sql_text = schema_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Failed to read schema file {schema_path}: {e}")
            return

        # connect to the newly created database as admin and execute statements
        conn2 = psycopg2.connect(host=args.host, port=args.port, dbname=args.dbname, user=args.admin_user, password=args.admin_password)
        try:
            with conn2.cursor() as cur:
                # naive split on semicolon; suitable for simple schema files
                for stmt in [s.strip() for s in sql_text.split(';') if s.strip()]:
                    cur.execute(stmt)
            conn2.commit()
            print(f"Applied schema from {schema_path} to database {args.dbname}")
        finally:
            conn2.close()


if __name__ == '__main__':
    main()
