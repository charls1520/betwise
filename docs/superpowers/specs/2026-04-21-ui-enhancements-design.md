# Diseño - Mejoras de UI, Menús Colapsables y Datos Completos de Partidos

## Arquitectura y Componentes
Este diseño aborda las mejoras solicitadas para la interfaz de BetWise enfocadas en la visualización, la experiencia de usuario con los menús laterales y la información completa de los partidos.

### 1. Backend (`main.py`)
- Modificar el endpoint `/api/dashboard`.
- En el parseo de archivos JSON de The-Odds-API (donde están guardados los objetos de partidos crudos con la llave `commence_time` y `sport_title`), inyectar en el `MatchData` devuelto los valores de "hora del partido" y "liga".
- Si la liga es muy técnica, podemos dejarla tal cual, pero debe ser dinámica en vez de decir siempre estáticamente "PREMIER LEAGUE".

### 2. Frontend: Datos y UI (`DashboardPanel.tsx` y `types.ts`)
- Añadir `match_time: string` y `league: string` a las interfaces de TypeScript.
- Quitar el método `.substring(0, 3).toUpperCase()` de la visualización de `home_team` y `away_team` en las "Tarjetas de Partido" (Match Cards) para mostrar los nombres completos.
- Agregar en la tarjeta un sub-header o label con la hora `match_time` (formateado a UTC-5, hora de Bogotá).
- Remplazar el label verde estático "PREMIER LEAGUE" por el valor real dinámico provisto en la propiedad `league`.

### 3. Frontend: Layout y Menús Colapsables (`App.tsx`)
- Definir estados reactivos `isNavOpen` e `isChatOpen` controlados desde el componente padre (`App.tsx`).
- Añadir un botón flotante y un icono en el Header para controlar `isNavOpen` (botón menú hamburguesa a la izquierda) y `isChatOpen` (botón de analista a la derecha).
- Convertir la clase Tailwind `w-64` y `w-80` junto con su `translate-x` a dinámicas para permitir ocultarse (`-translate-x-full` y `translate-x-full`) con una transición fluida (`transition-transform`).
- Ajustar el padding horizontal de `DashboardPanel` (actualmente `xl:ml-64 lg:mr-80`) para que ocupe `ml-0` y `mr-0` cuando los menús están cerrados, maximizando así la visualización.

## Manejo de Errores
- Si la propiedad `match_time` o `league` no están disponibles temporalmente en el caché JSON, proveer valores por defecto en el frontend (ej. `N/A`, o `TBA`) sin fallar el render.

## Testing
- Revisión manual rápida del estado del dashboard verificando que los nombres de los equipos no sean truncados.
- Verificación del toggle fluido de los menús izquierdo y derecho, comprobando que las dimensiones del panel principal reaccionan correctamente.
