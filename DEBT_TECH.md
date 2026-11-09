# Deuda técnica pendiente

Lo que no se pudo hacer el 2026-11-09 porque la sesión corría en un servidor en la nube y no en el PC de casa. Se completa en la primera sesión en el PC. Al terminar cada punto, márcalo `[x]` y anota el resultado en una línea.

## Lo que se comprobó en la nube (2026-11-09)

| Qué | Resultado |
| --- | --- |
| Skills de Matt Pocock | Instaladas (plugin `mattpocock-skills`). |
| ffmpeg / ffprobe | 6.1.1, ya instalado. |
| Node / npm / npx | 22 / 10.9, ya instalados. |
| Python / uv | 3.13 / 0.11, ya instalados. |
| Blender oficial (download.blender.org) | **Bloqueado** por la red de este entorno. |
| Blender como módulo Python (`bpy` 5.2.3, PyPI) | Se instala (~3,5 min). Cycles en CPU: **14,9 s por fotograma** 1080x1920 a 32 muestras con la escena por defecto (un cubo). EEVEE y Workbench **no arrancan** sin tarjeta gráfica. |
| Poly Haven (HDRIs y texturas) | **Bloqueado** por la red de este entorno. |
| Modelos de Whisper (openaipublic.azureedge.net, huggingface.co) | **Bloqueados** por la red de este entorno. |
| Repos de GitHub de terceros | La web y la API dan 403, pero `git clone` de repos públicos sí funciona. |

**Conclusión:** en la nube un episodio de 65 s (1.950 fotogramas) tardaría más de 8 horas en renderizar, y eso con una escena vacía. El estudio tiene que vivir en el PC de casa, con tarjeta gráfica. La nube solo sirve para escribir (guion, lista de planos, specs) y para pruebas puntuales de un fotograma.

## Pendiente en el PC

### 1. Conocer la máquina (lo hace el agente)

- [ ] Sistema operativo, tarjeta gráfica (modelo y memoria), RAM y disco libre.
- [ ] Herramientas ya instaladas: Blender, Python, uv, Node, ffmpeg, git.

### 2. Instalar el estudio

Antes de instalar cada repo, leerlo (el propio plan lo pide: las skills son código que se ejecuta con el agente).

- [ ] Blender 4.2 o superior (lo exige `mcp-for-blender`). Preferir una versión LTS.
- [ ] uv, Node LTS, ffmpeg y git, si faltan.
- [ ] `mcp-for-blender` (paquete PyPI 2.2.7, repo `ahujasid/blender-mcp`): `uvx mcp-for-blender setup`. Comprobar que la herramienta `look` devuelve una imagen del visor y que `search_assets` descarga de Poly Haven.
- [ ] Skill `LottieFiles/motion-design-skill` (temporización, curvas de movimiento, los 12 principios de animación de Disney).
- [ ] Skill `remotion-dev/skills` (montaje de imagen, subtítulos y sonido).
- [ ] Whisper para las marcas de tiempo palabra a palabra: decidir entre `openai-whisper` y `faster-whisper` según la tarjeta gráfica, y comprobar que el modelo se descarga.
- [ ] MCP `earshot` (`Leonxlnx/earshot`) para que el agente escuche la mezcla.

**Ojo con dónde van las skills de terceros.** `scripts/sincronizar-skills.sh` borra `.claude/skills/` y la vuelve a copiar desde `.agents/skills/`. Una skill instalada solo en `.claude/skills/` (lo que hace `npx skills add` para Claude Code) desaparecería en la siguiente sincronización. Hay que decidir si van en `.agents/skills/` (y luego se sincroniza) o fuera del proyecto, en `~/.claude/skills/`.

### 3. Prueba de humo

- [ ] Renderizar un fotograma 1080x1920 con EEVEE en la tarjeta gráfica y medir el tiempo. Compararlo con los 14,9 s de la nube.
- [ ] Desde Claude Code, crear un escenario mínimo en Blender a través del MCP y recibir su hoja de `look`.
- [ ] Transcribir 10 s de audio con Whisper y obtener un JSON con las palabras y sus tiempos.
- [ ] Generar una hoja de contactos con ffmpeg a partir de un vídeo de prueba.

## Pendiente de aportar por el usuario

- [ ] La skill que convierte el contenido en un diálogo estructurado entre el perro y el tutor. Al recibirla: leerla, ver su formato de salida y encajarlo con la lista de planos.
- [ ] Un primer contenido de ejemplo, para el episodio piloto.

## Incoherencias del plan base (`docs/PlanBase.md`)

- [ ] La skill final se llama `cartoon-studio`, pero el texto dice que se invoca con `/motion-studio`. Hay que elegir un nombre.
- [ ] El plan pone las "reglas de la casa" en `CLAUDE.md`. En esta plantilla, las reglas van en `AGENTS.md` (ADR 0001), o en la skill del estudio si solo aplican al hacer un episodio.
- [ ] El texto pegado arrastra restos de la web original: la palabra `copy` al final de los bloques de código, y vídeos e imágenes incrustados que no cargan.
