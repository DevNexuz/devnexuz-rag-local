# Roadmap de Desarrollo — DevNexuz Local RAG Knowledge Engine

Ruta completa de 0 a producción. Estado actualizado: 2026-05-04.

---

## Fase 0 — Fundación ✅ COMPLETADA

Todo lo que ya existe en el repo.

| Tarea | Archivo | Estado |
|---|---|---|
| README con arquitectura y decisiones de diseño | `README.md` | ✅ |
| pyproject.toml con dependencias y script `rag` | `pyproject.toml` | ✅ |
| .gitignore | `.gitignore` | ✅ |
| Stubs de los 6 módulos core con firmas y docstrings | `src/rag/*.py` | ✅ |
| Tests de contrato para chunker | `tests/test_chunk.py` | ✅ |
| Estructura de carpetas | `data/`, `notebooks/` | ✅ |

**Próximo paso manual:** `git init` + primer commit.

---

## Fase 1 — Pipeline Core (MVP funcional)

**Meta:** `rag ingest <dir>` y `rag ask "<pregunta>"` corren end-to-end.
**Estimado:** 3–4 sesiones de trabajo.

### 1.1 — Entorno local
- [ ] Crear y activar virtualenv (`uv venv` o `python -m venv`)
- [ ] Instalar dependencias (`uv pip install -e ".[dev]"`)
- [ ] Verificar que los stubs importan sin error

### 1.2 — Loaders (`ingest.py`)
- [x] `_load_txt` — leer archivo plano con metadata básica
- [x] `_load_markdown` — extraer texto limpio (sin sintaxis MD)
- [x] `_load_pdf` — texto por página con número de página en metadata
- [x] `_load_docx` — párrafos como unidades de texto
- [x] `load_directory` — iterar recursivo con filtro por extensión
- [x] 10 tests pasando en `tests/test_ingest.py`

### 1.3 — Chunker (`chunk.py`)
- [x] Implementar `split_document` con `RecursiveCharacterTextSplitter`
- [x] Propagar metadata: `source`, `page`, `chunk_id` (hash md5 deterministico), `chunk_index`
- [x] Pasar los 6 tests de `test_chunk.py`

### 1.4 — Embedder (`embed.py`)
- [x] Lazy-load de `SentenceTransformer("all-MiniLM-L6-v2")`
- [x] `embed(texts)` — batch processing
- [x] `embed_one(text)` — para queries
- [x] Property `dimension` — 384 para MiniLM
- [x] 8 tests pasando incluyendo test de similitud semántica

### 1.5 — Vector Store (`store.py`)
- [x] `ChromaStore._connect()` — lazy, PersistentClient con espacio coseno
- [x] `ChromaStore.add(chunks, embeddings)` — upsert por chunk_id (sin duplicados)
- [x] `ChromaStore.search(embedding, k)` — devuelve chunks con score [0,1]
- [x] `ChromaStore.count()` — número de chunks
- [x] `ChromaStore.reset()` — limpieza para tests
- [x] 9 tests pasando con vectores sintéticos (no requieren modelo)

### 1.6 — Retriever (`retrieve.py`)
- [x] `retrieve(query, embedder, store, k)` — embed query + search
- [x] `retrieve_mmr(...)` — Maximal Marginal Relevance con embeddings reales
- [x] `_cosine_similarity` — utilidad interna para MMR
- [x] 11 tests pasando con FakeEmbedder (sin cargar modelo)

### 1.7 — Q&A (`qa.py`)
- [x] `build_context(chunks)` — citas `[filename:página]` usando solo el nombre del archivo
- [x] `answer_extractive(chunks, question)` — fallback sin LLM
- [x] `answer_with_ollama(chunks, question, model)` — cliente Ollama con prompt template
- [x] `answer(...)` — fallback silencioso a extractivo si Ollama falla
- [x] 15 tests pasando, ninguno requiere Ollama ni modelo de embeddings

### 1.8 — CLI (`cli.py`)
- [x] `rag ingest <path>` — pipeline completo con progress bar
- [x] `rag ask "<pregunta>"` — retrieval + qa con panel de respuesta y tabla de fuentes
- [x] `rag status` — chunks indexados en el store
- [x] Flag `--no-llm` para modo extractivo sin Ollama
- [x] Flag `--mmr` para retrieval con diversidad
- [x] UTF-8 forzado en Windows para compatibilidad con Rich
- [x] Demo end-to-end verificado con intro_rag.md

**Entregable Fase 1:** Demo grabada o README con ejemplo de output real. Tests pasando en CI.

---

## Fase 2 — Calidad de Retrieval

**Meta:** Mejorar qué tan buenos son los chunks que se recuperan.
**Estimado:** 2–3 sesiones.

### 2.1 — MMR (`retrieve.py`)
- [ ] Implementar `retrieve_mmr` (Maximal Marginal Relevance)
- [ ] Flag `--mmr` en CLI
- [ ] Comparativa manual: top-5 similarity vs top-5 MMR

### 2.2 — Hybrid Search
- [ ] Añadir `rank_bm25` al proyecto
- [ ] BM25 index sobre los chunks al momento de ingest
- [ ] Función `retrieve_hybrid(query, bm25_index, store, alpha)` — fusión de scores
- [ ] Test: queries con keywords exactas vs semánticas

