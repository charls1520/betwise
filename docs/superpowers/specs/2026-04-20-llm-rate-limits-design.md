# Design Spec: Mitigación de Rate Limits del LLM (Auto-Healing Normalizer)

## Contexto
El `TeamNormalizer` con Auto-Healing implementado en BetWise utiliza una instancia dinámica del LLM (sea Ollama local o OpenRouter vía la API de LlamaIndex). Durante entrenamientos masivos que abarcan múltiples ligas, un número elevado de equipos desconocidos puede provocar llamadas concurrentes al LLM. Si el usuario utiliza modelos gratuitos en OpenRouter (los cuales imponen *Rate Limits* estrictos, ej. X peticiones por minuto), el sistema arroja errores `429 Too Many Requests`.
Actualmente, el normalizador captura genéricamente estas excepciones devolviendo `None`, lo que desencadena que esa fila entera de datos valiosos sea descartada silenciosamente.

## Objetivos
1. **Evitar la Pérdida de Datos:** Prevenir que un error `429` temporal haga que el normalizador abandone el intento y se pierda el partido.
2. **Resiliencia en APIs Externas:** Hacer que la llamada al LLM espere de forma inteligente hasta que la cuota de la API se restaure.
3. **Logs Limpios:** Suprimir o mejorar la legibilidad de las trazas de error (Stack Traces) de LlamaIndex al topar con *rate limits*.

## Arquitectura de Mitigación

### 1. Reintentos Estructurados (Backoff Exponencial)
Se integrará la librería `tenacity`, que ya es parte de la arquitectura del proyecto (usada en *The-Odds-API* y *Clubelo*).
- Se creará una función envoltorio (wrapper) aislada o se aplicará directamente sobre el método `_ask_llm` del `TeamNormalizer`.
- El decorador `@retry` será configurado con `stop_after_attempt(5)` y un tiempo de espera exponencial `wait_exponential(multiplier=2, min=5, max=30)`.
- Esto significa que el sistema esperará ~5 segundos al primer fallo, ~10s al segundo, y así sucesivamente, brindándole tiempo suficiente al proveedor del LLM (como OpenRouter) para vaciar su ventana de *Rate Limit*.

### 2. Captura Específica de Errores de Rate Limit
En LlamaIndex o directamente en la solicitud HTTP al modelo, la respuesta suele levantar una excepción si se reciben códigos de error. El bloque de código actual:
```python
except Exception as e:
    print(f"LLM Auto-Healing error for '{raw_name}': {e}")
```
Se refactorizará para relanzar explícitamente (`raise`) el error dentro del contexto supervisado por `tenacity`, de modo que el decorador pueda capturarlo y aplicar el tiempo de espera, emitiendo un Warning limpio ("Rate Limit alcanzado, reintentando en X segundos...") en lugar de romper o descartar el flujo. Solo si agota los reintentos permitidos, se descartará devolviendo `None`.

## Componentes a Modificar
- `src/ingestion/normalizer.py`: Importar dependencias de `tenacity`. Añadir el decorador y ajustar la captura de excepciones dentro de `_ask_llm`.
- El código se escribirá de forma genérica para manejar también escenarios donde Ollama (local) está saturado.

## Manejo de Errores y Seguridad
- Al implementar esta solución, la carga (training) histórica masiva no colapsará ni omitirá registros por fallos esporádicos en la nube. 
- La demora total del proceso de scraping se incrementará un poco únicamente cuando se activen los bloqueos temporales, protegiendo al usuario de ser baneado.