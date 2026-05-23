# risco-credito-simulacoes

Este repositório foi organizado para que outra pessoa consiga baixar o projeto e repetir as simulações com o mínimo de fricção. O fluxo principal usa scripts Python e banco SQLite local. Os notebooks originais ficaram apenas como histórico em `notebooks/historico/`.

## Estrutura

- `data/`: CSVs de entrada, dataset consolidado e banco SQLite gerado pela rotina de ETL.
- `src/`: scripts Python usados nas simulações, calibração e análise.
- `notebooks/historico/`: notebooks originais, somente para consulta.
- `outputs/`: gráficos, tabelas e arquivos gerados nas execuções.
- `scripts/`: utilitários de apoio para preparar ambiente, organizar arquivos e carregar dados.

## Como rodar do zero

Se você acabou de baixar o projeto, siga exatamente esta sequência no PowerShell:

```powershell
git clone https://github.com/jpcosta90/risk-credito-simulacoes.git
cd risk-credito-simulacoes
powershell -ExecutionPolicy Bypass -File .\scripts\setup_env.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\organize_workspace.ps1
.\.venv\Scripts\python.exe .\scripts\prepare_dataset.py
.\.venv\Scripts\python.exe .\scripts\init_db.py --sqlite-file .\data\simulacred.db --apply-schema
.\.venv\Scripts\python.exe .\scripts\etl_populate.py --apply --sqlite-file .\data\simulacred.db
```

Se você já tiver o ambiente criado, pode começar direto da etapa de organização ou da etapa do banco.

## O que cada etapa faz

1. `setup_env.ps1` cria o ambiente virtual e instala as dependências.
2. `organize_workspace.ps1` cria a estrutura final e move os notebooks para `notebooks/historico/`.
3. `prepare_dataset.py` junta os CSVs em um arquivo consolidado, quando necessário.
4. `init_db.py` cria o SQLite local em `data/simulacred.db` e aplica o schema.
5. `etl_populate.py` lê os CSVs e popula as tabelas principais e derivadas.

## Onde editar para mudar o modelo

Se a ideia for alterar as equações, as probabilidades ou as premissas de simulação, os arquivos mais importantes são estes:

- [src/Markov.py](src/Markov.py): cadeia de Markov, transições e lógica de estados.
- [src/matrizes.py](src/matrizes.py): matrizes usadas nas simulações e nas probabilidades.
- [src/calibragem.py](src/calibragem.py): calibração dos parâmetros.
- [src/PD_LGD_ECL_PCLD.py](src/PD_LGD_ECL_PCLD.py): cálculos de PD, LGD, ECL e PCLD.
- [src/Simulacao.py](src/Simulacao.py): versão principal da simulação.
- [src/Simulacao_choque.py](src/Simulacao_choque.py): cenário de choque.
- [src/Simulacao_v2.py](src/Simulacao_v3.py) e variantes: versões alternativas da simulação.
- [src/Analise_final_simulacao.py](src/Analise_final_simulacao.py): consolidação da análise final.
- [scripts/etl_populate.py](scripts/etl_populate.py): carga dos CSVs e criação das tabelas derivadas.
- [scripts/init_db.py](scripts/init_db.py): criação do banco SQLite e aplicação do schema.

## GitHub

O nome esperado do repositório no GitHub é `risk-credito-simulacoes`.

Se o projeto já estiver clonado e você quiser publicar as alterações, o fluxo básico é:

```powershell
git add .
git commit -m "Organiza projeto e documentação"
git push -u origin main
```

