#!/usr/bin/env bash
# ============================================================
# setup.sh — Crea el entorno virtual e instala dependencias
# Compatible con: Linux, macOS, WSL
#
# Uso:
#   chmod +x scripts/setup.sh   # solo la primera vez
#   ./scripts/setup.sh
# ============================================================

set -euo pipefail  # salir si cualquier comando falla

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # sin color

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN} DevNexuz Local RAG Knowledge Engine — Setup${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# ----------------------------------------------------------
# 1. Verificar Python 3.11+
# ----------------------------------------------------------
PYTHON_BIN=""

for cmd in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON_BIN="$cmd"
            echo -e "${GREEN}[OK]${NC} Python $version encontrado en: $(command -v $cmd)"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}[ERROR]${NC} Python 3.11+ no encontrado."
    echo "        Instálalo desde: https://www.python.org/downloads/"
    echo "        O con tu gestor de paquetes:"
    echo "          Ubuntu/Debian: sudo apt install python3.11"
    echo "          macOS (brew):  brew install python@3.11"
    exit 1
fi

# ----------------------------------------------------------
# 2. Eliminar venv anterior si existe
# ----------------------------------------------------------
if [ -d ".venv" ]; then
    echo -e "${YELLOW}[INFO]${NC} Eliminando entorno anterior..."
    rm -rf .venv
fi

# ----------------------------------------------------------
# 3. Crear nuevo venv
# ----------------------------------------------------------
echo -e "${YELLOW}[INFO]${NC} Creando entorno virtual..."
"$PYTHON_BIN" -m venv .venv
echo -e "${GREEN}[OK]${NC} Entorno virtual creado en .venv/"

# ----------------------------------------------------------
# 4. Instalar dependencias
# ----------------------------------------------------------
echo -e "${YELLOW}[INFO]${NC} Instalando dependencias (puede tardar unos minutos)..."
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -e ".[dev]" --quiet
echo -e "${GREEN}[OK]${NC} Dependencias instaladas."

# ----------------------------------------------------------
# 5. Verificación final
# ----------------------------------------------------------
echo -e "${YELLOW}[INFO]${NC} Verificando instalación..."
.venv/bin/python -c "
import rag, chromadb, sentence_transformers
print(f'  rag: {rag.__version__}')
print(f'  chromadb: {chromadb.__version__}')
print(f'  sentence_transformers: {sentence_transformers.__version__}')
"
echo -e "${GREEN}[OK]${NC} Paquetes verificados correctamente."

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN} Setup completado exitosamente.${NC}"
echo ""
echo " Para activar el entorno:"
echo -e "   ${CYAN}source .venv/bin/activate${NC}"
echo ""
echo " Comandos disponibles (con make):"
echo -e "   ${CYAN}make test${NC}    — correr tests"
echo -e "   ${CYAN}make lint${NC}    — verificar estilo"
echo -e "   ${CYAN}make setup${NC}   — recrear entorno"
echo -e "${CYAN}========================================${NC}"
echo ""
