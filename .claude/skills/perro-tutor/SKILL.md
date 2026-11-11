---
name: perro-tutor
description: La receta del estudio para producir un episodio del formato Perro–Tutor (vídeo vertical de 55-70 s en el que el Perro explica un tema de perros al Tutor y acaba invitando a probar la App K9 Architect), con las reglas de la casa. Usar cuando el creador pida "un episodio nuevo", "haz un episodio sobre…", "produce este contenido", deje un contenido para un episodio o quiera retomar uno ("sigue con el episodio 002"). Hoy llega hasta la parada 2 (guion, fuentes y CTA; luego lista de planos, voces y versión previa para juzgar el ritmo); los pasos siguientes se añaden con los tickets 18 en adelante.
---

# Perro–Tutor: la receta del estudio

Dirige un episodio de principio a fin, con **una sola instrucción** del creador, hasta la siguiente parada. Lo creativo (escribir, elegir, criticar) lo haces tú siguiendo esta receta. Lo mecánico lo hace la herramienta del estudio (`uv run estudio …`). El creador solo interviene en las paradas.

Spec: [.scratch/estudio-de-episodios/spec.md](../../../.scratch/estudio-de-episodios/spec.md). Formato del guion: [docs/formato-del-guion.md](../../../docs/formato-del-guion.md). Estado del episodio: [docs/estado-del-episodio.md](../../../docs/estado-del-episodio.md).

## Reglas de la casa

Valen para todos los episodios. Si el creador pide saltarse una, se hace y se anota en el estado del episodio con su motivo.

**Formato**
- Vertical 1080x1920, 30 fps, 55-70 segundos. Un plano por idea.
- Solo hablan el **Perro** (quien sabe, en voz en off; no mueve la boca) y el **Tutor** (quien aprende).
- La conversación tiene 150-170 palabras. Detrás va el CTA: 1 o 2 frases del Perro, como mucho unas 15 palabras (unos 5 segundos), siempre al final.
- Cada dato que se afirma lleva su fuente. Ningún dato en pantalla ni en la voz va más allá de lo que dice su fuente.

**Aspecto**
- Personajes planos dentro de escenarios 3D con una luz con motivo (una ventana, una lámpara, el sol de la tarde).
- Materiales con desgaste, nada de plástico limpio.
- Sombra de contacto bajo los personajes.

**Prohibido**
- Un título centrado sobre un degradado.
- Etiquetas en las esquinas, códigos de tiempo o marcos.
- Que todo aparezca con un fundido.
- Un «whoosh» en cada corte.
- Cualquier dato en pantalla que no esté en las fuentes.
- Copiar personajes, diseños o guiones de otros canales.

**Originalidad**
- Ninguna frase, escena, personaje ni remate de otro creador, ni siquiera adaptado a perros. Las técnicas se aprenden; las frases no se copian.
- Las dinámicas del diálogo se alternan entre episodios (lo controla la skill `dialogo-perro-tutor`).
- El repositorio es público: no se suben transcripciones ni guiones de terceros.

## Paso 1: el guion, hasta la parada 1

Con una instrucción del tipo «haz un episodio sobre este contenido», haz todo esto sin parar a preguntar:

1. **Crea la carpeta del episodio**, con un nombre corto que diga el tema (minúsculas, sin tildes, con guiones):
   ```bash
   uv run estudio crear-episodio episodios/<nombre-corto>
   ```
   Si el creador retoma un episodio que ya existe, no lo crees: mira su estado (`uv run estudio estado <carpeta>`) y sigue desde el paso que diga.
2. **Deja el contenido en `contenido.md`**, tal cual lo dio el creador, con lo que diga sobre el enfoque. Si lo dejó en su carpeta de Windows (`/mnt/c/Users/Usuario/Documents/VideoStudio/`), cópialo de ahí.
3. **Escribe el guion con la skill `dialogo-perro-tutor`.** Ya escribe `guion.md`, `fuentes.md` y `acotaciones.md` en el formato canónico, sin el CTA, y te da la ficha de la dinámica.
   - Si el contenido trae afirmaciones que «conviene evitar», no aparecen en el guion, ni siquiera matizadas.
   - Si trae dos líneas de investigación que no están unidas por un experimento, el guion no las une como causa y efecto.
