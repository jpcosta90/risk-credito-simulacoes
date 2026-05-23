Param(
    [string]$envName = ".venv"
)

Write-Output "Criando ambiente virtual $envName..."
python -m venv $envName
Write-Output "Instalando dependências..."
& "$envName\\Scripts\\python.exe" -m pip install --upgrade pip
& "$envName\\Scripts\\python.exe" -m pip install -r ..\\requirements.txt
Write-Output "Pronto. Ative com: .\\$envName\\Scripts\\Activate.ps1"
