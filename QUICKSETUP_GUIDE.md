# Guía de Inicio Rápido

¡Hola! Gracias por tu interés en este proyecto. Esta guía está escrita para que puedas tenerlo funcionando lo antes posible, sin importar tu sistema operativo ni tu nivel de experiencia con Python.

Si en algún momento algo no funciona como esperas, revisa la sección [Solución de Problemas](#solución-de-problemas) al final. Si el problema persiste, abre un [issue en GitHub](../../issues) y con gusto te ayudo.

---

## ¿Qué necesitas antes de empezar?

Solo dos cosas:

| Requisito | Versión mínima | ¿Cómo verificar? |
|---|---|---|
| **Python** | 3.11 o superior | `python --version` o `python3 --version` |
| **Git** | Cualquier versión reciente | `git --version` |

> **¿No tienes Python 3.11+?**
> - Windows: descárgalo desde [python.org](https://www.python.org/downloads/). Durante la instalación, marca **"Add Python to PATH"**.
> - Ubuntu/Debian: `sudo apt update && sudo apt install python3.11`
> - macOS con Homebrew: `brew install python@3.11`
> - WSL: sigue las instrucciones de Ubuntu arriba.

---

## Instalación paso a paso

### Windows

**Opción A — Doble click (la más fácil)**

1. Descarga o clona el proyecto:
   ```
   git clone https://github.com/tu-usuario/local-rag-engine.git
   ```
2. Abre la carpeta `local-rag-engine` en el Explorador de archivos.
3. Entra a la carpeta `scripts`.
4. Haz doble click en `setup.bat`.
5. Verás una ventana negra que instala todo automáticamente. Al final dirá **"Setup completado exitosamente"**.

**Opción B — PowerShell**

```powershell
git clone https://github.com/tu-usuario/local-rag-engine.git
cd local-rag-engine
.\scripts\setup.ps1
```

> Si PowerShell te dice que no puede ejecutar scripts, corre este comando primero y luego repite:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

**Activar el entorno en Windows**

Cada vez que abras una terminal nueva y quieras trabajar en el proyecto:
```cmd
.venv\Scripts\activate
```
Sabrás que está activo porque verás `(.venv)` al inicio de tu línea de comandos.

---

### Linux y macOS

```bash
# 1. Clona el proyecto
git clone https://github.com/tu-usuario/local-rag-engine.git
cd local-rag-engine

# 2. Da permisos al script (solo la primera vez)
chmod +x scripts/setup.sh

# 3. Ejecuta el setup
./scripts/setup.sh
```

Al terminar verás **"Setup completado exitosamente"** con instrucciones para el siguiente paso.

**Activar el entorno en Linux / macOS**

Cada vez que abras una terminal nueva:
```bash
source .venv/bin/activate
```
Sabrás que está activo porque verás `(.venv)` al inicio de tu línea de comandos.

---

### WSL (Windows Subsystem for Linux)

WSL se comporta exactamente igual que Linux. Sigue las instrucciones de la sección anterior dentro de tu terminal WSL.

> **Tip:** Clona el proyecto dentro del sistema de archivos de Linux (por ejemplo `~/projects/`), no en `/mnt/c/`. Esto evita problemas de permisos y mejora el rendimiento.

---

## Verificar que todo funciona

Con el entorno activado, corre:

```bash
python -c "import rag, chromadb, sentence_transformers; print('Todo OK')"
```

Si ves `Todo OK`, estás listo para usar el proyecto.

---

## Comandos útiles

### Linux / macOS / WSL (con Make)

```bash
make help       # ver todos los comandos disponibles
make test       # correr los tests
make lint       # verificar estilo del código
make format     # formatear código automáticamente
make reinstall  # borrar el entorno y reinstalar desde cero
make clean      # limpiar entorno y archivos temporales
```

### Windows (CMD o PowerShell)

```cmd
# Reinstalar desde cero si algo salió mal
scripts\setup.bat
```

---

## Usar el proyecto (próximamente en v0.1)

```bash
# Ingestar documentos (PDF, Markdown, TXT, DOCX)
rag ingest ./data/sample/

# Hacer una pregunta sobre los documentos
rag ask "¿Cuál es la idea principal del documento?"

# Ver cuántos documentos están indexados
rag status
```

---

## Solución de Problemas

**"python no se reconoce como comando"** (Windows)
> Python no está en tu PATH. Reinstálalo desde [python.org](https://www.python.org/downloads/) marcando la opción **"Add Python to PATH"**, o usa `py` en lugar de `python`.

**"Python 3.11+ no encontrado"** (Linux/Mac)
> El script busca versiones específicas. Instala Python 3.11+ con tu gestor de paquetes y vuelve a correr el setup.

**El script de PowerShell no corre**
> Ejecuta en PowerShell como administrador:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

**La instalación falla a mitad**
> Borra el entorno y empieza de nuevo:
> ```bash
> # Linux/Mac/WSL
> make reinstall
>
> # Windows
> scripts\setup.bat
> ```

**"No module named 'rag'"**
> El entorno no está activado. Actívalo primero:
> ```bash
> source .venv/bin/activate   # Linux/Mac/WSL
> .venv\Scripts\activate      # Windows
> ```

**Algo más salió mal**
> Abre un [issue en GitHub](../../issues) describiendo:
> 1. Tu sistema operativo y versión
> 2. La versión de Python (`python --version`)
> 3. El mensaje de error completo
>
> Con eso puedo ayudarte rápido.

---

## ¿Todo listo?

Con el entorno activo puedes explorar el código en `src/rag/`, correr los tests con `make test` (Linux/Mac) o `pytest` (Windows), y seguir el [ROADMAP](ROADMAP.md) para ver hacia dónde va el proyecto.

¡Gracias por tomarte el tiempo de probarlo!
