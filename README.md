# risco-credito-simulacoes — resumo técnico

Este repositório contém a implementação das simulações, calibração e análises. Os notebooks originais foram preservados como referência apenas; o código executável foi reorganizado em `src/` e utilitários em `scripts/`.

Principais mudanças aplicadas
- Código refatorado para ser import-safe (nenhuma execução pesada no import).
- Substituição de `np.pmt` por `numpy_financial.pmt` onde aplicável.
- Demo functions: cada módulo relevante expõe uma função de demonstração (ex.: `_run_pd_lgd_demo`, `_run_matrizes_demo`, `main`, `run_markov_sim`).
- Banco local: suporte a fallback para SQLite (`data/simulacred.db`) para executar análises sem Postgres.
- Scripts ETL em `scripts/etl_populate.py` para popular o banco a partir dos CSVs.

Estrutura relevante
- `data/` — CSVs e arquivo SQLite (`data/simulacred.db`).
- `src/` — módulos Python (simulação, markov, matrizes, calibragem, análises).
- `scripts/` — utilitários: ETL e inicialização do DB.

Quick start (conciso, técnico)
1) criar e ativar venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) instalar dependências (recomendado usar `requirements.txt` se disponível)

```powershell
pip install -r requirements.txt
# se não houver requirements.txt, instale o mínimo:
pip install pandas numpy numpy-financial matplotlib
```

3) popular o banco SQLite a partir dos CSVs (cria `data/simulacred.db`)

```powershell
.\.venv\Scripts\python.exe scripts/etl_populate.py --apply --sqlite-file data/simulacred.db
```

4) verificar módulos e executar demos (exemplos)

```powershell
# importar módulo e executar demo leve
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'.'); import src.Simulacao as S; S.main(sample_clients=100)"
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'.'); import src.Markov as M; print(M.run_markov_sim(10,2,None))"
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'.'); import src.PD_LGD_ECL_PCLD as P; P._run_pd_lgd_demo()"
```

Notas de operação e desenvolvimento
- Os módulos foram escritos para tentar Postgres primeiro e, em seguida, usar o SQLite quando Postgres não está disponível. O SQLite local é suficiente para reproduzir os passos de análise se os CSVs forem carregados via ETL.
- Evite executar módulos diretamente se você espera que eles criem ou insiram dados; prefira rodar as funções de demo/CLI (por exemplo `main()` ou `_run_*_demo()`), que aceitam parâmetros para reduzir amostras.
- Se precisar reproduzir o ambiente com Postgres, os módulos usam a string `host=localhost dbname=Simulacred user=postgres password=12345678` por padrão — trocar conforme necessário.

Arquivo-chave para revisão rápida
- `scripts/etl_populate.py` — leitura dos CSVs, normalização e inserção nas tabelas `operacoes`, `perda_obs`, `calculo_pd` (suporta insert via sqlite quando Postgres não estiver disponível).

Se quiser, eu atualizo este README com uma seção opcional de troubleshooting (erros comuns e como corrigi-los) ou adiciono um script `scripts/run_smoketests.py` para automatizar as verificações. Qual prefere?

