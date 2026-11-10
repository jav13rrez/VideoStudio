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
| HyperFrames 0.9.26 (render) | **Funciona** con el Chrome del sistema: los 62 s del episodio de ejemplo (voces y subtítulos) en unos 30 s. `cdn.jsdelivr.net` está bloqueado, así que la composición no carga nada de internet: ni GSAP ni la letra, que va con el estudio (ticket 06). |

**Conclusión:** en la nube un episodio de 65 s (1.950 fotogramas) tardaría más de 8 horas en renderizar, y eso con una escena vacía. El estudio tiene que vivir en el PC de casa, con tarjeta gráfica. La nube solo sirve para escribir (guion, lista de planos, specs) y para pruebas puntuales de un fotograma.

## Lo que se adelantó desde la nube (2026-11-10)

El creador ya está delante del PC de casa: **NVIDIA RTX 4060 con 8 GB y 32 GB de RAM** (lo dice él; falta comprobarlo en la máquina, con el sistema operativo y el disco libre). Pero la sesión de ese día seguía corriendo en el servidor en la nube (4 núcleos, 15 GB, sin tarjeta gráfica) y no podía llegar al PC: el PC no tenía ninguna carpeta compartida con las sesiones de la nube. Desde la nube se hizo lo que no necesita el PC:

| Qué | Resultado |
| --- | --- |
| Red de la nube | Siguen bloqueados Blender oficial, Poly Haven, Hugging Face (modelos de Whisper) y `cdn.jsdelivr.net`. Sí se descargan las versiones publicadas en GitHub (`github.com/…/releases`) y PyPI. |
| Skills de terceros | Leídas e instaladas en `.agents/skills/` (ver `.agents/skills/TERCEROS.md`). Siguen ahí después de dos sincronizaciones seguidas, y `--check` da OK. |
| `mcp-for-blender` 2.2.7 | Leído (licencia MIT). Instala un complemento en Blender y un servidor MCP. **Envía datos de uso** salvo que se apague con `DISABLE_TELEMETRY=1`. |
| earshot (`Leonxlnx/earshot`) | Leído (licencia MIT). Corre en CPU con PyTorch y dos modelos de ~1,1 GB que se bajan con `earshot doctor --fetch`, desde Hugging Face: va en el PC. |
| Voz y marcas de tiempo con HyperFrames 0.9.26 | Leído en su código. `npx hyperframes tts` genera la voz en el propio PC con **Kokoro**, que tiene tres voces en español: `ef_dora` (mujer), `em_alex` y `em_santa` (hombres), comprobadas en su archivo de voces. Kokoro **no** da marcas por palabra: las da `npx hyperframes transcribe --model small --language es` (whisper.cpp). Así que HyperFrames cubre la voz y las marcas, y no hace falta instalar Whisper ni un motor de voz aparte. |

## Pendiente en el PC

### 0. Abrir Claude Code en el PC

Lo que queda solo se puede hacer con Claude Code corriendo **en el PC**, no desde la app conectada a una sesión en la nube. Dos formas:

- **Recomendada:** instalar Claude Code en el PC y abrirlo en la carpeta del proyecto (los comandos están en `PROGRESS.md`, "Siguiente paso").
- Compartir la carpeta del PC con las sesiones de la nube (app de escritorio de Claude: Settings → Claude Code → Remote Control). No está disponible para todas las cuentas, y Blender y los renders irían igual por el PC.

### 1. Conocer la máquina (lo hace el agente)

- [ ] Sistema operativo, tarjeta gráfica (modelo y memoria), RAM y disco libre. El creador dice RTX 4060 de 8 GB y 32 GB de RAM, y que el estudio va en **WSL** (Linux dentro de Windows); falta comprobarlo (`nvidia-smi` dentro de WSL tiene que ver la tarjeta) y anotar la distribución y el disco.
- [ ] Decidir si Blender corre dentro de WSL o en Windows. Primero, dentro de WSL: Cycles usa la tarjeta por CUDA u OptiX sin problema, pero EEVEE y el visor van por la capa gráfica de WSL, que puede fallar o ir lenta. Si EEVEE no va fino ahí, Blender en Windows y el MCP conectado desde WSL por la red local (modo de red `mirrored` de WSL). Anotar la decisión aquí.
- [ ] Herramientas ya instaladas: Blender, Python, uv, Node, ffmpeg, git.

### 2. Instalar el estudio

Antes de instalar cada repo, leerlo (el propio plan lo pide: las skills son código que se ejecuta con el agente).

