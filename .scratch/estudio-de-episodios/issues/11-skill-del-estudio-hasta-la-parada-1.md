# 11: Skill del estudio: hasta la parada 1

**What to build:** La skill del estudio (la receta del formato Perro–Tutor), con las reglas de la casa. Al pedir un episodio nuevo con una sola instrucción, la skill crea su carpeta, pasa el contenido por la skill de diálogo del creador, adapta la salida al formato canónico del guion, busca fuentes si faltan, propone la funcionalidad de la App para el CTA, pasa la comprobación del guion y se detiene en la parada 1 para presentárselo todo al creador.

**Blocked by:** 01 (Aportaciones del creador), 03 (Comprobar un guion), 10 (Crear un episodio y seguir su estado)

**Status:** ready-for-agent

- [ ] La skill vive con las skills propias del proyecto y la sincronización la copia (ADR 0004).
- [ ] Las reglas de la casa están escritas: formato, aspecto, prohibiciones y originalidad.
- [ ] Con el contenido del piloto, una sola instrucción llega a la parada 1 con el guion, las fuentes y la propuesta de CTA, sin errores de comprobación.
- [ ] La propuesta de CTA dice qué funcionalidad y por qué, priorizando las de tutores.
- [ ] La aprobación de la parada 1 queda registrada en el estado del episodio.
- [ ] El creador ha visto la parada 1 funcionando.

## Comments

**2026-11-10, agente.** La skill del estudio se llama `perro-tutor`, como el formato: cada formato es una receta aparte (ADR 0006), y las skills del proyecto van en español. El plan base la llamaba `cartoon-studio` y la invocaba con `/motion-studio`; ese nombre se descarta. Va en `.agents/skills/perro-tutor/` y se sincroniza (ADR 0004).
