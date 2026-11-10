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

- [x] Sistema operativo, tarjeta gráfica (modelo y memoria), RAM y disco libre. **Comprobado el 2026-11-10:** Windows 11 Pro con Ubuntu 24.04 en WSL2; NVIDIA RTX 4060 de 8 GB (controlador 610.88, `nvidia-smi` la ve desde WSL); AMD Ryzen 7 5700X3D (8 núcleos, 16 hilos); 32 GB de RAM. Disco de WSL: 855 GB libres; `C:`: 250 GB libres. Ojo: el `.wslconfig` del usuario de Windows `Usuario` limita WSL a 16 GB y **4 de los 16 hilos**, y la red está en modo `nat` (el `.wslconfig` con `mirrored` es el del usuario `jav13`, que no es el que se usa).
- [x] **Decidido el 2026-11-10: Blender corre en Windows** (5.2.2 LTS, ya instalado en `C:\Program Files\Blender Foundation\Blender 5.2`). Dentro de WSL, el Blender 5.2.2 de Linux no llega a la tarjeta: EEVEE cae a llvmpipe (dibujo por procesador) y tarda 28,9 s por fotograma, y OptiX no arranca (error 7804); en Windows, EEVEE tarda 1,7 s. Desde WSL se lanza `blender.exe -b` sin problema, pasando las rutas con `wslpath -w`. El Blender de Linux se quedó en `~/.local/opt/blender-5.2.2-linux-x64` y se puede borrar.
- [x] Herramientas ya instaladas: Blender 5.2.2 LTS (Windows), Python 3.12, uv 0.11.29, Node 22.14 / npm 10.9, ffmpeg 6.1.1, git 2.43, gcc 13.3, Chrome for Testing 149. Faltaba CMake: instalado con `uv tool install cmake` (4.4.4), sin `sudo`.

### 2. Instalar el estudio

Antes de instalar cada repo, leerlo (el propio plan lo pide: las skills son código que se ejecuta con el agente).

- [x] Blender 4.2 o superior. Ya estaba: 5.2.2 LTS en Windows.
- [x] uv, Node LTS, ffmpeg y git, si faltan. Ya estaban.
- [ ] MCP de Blender. **Decidido el 2026-11-10: el MCP oficial de Blender Lab** (`projects.blender.org/lab/blender_mcp`, GPL-3.0, versión 1.0.3) en lugar de `mcp-for-blender`. Motivos: lo hace la propia Blender, no envía datos de uso, y el creador ya lo tenía instalado (el complemento "MCP" 1.0.3 en Blender 5.2 y la extensión en la app de escritorio de Claude). Trae ejecutar código en Blender, capturas del visor y de la ventana (lo que el plan llamaba `look`), render del visor a archivo y búsqueda en la documentación de Blender. No trae búsqueda en Poly Haven: los HDRI y texturas se bajan de su API pública (`dl.polyhaven.org`), que funciona desde el PC (ticket 14). El complemento escucha en `localhost:9876` de Windows; el servidor MCP corre en WSL, así que WSL necesita la red en modo `mirrored` para llegar a ese `localhost`.
- [x] Skill `LottieFiles/motion-design-skill` (temporización, curvas de movimiento, los 12 principios de animación de Disney). Instalada en `.agents/skills/motion-design` el 2026-11-10, desde la nube.
- [x] Skills locales de HyperFrames para el montaje, de la versión fijada (`hyperframes@0.9.26`). Instaladas `hyperframes` y `hyperframes-cli` en `.agents/skills/` el 2026-11-10, desde la nube; `media-use` no, porque empuja a gastar créditos de HeyGen (ver `.agents/skills/TERCEROS.md`).
- [x] Apagar la telemetría de HyperFrames en el PC: `npx --yes hyperframes@0.9.26 telemetry disable`. Hecho el 2026-11-10.
- [x] Ver si `/hyperframes-media` (voz sintética, transcripción, quitar fondo) cubre la voz y las marcas de tiempo. Sí: la skill se llama ahora `media-use`, y la voz (Kokoro) y las marcas (whisper.cpp) son órdenes de la propia CLI, `npx hyperframes tts` y `npx hyperframes transcribe`. Ver "Lo que se adelantó desde la nube".
- [x] ~~Whisper aparte~~: no hace falta, lo cubre `npx hyperframes transcribe`.
- [x] Que `npx hyperframes transcribe` funcione en el PC. **Funciona (2026-11-10)** con `--engine whisper --model small --language es`: HyperFrames compila whisper.cpp solo (hacía falta CMake) y baja el modelo; la primera vez, 79 s, y después **6,5 s para 10 s de audio**, en el procesador. Sin CUDA: para usar la tarjeta haría falta el kit CUDA en WSL; no compensa por ahora.
- [x] Que `npx hyperframes tts` funcione en el PC con `ef_dora`, `em_alex` y `em_santa`. **Funciona (2026-11-10):** `kokoro-onnx` y `soundfile` van en un entorno aparte, `~/.local/share/estudio/kokoro`, y HyperFrames lo usa con `HYPERFRAMES_PYTHON=~/.local/share/estudio/kokoro/bin/python`. Unos 8,4 s de voz en 4 s (12 s la primera vez, al bajar el modelo). Ojo: en la prueba, Whisper transcribió "Huelo" como "Vuelo"; hay que escuchar si es la pronunciación de Kokoro (ticket 13).
- [ ] MCP `earshot` (`Leonxlnx/earshot`, ya leído) para que el agente escuche la mezcla. Bajar sus modelos con `earshot doctor --fetch`.

