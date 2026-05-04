"""CLI — comandos `rag ingest`, `rag ask` y `rag status`."""

import sys
from pathlib import Path

# Forzar UTF-8 en Windows para que Rich pueda renderizar spinners y paneles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import box

app = typer.Typer(
    name="rag",
    help="Local RAG Knowledge Engine — ingesta documentos y responde preguntas.",
    add_completion=False,
)
# force_terminal evita el renderer legacy de Windows que no soporta UTF-8
console = Console()


@app.command()
def ingest(
    path: Path = typer.Argument(..., help="Archivo o directorio a ingestar"),
    chunk_size: int = typer.Option(512, help="Tamaño de chunk en tokens aprox."),
    overlap: int = typer.Option(64, help="Solapamiento entre chunks"),
    db: str = typer.Option("chroma_db", help="Ruta del vector store"),
):
    """Ingesta documentos: carga, trocea, embebe y almacena."""
    from rag.ingest import load_document, load_directory
    from rag.chunk import split_documents
    from rag.embed import Embedder
    from rag.store import ChromaStore

    if not path.exists():
        console.print(f"[red]Error:[/red] No existe la ruta: {path}")
        raise typer.Exit(1)

    # 1. Cargar documentos
    with console.status("[cyan]Cargando documentos...[/cyan]"):
        if path.is_dir():
            docs = list(load_directory(path))
        else:
            docs = list(load_document(path))

    if not docs:
        console.print("[yellow]No se encontraron documentos soportados.[/yellow]")
        raise typer.Exit(0)

    console.print(f"[green]OK[/green] {len(docs)} documento(s) cargado(s)")

    # 2. Chunking
    with console.status("[cyan]Dividiendo en chunks...[/cyan]"):
        chunks = split_documents(docs, chunk_size=chunk_size, overlap=overlap)

    console.print(f"[green]OK[/green] {len(chunks)} chunk(s) generado(s) "
                  f"(size~{chunk_size} tokens, overlap={overlap})")

    # 3. Embeddings
    embedder = Embedder()
    texts = [c["text"] for c in chunks]

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Generando embeddings...[/cyan]"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("embed", total=len(texts))
        # Procesamos en lotes de 64 para mostrar progreso
        batch_size = 64
        all_vectors = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            all_vectors.extend(embedder.embed(batch))
            progress.update(task, advance=len(batch))

    console.print(f"[green]OK[/green] {len(all_vectors)} embedding(s) generado(s) "
                  f"(dim={embedder.dimension})")

    # 4. Guardar en vector store
    store = ChromaStore(persist_dir=db)
    before = store.count()

    with console.status("[cyan]Guardando en vector store...[/cyan]"):
        store.add(chunks, all_vectors)

    after = store.count()
    new = after - before

    console.print(f"[green]OK[/green] Vector store actualizado: "
                  f"{new} nuevo(s), {after} total en [bold]{db}[/bold]")
    console.print()
    console.print(Panel(
        f"[bold green]Ingesta completada[/bold green]\n"
        f"Documentos: {len(docs)}  |  Chunks: {len(chunks)}  |  "
        f"Store: {after} total",
        title="rag ingest",
        border_style="green",
    ))


@app.command()
def ask(
    question: str = typer.Argument(..., help="Pregunta a responder"),
    k: int = typer.Option(5, help="Número de chunks a recuperar"),
    db: str = typer.Option("chroma_db", help="Ruta del vector store"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Modo extractivo (sin Ollama)"),
    model: str = typer.Option("llama3.2:3b", help="Modelo Ollama a usar"),
    mmr: bool = typer.Option(False, "--mmr", help="Usar MMR para diversidad en retrieval"),
):
    """Responde una pregunta usando los documentos ingestados."""
    from rag.embed import Embedder
    from rag.store import ChromaStore
    from rag.retrieve import retrieve, retrieve_mmr
    from rag.qa import answer

    store = ChromaStore(persist_dir=db)

    if store.count() == 0:
        console.print(f"[yellow]El store está vacío.[/yellow] "
                      f"Ejecuta [bold]rag ingest <ruta>[/bold] primero.")
        raise typer.Exit(1)

    embedder = Embedder()

    # Retrieval
    with console.status("[cyan]Buscando chunks relevantes...[/cyan]"):
        if mmr:
            chunks = retrieve_mmr(question, embedder, store, k=k)
        else:
            chunks = retrieve(question, embedder, store, k=k)

    if not chunks:
        console.print("[yellow]No se encontraron chunks relevantes.[/yellow]")
        raise typer.Exit(0)

    # Q&A
    with console.status("[cyan]Generando respuesta...[/cyan]"):
        result = answer(chunks, question, use_ollama=not no_llm, model=model)

    # Mostrar respuesta
    mode_label = {
        "generative": f"[blue]generative[/blue] ({result.get('model', '')})",
        "extractive": "[yellow]extractive[/yellow] (sin LLM)",
    }.get(result["mode"], result["mode"])

    console.print()
    console.print(Panel(
        result["answer"],
        title=f"[bold]Respuesta[/bold] — modo {mode_label}",
        border_style="blue",
        padding=(1, 2),
    ))

    # Mostrar fuentes
    if result["sources"]:
        console.print()
        table = Table(title="Fuentes", box=box.SIMPLE, show_header=False)
        table.add_column("", style="dim")
        for src in result["sources"]:
            table.add_row(f"• {src}")
        console.print(table)


@app.command()
def status(
    db: str = typer.Option("chroma_db", help="Ruta del vector store"),
):
    """Muestra cuántos chunks hay almacenados en el vector store."""
    from rag.store import ChromaStore

    store = ChromaStore(persist_dir=db)
    count = store.count()

    if count == 0:
        console.print(Panel(
            "[yellow]Store vacío.[/yellow] "
            "Ejecuta [bold]rag ingest <ruta>[/bold] para ingestar documentos.",
            title="rag status",
            border_style="yellow",
        ))
    else:
        console.print(Panel(
            f"[green]{count}[/green] chunk(s) indexado(s) en [bold]{db}[/bold]",
            title="rag status",
            border_style="green",
        ))
