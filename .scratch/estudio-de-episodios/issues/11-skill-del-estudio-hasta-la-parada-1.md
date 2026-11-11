# 11: Skill del estudio: hasta la parada 1

**What to build:** La skill del estudio (la receta del formato Perro–Tutor), con las reglas de la casa. Al pedir un episodio nuevo con una sola instrucción, la skill crea su carpeta, pasa el contenido por la skill de diálogo del creador, adapta la salida al formato canónico del guion, busca fuentes si faltan, propone la funcionalidad de la App para el CTA, pasa la comprobación del guion y se detiene en la parada 1 para presentárselo todo al creador.

**Blocked by:** 01 (Aportaciones del creador), 03 (Comprobar un guion), 10 (Crear un episodio y seguir su estado)

**Status:** in-progress (espera la aprobación de la parada 1 del piloto)

- [x] La skill vive con las skills propias del proyecto y la sincronización la copia (ADR 0004).
- [x] Las reglas de la casa están escritas: formato, aspecto, prohibiciones y originalidad.
- [x] Con el contenido del piloto, una sola instrucción llega a la parada 1 con el guion, las fuentes y la propuesta de CTA, sin errores de comprobación.
- [x] La propuesta de CTA dice qué funcionalidad y por qué, priorizando las de tutores.
- [ ] La aprobación de la parada 1 queda registrada en el estado del episodio.
- [ ] El creador ha visto la parada 1 funcionando.

## Comments

**2026-11-10, agente.** La skill del estudio se llama `perro-tutor`, como el formato: cada formato es una receta aparte (ADR 0006), y las skills del proyecto van en español. El plan base la llamaba `cartoon-studio` y la invocaba con `/motion-studio`; ese nombre se descarta. Va en `.agents/skills/perro-tutor/` y se sincroniza (ADR 0004).

**2026-11-11, agente.** Hecha la skill `perro-tutor` (`.agents/skills/perro-tutor/`, sincronizada). Lleva las reglas de la casa, el paso 1 hasta la parada 1 y cómo elegir el CTA. El creador aportó el contenido del piloto (la mirada, la oxitocina y las lágrimas) y los dos manuales de la App K9 Architect. Del resumen de los manuales salió `app/funcionalidades.md` (los manuales completos se quedan en su carpeta de Windows, fuera del repositorio público). `app/app.toml` lleva el nombre; faltan el logo y el enlace. El creador pidió que, cuando el tema no conecte con ninguna funcionalidad, el Perro invite igual con un «Por cierto…» y lo que hace la App en general, y así lo dice la skill. El piloto, `episodios/001-mirada`, llegó a la parada 1 sin errores de comprobación. Las dos fuentes están sin revisar, y la de Murata se apoya en la nota de prensa de Cell Press. Faltan la aprobación del creador y anotarla con `aprobar`.
