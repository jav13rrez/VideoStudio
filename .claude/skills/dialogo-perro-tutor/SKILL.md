---
name: dialogo-perro-tutor
description: Convierte un contenido del mundo canino (un estudio científico, neurociencia, etología, aprendizaje, un mito frente a lo que dice la evidencia, un dato curioso o una historia de vínculo) en el guion de un episodio del estudio: una conversación de 55-70 segundos en la que el Perro explica y el Tutor aprende, escrita directamente en el formato del guion del estudio (guion.md y fuentes.md). Usar cuando el creador diga "crea el diálogo para este contenido", "haz un diálogo perro-tutor sobre esto", "pásalo a diálogo" o deje un contenido en contenido.md, y siempre que la skill perro-tutor llegue al paso del guion.
---

# Diálogo Perro–Tutor

Convierte el contenido de un episodio en su guion: una conversación entre el **Perro** (quien sabe y explica, en voz en off) y el **Tutor** (quien no sabe y aprende). La escribe directamente en el formato del guion del estudio, para que la herramienta la pueda comprobar sin adaptarla.

Es la fusión de las dos skills de diálogo del creador (2026-11-11): el menú de dinámicas y el arco de la de divulgación científica, más las técnicas dramáticas de su segunda skill como una dinámica más, «La escena-negocio». Los originales del creador siguen en su carpeta de Windows y no se tocan.

## Lo que entrega

1. **`guion.md`** en la carpeta del episodio, con el formato de [docs/formato-del-guion.md](../../../docs/formato-del-guion.md). Hay un ejemplo completo en `tests/episodios/001-olfato/guion.md`.
2. **`fuentes.md`**, con una fuente por cada dato que se afirma. Las fuentes nuevas van sin revisar, `[ ]`: las revisa el creador.
3. **`acotaciones.md`**: el tono y el gesto de cada frase (ver "Acotaciones"). No van en el guion, porque la voz las leería en alto.
4. **Una ficha breve** para presentar en la parada 1: la dinámica elegida y por qué, el dato o mito central, y las dos dinámicas alternativas que también encajarían.

No entrega ni el texto limpio para la voz (lo saca la herramienta del guion), ni el caption, ni los hashtags (la hoja de publicación sale de `uv run estudio hoja-de-publicacion`), ni marcas de tiempo `[MM:SS]` (los tiempos salen de la línea de tiempo, en fotogramas).

## Reglas fijas del formato

- **Duración:** la conversación, sin el CTA, tiene **150-170 palabras**, que caben en 55-70 segundos. No hay versión extendida. Si el contenido no cabe, se elige lo esencial y lo demás se guarda para otro episodio. Se dice en la ficha.
- **Solo hablan `Perro` y `Tutor`**, escritos así. No hay otros personajes, ni siquiera personificaciones («la Motivación», «el Olfato»). Si la escena lo pide, el Perro las interpreta o las nombra, pero nunca hablan ellas.
- **Una frase por línea**, `Personaje: texto`. Cada línea es un audio: las réplicas rápidas son líneas cortas.
- **`[gancho]`** en la primera frase y **`[remate]`** en la última de la conversación.
- **El CTA no lo escribe esta skill.** Lo añade la skill `perro-tutor` (o el agente, si se usa sola) como 1 o 2 frases `[cta]` del Perro justo después del remate, con la funcionalidad de la App que encaje con el tema. Por eso el remate tiene que cerrar la conversación y dejar paso a la invitación, sin anticiparla.
- **Marca de fuente** `[fuente: id]` detrás de cada dato que se afirma (cifras, resultados de estudios, mecanismos biológicos). Si el contenido no trae fuentes, se buscan fuentes fiables (skill `research`) y se presentan sin revisar. Ningún dato se queda sin fuente: si no se encuentra, se quita el dato.
- **Palabras acentuadas** entre asteriscos, `*así*`. Son donde el Tutor mueve la boca y donde se anima el subtítulo: una o dos por frase como mucho, en la palabra que de verdad se golpearía al decirla. Las expresiones híbridas (ver la escena-negocio) son buenas candidatas.
- Dentro del texto no va ningún corchete aparte de las marcas de fuente, ni paréntesis con acotaciones.

## Paso 1: elegir la dinámica (sin parar)

Si el creador ha dicho qué dinámica quiere, se usa esa. Si no, **elige tú** la que mejor sirva al contenido y explica el porqué en la ficha. No se pregunta antes de escribir: el estudio llega a la parada 1 con una sola instrucción, y el creador puede pedir otra dinámica allí.

| Dinámica | Perro | Tutor | Va bien con |
| --- | --- | --- | --- |
| **El académico sarcástico** | Intelectual, irónico pero cariñoso; juzga con suavidad las costumbres humanas. | Hace las preguntas típicas llenas de mitos e intenta justificarse con ternura. | Mitos de adiestramiento y creencias populares. |
| **El terapeuta paciente** | Calmado y empático; traduce su biología para calmar la ansiedad del humano. | Preocupado, sobreanaliza cada gesto o proyecta emociones humanas. | Estrés, miedos, señales de calma, antropomorfismo. |
| **El divulgador apasionado** | Entusiasta y didáctico; metáforas cotidianas y ejemplos olfativos para explicar ciencia compleja. | Curioso, se sorprende con cada dato y pregunta lo que da pie al siguiente. | Datos curiosos, sentidos, estudios con un hallazgo llamativo. |
| **El filósofo con los pies en el suelo** | Poético y observador, pero con un cable a tierra muy canino (la siesta al sol, el trozo de queso). | Cómplice, reflexivo, emocionalmente conectado. | Historias de vínculo, vejez, despedidas, rutinas compartidas. |
| **La escena-negocio** | El profesional irónico de un mostrador: dependiente, camarero, agente de aduanas. | El cliente bienintencionado que pide atajos y excusas. | Excusas del tutor, falta de constancia, refuerzo accidental, "métodos mágicos". |

