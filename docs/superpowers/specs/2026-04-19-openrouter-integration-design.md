# Design Spec: Integración Dinámica de OpenRouter como Alternativa a Ollama

## Contexto
El sistema actual (Chatbot RAG y Auto-Healing Team Normalizer) depende exclusivamente de una instancia local de **Ollama** para ejecutar el modelo de lenguaje (Gemma4). Sin embargo, existen limitaciones de hardware local o necesidad de acceder a modelos más avanzados (ej. GPT-4, Claude 3.5, Llama 3 70B) para mejorar la calidad de las respuestas y la resolución de alias.
Se requiere conectar la aplicación a **OpenRouter.ai**, una plataforma que actúa como puente universal hacia múltiples LLMs. Esta integración no debe reemplazar a Ollama, sino funcionar como una alternativa flexible y dinámica (Fallback).

## Objetivos
1. **Flexibilidad de Proveedor:** Permitir que la aplicación cambie de un LLM local (Ollama) a un LLM en la nube (OpenRouter) instantáneamente, con solo configurar una variable de entorno.
2. **Homogeneidad:** El modelo seleccionado se usará de manera uniforme tanto para el RAG (Chat) como para el Normalizador (Auto-Ajuste de nombres).
3. **Cero Hardcoding:** El nombre del modelo a utilizar en OpenRouter (ej. `anthropic/claude-3-haiku`) se leerá de una variable de entorno `LLM_MODEL_NAME`.

## Arquitectura de Selección Dinámica

### 1. Variables de Entorno (El Gatillo)
- Se leerá `OPENROUTER_API_KEY` desde el archivo `.env`.
- Si esta clave está presente y no está vacía, el sistema asumirá que debe usar **OpenRouter**.
- Si no está presente, el sistema hará el "Fallback" y utilizará la configuración actual de **Ollama** (`OLLAMA_BASE_URL`).
- La variable `OLLAMA_MODEL` se refactorizará a `LLM_MODEL_NAME` para que aplique a cualquier proveedor.

### 2. Configuración Global de LlamaIndex
- En `src/rag/config.py`, el método `init_llama_index()` implementará una bifurcación (`if/else`).
  - **Rama OpenRouter:** Se importará el cliente de OpenAI integrado en LlamaIndex (`llama_index.llms.openai.OpenAI`). Se instanciará configurando la `api_key` con la clave de OpenRouter y el `api_base` apuntando a `https://openrouter.ai/api/v1`.
  - **Rama Ollama:** Se instanciará el cliente habitual de Ollama.
- El cliente resultante se asignará globalmente a `Settings.llm`.

### 3. Consumidores del LLM
Dado que `Settings.llm` actúa como una interfaz estandarizada (*abstraction layer*):
- **TeamNormalizer (`src/ingestion/normalizer.py`)**: Su método `_ask_llm()` seguirá llamando a `Settings.llm.complete(prompt)` sin necesidad de modificar ni una sola línea de lógica. Automáticamente enviará el prompt a OpenRouter o a Ollama.
- **Chat Endpoint (`src/main.py`)**: El método `pipeline.query_index()` internamente usa `Settings.llm` para sintetizar la respuesta, por lo que tampoco requiere modificaciones profundas.

## Componentes a Modificar
- `.env.example`: Añadir las variables `OPENROUTER_API_KEY` y actualizar los comentarios explicativos sobre `LLM_MODEL_NAME`.
- `docker-compose.yml`: Asegurarse de que el contenedor backend reciba la variable `OPENROUTER_API_KEY` desde el entorno host.
- `requirements.txt`: Asegurar que esté instalado el plugin `llama-index-llms-openai`, el cual es necesario para comunicarse con APIs compatibles con OpenAI (como OpenRouter).
- `src/rag/config.py`: Reescribir `init_llama_index()` para implementar la inyección dinámica del LLM y de los Embeddings (estos últimos pueden mantenerse locales con BAAI/bge-small para ahorrar costos de API y solo tercerizar la generación de texto, o también pueden moverse a OpenAI).

## Manejo de Errores y Seguridad
- Si `OPENROUTER_API_KEY` está configurada pero es inválida, el LLM arrojará un error 401 en el Chat o en el Normalizador. Se mostrará un log claro, y la petición fallará de forma segura.
- Las credenciales nunca se expondrán en el código fuente ni en el Frontend.