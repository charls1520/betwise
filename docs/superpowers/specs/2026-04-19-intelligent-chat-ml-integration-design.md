# Design Spec: Intelligent Chat con ML Integration y Normalizador Auto-Ajustable

## Contexto
El usuario experimentó respuestas genéricas ("No tengo información...") en el Chat RAG de BetWise porque Gemma4 solo recibía recortes de noticias y nombres de equipos no procesados. El Chat actualmente ignora por completo el núcleo del proyecto: las sugerencias de apuestas (Value Edge) generadas por el motor de Machine Learning.
Además, si un usuario emplea apodos o nombres incompletos ("Wolves", "Man Utd"), el Chatbot carece de herramientas para alinearlos con la base de datos oficial.
Se requiere conectar el pipeline de Machine Learning directamente en el flujo del Chat para inyectar *Edge Values* en el Prompt y usar el *TeamNormalizer* para asegurar la comprensión del usuario.

## Objetivos
1. **Inteligencia Cuantitativa:** Que Gemma4 analice las cuotas y predicciones de los próximos partidos para poder recomendar "apuestas de valor" (Sugerencias).
2. **Robustez ante el Usuario (Normalización):** Auto-ajustar las preguntas del usuario traduciendo apodos a nombres oficiales.
3. **Optimización de APIs:** Que las consultas de Chat no disparen nuevas descargas a *The-Odds-API*, ahorrando peticiones al límite de cuota y maximizando la velocidad.

## Arquitectura del Chat Inteligente

### 1. Inferencia Local Silenciosa (Sin red externa)
Para inyectar las predicciones, el backend ejecutará la función `predict_matches` sobre los últimos archivos RAW disponibles (`data/raw/**/odds_*.json` y `xg_*.json`).
En lugar de ir a internet (como hace el Dashboard actualmente), el Chat consumirá estrictamente la caché descargada por los Cron Jobs (máximo de 48h). 
Se generará una cadena de texto estructurada con el análisis del ML:
> "Sugerencia del Sistema: En el partido Bournemouth vs Crystal Palace, el equipo Local tiene una probabilidad matemática de 37%, con un Value Edge de -12%. No se sugiere apostar."
> "Sugerencia del Sistema: Burnley vs Man City, el Local tiene Value Edge de 54%. Oportunidad alta."

### 2. Capa de Normalización (Auto-Ajuste del Prompt)
- Antes de enviar el mensaje del usuario a LlamaIndex, el backend extraerá potenciales nombres de equipos (usando expresiones regulares o heurísticas básicas sobre palabras en mayúscula).
- Estos nombres se enviarán al `TeamNormalizer` (el cual, si encuentra un término desconocido, ya cuenta con la función *Auto-Healing* para deducirlo y aprenderlo).
- Se añadirá al Prompt final una aclaración (si el normalizador detectó alias):
  > "[Contexto Auto-Ajustado]: El usuario mencionó 'Wolves', refiriéndose a 'Wolverhampton Wanderers'."

### 3. Prompt Engineering Avanzado (LlamaIndex)
El texto inyectado en `pipeline.query_index(global_index, prompt)` se enriquecerá:
```text
Actúas como un experto asesor de apuestas de la Premier League.
Tienes la siguiente información matemática proveniente de nuestro modelo de Machine Learning:
{ml_predictions_text}

[Contexto Auto-Ajustado del usuario]: {normalized_context}

Pregunta del usuario: {request.message}

Usa el contexto matemático anterior y las noticias de tu base de datos para dar recomendaciones sólidas, explicando SIEMPRE el "Value Edge" o la probabilidad matemática.
```

## Componentes a Modificar
- `src/main.py`: Refactorizar la función `get_dashboard_data()` para separar la lógica de Inferencia y Cálculo de Edge en un método independiente (`get_latest_ml_suggestions()`) que pueda ser llamado tanto por el Dashboard como por el Chat sin golpear la API de cuotas.
- Modificar el Endpoint `@app.post("/api/chat")` para incluir la llamada a `get_latest_ml_suggestions()` y ensamblar el super-prompt.
- Incorporar el `TeamNormalizer` dentro de la ruta del chat.

## Manejo de Errores y Seguridad
- Si los archivos de `data/raw` no existen o están corruptos, la inyección del ML será ignorada y el Chat avisará de forma elegante que los servidores de datos no han corrido hoy.
- Las alucinaciones ("alucinations") matemáticas de Gemma4 se reducen a cero, ya que el modelo será instruido explícitamente a ceñirse a las cifras proporcionadas en el Prompt (`ml_predictions_text`).