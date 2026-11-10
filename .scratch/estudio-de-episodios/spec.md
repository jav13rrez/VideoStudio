# Spec: estudio de episodios Perro–Tutor

Status: ready-for-agent

Vocabulario: [GLOSSARY.md](../../GLOSSARY.md). Decisiones previas: [ADR 0005](../../docs/adr/0005-el-estudio-vive-en-el-pc-de-casa.md) (el estudio vive en el PC de casa), [ADR 0006](../../docs/adr/0006-estudio-sin-aplicacion-propia.md) (carpeta con skills, sin aplicación), [ADR 0007](../../docs/adr/0007-herramientas-blender-y-hyperframes.md) (Blender + HyperFrames). Plan de partida: [docs/PlanBase.md](../../docs/PlanBase.md). Instalaciones pendientes: [DEBT_TECH.md](../../DEBT_TECH.md).

## Problema

El creador quiere un canal de episodios cortos de animación en vertical, en español, que atraiga tutores y educadores caninos a su App. En cada episodio, el Perro (su perro, en voz en off) le explica un tema de perros al Tutor (el propio creador), y al final invita a usar la App.

Hacer un solo episodio de animación 2.5D (personajes planos dentro de escenarios 3D iluminados) exige normalmente un modelador, un animador, un iluminador, un montador y un técnico de sonido. Sin un proceso fijo, cada episodio empieza de cero: es lento, el resultado cambia de un episodio a otro, se arriesga a parecer "hecho por IA" y puede afirmar datos falsos sobre la salud o el comportamiento de los perros, que es lo que más confianza destruye. Además, el creador no programa: necesita un estudio que se maneje hablando con un agente y que solo le pida decisiones y aprobaciones.

## Solución

Un estudio que vive en el PC del creador: una carpeta de trabajo con skills que maneja Claude Code, más una herramienta del estudio que hace todo lo mecánico y comprobable. El creador deja el contenido de un episodio y pide un episodio nuevo con una sola instrucción. A partir de ahí:

1. Su skill de diálogo convierte el contenido en un guion entre el Perro y el Tutor. El estudio lo comprueba (duración, gancho, remate, fuentes de cada dato) y propone qué funcionalidad de la App mencionar en el CTA. → **Parada 1**: el creador aprueba el guion, las fuentes y el CTA.
2. El estudio divide el guion en una lista de planos, reutiliza o construye escenarios (domésticos o de naturaleza), personajes (a partir de las hojas de personaje del creador) y, si el tema lo tiene, el objeto protagonista. Cada escenario o personaje nuevo pasa por el creador la primera vez.
3. Genera dos voces sintéticas gratuitas (una frase, un audio), cronometra todo en fotogramas, crea los subtítulos con el color de cada personaje y monta una versión previa. → **Parada 2**: el creador juzga el ritmo.
4. Renderiza en Blender, monta el episodio con HyperFrames (planos, voces, música, subtítulos y el CTA con el nombre y el logo de la App), pasa su propia crítica sobre la hoja de contactos y corrige. → **Parada 3**: el creador aprueba el episodio final.
5. Comprueba la exportación (1080x1920, 30 fotogramas por segundo, duración planificada) y deja una hoja de publicación con la descripción y un enlace con seguimiento por plataforma. El creador sube el episodio a mano.

El primer hito es un **episodio piloto** listo para subir, con el registro de horas de cada etapa.

## Historias de usuario

### Contenido y guion

