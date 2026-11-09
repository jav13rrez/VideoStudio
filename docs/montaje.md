# Montaje y render

Con las voces generadas, la herramienta del estudio monta el episodio: escribe la composición de HyperFrames y la renderiza a un MP4 vertical. La composición une una imagen por plano, las voces, los subtítulos y el cierre del CTA con el nombre y el logo de la App. Mientras un plano no tiene su render, lleva un cartel: así sale la versión previa de cartón, el primer esqueleto completo del episodio. Es la misma composición que después lleva las imágenes reales. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Subtítulos" y "Montaje (HyperFrames)", y [ADR 0007](adr/0007-herramientas-blender-y-hyperframes.md).

```bash
uv run estudio montar ruta/a/la/carpeta-del-episodio
```

```bash
uv run estudio renderizar ruta/a/la/carpeta-del-episodio
```

Las dos órdenes cronometran antes de montar (vuelven a escribir `linea-de-tiempo.json`), así que la composición siempre corresponde al guion, las voces y la lista de planos de ese momento. Se niegan a seguir por lo mismo que `cronometrar` (ver [voces-y-linea-de-tiempo.md](voces-y-linea-de-tiempo.md)), y también si el guion tiene CTA y no entienden `app/app.toml` (ver "El cierre del CTA"). Entonces terminan con código de salida 1 sin escribir la composición.

## Planos: carteles e imágenes

Cada plano de la línea de tiempo es una capa de imagen (`plano-01`, `plano-02`…) que se ve desde el primer fotograma del plano hasta el primero del siguiente, a pantalla completa. Si el episodio no tiene lista de planos, no hay capas de imagen y se ve un fondo liso (`#3B4A5A`).

- **Imagen del plano**: su render, una imagen PNG en `planos/` con el `id` del plano por nombre: `planos/05.png` para el plano `"05"`. Tiene que medir 1080x1920, como todos los renders. Si no, la composición la recorta para llenar la pantalla sin deformarla, y no avisa.
- **Cartel**: mientras un plano no tiene imagen, `montar` le genera un cartel en `assets/carteles/<id>.svg`. Lleva el número del plano y su escenario sobre un color liso. Cada escenario tiene su color, en el orden en que aparece (`COLORES_DE_LOS_CARTELES`, en `src/estudio/montaje.py`), para ver de un vistazo dónde cambia. Son imágenes SVG, texto sin nada que instalar. Una imagen SVG no puede cargar letras, así que usan la del sistema (Arial, o la que más se le parezca).
- **Para sustituir un cartel por su imagen**, se deja la imagen en `planos/` con el `id` del plano y se vuelve a montar (o a renderizar, que monta antes). En la composición solo cambia la imagen de esa capa: nada más se toca. Nombrar las imágenes por el `id` del plano, y no por su posición, hace que no se descoloquen si se inserta un plano.
- **Planos con movimiento**: una imagen PNG es un fotograma fijo, que basta para la versión previa. Si el render de un plano es un vídeo (cámara que se acerca o se desplaza), su capa pasará a ser de vídeo. Lo decide el ticket 18 al elegir el formato del render, ampliando `imagen_del_plano` en `src/estudio/montaje.py`; el resto de la composición no cambia.

## El cierre del CTA

Mientras el Perro dice el CTA, arriba en el centro se ven el logo y el nombre de la App: desde el primer fotograma del CTA hasta el final del episodio, que es donde acaba el CTA. Es lo que dura el último plano, que empieza con la primera palabra del CTA (la lista de planos avisa si no es así: ver [lista-de-planos.md](lista-de-planos.md)). Si el guion no tiene CTA, no hay cierre y la documentación de la App no se lee.

