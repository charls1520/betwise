# Spec — Backend Hardcodes & Mocks Cleanup

**Última actualización:** 23 de Abril de 2026

## 1. Visión General

El objetivo de este diseño es purgar el backend de BetWise de todos los valores *hardcodeados*, *mocks* temporales y *fallbacks* inseguros. Se busca garantizar que la aplicación dependa estrictamente de variables de entorno (`.env`) para su configuración y que las validaciones de datos se basen exclusivamente en información real obtenida del scraping o base de datos.

## 2. Remoción de Fallbacks y Keys Hardcodeadas

Actualmente, componentes críticos como la ingesta de datos tienen comportamientos inseguros por defecto:

*   **Archivo afectado:** `src/ingestion/tasks.py`
*   **Cambio:** Eliminar la lógica de fallback `os.environ.get("ODDS_API_KEY", "DEMO_KEY")`.
*   **Nuevo Comportamiento:** Si `ODDS_API_KEY` no está definida en el `.env`, el sistema debe levantar una excepción crítica (ej. `ValueError("ODDS_API_KEY is not set in environment variables")`) y detener la ejecución. No se permitirá el uso de claves "demo" que enmascaren errores de configuración en producción.

## 3. Limpieza de Mocks en Reglas de Fiabilidad

El motor de fiabilidad usa un *mock* lógico para determinar si un equipo tiene suficientes partidos jugados.

*   **Archivo afectado:** `src/ml/reliability.py`
*   **Cambio:** En la función `meets_data_threshold`, eliminar el comentario y la lógica que asume que la existencia del equipo en el diccionario es suficiente (`return True`).
*   **Nuevo Comportamiento:** La validación exigirá estrictamente que la clave `matches_played` exista en los datos del equipo y que su valor sea mayor o igual al mínimo requerido (`min_matches`). Si no existe la clave, la función retornará `False`, asegurando que no se generen predicciones con datos incompletos.

## 4. Limpieza de Entorno y Configuración

Se deben organizar los archivos de configuración para reflejar las mejores prácticas de seguridad y despliegue:

*   **Eliminación:** Borrar el archivo `.env.old` para evitar confusiones de configuración.
*   **Actualización de `.env.example`:** Limpiar valores por defecto engañosos (reemplazar `DEMO_KEY` por valores descriptivos como `tu_api_key_aqui`).

## 5. Impacto en Testing

La eliminación de *mocks* en la lógica de producción requerirá actualizar los tests unitarios.

*   Los tests que prueben la lógica de `tasks.py` deberán inyectar una variable de entorno `ODDS_API_KEY` simulada mediante `monkeypatch`.
*   Los tests de `reliability.py` deberán proveer diccionarios de prueba que incluyan explícitamente la clave `matches_played` para que la validación pase.