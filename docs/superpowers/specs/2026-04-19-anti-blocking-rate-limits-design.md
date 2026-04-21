# Design Spec: Rate Limits, Anti-Bot y Estabilización de Ingesta (Anti-Bloqueos)

## Contexto
Durante el proceso de Ingesta Histórica Masiva (cruzando *football-data.co.uk*, *Understat* y *Clubelo* para 5 grandes ligas durante 3 a 5 temporadas), el sistema ejecutó cientos de solicitudes HTTP y llamadas concurrentes al navegador (Playwright) en menos de 10 segundos. 
Esto provocó que las plataformas destino detectaran un comportamiento anómalo (DDoS o bot scraping) e intervinieran mediante bloqueos por IP (`Max retries exceeded`) o cierre abrupto de la conexión del navegador (`Target page, context or browser has been closed`).
Se requiere implementar medidas de "Rate Limiting" (límites de frecuencia) y técnicas pasivas Anti-Bot (retrasos aleatorios y configuración sigilosa de headers) para estabilizar la extracción masiva de datos y evitar baneos temporales.

## Objetivos
1. **Pausas Humanizadas (Jitter):** Introducir tiempos de espera variables (aleatorios) entre cada solicitud consecutiva a un mismo dominio para mimetizar la navegación humana.
2. **Reintentos Estructurados (Backoff):** Manejar los errores transitorios (`Timeout`, `503`, `429`) esperando gradualmente más tiempo antes de reintentar, en lugar de bombardear el servidor inmediatamente.
3. **Resiliencia Global:** Asegurar que si una liga o temporada falla permanentemente después de los reintentos, el proceso no colapse, permitiendo que la ingesta de las demás ligas continúe sin problemas.
4. **Optimización de Playwright:** Reducir la sobrecarga bloqueando recursos multimedia pesados (imágenes, CSS, fuentes) que elevan la probabilidad de bloqueos o errores por memoria.

## Arquitectura Anti-Bloqueos (Rate Limiting)

### 1. Ingesta Estándar (`requests` y APIs)
- En `src/ingestion/historical.py` y `src/ingestion/scrapers/clubelo.py`, se envolverá cada llamada a `requests.get()` en retardos aleatorios (`time.sleep(random.uniform(2.0, 5.0))`).
- Se configurarán encabezados HTTP (`Headers`) estándar y realistas (User-Agent, Accept-Language) para que `football-data.co.uk` no bloquee a la librería Python por defecto.
- Se configurarán tiempos de espera (Timeout) explícitos (ej. 15-20 segundos) para permitir que conexiones lentas se completen.

### 2. Ingesta Sigilosa (`Playwright` y Scrapling)
- En `src/ingestion/scrapers/understat_historical.py` y `understat.py`, se introducirán pausas asíncronas (`await asyncio.sleep(...)`) antes de cada navegación de URL.
- Se configurará la sesión de Playwright (`browser.new_context()`) para enmascarar el agente, configurando las dimensiones de la pantalla y esquivando detecciones básicas (`headless=True` no suele ser problema para Understat, pero añadir *User Agents* reales ayuda).
- Se habilitará el bloqueo de carga de recursos no esenciales (`route.abort()` en `.png`, `.jpg`, `.css`) para acelerar la navegación y reducir la huella de tráfico, lo que aminora el riesgo de bloqueos.

### 3. Aislamiento de Errores
- Cada iteración del bucle masivo en `historical.py` (por liga y temporada) tendrá un bloque `try-except` que atrapará todas las excepciones de red.
- Si una descarga falla definitivamente, registrará un error (`logging.error`) y usará `continue` para saltar a la siguiente liga/temporada de forma segura. El Sistema de Caché existente (`merged_history_cache.csv`) garantiza que en la próxima ejecución del Cron, el proceso únicamente intentará recuperar las temporadas que fallaron.

## Componentes a Modificar
- `src/ingestion/historical.py`: Inyectar `import time`, `import random` e incorporar pausas y retries nativos o mediante `tenacity`.
- `src/ingestion/scrapers/understat_historical.py`: Actualizar la inicialización del contexto de Playwright y las pausas `asyncio`.
- `src/ingestion/scrapers/understat.py`: Similar actualización de contexto y pausas.
- `src/ingestion/scrapers/clubelo.py`: Añadir retardo de seguridad antes del fetch y soporte de reintentos.

## Manejo de Errores y Seguridad
- Todo el manejo es reactivo. No se requiere proxy ni configuraciones complejas externas. 
- La estabilidad del contenedor mejorará al evitar miles de peticiones simultáneas, resultando en un entorno Docker más limpio y sin caídas abruptas de los sub-procesos.