- **Sitio**: el logo, de 240x240 px, a 260 px del borde de arriba, y debajo el nombre. Así quedan por debajo de las pestañas de TikTok e Instagram y lejos de los subtítulos. El nombre lleva la letra y los colores de los subtítulos del Tutor (blanco con borde negro) y va en una línea, de 78 px hacia abajo como las tarjetas. Aparece sin animación.
- **De dónde salen**: de la documentación de la App, la carpeta `app/` que está junto a `estudio.toml` (como la biblioteca). En ella va todo lo de la App: su logo, lo que lee la herramienta, en `app/app.toml`, y lo que lee el agente (funcionalidades, colores) en los archivos que se añadan. Hoy `app/app.toml` lleva:

  ```toml
  nombre = "Nombre de la App"
  logo = "logo.png"    # una imagen (PNG o SVG) de la carpeta app/
  ```

  `montar` copia el logo en la carpeta del episodio, en `assets/app/logo.png` (o `.svg`). Los tests tienen su propia App de ejemplo en `tests/episodios/app/`.
- **Mientras falten**: sin `nombre`, el cierre lleva «Nombre de la App»; sin `logo`, o si el logo no está en `app/`, un marcador (un recuadro de puntos con la palabra LOGO, en `assets/app/marcador-del-logo.svg`). En todos los casos, `montar` avisa. Si `app/app.toml` no sigue el formato, es un error y no se monta.

## Subtítulos

Las tarjetas de subtítulo salen en la línea de tiempo, en `subtitulos` (formato en [voces-y-linea-de-tiempo.md](voces-y-linea-de-tiempo.md)).

Las reglas son las que recomienda HyperFrames para los subtítulos de un vídeo rápido (decisión del creador, 2026-11-09):

- Cada tarjeta lleva hasta 3 palabras de una misma frase.
- Una tarjeta acaba al final de cada oración (una palabra que termina en `.` `?` `!` o `…`) y en cada pausa de la voz de 150 ms o más. Las comas no cortan por sí solas: si la voz hace pausa, la corta la regla de las pausas. «Exacto. Y yo ni siquiera tengo manos para recuperarlo.» sale como «Exacto.» · «Y yo ni» · «siquiera tengo manos» · «para recuperarlo.».
- Además, una palabra acentuada abre siempre su tarjeta, salvo que vaya detrás de otra acentuada. Así la animación de entrada cae justo cuando se dice la palabra, y un tramo acentuado da una sola animación: «Tengo hasta \*trescientos millones\* de receptores…» sale como «Tengo hasta» · «trescientos millones de» · «receptores…».
- Cada tarjeta empieza en el fotograma en que empieza su primera palabra y acaba donde empieza la siguiente tarjeta de su frase; la última, donde acaba la frase. En la pausa entre frases no hay subtítulo.
- **Estilo**:
  - Tutor: texto blanco (`#FFFFFF`) con borde negro (`#000000`).
  - Perro: texto lightcyan (`#E0FFFF`) con borde maroon (`#800000`).
  - Los dos: Montserrat en su grosor más negro (900), con un borde redondeado de 10 px alrededor de cada letra. El borde se dibuja con 24 copias del texto alrededor (sombras sin difuminar), porque el borde de texto del navegador deja picos en las tildes.
- **Tamaño**: cada tarjeta va en una sola línea. Empieza a 78 px y, si no cabe, baja de 2 en 2 hasta que cabe, sin pasar de 42 px. Es lo que recomienda HyperFrames, y lo calcula su función `fitTextFontSize` al renderizar.
- **Sitio**: abajo en el centro, con la línea apoyada a 480 px del borde de abajo: la línea del primer cuarto de la pantalla contando desde abajo (decisión del creador, 2026-11-09). El texto queda entre los 1350 y los 1440 px desde arriba. Deja 120 px a cada lado, fuera de la columna de botones de la derecha.
  - La guía de HyperFrames para vertical pide más margen: ningún texto por debajo de los 1330 px desde arriba (unos 590 px desde abajo), porque ahí TikTok e Instagram ponen el nombre, la descripción y los botones. Su revisión automática (`hyperframes check`) no avisa a 480 px. Si una descripción larga llegara a tapar los subtítulos, se suben cambiando `bottom: 480px` en `src/estudio/montaje.py`.
- **Animación**: solo entran animadas las tarjetas que empiezan por una palabra acentuada. Crecen del 60 % al 100 % de su tamaño en 6 fotogramas (`FOTOGRAMAS_DE_ENTRADA`), con un pequeño rebote. Las demás aparecen sin más.

Los colores están en `COLORES`, en `src/estudio/montaje.py`, y el resto del estilo, en la hoja de estilo de esa misma plantilla.

