# Especificación: Migración a Scrapling y Sistema Centralizado de Logs

## Contexto
Actualmente, los scrapers (específicamente Understat usando Playwright) están sufriendo errores de `Timeout` debido a la pesadez del navegador headless y posibles bloqueos de red o antibots. Además, los errores son silenciados y los datos inválidos se descartan sin dejar un rastro claro, ya que la aplicación utiliza únicamente sentencias `print()` que dificultan la trazabilidad.

## Objetivo
1.  **Reemplazar Playwright por Scrapling** para optimizar el scraper de Understat, haciéndolo más ligero, rápido y resistente a bloqueos.
2.  **Implementar un sistema de logs centralizado (usando `loguru`)** para tener registro tanto en consola como en un archivo persistente (`logs/ingestion.log`), permitiendo detectar y depurar fallos silenciosos o bloqueos de red.

## Arquitectura y Componentes

### 1. Sistema de Logs (`backend/src/utils/logger.py`)
*   Se creará un nuevo módulo de utilidad que configurará `loguru`.
*   **Salidas (Sinks):**
    *   **Consola:** Salida estándar con colores y formato claro (`sys.stderr`).
    *   **Archivo:** Archivo rotativo en `logs/ingestion.log` (rotación a los 10MB).
*   **Formato:** Incluirá el timestamp, nivel de log (INFO, WARNING, ERROR, DEBUG), módulo/función y el mensaje.
*   **Refactorización:** Se modificarán los archivos `historical.py`, `clubelo.py` y `normalizer.py` para reemplazar las llamadas a `print()` por las funciones correspondientes del logger (`logger.info()`, `logger.error()`, `logger.warning()`, `logger.exception()`).

### 2. Migración del Scraper de Understat (`backend/src/ingestion/scrapers/understat_historical.py`)
*   Se eliminará la dependencia de Playwright.
*   Se instalará `scrapling` y sus dependencias (ej. `scrapling[fetchers]`) en el entorno/Dockerfile del backend.
*   Se utilizará la clase `Fetcher` o `StealthyFetcher` de Scrapling para realizar la petición HTTP, sorteando protecciones antibot si las hubiera, obteniendo el HTML de la página.
*   Dado que los datos de Understat (xG) vienen incrustados en un bloque de código JavaScript (`var teamsData = JSON.parse(...)`), se utilizarán expresiones regulares (`re`) sobre el texto HTML devuelto por Scrapling para extraer y decodificar el JSON.
*   El manejo de errores usará el nuevo sistema de logs. Cualquier excepción en la extracción o descarga se registrará con la traza completa utilizando `logger.exception()`, para asegurar visibilidad en caso de fallos.
*   La función dejará de ser obligatoriamente asíncrona, simplificando la integración.

## Flujo de Datos
1.  Los scripts de ingesta y normalización importarán la instancia unificada de `logger`.
2.  Al descargar datos de Understat, se llamará a la nueva función basada en Scrapling.
3.  Si la red está bloqueada o hay un fallo, Scrapling o el regex de extracción generarán una excepción, la cual será capturada en un bloque `try/except`.
4.  El error se escribirá en `logs/ingestion.log` y en la terminal mediante `logger.exception()`.
5.  La función de scraping retornará un DataFrame vacío y el script principal (`historical.py`) registrará el fallo para la liga/temporada, permitiendo al sistema continuar con el resto de datos pero dejando un historial claro del motivo del fallo.

## Dependencias
*   Añadir `scrapling[fetchers]` o equivalente y `loguru` a las dependencias del proyecto (ej. `backend/requirements.txt` o la configuración de Docker).
*   Asegurar de remover la instalación de `playwright` y sus navegadores si ya no se utilizan en ninguna otra parte.

## Testing
*   Se ejecutarán pruebas manuales comprobando la extracción de la temporada actual de Understat mediante Scrapling (`python -c "from src.ingestion.scrapers.understat_historical import fetch_understat_historical_season..."`).
*   Se verificará la creación automática de la carpeta `logs/` y el archivo `ingestion.log`.
*   Se forzará un error controlado (ej. URL incorrecta) para comprobar que `loguru` escribe correctamente el error en la consola y en el archivo de log.
