---
# Instrucciones del proyecto

## Método de trabajo

Antes de escribir código o crear cualquier cosa, SIEMPRE usa el skill brainstorming de superpowers para explorar la idea primero.

## Flujo obligatorio

Para cualquier tarea nueva:
1. Brainstorming — conversar sobre la idea, explorar opciones, definir el diseño
2. Spec — documentar el diseño acordado en docs/superpowers/specs/
3. Plan — crear el plan de implementación en docs/superpowers/plans/
4. Ejecución — implementar siguiendo el plan paso a paso
5. Actualizar SPEC.md — reflejar los cambios implementados en la spec del proyecto

Nunca saltes directo a implementar. Siempre planifica primero.

## SPEC.md — Fuente de verdad de la aplicación

Mantén docs/SPEC.md como la especificación completa y actualizada de lo que la aplicación ES y HACE. Este archivo describe el estado real del proyecto, no lo que se planea hacer.

Debe incluir:
- Qué hace la aplicación (descripción funcional)
- Features implementadas
- Estructura y arquitectura actual
- Tecnologías usadas
- Cualquier detalle relevante sobre cómo funciona

**Regla crítica:** Después de implementar cualquier cambio (nueva feature, refactor, bugfix, cambio de arquitectura), actualiza SPEC.md para que refleje el estado actual. La spec nunca debe quedarse atrás del código.

## Master Plan

Mantén docs/MASTER-PLAN.md como la fuente de verdad del proyecto:
- Visión general del proyecto
- Sub-proyectos con tabla de pasos y estado (pendiente / en progreso / completo)
- Links a specs y plans relevantes
- Próximos pasos priorizados

Después de completar cada sub-proyecto o paso importante, actualiza el MASTER-PLAN.md.

## Idioma

Responde siempre en el idioma en que te hablo. El código, nombres de variables, commits y nombres de archivos se mantienen en inglés. Los documentos del proyecto (specs, plans, README) se escriben en el idioma del usuario.

## Stack por defecto

Cuando quiera construir una aplicación web, sugiere este stack por defecto:
- **Backend:** Express (Node.js) + TypeScript
- **Frontend:** React + TypeScript
- **Base de datos:** SQLite

Si pido otro stack, usa el que te pida. Este es solo el punto de partida sugerido.

## README de ejecución

Cuando termines de implementar cualquier cosa que se ejecute, deja en el README.md una sección "## Cómo ejecutar" con un único comando (ej: `npm run dev`) que levante todo lo necesario. El usuario no debería necesitar abrir múltiples terminales ni ejecutar pasos manuales.

## Comunicación con el usuario

El usuario puede no tener experiencia técnica. Aplica estas reglas siempre:

- **Antes de ejecutar cualquier comando**, explica en una línea qué hace y por qué lo estás ejecutando. Ejemplo: "Voy a ejecutar `npm install` — esto descarga las dependencias del proyecto, que son las librerías de código que necesita tu aplicación para funcionar."
- **Cuando uses un término técnico** que el usuario probablemente no conozca (dependencias, servidor, puerto, variable de entorno, etc.), explícalo brevemente en la misma oración o en paréntesis.
- **No asumas conocimiento previo.** Si algo puede no ser obvio para alguien que está aprendiendo, dale contexto sin sonar condescendiente.
- **Sé conciso.** Las explicaciones deben ser de una o dos oraciones, no lecciones. El objetivo es que el usuario entienda qué está pasando, no que aprenda a fondo.
- **Cuando el usuario tenga que hacer algo por su cuenta** (crear una API key, configurar una cuenta, obtener un token, etc.), nunca digas simplemente "crea una API key en OpenAI". Da instrucciones paso a paso: a qué URL ir, qué botones o secciones buscar, qué copiar, y dónde pegarlo. El usuario no sabe dónde está nada.
---