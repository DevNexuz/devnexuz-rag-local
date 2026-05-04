@echo off
:: ============================================================
:: setup.bat — Crea el entorno virtual e instala dependencias
:: Uso: doble click o ejecutar desde CMD en la raiz del proyecto
:: ============================================================

echo.
echo ========================================
echo  Local RAG Knowledge Engine — Setup
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instala Python 3.11 o superior.
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% encontrado.

:: Eliminar venv anterior si existe
if exist .venv (
    echo [INFO] Eliminando entorno anterior...
    rmdir /s /q .venv
)

:: Crear nuevo venv
echo [INFO] Creando entorno virtual...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado en .venv\

:: Instalar dependencias
echo [INFO] Instalando dependencias (puede tardar unos minutos)...
.venv\Scripts\pip install -e ".[dev]" --quiet
if errorlevel 1 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.

:: Verificacion final
echo [INFO] Verificando instalacion...
.venv\Scripts\python -c "import rag, chromadb, sentence_transformers; print('[OK] Paquetes verificados correctamente.')"
if errorlevel 1 (
    echo [ERROR] Verificacion fallida. Revisa el output anterior.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setup completado exitosamente.
echo.
echo  Para activar el entorno:
echo    CMD:        .venv\Scripts\activate
echo    PowerShell: .venv\Scripts\Activate.ps1
echo ========================================
echo.
pause