**Dónde van las skills de terceros (decidido el 2026-11-10).** En `.agents/skills/`, junto a las propias, copiadas en la versión fijada y con su licencia, y luego `bash scripts/sincronizar-skills.sh`. Nunca solo en `.claude/skills/` (lo que hace `npx skills add` para Claude Code), porque la sincronización la borra. Así quedan fijadas con el proyecto y viajan con él. Ver `.agents/skills/TERCEROS.md`.

### 3. Prueba de humo

- [x] Renderizar un fotograma 1080x1920 con EEVEE en la tarjeta gráfica y medir el tiempo. **1,7 s** con la escena por defecto (Blender en Windows), frente a los 14,9 s de Cycles en el procesador de la nube. Cycles en la tarjeta (OptiX, 32 muestras): 8,1 s.
- [x] Repetir con un escenario de naturaleza mínimo (hierba, árboles, agua y cielo HDRI). **Hecho (2026-11-10):** terreno, unas 200.000 briznas de hierba y árboles repartidos con Geometry Nodes, un lago con transmisión y el HDRI `kloofendal_48d_partly_cloudy_puresky` a 2K de Poly Haven (se descarga bien desde el PC). EEVEE a 64 muestras: **2,2 s** el primer fotograma y **1,2 s** los siguientes; la tarjeta llega a **2,5 GB** de 8 (1,1 GB ya ocupados por Windows). Hay margen de sobra.
- [x] En el PC, `uv run pytest` pasa y HyperFrames renderiza una copia del episodio de ejemplo a MP4 1080x1920 a 30 fps. **Hecho (2026-11-10):** 126 tests en verde; la copia del ejemplo (62 s) se renderiza a MP4 1080x1920 a 30 fps en **24 s**, y su hoja de contactos se ve bien.
- [ ] Desde Claude Code, crear un escenario mínimo en Blender a través del MCP y recibir su hoja de `look`.
- [x] Transcribir 10 s de audio con Whisper y obtener un JSON con las palabras y sus tiempos. Hecho con `npx hyperframes transcribe`: 35 palabras, cada una con `text`, `start` y `end`.
- [x] Generar una hoja de contactos con ffmpeg a partir de un vídeo de prueba. Hecho con el render del ejemplo (`fps=1/4,scale=216:384,tile=8x2`).

## Pendiente de aportar por el usuario

- [ ] La skill que convierte el contenido en un diálogo estructurado entre el perro y el tutor. Al recibirla: leerla, ver su formato de salida y encajarlo con la lista de planos.
- [ ] Un primer contenido de ejemplo, para el episodio piloto.
- [ ] Hojas de personaje del Tutor (el usuario) y del Perro (su perro). Al recibirlas, comprobar que traen vistas (frente, tres cuartos, perfil) y juegos de ojos y bocas; si faltan, pedirlos o proponerlos.
- [ ] Documentación de la App: nombre, enlace, logo, colores y lista de funcionalidades para tutores y para educadores caninos, para elegir la del CTA de cada episodio.

## Incoherencias del plan base (`docs/PlanBase.md`)

- [x] La skill final se llama `cartoon-studio`, pero el texto dice que se invoca con `/motion-studio`. Decidido el 2026-11-10: la skill del estudio se llama **`perro-tutor`**, como el formato, porque cada formato es una receta aparte (ADR 0006) y las skills del proyecto van en español. Apuntado en el ticket 11.
- [x] El plan pone las "reglas de la casa" en `CLAUDE.md`. Resuelto en la spec (historia 64): van en la skill del estudio, porque solo aplican al hacer un episodio.
- [x] El texto pegado arrastra restos de la web original. Limpiado el 2026-11-10: fuera las 22 palabras `copy` pegadas al final de las líneas y los 7 vídeos incrustados, cada uno cambiado por una nota. Las imágenes son enlaces a la web original y se dejan.