1. Como creador, quiero dejar el contenido de un episodio en un único sitio de su carpeta, para que el estudio sepa de qué trata sin que yo tenga que explicarlo en el chat.
2. Como creador, quiero que mi skill de diálogo convierta el contenido en el guion entre el Perro y el Tutor, para mantener mi forma de estructurar las conversaciones.
3. Como creador, quiero que el guion quede en un formato fijo y legible, con cada frase marcada con quién la dice, para revisarlo sin conocimientos técnicos.
4. Como creador, quiero que el estudio me avise si la conversación se sale de 150-170 palabras, para que el episodio quepa en 55-70 segundos.
5. Como creador, quiero que el estudio compruebe que solo hablan el Perro y el Tutor, para que no se cuelen personajes no previstos.
6. Como creador, quiero que el estudio me señale si al guion le falta gancho o remate, sin reescribirlo, para decidir yo si lo cambio.
7. Como creador, quiero que cada dato que se afirma en el guion apunte a una de sus fuentes, para no publicar errores sobre la salud o el comportamiento de los perros.
8. Como creador, quiero que, si mi contenido no trae fuentes, el estudio las busque y me las presente para revisarlas, para no buscarlas yo desde cero.
9. Como creador, quiero que el estudio detecte referencias a fuentes que no existen y fuentes que ninguna frase usa, para que la lista de fuentes esté limpia.
10. Como creador, quiero que el estudio me diga qué fuentes he revisado ya y cuáles no, para no aprobar un guion con datos sin comprobar.
11. Como creador, quiero que el CTA vaya siempre al final, justo después del remate, y que lo diga el Perro, para que todos los episodios cierren igual.
12. Como creador, quiero que el estudio proponga qué funcionalidad de la App mencionar en el CTA según el tema del episodio, para que la invitación resulte relevante.
13. Como creador, quiero que se prioricen las funcionalidades para tutores y que las de educadores caninos solo se usen cuando el tema lo pida, porque los episodios hablan a tutores.
14. Como creador, quiero que el CTA sean 1 o 2 frases del Perro, unos 5 segundos, para que no parezca un anuncio largo.
15. Como creador, quiero que el estudio se detenga en la parada 1 con el guion, las fuentes y la propuesta de CTA, para aprobar o corregir antes de gastar horas en producir.

### Planos

16. Como creador, quiero que el guion se divida en una lista de planos con un plano por idea, para que cada corte tenga un motivo y no dependa de un temporizador.
17. Como creador, quiero que cada plano dure entre 1,5 y 3 segundos y que el estudio avise si alguno se sale, para mantener el ritmo del formato.
18. Como creador, quiero que todos los tiempos del episodio se expresen en fotogramas, para que cualquier corrección sea un número que el agente no pueda malinterpretar.
19. Como creador, quiero que cada plano indique escenario, encuadre y movimiento de cámara con su motivo, personaje y gesto, objeto protagonista y sonido, para que la imagen esté decidida antes de construirla.
20. Como creador, quiero que la cámara solo haga acercamientos lentos o desplazamientos con un motivo, nunca derivas al azar ni giros constantes, para que el episodio se vea dirigido.
21. Como creador, quiero que un episodio use como mucho 3-5 escenarios y reutilice los de la biblioteca, para no construir decorados nuevos cada vez.
22. Como creador, quiero que cada corte de plano caiga sobre la palabra a la que pertenece, para que la imagen acompañe a lo que se dice.

### Escenarios, personajes y objetos

23. Como creador, quiero escenarios domésticos (salón, cocina, consulta del veterinario…) y de naturaleza (montaña, prados, bosques, lagos, mar), para que el entorno cambie según el tema.
24. Como creador, quiero que cada escenario se construya por pasadas (bloquear, iluminar, vestir), con una hoja de vistas desde cada cámara al final de cada pasada, para corregir pronto y barato.
25. Como creador, quiero que los escenarios tengan una luz principal con motivo (ventana, sol), luces cálidas de ambiente, materiales con desgaste y profundidad de campo enfocada donde está el personaje, para que se vean de cine.
26. Como creador, quiero aprobar cada escenario nuevo la primera vez que se crea, para que la biblioteca solo tenga escenarios que me gustan.
27. Como creador, quiero que el Tutor y el Perro se construyan a partir de mis hojas de personaje, para que se parezcan a mí y a mi perro.
28. Como creador, quiero que el estudio me avise si a una hoja de personaje le faltan vistas o expresiones necesarias para animar, para dárselas antes de empezar.
29. Como creador, quiero que los personajes sean planos, sin sombreado realista, con contorno grueso y una sombra de contacto en el suelo, para conseguir el contraste 2.5D y que no floten.
30. Como creador, quiero aprobar cada personaje la primera vez que se monta, para que no se use una versión que no me representa.
31. Como creador, quiero que el Tutor mueva la boca solo en las palabras acentuadas y que el Perro no la mueva nunca, porque habla en voz en off.
32. Como creador, quiero que el Perro actúe con orejas, cabeza, mirada y cola, y que cada gesto empiece con una mirada antes de moverse, para que parezca que piensa.
33. Como creador, quiero que ningún personaje rebote ni se mueva sin motivo, para que no se note que es animación generada.
34. Como creador, quiero que, cuando el tema lo tenga, el objeto protagonista se construya en 3D a escala real, con una hoja de seis vistas antes de entrar en el escenario, para que tenga su momento en pantalla.
35. Como creador, quiero que escenarios, personajes y objetos aprobados se guarden en la biblioteca, para que cada episodio cueste menos que el anterior.