- [ ] Blender 4.2 o superior (lo exige `mcp-for-blender`). Preferir una versión LTS.
- [ ] uv, Node LTS, ffmpeg y git, si faltan.
- [ ] `mcp-for-blender` (paquete PyPI 2.2.7, repo `ahujasid/blender-mcp`, ya leído): `uvx mcp-for-blender setup`, y darlo de alta en Claude Code con la telemetría apagada (`DISABLE_TELEMETRY=1` en su configuración). Comprobar que la herramienta `look` devuelve una imagen del visor y que `search_assets` descarga de Poly Haven.
- [x] Skill `LottieFiles/motion-design-skill` (temporización, curvas de movimiento, los 12 principios de animación de Disney). Instalada en `.agents/skills/motion-design` el 2026-11-10, desde la nube.
- [x] Skills locales de HyperFrames para el montaje, de la versión fijada (`hyperframes@0.9.26`). Instaladas `hyperframes` y `hyperframes-cli` en `.agents/skills/` el 2026-11-10, desde la nube; `media-use` no, porque empuja a gastar créditos de HeyGen (ver `.agents/skills/TERCEROS.md`).
- [ ] Apagar la telemetría de HyperFrames en el PC: `npx --yes hyperframes@0.9.26 telemetry disable`.
- [x] Ver si `/hyperframes-media` (voz sintética, transcripción, quitar fondo) cubre la voz y las marcas de tiempo. Sí: la skill se llama ahora `media-use`, y la voz (Kokoro) y las marcas (whisper.cpp) son órdenes de la propia CLI, `npx hyperframes tts` y `npx hyperframes transcribe`. Ver "Lo que se adelantó desde la nube".
- [x] ~~Whisper aparte~~: no hace falta, lo cubre `npx hyperframes transcribe`.
- [ ] Que `npx hyperframes transcribe` funcione en el PC. Necesita el programa `whisper-cli` de whisper.cpp. En Windows, lo más simple es bajar de las versiones publicadas de `ggml-org/whisper.cpp` el zip con CUDA (`whisper-cublas-…-bin-x64.zip`, aprovecha la RTX 4060) y apuntar `HYPERFRAMES_WHISPER_PATH` a su `whisper-cli.exe`; si no, HyperFrames lo compila y pide CMake y las herramientas de compilación de Visual Studio. En Linux, `git`, `cmake` y un compilador. Con 8 GB de tarjeta cabe el modelo `large-v3`.
- [ ] Que `npx hyperframes tts` funcione en el PC con `ef_dora`, `em_alex` y `em_santa` (necesita Python con el paquete `kokoro-onnx`; baja el modelo, ~311 MB, la primera vez). La elección de voces es del creador, en el ticket 13; si no convencen, que el creador grabe la del Tutor o una voz de pago.
- [ ] MCP `earshot` (`Leonxlnx/earshot`, ya leído) para que el agente escuche la mezcla. Bajar sus modelos con `earshot doctor --fetch`.

**Dónde van las skills de terceros (decidido el 2026-11-10).** En `.agents/skills/`, junto a las propias, copiadas en la versión fijada y con su licencia, y luego `bash scripts/sincronizar-skills.sh`. Nunca solo en `.claude/skills/` (lo que hace `npx skills add` para Claude Code), porque la sincronización la borra. Así quedan fijadas con el proyecto y viajan con él. Ver `.agents/skills/TERCEROS.md`.

### 3. Prueba de humo

- [ ] Renderizar un fotograma 1080x1920 con EEVEE en la tarjeta gráfica y medir el tiempo. Compararlo con los 14,9 s de la nube.
- [ ] Repetir con un escenario de naturaleza mínimo (hierba, árboles, agua y cielo HDRI). La vegetación y el agua son lo que más cuesta renderizar, y los escenarios de naturaleza (montaña, prados, bosques, lagos, mar) entran en el formato. Con 8 GB de memoria en la tarjeta, mirar cuánta usa la escena (en Blender, la barra de estado o `nvidia-smi`): si se acerca al límite, texturas y HDRI a 2K en lugar de 4K u 8K, y vegetación instanciada.
- [ ] En el PC, `uv run pytest` pasa y HyperFrames renderiza una copia del episodio de ejemplo a MP4 1080x1920 a 30 fps (`generar-voces`, `cronometrar` y `renderizar`; la copia, como se explica en `docs/montaje.md`, "Para subir de versión").
- [ ] Desde Claude Code, crear un escenario mínimo en Blender a través del MCP y recibir su hoja de `look`.
- [ ] Transcribir 10 s de audio con Whisper y obtener un JSON con las palabras y sus tiempos.
- [ ] Generar una hoja de contactos con ffmpeg a partir de un vídeo de prueba.

## Pendiente de aportar por el usuario

- [ ] La skill que convierte el contenido en un diálogo estructurado entre el perro y el tutor. Al recibirla: leerla, ver su formato de salida y encajarlo con la lista de planos.
- [ ] Un primer contenido de ejemplo, para el episodio piloto.
- [ ] Hojas de personaje del Tutor (el usuario) y del Perro (su perro). Al recibirlas, comprobar que traen vistas (frente, tres cuartos, perfil) y juegos de ojos y bocas; si faltan, pedirlos o proponerlos.
- [ ] Documentación de la App: nombre, enlace, logo, colores y lista de funcionalidades para tutores y para educadores caninos, para elegir la del CTA de cada episodio.

## Incoherencias del plan base (`docs/PlanBase.md`)

- [x] La skill final se llama `cartoon-studio`, pero el texto dice que se invoca con `/motion-studio`. Decidido el 2026-11-10: la skill del estudio se llama **`perro-tutor`**, como el formato, porque cada formato es una receta aparte (ADR 0006) y las skills del proyecto van en español. Apuntado en el ticket 11.
- [x] El plan pone las "reglas de la casa" en `CLAUDE.md`. Resuelto en la spec (historia 64): van en la skill del estudio, porque solo aplican al hacer un episodio.
- [x] El texto pegado arrastra restos de la web original. Limpiado el 2026-11-10: fuera las 22 palabras `copy` pegadas al final de las líneas y los 7 vídeos incrustados, cada uno cambiado por una nota. Las imágenes son enlaces a la web original y se dejan.
