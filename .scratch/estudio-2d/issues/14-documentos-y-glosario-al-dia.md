# 14 — Glosario y documentos al día

Spec: [estudio-2d](../spec.md). Decisión: [ADR 0008](../../../docs/adr/0008-estudio-2d-ilustrado-con-exteriores.md).

**What to build:** que ningún agente trabaje con el Blender antiguo por culpa de un documento desfasado. El glosario deja de decir que el escenario es un decorado 3D y gana los términos nuevos; el mapa del repositorio y los documentos de formato describen la imagen 2D; y las skills del estudio siguen el flujo nuevo.

**Blocked by:** 13 — La versión previa y la revisión con la imagen 2D.

**Status:** ready-for-agent

- [ ] El glosario define Escenario (dibujado plano y exterior), Pose, Zona blanda, Línea de suelo, Soporte y Ficha de pose, y deja Objeto protagonista como lo decida el ticket 17.
- [ ] El mapa de `AGENTS.md` y los documentos de formato (colocación de los planos, poses y `generar-poses`) sustituyen a los de las tomas de Blender.
- [ ] El estado del proyecto y los tickets 14, 15 y 18 de `estudio-de-episodios` quedan marcados como sustituidos por el ADR 0008.
- [ ] La skill `perro-tutor` sigue el flujo 2D y su copia para Claude Code está sincronizada.
- [ ] Ningún documento dice ya que el escenario o los personajes se construyen en Blender.
