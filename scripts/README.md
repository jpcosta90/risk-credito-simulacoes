## Scripts de suporte

### `setup_env.ps1`

Cria o ambiente virtual `.venv` e instala as dependências.

### `organize_workspace.ps1`

Organiza o projeto em:

- `data/` para dados e banco local;
- `notebooks/historico/` para notebooks antigos;
- `src/` para scripts da simulação;
- `outputs/` para resultados gerados.

### `prepare_dataset.py`

Junta os CSVs encontrados em um arquivo consolidado em `data/combined_dataset.csv`.

### `init_db.py`

Cria o banco SQLite local e aplica o schema do projeto.

```powershell
python init_db.py --sqlite-file ..\data\simulacred.db --apply-schema
```

### `etl_populate.py`

Lê os CSVs da simulação e popula as tabelas principais e derivadas.

```powershell
python etl_populate.py --apply --sqlite-file ..\data\simulacred.db
```

## Onde alterar a lógica

Se quiser mudar equações, probabilidades ou incluir variáveis macroeconômicas nas probabilidades, normalmente você vai editar estes arquivos:

- `src/Markov.py`
- `src/matrizes.py`
- `src/calibragem.py`
- `src/PD_LGD_ECL_PCLD.py`
- `src/Simulacao.py`
- `src/Simulacao_choque.py`
- `scripts/etl_populate.py`
- `scripts/init_db.py`

## Sequência mínima para rodar

```powershell
cd scripts
.\setup_env.ps1
.\organize_workspace.ps1
python prepare_dataset.py
python init_db.py --sqlite-file ..\data\simulacred.db --apply-schema
python etl_populate.py --apply --sqlite-file ..\data\simulacred.db
```