### Voz, subtítulos y sonido

36. Como creador, quiero dos voces sintéticas distintas en español, una para el Perro y otra para el Tutor, generadas gratis en mi PC, para no tener que grabar cada episodio.
37. Como creador, quiero que cada frase del guion sea un audio separado, para saber exactamente quién habla y cuándo.
38. Como creador, quiero poder cambiar la voz de cualquiera de los dos personajes por una grabación mía o por un servicio de pago sin tocar el resto del estudio, por si la voz gratuita no convence.
39. Como espectador, quiero subtítulos de 2-3 palabras (lo que recomienda HyperFrames; el creador lo cambió de 1-2 el 2026-11-09) que cambien justo cuando empieza su primera palabra, para leerlos al ritmo de la voz.
40. Como espectador, quiero distinguir quién habla por el color del subtítulo (Tutor: blanco con borde negro; Perro: lightcyan con borde maroon), para seguir la conversación sin sonido.
41. Como espectador, quiero subtítulos en negrita, con un borde grueso alrededor de cada letra y colocados abajo en el centro, dentro de la zona segura del vertical, para leerlos en el móvil sin que nada los tape.
42. Como espectador, quiero que los subtítulos no salten con una animación en cada palabra, solo en las acentuadas, para que no cansen.
43. Como creador, quiero música gratuita y libre de derechos, baja por debajo de las voces, que resuelva en el último fotograma, para que el final suene cerrado.
44. Como creador, quiero efectos de sonido solo cuando pasa algo físico, y nunca el mismo "whoosh" en cada corte, para no saturar el episodio.
45. Como creador, quiero que la licencia de cada música y efecto quede anotada en la carpeta del episodio, para poder demostrar que puedo usarlos.

### Montaje y revisión

46. Como creador, quiero una versión previa rápida con voces, subtítulos y planos sin pulir, para juzgar el ritmo antes del render final (parada 2).
47. Como creador, quiero que el episodio final se monte con HyperFrames a partir de los planos renderizados, las voces, la música, los subtítulos y el CTA, para que el resultado se pueda reproducir exactamente.
48. Como creador, quiero que el último plano muestre el nombre y el logo de la App mientras el Perro dice el CTA, para que el espectador sepa qué buscar.
49. Como creador, quiero una hoja de contactos y una prueba de móvil (el episodio visto a 360 px de ancho) de cada versión, para revisarla de un vistazo.
50. Como creador, quiero que el agente haga de crítico sobre esas hojas antes de enseñármelas, arregle los 3 peores problemas y repita, para que me lleguen versiones ya pulidas.
51. Como creador, quiero que cada corrección se describa con dónde (fotogramas), qué falla, qué cambia y qué no se toca, para que el agente no rompa lo que ya estaba bien.
52. Como creador, quiero que al corregir solo se vuelvan a renderizar los fotogramas afectados, para no esperar horas por un cambio pequeño.
53. Como creador, quiero aprobar el episodio final con su hoja de contactos (parada 3), para que nada salga sin mi visto bueno.
54. Como creador, quiero que el estudio compruebe que la exportación mide 1080x1920, va a 30 fotogramas por segundo y dura lo planificado, para no subir un archivo defectuoso.

### Publicación y medida

55. Como creador, quiero que cada episodio deje una hoja de publicación con el texto de la descripción y un enlace con seguimiento distinto para YouTube, TikTok e Instagram, para saber de dónde llega cada alta en la App.
56. Como creador, quiero que la hoja de publicación me recuerde marcar el aviso de marca propia donde la plataforma lo pida, para que no limiten el vídeo.
57. Como creador, quiero subir yo los episodios a mano, porque publicar siempre pasa por mí.
58. Como creador, quiero que los enlaces con seguimiento me permitan repasar, tras cada tanda de episodios, las altas por plataforma junto a la gráfica de retención de YouTube, para mejorar los planos donde la gente se va.

