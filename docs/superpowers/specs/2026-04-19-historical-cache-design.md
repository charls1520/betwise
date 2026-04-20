# Design Spec: Sistema de Caché Persistente para Ingesta Histórica y Validación de Vacíos

## Contexto
Actualmente, el pipeline de Machine Learning descarga *toda* la información histórica (`football-data.co.uk`, Understat, Clubelo) cada vez que se ejecuta el entrenamiento (`src.ml.train`). Esto provoca consultas reduntantes a las APIs, desgaste innecesario de red y tiempo de espera excesivo, especialmente para datos que ya han ocurrido (ej. temporadas 2021, 2022) y que nunca van a cambiar.
Además, se necesita una política estricta de "Cero Vacíos": si un registro se procesa con datos faltantes, no debe ni usarse ni guardarse.

## Objetivos
1. **Evitar Consultas Repetidas:** Implementar un mecanismo de caché local (en disco, JSON o CSV) para que los datos históricos que ya fueron descargados exitosamente no se vuelvan a pedir a las APIs.
2. **Actualización Incremental:** El pipeline debe ser capaz de detectar qué temporadas o fechas faltan en el caché, hacer *scraping* únicamente de ese diferencial, y anexarlo al caché existente.
3. **Validación Estricta:** Ninguna fila o registro con campos nulos o incompletos (`None`, `NaN`, `""`) tras el cruce (Merge) podrá ser insertada en la base final o en el caché.

## Arquitectura de Caché

### 1. El Almacén Local
- Se creará un archivo o estructura en `data/historical/` (ej. `merged_history_cache.csv`).
- Este archivo será la "fuente de la verdad" del entrenamiento. 

### 2. Flujo de Lectura y Extracción Incremental
Cuando se llame a `download_football_data_co_uk(seasons=[...])` (que cruza todo):
1. El script lee el caché local `merged_history_cache.csv` si existe.
2. Extrae qué fechas y/o temporadas ya están cubiertas dentro del archivo.
3. Para cada `season` solicitada, verifica si la última fecha de esa temporada ya fue guardada completamente. Si la temporada está completa, se salta la descarga. Si está parcialmente completa (ej. la temporada actual en curso), descarga el CSV oficial de `football-data.co.uk` de esa temporada.
4. Antes de buscar los xG y Elo de todos los partidos de ese CSV, el script comprueba qué partidos *ya existen* en el caché. **Solo** realiza peticiones a `Understat` y `Clubelo` para las filas (partidos) que no existan en el disco.

### 3. Filtro Anti-Vacíos
- En el momento de hacer el `Merge` de las 3 fuentes (Oficial + xG + Elo), si por alguna razón Playwright falla, Clubelo no tiene datos de ese equipo, o el `TeamNormalizer` no los puede emparejar, las variables `Home_xG`, `Away_xG`, `Home_Elo` o `Away_Elo` quedarán nulas.
- **Regla Estricta:** Se aplicará un `.dropna(subset=['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo'])` *antes* de anexar los datos nuevos al caché. De este modo, el caché siempre estará inmaculado.

### 4. Cache Secundario por Servicio (Opcional)
- Dado que Clubelo extrae todo el historial de un club, este historial bruto también puede guardarse en `data/historical/clubelo_<team>.csv` para evitar golpear su API más de una vez al día por equipo.
- Lo mismo para Understat: `understat_season_<year>.json`.
- El archivo maestro (`merged_history_cache.csv`) juntará las piezas de la memoria de forma ultra-rápida.

## Componentes a Modificar
- `src/ingestion/historical.py`: Rediseñar la lógica principal para orquestar la lectura, el cálculo diferencial (qué falta descargar), y la inserción segura sin vacíos.
- `src/ml/train.py`: Continuar llamando a esta función de Ingestión Histórica que ahora responderá en segundos si la data ya fue extraída, y en minutos si requiere anexar una nueva jornada semanal.

## Manejo de Errores y Seguridad
- Si el archivo de caché se corrompe (ej. interrumpido a la mitad), el desarrollador puede borrar el archivo `data/historical/merged_history_cache.csv` y el script volverá a construir todo el histórico desde cero limpiamente en la siguiente ejecución.
- Al aislar las peticiones y solo pedir el diferencial, evitamos IPs baneadas por Cloudflare (Understat) o timeouts masivos.