4. **Busca las fuentes que falten** (skill `research`). Usa fuentes primarias si las hay (el artículo científico) y, si no, la nota de prensa oficial (por ejemplo, la de la revista). Las fuentes nuevas van sin revisar, `[ ]`. Un dato sin fuente se quita.
5. **Propón el CTA** (ver "El CTA") y añádelo al final de `guion.md`.
6. **Comprueba el guion** y corrige hasta que no haya errores:
   ```bash
   uv run estudio comprobar-guion episodios/<carpeta>
   ```
   De los avisos, arregla los de palabras, gancho, remate y fuentes sin usar. Los de fuentes sin revisar son normales: las revisa el creador.
7. **Anota las horas** que te ha llevado, si el creador te las dice o las has medido:
   ```bash
   uv run estudio registrar-horas episodios/<carpeta> guion <horas>
   ```
8. **Para en la parada 1** (ver abajo).

## El CTA

Lo dice el Perro, justo después del remate, en 1 o 2 frases `[cta]` y con unas 15 palabras como mucho. Lee la documentación de la App en `app/` (junto a `estudio.toml`): el nombre en `app/app.toml` y las funcionalidades en `app/funcionalidades.md`.

1. **Si el tema conecta con una funcionalidad para tutores**, usa esa y dila como un beneficio para el tutor, no como el nombre de una función.
2. **Si no conecta con ninguna**, no fuerces la conexión. El Perro invita igual con un puente natural («Por cierto…», «Y ya que estamos…») y lo que hace la App en general: crear planes de educación personalizados. Es la idea del creador: «Por cierto, ¿sabías que K9 Architect crea planes de educación personalizados?».
3. **Las funcionalidades para educadores caninos** se usan solo cuando el episodio trata de trabajar con un profesional.
4. **Nombra la App** («K9 Architect»): en pantalla salen su nombre y su logo mientras el Perro dice el CTA.
5. Respeta "Lo que no se puede decir en un CTA" de `app/funcionalidades.md`. No hay app en las tiendas, así que nada de «descárgala».
6. El CTA no lleva datos, así que tampoco lleva marcas de fuente.

En la propuesta para el creador pones el CTA elegido, la funcionalidad, por qué esa y una alternativa.

## La parada 1

Le presentas al creador, en el chat, en este orden y en lenguaje llano:

1. **El guion entero**, tal cual está en `guion.md`.
2. **La ficha del diálogo**: la dinámica elegida y por qué, el dato o mito central, lo que se ha quedado fuera por no caber y las dos dinámicas alternativas.
3. **Las fuentes**: cada una con el dato que respalda, señalando cuáles están sin revisar y cuáles son resúmenes de prensa en vez del artículo original.
4. **La propuesta de CTA**: la funcionalidad, por qué y una alternativa.
5. **El resultado de la comprobación**: errores (tiene que haber cero) y avisos.
6. **La pregunta de la parada**, con `AskUserQuestion` si la tienes: aprobar, aprobar con cambios (cuáles) o cambiar de dinámica.

No sigas al paso 2 sin la aprobación. Cuando el creador apruebe:

- marca como revisadas (`[x]`) en `fuentes.md` las fuentes que el creador dé por buenas;
- anota la aprobación:
  ```bash
  uv run estudio aprobar episodios/<carpeta> parada 1
  ```
- haz commit con la carpeta del episodio (un «punto de guardado» para el creador).

Si pide cambios, corrige, vuelve a comprobar y vuelve a presentar solo lo que ha cambiado.

## Paso 2: la versión previa, hasta la parada 2

Con la parada 1 aprobada (`uv run estudio estado <carpeta>` dice «Paso: 2 de 4»), haz todo esto sin parar a preguntar:

1. **Genera las voces** con el proveedor de `estudio.toml` (con Kokoro, unos 2-3 minutos):
   ```bash
   uv run estudio generar-voces episodios/<carpeta>
   ```
2. **Cronometra sin lista de planos** y mira cuándo empieza cada palabra en `linea-de-tiempo.json`. La lista de planos se escribe con los tiempos reales, no a ojo:
   ```bash
   uv run estudio cronometrar episodios/<carpeta>
   python3 -c "import json;d=json.load(open('episodios/<carpeta>/linea-de-tiempo.json'))
   for f in d['frases']: print(f['numero'],f['personaje'],' '.join(p['texto']+'@'+str(p['inicio']) for p in f['palabras']))"
   ```