### Proceso y coste

59. Como creador, quiero que cada episodio viva en su propia carpeta con contenido, guion, fuentes, lista de planos, audios, versiones, exportación y hoja de publicación, para que todo esté junto y sirva de plantilla para el siguiente.
60. Como creador, quiero que la carpeta de cada episodio diga en qué parada está y qué he aprobado, para retomarlo otro día en una conversación nueva sin explicar nada.
61. Como creador, quiero que se anoten las horas de cada etapa (guion, escenarios, personajes, animación, voces, sonido, revisión), para saber cuánto cuesta de verdad un episodio y decidir el ritmo de publicación.
62. Como creador, quiero que el estudio no gaste dinero, y que activar un servicio de pago consista en cambiar una línea de configuración y pegar yo la clave en `.env`, para crecer sin rehacer nada.
63. Como creador, quiero pedir un episodio nuevo con una sola instrucción a Claude Code, para no tener que recordar los pasos.
64. Como agente que produce un episodio, quiero las reglas de la casa (formato, aspecto, prohibiciones) escritas en la skill del estudio, para que todos los episodios salgan con el mismo criterio.
65. Como creador, quiero que el estudio nunca copie personajes, diseños ni guiones de otros canales, para cumplir las normas de las plataformas y que el canal dure.
66. Como creador, quiero que el estudio esté preparado para añadir otro formato como una receta aparte, para no rehacerlo si un día quiero otro tipo de vídeo.

## Decisiones de implementación

### Piezas del estudio

- **Skill del estudio (receta del formato Perro–Tutor).** Dirige el proceso de un episodio de principio a fin: pasos, paradas, reglas de la casa e instrucciones para guion, planos, escenarios, personajes, voces, montaje, crítica y publicación. Vive con las skills propias del proyecto y se sincroniza según el ADR 0004. Lo creativo (redactar, construir en Blender, actuar, criticar) lo hace el agente siguiendo esta skill.
- **Herramienta del estudio.** Pequeña herramienta de línea de comandos en Python (gestionada con uv) que trabaja siempre sobre una carpeta de episodio y hace todo lo determinista: comprobar, cronometrar, subtitular, componer, revisar y preparar la publicación. Python porque Blender, Whisper y los motores de voz libres son Python; HyperFrames y Blender se llaman como programas externos.
- **Biblioteca.** Escenarios, personajes y objetos protagonistas aprobados, como archivos de Blender reutilizables. Los episodios **enlazan** los elementos de la biblioteca en lugar de copiarlos, para que una mejora en un escenario llegue a los episodios siguientes.
- **Receta.** Todo lo específico del formato (la skill y su configuración) va separado de la herramienta y la biblioteca, que son comunes. Un formato nuevo es otra receta (ADR 0006).

### Carpeta de episodio (el contrato central)

- Una carpeta por episodio, con número y nombre corto. Contiene: el contenido, el guion, las fuentes, la lista de planos, los audios por frase y sus marcas de tiempo, los archivos generados (línea de tiempo, subtítulos, composición de HyperFrames), las versiones (previa y final), las hojas de revisión, la exportación, la hoja de publicación, las licencias de música y efectos, el registro de horas y el estado del episodio.
- **Estado del episodio:** en qué paso está, qué paradas están aprobadas y cuándo, y qué escenarios o personajes nuevos esperan aprobación. Permite retomar un episodio en otra conversación.
- Los archivos generados nunca se editan a mano: se regeneran con la herramienta.

### Guion y fuentes

- **Formato canónico del guion**, propiedad del estudio. Es texto legible por el creador y estructurado para la herramienta: una secuencia de frases, cada una con su personaje (solo Perro o Tutor) y su texto. Marca la primera frase como gancho, la última de la conversación como remate y, aparte, el CTA (solo frases del Perro). Las palabras acentuadas pueden marcarse (sirven para las bocas del Tutor y para animar subtítulos). Cada dato afirmado lleva una marca que apunta a una fuente por su identificador.
- La salida de la skill de diálogo del creador se adapta a este formato. Si la skill puede producirlo directamente, mejor. Está pendiente de leer la skill (`DEBT_TECH.md`).
- **Fuentes:** lista con identificador, descripción, enlace o referencia, y si el creador la ha revisado.
- **Comprobaciones del guion:**
  - **Errores** (impiden pasar la parada 1): personajes distintos de Perro y Tutor; CTA que no está al final o que no dice el Perro; marcas que apuntan a fuentes inexistentes.
  - **Avisos:** conversación fuera de 150-170 palabras; CTA de más de unas 15 palabras; falta marca de gancho o de remate; fuentes sin usar; fuentes sin revisar.
  - Detectar qué frases afirman datos es trabajo del agente. La herramienta solo comprueba que las marcas y las fuentes cuadran.
