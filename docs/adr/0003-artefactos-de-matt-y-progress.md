# Artefactos de Matt Pocock como fuente de verdad y PROGRESS.md como único documento de estado propio

El flujo de Matt Pocock ya produce los artefactos del proyecto: `GLOSSARY.md` (vocabulario), `docs/adr/` (decisiones), la spec y los tickets en el gestor de tickets, y `/handoff` para traspasos. Mantener además `PLANNING.md` (que duplica la spec) y `HANDOFF.md` (que duplica `/handoff`) contaría lo mismo dos veces. Por eso se eliminan, y solo se conserva `PROGRESS.md`: un documento corto que dice en qué fase está el proyecto y cuál es el siguiente paso. El agente lo lee al empezar cada sesión y lo actualiza al cerrar cada fase. Es lo que le permite ser proactivo con un usuario que no recuerda dónde se quedó.

## Consecuencias

- `PROGRESS.md` enlaza a specs, tickets y ADRs, pero nunca copia su contenido.
- Las skills propias (`crear-loop`, `crear-grafo`) leen estos artefactos en lugar de `PLANNING.md` o `HANDOFF.md`.
