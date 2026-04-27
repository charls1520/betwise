# Especificación de Diseño: Nuevas Variables Predictivas ML - Fase A

**Fecha:** 26 de Abril de 2026
**Contexto Tecnológico:** Python, Pandas, Scikit-Learn
**Módulos Afectados:** `src/ml/features.py`, `src/ml/train.py`, `src/ml/inference.py`

---

## 1. Overview / Objetivo

El objetivo principal de esta fase (Fase A) es mejorar el poder predictivo de nuestros modelos de Machine Learning (específicamente los modelos de **Ganador 1X2** y **Más de 2.5 Goles**). Actualmente, los modelos tienen un alcance limitado, ya que solo utilizan las variables `xg_diff` y `elo_diff`. 

En esta fase, introduciremos nuevas variables (features) centradas en tres pilares: **Fatiga**, **Estadísticas de Tiro** y **Contexto de Temporada**. La restricción principal de la Fase A es utilizar *únicamente* los datos que ya están disponibles en los archivos CSV proveídos por `football-data.co.uk`, sin requerir la integración de nuevas APIs externas.

## 2. Arquitectura y Flujo de Datos

El proceso de ingesta de datos en crudo (CSV) se mantendrá sin alteraciones. La transformación y creación de las nuevas variables ocurrirá "al vuelo" dentro del módulo `src/ml/features.py`.

Específicamente, se expandirá la función `build_features_for_matches`. Esta función será responsable de agrupar los datos históricos, calcular promedios móviles (rolling averages) y generar métricas específicas por equipo antes de pasar los datos a las etapas de entrenamiento o inferencia. Hacer esto dinámicamente facilita la experimentación rápida con diferentes ventanas de tiempo (ej. últimos 3, 5 o 10 partidos) sin necesidad de reestructurar las bases de datos subyacentes.

## 3. Definición de Nuevas Variables (Features)

Se implementarán las siguientes características basándonos en las columnas existentes (Date, HomeTeam, AwayTeam, FTHG, FTAG, HST, AST):

*   **Fatiga (Rest Days):**
    *   *Lógica:* Calcular la cantidad de días de descanso transcurridos desde el último partido oficial disputado por el equipo (sea de local o visitante).
    *   *Ajuste:* Para evitar que valores atípicos (outliers) sesguen el modelo —como las vacaciones de verano, los parones de invierno o las ventanas internacionales de la FIFA— este valor tendrá un tope máximo (cap) de **10 días**. Cualquier descanso mayor a 10 días se registrará como 10.
    *   *Variables Finales:* `home_rest_days`, `away_rest_days`, `rest_days_diff` (Local - Visitante).

*   **Estadísticas de Tiro (Shots on Target):**
    *   *Lógica:* Calcular el promedio móvil de los últimos *N* partidos (por defecto $N=5$). Se medirán los Tiros a Puerta a favor (basado en las columnas `HST` / `AST` del CSV) y los Tiros a Puerta concedidos al rival, tanto para el equipo local como para el visitante.
    *   *Variables Finales:* Se creará una característica diferencial: `shots_on_target_diff` (Promedio Tiros a Puerta Local - Promedio Tiros a Puerta Visitante).

*   **Motivación / Contexto (End of Season):**
    *   *Lógica:* Identificar si un partido se está jugando en la recta final de la temporada, donde la motivación por evitar el descenso o ganar competencias europeas altera el rendimiento esperado.
    *   *Implementación:* Se calculará el conteo acumulado de partidos jugados por cada equipo en una ventana de tiempo de 1 año o temporada. Si el equipo local o visitante ha jugado más de 30 partidos en la temporada actual, se activará un peso numérico o flag `is_end_of_season`. (Simplificación: Como cada liga tiene un número distinto de equipos, usaremos el umbral > 30 partidos jugados como estándar de "recta final").

## 4. Manejo de Fuga de Datos (Data Leakage)

La prevención de fuga de datos es crítica para la viabilidad de los modelos. 
*   **Regla Estricta:** Todos los promedios móviles, conteos de partidos y cálculos de días de descanso **DEBEN** computarse utilizando estrictamente información de partidos que hayan ocurrido *antes* de la fecha del partido actual (`Date`). 
*   Para lograr esto en Pandas, agruparemos por equipo, ordenaremos por fecha y usaremos la función `.shift(1)` antes de calcular las ventanas móviles (`.rolling()`). Esto asegura que el partido de "hoy" no se incluya en el promedio de "hoy".

## 5. Impacto en los Modelos (`train.py` & `inference.py`)

La integración de estas variables requerirá los siguientes cambios en los scripts principales:

1.  **Actualización de `features`:** Las nuevas columnas (ej. `rest_days_diff`, `shots_on_target_diff`, `is_end_of_season`) deberán agregarse explícitamente a la lista de variables predictivas (`features = [...]`) utilizada para alimentar los modelos en `src/ml/train.py`.
2.  **Ajuste del Pipeline de Imputación (Scikit-Learn):** 
    *   *Problema:* El cálculo de promedios móviles (ej. últimos 5 partidos) inevitablemente generará valores nulos (`NaN`) para los primeros encuentros de cada temporada o para equipos recién ascendidos. También la variable de descanso será nula en el partido 1.
    *   *Solución:* El pipeline actual usa `SimpleImputer(strategy='median')`. Mantendremos esta estrategia, ya que imputar con la mediana es robusto para arranques de temporada. Para los días de descanso, la mediana global representará un "descanso estándar" de 7 días.

---
*Aprobación pendiente por el usuario antes de proceder con el plan de implementación.*