# Design Spec: Filtro Temporal Estricto (48 Horas) y Zona Horaria UTC-5

## Contexto
Actualmente, el pipeline de Ingesta (Odds, xG, etc.) descarga todos los partidos próximos de una jornada sin importar qué tan lejos en el futuro estén. Las predicciones deportivas (Value Edge) a más de dos días de distancia pierden precisión y fiabilidad, ya que están sujetas a eventos imprevistos (lesiones de última hora, cambios tácticos o variaciones drásticas en las cuotas).
Se requiere restringir la ventana de predicción del sistema entero a un máximo de 48 horas (hoy y mañana) usando de manera consistente la zona horaria **UTC-5**.

## Objetivos
1. **Calidad de Predicción:** Garantizar que el Dashboard y el Chat RAG solo sugieran y analicen partidos próximos (48h) donde la confianza del modelo es mayor.
2. **Eficiencia en Scraper:** Bloquear la ingesta desde la raíz (Scraper) para ni siquiera almacenar partidos fuera de este rango.
3. **Zona Horaria Consistente:** Configurar el sistema para usar globalmente `America/Bogota` o `America/Lima` (UTC-5) para todos los cálculos de fecha.

## Arquitectura de Filtro Temporal

### 1. The-Odds-API (Filtro en Origen)
- El scraper `src/ingestion/scrapers/odds_api.py` se modificará para inspeccionar el campo `commence_time` (fecha de inicio del partido) que provee la API de cuotas.
- Al recibir la lista de partidos desde la API, el script calculará:
  - `ahora_utc5` = Hora y fecha actual en UTC-5.
  - `limite_utc5` = `ahora_utc5` + 48 horas.
- Cualquier partido cuyo `commence_time` (convertido a UTC-5) sea posterior a `limite_utc5` será descartado inmediatamente y no se guardará en `data/raw/` ni será procesado.

### 2. Understat xG (Filtro Derivado)
- Como la ingesta de The-Odds dicta qué partidos se analizan en el Dashboard (`raw_odds`), limitar las cuotas limitará implícitamente qué equipos se buscan y predicen en todo el ciclo de vida del Endpoint.
- No es estrictamente necesario bloquear Understat, ya que sus promedios `xG` de la temporada se usan globalmente para los equipos que pasaron el filtro 1.

### 3. Dashboard y RAG Chat
- El Endpoint `/api/dashboard` leerá los últimos archivos de cuotas. Como estos ya vienen pre-filtrados, el Dashboard solo mostrará partidos de "Hoy y Mañana".
- El Endpoint `/api/chat` inyectará esta misma lista recortada al contexto del LLM (Gemma), por lo que si el usuario pregunta "Cuáles son los próximos partidos", el bot responderá únicamente con los eventos confirmados para las próximas 48 horas y usará las noticias recientes para argumentar.

## Componentes a Modificar
- `src/ingestion/scrapers/odds_api.py`: Importar `datetime` y `pytz` o `zoneinfo` para parsear la fecha de cada evento y eliminar los que estén fuera de rango antes de retornar la lista.
- `requirements.txt`: Asegurar que la librería `pytz` (o el soporte nativo de `zoneinfo` en Python 3.9+) esté disponible para la conversión estricta a `America/Bogota` (UTC-5).

## Manejo de Errores y Seguridad
- Si no hay partidos en las próximas 48 horas (ej. a mitad de semana cuando no hay jornada), el scraper guardará una lista vacía `[]`. 
- El Frontend (Dashboard) ya está preparado para mostrar un mensaje amigable ("No se encontraron próximos partidos") y el RAG Chat responderá que "No hay partidos programados para hoy ni mañana", evitando que el sistema colapse o el usuario apueste en datos desactualizados.