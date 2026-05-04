# Introducción a RAG

## ¿Qué es RAG?

RAG (Retrieval-Augmented Generation) es una técnica que combina la recuperación de documentos con la generación de texto mediante modelos de lenguaje. Fue propuesta para reducir las alucinaciones en los LLMs al anclar las respuestas en fuentes verificables.

## Componentes principales

Un sistema RAG tiene tres componentes principales: el indexador, el recuperador y el generador.

El indexador transforma documentos en vectores numéricos llamados embeddings. Estos vectores capturan el significado semántico del texto y se almacenan en una base de datos vectorial.

El recuperador recibe una pregunta del usuario, la convierte en un vector y busca los documentos más similares en la base de datos vectorial usando similitud coseno.

El generador recibe los documentos recuperados como contexto y genera una respuesta coherente usando un modelo de lenguaje, citando las fuentes.

## Ventajas sobre los LLMs tradicionales

Los modelos de lenguaje tradicionales solo pueden responder basándose en su conocimiento de entrenamiento, que puede estar desactualizado o ser incompleto.

RAG permite actualizar el conocimiento del sistema sin reentrenar el modelo, simplemente actualizando los documentos indexados. También permite citar fuentes específicas, lo que mejora la trazabilidad y confianza en las respuestas.

## Chunking y embeddings

El chunking es el proceso de dividir documentos largos en fragmentos más pequeños. El tamaño del chunk afecta directamente la calidad del retrieval: chunks muy grandes incluyen demasiado contexto irrelevante, mientras que chunks muy pequeños pueden perder el contexto necesario para entender una idea completa.

Los embeddings son representaciones vectoriales del texto que capturan su significado semántico. Modelos como sentence-transformers permiten generar embeddings de alta calidad que corren localmente sin necesidad de APIs externas.