### 2.3 — Reranking (cross-encoder)
- [ ] Añadir `sentence-transformers` cross-encoder (`bge-reranker-base`)
- [ ] `rerank(query, chunks, top_n)` — re-ordenar candidatos
- [ ] Integrar en el pipeline como paso opcional (`--rerank` en CLI)

**Entregable Fase 2:** Comparativa documentada de configuraciones.

---

## Fase 3 — Evaluación Cuantitativa

**Meta:** Números reales sobre qué tan bueno es el sistema.
**Estimado:** 2 sesiones.

### 3.1 — Dataset de evaluación
- [ ] Seleccionar 2–3 documentos de dominio conocido
- [ ] Escribir 25–30 pares Q&A ground-truth a mano
- [ ] Guardar en `data/eval/qa_groundtruth.json`

### 3.2 — Métricas de retrieval
- [ ] Hit@k: ¿el chunk correcto está en los top-k?
- [ ] MRR (Mean Reciprocal Rank)
- [ ] Script `scripts/eval_retrieval.py`

### 3.3 — Métricas de generación
- [ ] Faithfulness: ¿la respuesta está soportada por el contexto?
- [ ] Answer relevancy: ¿responde la pregunta?
- [ ] Usar RAGAS o implementación propia simple
- [ ] Notebook `notebooks/eval.ipynb` completo con gráficas

### 3.4 — Comparativa de configuraciones
- [ ] Grid: chunk_size × k × modelo_embedding × con/sin reranking
- [ ] Tabla de resultados en README

**Entregable Fase 3:** Notebook reproducible con resultados reales.

---

## Fase 4 — Robustez y Formatos Avanzados

**Meta:** Manejar documentos del mundo real (con tablas, imágenes, PDFs sucios).
**Estimado:** 2–3 sesiones.

### 4.1 — Chunking semántico
- [ ] Comparar chunking por caracteres vs por párrafos vs semántico
- [ ] Implementar chunking por secciones (detectar headers en MD/DOCX)

### 4.2 — Tablas y estructura
- [ ] Extraer tablas de PDFs con `pdfplumber` o `unstructured`
- [ ] Serializar tablas como texto estructurado para el contexto

### 4.3 — OCR para PDFs escaneados
- [ ] Detectar PDF sin capa de texto
- [ ] Fallback a `pytesseract` + `pdf2image`

### 4.4 — Deduplicación
- [ ] Hash de chunks para evitar duplicados al re-ingestar
- [ ] Comando `rag ingest --update` que solo añade lo nuevo

**Entregable Fase 4:** Ingestar un PDF escaneado y responder preguntas sobre él.

---

## Fase 5 — API y UI

**Meta:** Accesible desde el navegador y consumible como servicio.
**Estimado:** 3–4 sesiones.

### 5.1 — API REST (FastAPI)
- [ ] `POST /ingest` — subir documento
- [ ] `POST /ask` — hacer pregunta, devuelve respuesta + fuentes
- [ ] `GET /status` — stats del store
- [ ] Validación con Pydantic
- [ ] Documentación automática en `/docs`

### 5.2 — UI (Streamlit)
- [ ] Upload de documentos con progress
- [ ] Chat interface para preguntas
- [ ] Mostrar fuentes como expander

### 5.3 — Observabilidad
- [ ] Logging estructurado (JSON) con `structlog`
- [ ] Latencia por etapa: ingest, embed, retrieve, generate
- [ ] Endpoint `/metrics` básico

**Entregable Fase 5:** Demo accesible en `localhost:8501`.

---

## Fase 6 — Producción

**Meta:** Deployable, reproducible, listo para mostrar en entrevistas técnicas.
**Estimado:** 2 sesiones.

### 6.1 — Containerización
- [ ] `Dockerfile` para la app
- [ ] `docker-compose.yml` con app + Ollama
- [ ] `.env.example` con configuración

### 6.2 — CI/CD (GitHub Actions)
- [ ] Workflow: lint (ruff) + tests en cada PR
- [ ] Badge de CI en README

### 6.3 — Documentación final
- [ ] README actualizado con demo GIF o screenshot
- [ ] Sección "Cómo correrlo localmente" paso a paso
- [ ] Arquitectura final documentada con decisiones actualizadas

**Entregable Fase 6:** `docker compose up` y el sistema corre completo.

---

## Resumen visual

```
Fase 0  ████████████████████  DONE
Fase 1  ░░░░░░░░░░░░░░░░░░░░  MVP — próxima
Fase 2  ░░░░░░░░░░░░░░░░░░░░  Retrieval quality
Fase 3  ░░░░░░░░░░░░░░░░░░░░  Evaluation
Fase 4  ░░░░░░░░░░░░░░░░░░░░  Robustness
Fase 5  ░░░░░░░░░░░░░░░░░░░░  API + UI
Fase 6  ░░░░░░░░░░░░░░░░░░░░  Production
```

## Para la entrevista (prioridad real)

Si el tiempo aprieta, las fases con mayor ROI para la entrevista son:

1. **Fase 1** — sin esto no hay nada que mostrar. Obligatoria.
2. **Fase 3** — tener métricas reales te separa del 90% de candidatos.
3. **Fase 6.2** — un badge de CI verde en GitHub impresiona más de lo que parece.
4. **Fases 2, 4, 5** — valiosas pero presentables como roadmap documentado.