3. **Escribe `planos.toml`** ([docs/lista-de-planos.md](../../../docs/lista-de-planos.md)), partiendo de `acotaciones.md`:
   - Un plano por idea, cada uno de 45 a 90 fotogramas (1,5-3 s). Un plano termina donde empieza el siguiente, así que se elige en qué palabra corta cada uno restando sus inicios.
   - Si una idea es corta (una réplica de un segundo), júntala con la de al lado; si es larga, pártela en una palabra que cambie la imagen.
   - El último plano empieza en la primera palabra del CTA y deja aire arriba para el nombre y el logo de la App.
   - La cámara se mueve solo con motivo (`motivo`), y casi siempre está fija. Como mucho 5 escenarios; mejor 1 o 2.
   - Los escenarios que no tienen carpeta en `biblioteca/escenarios/` van en `escenarios_nuevos`.
   - Los gestos de `personajes` salen de las acotaciones. Nada de personajes que no sean el Perro y el Tutor; si hace falta alguien más, que sea una silueta del escenario.
   - `sonido` solo para sonidos físicos con sentido (una llave, un móvil sobre el cojín), nunca un «whoosh» en el corte.
   - `empieza` tiene que aparecer una sola vez en el guion y no salir de su frase. Si una réplica entera se repite en otra frase (por ejemplo «¿Con los ojos?» dentro de «con los ojos húmedos»), ese plano no puede empezar ahí: júntalo con el anterior.
4. **Comprueba la lista** cronometrando otra vez, y corrige hasta que no haya errores ni avisos de duración:
   ```bash
   uv run estudio cronometrar episodios/<carpeta>
   ```
5. **Renderiza la versión previa** (de cartón mientras no haya renders en `planos/`) y saca sus hojas:
   ```bash
   uv run estudio renderizar episodios/<carpeta>
   uv run estudio revisar episodios/<carpeta>
   ```
   Los avisos de logo de la App o de `sonido.toml` que falten son normales mientras el creador no los aporte; díselos, sin bloquear.
6. **Critica tú las hojas antes de enseñarlas** (léelas como imágenes): `revision/previa-contactos.png` y `revision/previa-movil.png`. Mira que haya un cartel por plano y los cambios de escenario donde tocan, que los subtítulos se lean en el móvil y no los tape nada, y que en el CTA salgan el nombre y el logo (o su marcador). Si algo falla, arréglalo y vuelve a renderizar.
7. **Ábrele el vídeo al creador** en Windows:
   ```bash
   mkdir -p /mnt/c/Users/Usuario/Videos/VideoStudio
   cp episodios/<carpeta>/versiones/previa.mp4 /mnt/c/Users/Usuario/Videos/VideoStudio/<carpeta>-previa.mp4
   cd /mnt/c/Users/Usuario/Videos/VideoStudio && explorer.exe <carpeta>-previa.mp4
   ```
   `explorer.exe` devuelve el código 1 aunque lo abra bien.
8. **Para en la parada 2** (ver abajo).

## La parada 2

El creador juzga el **ritmo**: si los cortes caen bien, si algún plano se hace largo o corto, si las voces suenan bien y si los subtítulos se leen. No juzga el aspecto: son carteles. Le presentas, en lenguaje llano:

1. **La duración** total y la del CTA, y cuántos planos y escenarios hay.
2. **La lista de planos resumida**: una línea por plano con su número, dónde empieza en el guion, el escenario y lo que se verá.
3. **La hoja de contactos y la prueba de móvil** (rutas), con lo que has visto en ellas, y el vídeo abierto en Windows.
4. **Lo que falta y no bloquea**: el logo de la App, la música y los efectos, los escenarios y personajes nuevos (se aprueban cuando se construyan).
5. **La pregunta de la parada**, con `AskUserQuestion` si la tienes: aprobar el ritmo, o cambiar algo (qué plano, qué frase, qué voz).

No sigas al paso 3 sin la aprobación. Cuando el creador apruebe:

- anota la aprobación:
  ```bash
  uv run estudio aprobar episodios/<carpeta> parada 2
  ```
- haz commit con la carpeta del episodio.

Si pide cambios: en el guion, vuelve al paso 1 de esta receta para esa frase (comprobar, generar sus voces de nuevo); en los planos, cambia `planos.toml`. Después vuelve a renderizar, revisar y enseñar solo lo que ha cambiado.

## Lo que viene después

El paso 3 (render de los planos y montaje final, hasta la parada 3) se escribe aquí con los tickets 18 en adelante. Hasta entonces, cada orden tiene su documentación en `docs/`.
