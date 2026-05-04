# ============================================================
# setup.ps1 — Crea el entorno virtual e instala dependencias
# Uso: click derecho -> "Ejecutar con PowerShell"
#      o desde terminal: .\scripts\setup.ps1
# ============================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Local RAG Knowledge Engine — Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "[OK] $pyVersion encontrado." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no encontrado. Instala Python 3.11 o superior." -ForegroundColor Red
    Write-Host "        https://www.python.org/downloads/"
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Eliminar venv anterior si existe
if (Test-Path ".venv") {
    Write-Host "[INFO] Eliminando entorno anterior..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

# Crear nuevo venv
Write-Host "[INFO] Creando entorno virtual..." -ForegroundColor Yellow
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] No se pudo crear el entorno virtual." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "[OK] Entorno virtual creado en .venv\" -ForegroundColor Green

# Instalar dependencias
Write-Host "[INFO] Instalando dependencias (puede tardar unos minutos)..." -ForegroundColor Yellow
.venv\Scripts\pip install -e ".[dev]" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Fallo al instalar dependencias." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "[OK] Dependencias instaladas." -ForegroundColor Green

# Verificacion final
Write-Host "[INFO] Verificando instalacion..." -ForegroundColor Yellow
.venv\Scripts\python -c "import rag, chromadb, sentence_transformers; print('[OK] Paquetes verificados correctamente.')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Verificacion fallida." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup completado exitosamente." -ForegroundColor Green
Write-Host ""
Write-Host " Para activar el entorno:" -ForegroundColor White
Write-Host "   CMD:        .venv\Scripts\activate" -ForegroundColor Gray
Write-Host "   PowerShell: .venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Presiona Enter para salir"