- **Propuesta de CTA:** el agente elige la funcionalidad leyendo la documentación de la App que estará en el repositorio (nombre, enlace, logo, colores, funcionalidades para tutores y para educadores caninos). Prioriza las de tutores. La propuesta va con el guion a la parada 1.
- **Documentación de la App:** la carpeta `app/` junto a `estudio.toml`, como la biblioteca. Lo que lee la herramienta (nombre, logo y, con el ticket 09, el enlace) va en `app/app.toml`; lo que lee el agente, en la misma carpeta (decidido en el ticket 07; formato en `docs/montaje.md`).

### Lista de planos

- Archivo estructurado con un elemento por plano: identificador, palabra del guion en la que empieza, escenario, encuadre y movimiento de cámara con su motivo, personajes y gesto, objeto protagonista y sonido físico si lo hay.
- La duración de los planos **no se escribe a mano**: sale de la línea de tiempo. Cada plano empieza en el fotograma en que empieza su palabra, así que los cortes caen siempre sobre la palabra a la que pertenecen.
- **Comprobaciones:**
  - **Errores:** frases del guion que ningún plano cubre; planos fuera de orden; escenarios que no están en la biblioteca y no van marcados como nuevos.
  - **Avisos:** planos de menos de 45 o más de 90 fotogramas (1,5 a 3 s); más de 5 escenarios en el episodio.

### Cronometraje (línea de tiempo)

- Es la pieza central de la herramienta, y es determinista. Recibe el guion, la duración de cada audio de frase, las marcas de tiempo de cada palabra, la lista de planos y la pausa entre frases (configurable). Devuelve, en fotogramas globales a 30 fps: el inicio y el final de cada frase, de cada palabra, de cada plano, de cada tarjeta de subtítulo y del CTA, y el total del episodio.
- **Avisos:** total fuera de 1.650-2.100 fotogramas (55-70 s); CTA muy lejos de unos 150 fotogramas.

### Voces (enchufe de voz)

- Interfaz única: dada una frase y su personaje, el proveedor deja un archivo de audio y su duración, y las marcas de tiempo por palabra si las sabe dar.
- **Proveedores:**
  - **local gratuito:** se elige mañana en el PC (`DEBT_TECH.md`);
  - **grabación:** el creador deja sus propios audios por frase y el proveedor solo los recoge;
  - **pago:** un servicio por API, con la clave en `.env`;
  - **falso:** para los tests, silencio de una duración proporcional a las palabras, con marcas de tiempo sintéticas.
- La configuración del estudio asigna a cada personaje un proveedor y una voz. Cambiar de proveedor es cambiar esa línea.
- Si el proveedor no da marcas por palabra, se alinea cada audio con su texto conocido mediante Whisper, o con la función de HyperFrames si la cubre (por verificar en el PC).

### Subtítulos

- Tarjetas de 2-3 palabras generadas desde las marcas de tiempo, con las reglas de subtítulos que recomienda HyperFrames (decisión del creador, 2026-11-09). Cada tarjeta empieza en el fotograma de inicio de su primera palabra y termina donde empieza la siguiente o donde acaba la frase.
- Estilo por personaje:
  - **Tutor:** texto blanco con borde negro.
  - **Perro:** texto lightcyan (`#E0FFFF`) con borde maroon (`#800000`).
  - **Ambos:** negrita, borde grueso en todo el contorno de cada letra, abajo en el centro, dentro de la zona segura del 9:16.
- Solo se anima la entrada de las tarjetas con palabras acentuadas.

### Música y efectos (enchufes)

- **Música:** pista de una biblioteca gratuita y libre de derechos, elegida por episodio, con su licencia anotada. Va baja por debajo de las voces y se ajusta para que resuelva en el último fotograma. La música generada o de pago queda como proveedor futuro del mismo enchufe.
- **Efectos:** solo los sonidos físicos que pide la lista de planos, también con su licencia. Cada efecto se coloca de forma que su golpe (el pico de la onda) caiga en el fotograma del evento.