## `montar`

La carpeta del episodio es el proyecto de HyperFrames. `montar` deja en ella `index.html`, la composición, y lo que usa en `assets/`: la letra de los subtítulos (`assets/fonts/subtitulos.woff2`), los carteles (`assets/carteles/`) y el logo de la App o su marcador (`assets/app/`). Las carpetas `assets/carteles/` y `assets/app/` se borran y se vuelven a generar cada vez, para que no queden carteles de planos que ya tienen imagen ni logos viejos. La composición lleva:

- 1080x1920, los fotogramas por segundo de `estudio.toml` y la duración total del episodio;
- una capa de imagen por plano (`plano-01`, `plano-02`…), con su imagen o su cartel;
- una capa de audio por frase (`voz-01`, `voz-02`…), que suena desde el principio de su frase hasta el final;
- el cierre del CTA (`cierre-del-cta`), con el logo y el nombre de la App;
- una capa por tarjeta de subtítulo (`subtitulo-001`, `subtitulo-002`…), con el estilo de su personaje, todas dentro de la pista de subtítulos de HyperFrames (`data-track-kind="captions"`). Así HyperFrames las trata como subtítulos que siguen a la voz, y no les exige el tiempo de lectura de un rótulo.

Lo que se ve delante lo decide el `z-index` de cada capa, y no la pista de HyperFrames (`data-track-index`, que solo ordena las filas de su editor): los planos, debajo; encima, el cierre del CTA; y encima de todo, los subtítulos. Las pistas son: 0, las voces; 1, los subtítulos; 2, los planos; 3, el cierre.

Los tiempos van en segundos, que es lo que lee HyperFrames, con seis decimales. HyperFrames los ajusta al fotograma, así que cada capa empieza y acaba en el fotograma exacto de la línea de tiempo. Son archivos generados: no se editan a mano.

**Todo sale de la carpeta del episodio; nada de internet.** Así el render no depende de la red ni de que alguien cambie algo fuera:

- La animación de entrada es CSS, que HyperFrames también lleva fotograma a fotograma, y no la librería GSAP, que suele cargarse de una web externa.
- La letra va con el estudio, en `src/estudio/letras/` (Montserrat 900 de `@fontsource/montserrat` 5.3.0, solo el alfabeto latino, que cubre el español; licencia OFL en `OFL.txt`). Se copia con un nombre propio, `Subtitulos`, para que HyperFrames no vaya a buscar Montserrat a Google Fonts.
- El logo de la App se copia en la carpeta del episodio, aunque esté fuera de ella. Las imágenes de los planos ya están dentro, en `planos/`.

## `renderizar`

Monta el episodio y lo renderiza con HyperFrames a `versiones/previa.mp4`: 1080x1920 a 30 fps, con las voces. Es la versión previa: calidad de borrador, que es la más rápida. Antes de renderizar borra el vídeo de la vez anterior, para que un render fallido no deje un vídeo viejo que parezca nuevo.

- **Versión fijada**: `hyperframes@0.9.26`, en `HYPERFRAMES`, en `src/estudio/montaje.py`. HyperFrames saca versiones casi a diario, y fijarla evita que una suya cambie los episodios. Fija HyperFrames, no las librerías de las que depende ni el navegador con el que renderiza. Si algún día hace falta un render idéntico en cualquier máquina, HyperFrames lo ofrece dentro de Docker (`--docker`).
- **Para subir de versión**: cambiar esa línea, renderizar una copia del episodio de ejemplo y revisarla en fotogramas. La copia tiene que llevar encima `tests/episodios/estudio.toml` y `tests/episodios/biblioteca/`, como hacen los tests. Así no quedan vídeos dentro de `tests/`.
- **Hace falta** Node.js 22 o más nuevo y ffmpeg. La primera vez, `npx` descarga HyperFrames; después lo usa de su caché.
- No renderiza si la composición tiene errores para HyperFrames (`--strict`).
- HyperFrames deja en la carpeta del episodio una carpeta `.hyperframes/` con su historial. Git la ignora y se puede borrar.
- En la nube (4 núcleos, sin tarjeta gráfica), los 62 s del episodio de ejemplo tardan entre 30 y 40 s.