Alterna las dinámicas entre episodios: el canal tiene que sonar a sí mismo, no a una sola fórmula. Antes de elegir, mira qué dinámica usaron los últimos episodios (su `acotaciones.md` la dice en la primera línea) y evita repetir la misma más de dos veces seguidas.

## Paso 2: el arco

Todas las dinámicas siguen el mismo arco, con estas proporciones aproximadas de las 150-170 palabras:

1. **Gancho** (una frase, menos de 15 palabras): una pregunta disruptiva, una afirmación chocante o una situación cotidiana que corte el scroll. Sin saludos ni preámbulos: empieza en mitad de la escena.
2. **El mito** (≈ 40 % de las palabras): el Tutor plantea la creencia popular, la excusa o la interpretación humana equivocada, y el Perro la desmonta.
3. **La ciencia** (≈ 25 %): el Perro explica el mecanismo real (olfato, cortisol, condicionamiento, habituación, corregulación…) en lenguaje de conversación, con sus marcas de fuente.
4. **Remate** (una o dos frases): una conclusión práctica o emocional, rematada con humor canino o con una frase que se quede.

## La escena-negocio, en detalle

Son técnicas dramáticas que el creador aprendió de los diálogos de Joaquín Caserza, contadas aquí con nuestras palabras y comprimidas a 55-70 segundos. Se toma la técnica, nunca sus frases, sus escenas ni sus remates (ver "Originalidad").

- **Escena real convertida en negocio.** El diálogo pasa en un sitio cotidiano y reconocible (el paseo, el comedero, el sofá, la puerta de casa, el parque), y el Perro lo convierte en un negocio con sus reglas: una ventanilla, un mostrador, una carta, una inspección. El negocio tiene que salir del tema, no ser un decorado. Si el tema es el refuerzo, el negocio es algo que se paga y se cobra.
- **Escalada en tres.** Después del gancho, un intercambio rápido de réplicas cortas (4 a 12 palabras por frase), en el que se desmontan tres excusas o mitos, uno detrás de otro, con ironía fina. El tercero es el más absurdo o el más revelador.
- **El quiebre.** A mitad del guion, el ritmo se para. El Perro dice una frase más larga y pausada (25 a 40 palabras, en una o dos líneas) que revela el mecanismo real. Es el único momento lento: su fuerza depende de que lo anterior haya sido rápido.
- **Expresiones híbridas (al menos dos).** Fusiones de una palabra de comercio, oficina o burocracia con un concepto de ciencia canina, inventadas para cada episodio: «una devolución de cortisol», «el seguro a todo riesgo del olfato», «horas extra de vigilancia». Que se entiendan a la primera.
- **Remate doble.** Una de dos: una frase luminosa y un poco paradójica sobre el vínculo, o el Perro rompiendo su explicación impecable con un impulso perruno irresistible.
- **Naturalidad oral.** Marcadores de conversación del español: «Pues mira…», «A ver…», «Vale, ¿y qué más?», «Uy, uy, uy». El Perro nunca recita definiciones.

## Acotaciones

`acotaciones.md` guarda el tono y el gesto de cada frase, para la voz y para la lista de planos (los gestos de `personajes` en `planos.toml`). Su formato:

```markdown
# Acotaciones: <título del episodio>

Dinámica: el divulgador apasionado. Escena: el recibidor, al volver del trabajo.

1. Perro: olfatea los zapatos con concentración de detective.
2. Tutor: medio en broma, medio ofendido.
…
```

Una línea por frase del guion, numerada en el mismo orden. Recuerda: el Perro no mueve la boca. Actúa con orejas, cabeza, mirada y cola, y cada gesto empieza con una mirada antes de moverse.

## Errores que evitar

- **Sonar a conferencia.** Si una frase del Perro pasa de 20 palabras fuera del quiebre, recórtala o pártela en réplica y contrarréplica.
- **Dos monólogos pegados.** Las preguntas e interrupciones del Tutor tienen que empujar la conversación, no solo dar paso.
- **Antropomorfizar al perro.** Habla con ironía como recurso, pero defiende siempre su naturaleza real (olfato, predicción del entorno, seguridad, refuerzo, descanso), nunca caprichos humanos.
- **Pedantería.** Los conceptos científicos se aterrizan con analogías caninas: olores, comida, sofás, correas, farolas.
- **Datos sin fuente** o más precisos de lo que dice la fuente. Si el estudio dice «más del doble», el guion no dice «2,3 veces».

## Originalidad

Una regla de la casa es no copiar guiones, personajes ni diseños de otros canales. Por eso, en cada episodio:

- no se reutiliza ninguna frase, escena ni remate de otro creador, aunque se adapte a perros (nada de tiendas de excusas, restaurantes del menú de siempre, aduanas de equipaje, ovejas contadas ni gritos de «¡Seguridad!»);
- las expresiones híbridas se inventan cada vez;
- el canal alterna dinámicas, para que ningún episodio suene a otro canal con un perro.

## Comprobar antes de entregar

Escrito el guion, pasa la comprobación y corrige hasta que no haya errores:

```bash
uv run estudio comprobar-guion <carpeta del episodio>
```

Revisa también los avisos: las 150-170 palabras, el gancho y el remate. Las fuentes sin revisar son normales en este punto; se las presentas al creador en la parada 1.