### Escenarios, personajes y objetos (agente + Blender)

- El agente construye en Blender a través del MCP oficial de Blender Lab (ADR 0007) y comprueba su propio trabajo con hojas de vistas: un render EEVEE de un fotograma desde cada cámara de la escena (con `bpy.ops.render.render` a través del MCP), unidos en una sola imagen con ffmpeg (filtro `tile`).
- **Escenarios:** se hacen por pasadas (bloquear, iluminar, vestir) con una hoja de vistas por pasada; el render es siempre a 1080x1920, nunca más grande para recortar después. Los cielos y el entorno lejano de los escenarios de naturaleza se resuelven con imágenes HDRI para contener el tiempo de render.
- **Personajes:** se separan en piezas recortadas a partir de las hojas de personaje (cabeza, cuerpo, extremidades, juegos de ojos y bocas). Van en planos con material plano, sin sombreado y con sombra de contacto. Al Perro no se le hacen bocas habladas.
- **Actuación:** antes de animar, el agente escribe por plano una línea de actuación: pensamiento, anticipación, acción y pausa.
- **Objeto protagonista:** se construye aparte, con una hoja de seis vistas, y luego se coloca en el escenario.
- **Render:** desde la línea de comandos de Blender, por rangos de fotogramas, para poder volver a renderizar solo lo corregido. La versión previa usa un render rápido (calidad baja o fotogramas fijos); el final, la calidad completa.

### Montaje (HyperFrames)

- La herramienta genera la composición de HyperFrames a partir de la línea de tiempo:
  - una capa de imagen por plano;
  - las capas de audio: frases, música y efectos;
  - la capa de subtítulos;
  - el cierre del CTA, con el nombre y el logo de la App.
- La versión previa y la final usan la misma composición; solo cambia la calidad de las imágenes de entrada. La exportación es un MP4 1080x1920 a 30 fps.
- Se usan las skills locales de HyperFrames, no el conector alojado de HeyGen (ADR 0007). La versión de HyperFrames se fija.

### Revisión

- La herramienta saca de cualquier versión la hoja de contactos y la prueba de móvil, y comprueba la exportación final: 1080x1920, 30/1 y duración igual a la de la línea de tiempo, con un fotograma de margen.
- La crítica la hace el agente siguiendo la skill. Actúa como el director de animación más exigente, sobre las hojas y no sobre el vídeo. Revisa sombras de contacto, personajes iluminados como objetos 3D, planos de más de 3 s sin idea nueva, legibilidad en el móvil y datos en pantalla sin fuente. Arregla los 3 peores problemas y repite.
- **Orden de prioridad de los arreglos:** lo que está mal o falta, después la legibilidad, después el ritmo y por último el detalle visual.
- Toda corrección se redacta con cuatro campos: dónde (fotogramas), qué falla, qué cambia y qué no se toca.

### Paradas

- La skill se detiene y espera al creador:
  - en la parada 1 (guion, fuentes y CTA);
  - en la parada 2 (versión previa);
  - en la parada 3 (episodio final con su hoja de contactos);
  - y en cada escenario o personaje nuevo.
- Cada aprobación queda registrada en el estado del episodio.

### Publicación

- La herramienta genera la hoja de publicación:
  - el texto de la descripción, con el CTA y el enlace;
  - un enlace a la App con etiquetas de seguimiento distintas por plataforma (YouTube, TikTok, Instagram) y el episodio como campaña;
  - recordatorios: marcar el aviso de marca propia donde se pida, sin etiqueta de IA por defecto, subida manual.
- El enlace base sale de la documentación de la App.

### Configuración, secretos y coste

- Un único archivo de configuración del estudio:
  - proveedor y voz por personaje;
  - proveedores de música y efectos;
  - fps y tamaño;
  - estilos de subtítulos;
  - pausa entre frases.
- Las claves solo van en `.env`; en `.env.example` solo van los nombres. Ningún proveedor de pago se activa sin la confirmación del creador (compuerta humana).

### Reglas de la casa (en la skill del estudio)

