from pathlib import Path
import pandas as pd
import sys


def find_csvs(root: Path):
    data_dir = root / "data"
    candidates = []
    if data_dir.exists():
        candidates = list(data_dir.glob("**/*.csv"))
    if not candidates:
        # fallback: look in repo root and current folder
        candidates = list(root.glob("*.csv")) + list((root / 'scripts').glob("*.csv"))
    return candidates, data_dir


def main():
    repo_root = Path(__file__).resolve().parent.parent
    csvs, data_dir = find_csvs(repo_root)
    if not csvs:
        print("Nenhum CSV encontrado em data/ ou na raiz. Coloque seus CSVs em 'data/' ou na pasta raiz do projeto.")
        sys.exit(1)

    print(f"Encontrados {len(csvs)} CSV(s). Lendo e concatenando...")
    dfs = []
    for p in csvs:
        try:
            df = pd.read_csv(p)
            df['__source_file'] = p.name
            dfs.append(df)
        except Exception as e:
            print(f"Falha ao ler {p}: {e}")

    if not dfs:
        print("Nenhum CSV válido foi lido.")
        sys.exit(1)

    combined = pd.concat(dfs, ignore_index=True, sort=False)
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / 'combined_dataset.csv'
    combined.to_csv(out, index=False)
    print(f"Dataset combinado salvo em: {out}")


if __name__ == '__main__':
    main()
