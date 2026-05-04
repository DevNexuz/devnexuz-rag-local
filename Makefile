# ============================================================
# Makefile — Comandos del proyecto
# Compatible con: Linux, macOS, WSL
#
# Uso: make <comando>
# ============================================================

VENV        := .venv
PYTHON      := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
PYTEST      := $(VENV)/bin/pytest
RUFF        := $(VENV)/bin/ruff

.PHONY: help setup test lint format clean reinstall

# Mostrar ayuda por defecto
help:
	@echo ""
	@echo "DevNexuz Local RAG Knowledge Engine — Comandos disponibles:"
	@echo ""
	@echo "  make setup      Crear entorno virtual e instalar dependencias"
	@echo "  make reinstall  Eliminar .venv y hacer setup desde cero"
	@echo "  make test       Correr suite de tests"
	@echo "  make lint       Verificar estilo con ruff"
	@echo "  make format     Formatear código con ruff"
	@echo "  make clean      Eliminar .venv y archivos temporales"
	@echo ""

# Crear entorno e instalar dependencias
setup: $(VENV)/bin/activate

$(VENV)/bin/activate: pyproject.toml
	@echo "[INFO] Creando entorno virtual..."
	python3 -m venv $(VENV)
	@echo "[INFO] Instalando dependencias..."
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -e ".[dev]" --quiet
	@echo "[OK] Setup completo. Activa con: source .venv/bin/activate"

# Eliminar venv y reinstalar desde cero
reinstall: clean setup

# Correr tests
test: $(VENV)/bin/activate
	$(PYTEST) -v

# Lint con ruff
lint: $(VENV)/bin/activate
	$(RUFF) check src/ tests/

# Formatear con ruff
format: $(VENV)/bin/activate
	$(RUFF) format src/ tests/
	$(RUFF) check --fix src/ tests/

# Limpiar entorno y caches
clean:
	@echo "[INFO] Eliminando entorno virtual y caches..."
	rm -rf $(VENV)
	rm -rf chroma_db/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "[OK] Limpieza completa."