- **Formato:** 1080x1920, 30 fps, 55-70 s; un plano por idea.
- **Aspecto:** personajes planos dentro de escenarios 3D con luz con motivo; materiales con desgaste; sombra de contacto.
- **Prohibido:**
  - un título centrado sobre un degradado;
  - etiquetas en las esquinas, códigos de tiempo o marcos;
  - que todo aparezca con un fundido;
  - un "whoosh" en cada corte;
  - cualquier dato en pantalla que no esté en las fuentes;
  - copiar personajes, diseños o guiones de otros canales.

## Decisiones de testing

- **Qué es un buen test aquí:** comprueba lo que se ve desde fuera, nunca cómo está hecho por dentro. Se da a la herramienta una carpeta de episodio de prueba y se comprueba qué archivos produce y qué errores o avisos da. Un test no debe romperse por reorganizar el código si el comportamiento no cambia.
- **Una sola costura** (el punto por el que se prueba): la herramienta del estudio ejecutada sobre una carpeta de episodio de prueba. Todos los tests automáticos entran por ahí. Usan el proveedor de voz falso, sin Blender, sin render de HyperFrames y sin red.
- **Qué se prueba automáticamente:**
  - comprobación del guion y las fuentes (cada error y cada aviso con su caso);
  - comprobación de la lista de planos;
  - cronometraje (frases, palabras, planos, CTA y total en fotogramas);
  - subtítulos (tarjetas de 2-3 palabras, inicio en el fotograma de la palabra, estilo por personaje);
  - composición de HyperFrames (que tenga las capas, los tiempos y los estilos esperados, sin comparar píxeles);
  - revisión (la comprobación de la exportación, contra un vídeo minúsculo generado con ffmpeg dentro del propio test, y que la hoja de contactos salga con el tamaño esperado);
  - hoja de publicación (enlaces con las etiquetas correctas por plataforma).
- **Qué no se prueba automáticamente:** la calidad de escenarios, personajes, actuación e imagen. Para eso están las hojas de vistas, la crítica del agente y las paradas del creador.
- **Prueba de humo en el PC** (a mano, fuera de los tests normales): un miniepisodio de dos frases con un escenario mínimo, recorriendo toda la cadena hasta el MP4 y su comprobación. Coincide con la prueba de humo de `DEBT_TECH.md`.
- **Precedentes:** ninguno. El repositorio aún no tiene código; los primeros tests marcan el patrón. Cada ticket se construye con tests primero (Fase 3).

## Fuera de alcance

- Subir o programar publicaciones automáticamente: lo hace el creador a mano.
- El nombre del canal, su imagen de marca, las miniaturas y el ritmo de publicación: se deciden después del piloto.
- Otros formatos (horizontales, largos, explicativos), otros idiomas y el doblaje. Solo queda preparada la separación en recetas.
- Una aplicación con pantallas propias (ADR 0006) y renderizar en la nube (ADR 0005).
- Integrar o contratar servicios de pago: solo se deja el enchufe listo.
- La skill de diálogo del creador (la aporta él) y la propia App, incluida su analítica: el estudio solo genera los enlaces con seguimiento.
- Clonar la voz de personas reales.
- Paneles automáticos de métricas: el repaso tras cada tanda se hace a mano con YouTube Studio y la analítica de la App.

## Notas

- **Bloqueos para empezar a construir:**
  - el PC de casa con las instalaciones de `DEBT_TECH.md`;
  - las aportaciones del creador: la skill de diálogo, un contenido para el piloto, las hojas de personaje del Tutor y del Perro, y la documentación de la App (nombre, enlace, logo, colores, funcionalidades).
- **Incertidumbres que hay que medir pronto:**
  - si las voces gratuitas en español convencen;
  - cuánto tarda en renderizar un escenario de naturaleza en la tarjeta gráfica del PC;
  - la madurez de HyperFrames (versión 0.9);
  - si `/hyperframes-media` cubre la voz y las marcas de tiempo.
- **Lo que se puede construir ya en la nube**, sin el PC: el formato del guion, la herramienta (comprobaciones, cronometraje, subtítulos, hoja de publicación) con sus tests, y la skill del estudio. Lo que necesita Blender, HyperFrames o voces reales espera al PC.
- **Primer hito:** episodio piloto de 55-70 s, 1080x1920, revisado y listo para subir, con el registro de horas por etapa.
