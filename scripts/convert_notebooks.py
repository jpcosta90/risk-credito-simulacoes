"""Converte notebooks (.ipynb) em scripts Python em ../src/.

Ferrolho simples: extrai células de código e grava em arquivos .py.
"""
from pathlib import Path
import json
import re


def notebook_to_script(nb_path: Path, out_dir: Path):
    name = nb_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{name}.py"
    with nb_path.open('r', encoding='utf-8') as f:
        nb = json.load(f)

    code_cells = [c for c in nb.get('cells', []) if c.get('cell_type') == 'code']
    lines = []
    lines.append(f"# Converted from {nb_path.name}\n")
    for i, cell in enumerate(code_cells, start=1):
        source = cell.get('source', [])
        # Normalize list of lines vs single string
        if isinstance(source, list):
            cell_lines = source
        else:
            cell_lines = source.splitlines(keepends=True)
        # Add a cell separator comment
        lines.append(f"# --- Cell {i} ---\n")
        # Remove IPython magics or prefix them with comment
        for ln in cell_lines:
            if re.match(r"^%|^!|^\s*\?|^\s*\.", ln):
                lines.append(f"# %magic: {ln}")
            else:
                lines.append(ln)
        lines.append("\n")

    with out_file.open('w', encoding='utf-8') as f:
        f.writelines(lines)

    return out_file


def find_notebooks(root: Path):
    candidates = list(root.glob('scripts/*.ipynb'))
    # also check scripts/notebooks and ../notebooks
    candidates += list(root.glob('scripts/**/*.ipynb'))
    candidates += list((root / 'notebooks').glob('*.ipynb')) if (root / 'notebooks').exists() else []
    # deduplicate
    seen = set()
    unique = []
    for p in candidates:
        if p.resolve() not in seen:
            seen.add(p.resolve())
            unique.append(p)
    return unique


def main():
    repo_root = Path(__file__).resolve().parent.parent
    notebooks = find_notebooks(repo_root)
    if not notebooks:
        print("Nenhum notebook encontrado.")
        return
    out_dir = repo_root / 'src'
    created = []
    for nb in notebooks:
        try:
            out = notebook_to_script(nb, out_dir)
            created.append(out)
            print(f"Converted: {nb} -> {out}")
        except Exception as e:
            print(f"Erro convertendo {nb}: {e}")

    # create __init__.py
    init = out_dir / '__init__.py'
    if not init.exists():
        init.write_text('# Package for converted notebooks\n')

    print(f"Feito. {len(created)} scripts criados em: {out_dir}")


if __name__ == '__main__':
    main()
