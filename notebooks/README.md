# Notebooks Históricos

Esta pasta guarda os notebooks originais do projeto apenas para consulta, auditoria e rastreio do processo de análise.

Use os scripts em `src/` para execuções reproduzíveis e os utilitários em `scripts/` para preparar dados, criar o banco SQLite e carregar as tabelas.

Fluxo recomendado:

1. Organizar o workspace com `scripts/organize_workspace.ps1`.
2. Rodar `scripts/init_db.py --sqlite-file ..\data\simulacred.db --apply-schema`.
3. Rodar `scripts/etl_populate.py --apply --sqlite-file ..\data\simulacred.db`.

Os notebooks aqui não são mais o formato principal de manutenção do projeto.