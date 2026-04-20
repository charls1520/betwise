# Design Spec: Auto-Healing Team Normalizer via LLM

## Contexto
Durante el proceso de Ingesta (Data Scraping) e Integración Histórica (Merge), es común encontrar nombres de equipos escritos de diversas formas ("Man Utd", "Wolves", "Nott'm Forest"). Actualmente, el `TeamNormalizer` usa *Fuzzy Matching* con un umbral alto (95%) para evitar falsos positivos que arruinarían el dataset del modelo de Machine Learning.
Si un equipo no supera el 95%, el sistema arroja un "WARNING" y la fila se descarta a menos que el equipo sea quemado ("hardcodeado") manualmente por un desarrollador en un diccionario interno (`manual_overrides`).

Este diseño propone eliminar la intervención humana ("hardcoding") en favor de un sistema "Auto-Ajustable" (Auto-Healing) que utiliza un LLM local (Ollama) para resolver y memorizar discrepancias semánticas o de apodos de los clubes de manera autónoma.

## Objetivos
1. **Reducción de Fallos Silenciosos:** Que el sistema identifique y recupere filas de datos (partidos) que de otra forma hubieran sido descartados por discrepancias leves de naming.
2. **Auto-Aprendizaje:** El sistema debe aprender y persistir estos alias en disco para no tener que consultarle al LLM la misma palabra cientos de veces (optimizando recursos de GPU/CPU).
3. **Cero Hardcoding:** Eliminar el diccionario estático de excepciones en el código.

## Arquitectura del Auto-Healing Normalizer

### 1. La Capa de Memoria Dinámica (`data/team_aliases.json`)
- El `TeamNormalizer` leerá este archivo JSON al inicializarse.
- Actuará como la principal fuente de verdad para los alias conocidos ("spurs": "Tottenham Hotspur").
- Estará almacenado en la carpeta de datos (`data/`) para sobrevivir a reinicios del backend.

### 2. Flujo de Normalización de 3 Etapas
Cuando se pase el string `raw_name` al método `normalize(self, raw_name)`:
1. **Búsqueda en Memoria (Caché O(1)):** Verifica si `raw_name` existe en su diccionario cargado de `team_aliases.json`. Si es así, retorna inmediatamente el nombre oficial.
2. **Fuzzy Matching Clásico (O(N)):** Si no está en memoria, utiliza `thefuzz` (Levenstein) contra los `canonical_teams`. Si el score es `> 95`, asume que es el mismo equipo, retorna el nombre oficial y **no** lo guarda en la memoria de alias (porque 95% ya es un match perfecto trivial).
3. **Escalada a LLM (Capa de Auto-Healing):** Si el score es `< 95` (pero `> 50` para evitar consultas de ruido puro o textos aleatorios), el Normalizador pausa.
   - Instancia un cliente de LlamaIndex (Ollama).
   - Genera un prompt con Zero-Shot Classification: *El scraper detectó el equipo '{raw_name}'. ¿A cuál de estos equipos oficiales de la Premier League se refiere: {self.canonical_teams}? Debes responder EXCLUSIVAMENTE con el nombre oficial del equipo de esa lista, sin puntuación ni texto adicional. Si no es ninguno de esos equipos o es una falla, responde 'NONE'.*
   - Si el LLM retorna un nombre válido que existe en la lista canónica, el Normalizador lo adopta.
   - **Persistencia:** Guarda la llave `{raw_name: respuesta_del_llm}` en `data/team_aliases.json` para que este proceso (Etapa 3) solo ocurra 1 vez en la vida útil de la aplicación.

### 3. Log y Auditoría
- Cada vez que el LLM genera una nueva "regla", el sistema lanzará un log de auditoría (ej. `INFO: Auto-Healing learned that 'Man United' means 'Manchester United'`).
- El desarrollador puede auditar `data/team_aliases.json` si sospecha que el LLM cometió un error ("alucinación").

## Componentes a Modificar
- `src/ingestion/normalizer.py`: Eliminar el `manual_overrides` fijo. Inyectar LlamaIndex (`Settings.llm`) y la lógica de lectura/escritura JSON.
- `src/main.py`: Asegurarse de que el RAG (LlamaIndex config) esté inicializado antes de ejecutar los procesos de scraping (ya lo está gracias a `init_llama_index()`).

## Manejo de Errores
- Si el LLM no responde en X segundos (Timeout) o si responde algo inválido (ej. un párrafo de explicación "Claro, ese equipo es..."), el Normalizador filtrará la respuesta, y si no hace match estricto con ningún canónico, retornará `None`. La fila se descarta, previniendo inyección de basura en la DB.