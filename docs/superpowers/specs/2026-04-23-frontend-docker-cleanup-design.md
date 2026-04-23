# Spec — Frontend & Infra Hardcodes Cleanup

**Última actualización:** 23 de Abril de 2026

## 1. Visión General

El objetivo de este diseño es completar la limpieza del proyecto eliminando las URLs de API "hardcodeadas" en el frontend de React y purgando las contraseñas por defecto de la configuración de Docker Compose. Todo el sistema debe configurarse exclusivamente mediante variables de entorno dinámicas.

## 2. Refactor del Frontend (React/Vite)

Actualmente, varios componentes del frontend tienen una URL de la API estática como fallback, lo cual impide un despliegue limpio y dinámico.

*   **Archivos afectados:** 
    *   `frontend/src/components/DashboardPanel.tsx`
    *   `frontend/src/components/ChatPanel.tsx`
    *   `frontend/src/components/AuditModal.tsx`
*   **Cambio propuesto:** Reemplazar `const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';` por la lectura estricta de la variable, lanzando un error o asumiendo que el proxy configurará correctamente el path relativo, o bien manteniendo solo la lectura de la variable global si está definida. Para mantener compatibilidad con Vite y Docker, cambiaremos a leer solo `import.meta.env.VITE_API_URL` pero dejaremos configurado el `.env` correctamente. Lo ideal es no tener `'http://localhost:8080'` dentro del código. Si no hay `VITE_API_URL`, Vite por defecto puede usar un path relativo `/api` (si configuramos un proxy) o lanzar una advertencia.
*   **Decisión de Diseño:** Reemplazaremos los fallbacks harcodeados a `http://localhost:8080` por la ruta relativa `/api` como fallback genérico, o simplemente usaremos la variable global inyectada. En este caso, estableceremos `const apiUrl = import.meta.env.VITE_API_URL || '';`. De esta forma, si no se provee URL, las llamadas se harán al mismo dominio (relativas), lo que es la mejor práctica para producción.

## 3. Actualización de Docker Compose y Entorno

La infraestructura tiene contraseñas y configuraciones sensibles harcodeadas como fallbacks en el archivo `docker-compose.yml`.

*   **Archivo afectado:** `docker-compose.yml`
*   **Cambio:** Eliminar los valores por defecto inseguros como `${POSTGRES_PASSWORD:-betwise_password}` y reemplazarlos por `${POSTGRES_PASSWORD}`. Docker Compose fallará o advertirá si la variable no está en el `.env`, lo cual es el comportamiento seguro deseado.
*   **Nuevo Comportamiento:** El entorno de docker exigirá un `.env` completo en la raíz del proyecto para levantar la base de datos y los servicios.

## 4. Actualización de Documentación

*   **Archivo afectado:** `.env.example` en la raíz (si existe) o crear uno unificado con todas las variables requeridas (VITE_API_URL, POSTGRES_PASSWORD, etc.).
*   Actualizar el README si es necesario para mencionar que el `.env` es de carácter obligatorio sin fallbacks automáticos.