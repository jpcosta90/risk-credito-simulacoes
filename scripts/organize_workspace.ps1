# Organiza o workspace: cria pastas e move CSVs e notebooks
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

New-Item -ItemType Directory -Force -Path "$root\\..\\data" | Out-Null
New-Item -ItemType Directory -Force -Path "$root\..\notebooks\historico" | Out-Null
New-Item -ItemType Directory -Force -Path "$root\\..\\src" | Out-Null
New-Item -ItemType Directory -Force -Path "$root\\..\\outputs" | Out-Null

Get-ChildItem -Path $root -Filter *.csv -File -Recurse | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "$root\\..\\data" -Force
}

Get-ChildItem -Path $root -Filter *.ipynb -File -Recurse | ForEach-Object {
    if ($_.Name -like '*-checkpoint.ipynb') { return }
    Move-Item -Path $_.FullName -Destination "$root\..\notebooks\historico" -Force
}

Write-Output "Arquivos movidos: CSVs -> data/, notebooks -> notebooks/historico/."
