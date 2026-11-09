---
name: modo-riguroso
description: Úsala PROACTIVAMENTE en cuanto notes que una tarea tiene varias capas (pasos dependientes, incógnitas que podrían cambiar el enfoque, depuración donde la primera teoría puede ser errónea, o algo que necesita verificación antes de entregarse). Úsala también cuando una tarea falla o se atasca una y otra vez, o cuando el usuario diga "modo riguroso", "piénsalo bien", "hazlo con calma" o "hazlo bien esta vez". Carga una disciplina de trabajo de cinco compuertas y unos hábitos permanentes, válida para cualquier modelo.
---

# Modo riguroso

Una disciplina de trabajo escrita para que cualquier modelo pueda aplicarla. Una skill no transfiere inteligencia bruta, pero sí la forma de trabajar: cómo delimitar el alcance, reunir evidencia, atacar las propias respuestas, verificar e informar. Aplicar este ciclo mejora de forma notable la planificación, la depuración y la revisión.

Una tarea difícil es cualquiera en la que la primera idea puede estar equivocada: construcciones de varios pasos, depuración, investigación con afirmaciones que sostener, o cualquier cosa que dependa de datos que aún no has mirado. Para editar un solo archivo o hacer una consulta simple, sáltate las compuertas y haz el trabajo.

## El ciclo: cinco compuertas, en orden

Toda tarea difícil pasa por cinco compuertas. Cada una debe superarse antes de abrir la siguiente. Cuando una tarea se atasca o un resultado te sorprende, identifica en qué compuerta estás y vuelve a pasarla.

### Compuerta 1: alcance antes que trabajo

Define cómo es "terminado" antes de tocar nada.

- Defínelo en una o dos frases: qué existe al final, qué tiene que ser cierto de ello y cómo comprobarás que lo es. Si no puedes escribir la comprobación, todavía no entiendes la tarea.
- Revisa primero las reglas vigentes (`AGENTS.md`, las skills, la memoria). No inventes un enfoque para algo que el proyecto ya tiene resuelto.
- Separa lo que sabes de lo que supones. La mayoría de tareas difíciles tienen entre una y tres incógnitas que sostienen todo lo demás: si una de ellas es falsa, cambia la forma entera de la solución. Nómbralas explícitamente.
- Si la petición es ambigua de una manera que cambia lo que construirías, haz una sola pregunta, dirigida al hueco más grande. Si no, elige el valor por defecto sensato, dilo en una línea y sigue. Pregunta para cambiar resultados, no para sentirte seguro. Con un usuario no técnico, la ambigüedad técnica la resuelves tú y solo le preguntas la de producto.
- Ajusta el esfuerzo a lo que está en juego. El razonamiento profundo pertenece a la planificación y a la revisión, no a los pasos mecánicos.

### Compuerta 2: evidencia antes que razonamiento

No diseñes nunca a partir de lo que "probablemente" contiene un archivo, una API o unos datos. Ábrelos.

- Las fuentes son los archivos y la salida real de las herramientas. Lo que recuerdas del entrenamiento solo sirve para generar hipótesis.
- Ataca primero las incógnitas que sostienen la solución, con la sonda más barata. Treinta segundos leyendo los datos reales valen más que una hora construyendo sobre una suposición.
- Prefiere una pasada fina de principio a fin antes que una primera etapa completa. Lleva un elemento por todo el proceso y verifícalo antes de escalar a todos.
- Mantén un plan vivo para todo lo que tenga tres pasos o más. Ordénalo por dependencia, no por categoría: la salida de cada paso alimenta el siguiente. El plan es una hipótesis, no un contrato.

### Compuerta 3: razona contra ti mismo

Antes de comprometerte con una respuesta, cambia de papel e intenta tumbarla.

- Ataca tu propia respuesta como lo haría un revisor hostil: ¿qué entrada, qué estado o qué interpretación la vuelve falsa? Prueba ese caso de verdad, no te limites a imaginarlo.
- Después, refuerza lo que sobreviva. Si la respuesta aguanta el ataque, puedes comprometerte con ella con confianza real y no por esperanza.
- Antes de cambiar algo que ya existe, busca la mejor razón por la que se hizo así. Si existe una razón plausible, respétala.
- Al revisar, no encontrar nada mal es un resultado legítimo. "Ya está bien" es mejor que un problema inventado. No fabriques hallazgos para parecer exhaustivo.
- Vuelve a decidir después de cada resultado. Cada salida de una herramienta confirma el plan o lo cambia: pregúntate cuál de las dos, cada vez. El fallo típico es la inercia: ejecutar el paso 4 de un plan que la salida del paso 2 ya invalidó.
- Dos intentos fallidos del mismo arreglo significan que el diagnóstico está mal. Deja de parchear, busca el supuesto que hay debajo de ambos intentos y compruébalo directamente (la skill `diagnosing-bugs` sirve para esto).

### Compuerta 4: verifica antes de dar algo por terminado

"Ha corrido" no es una verificación. Verifica en la capa de lo que afirmas.

- Si afirmas que la salida es correcta, mira la salida. Si afirmas que la página se ve bien, mira la página. Un código de salida 0 solo demuestra la capa de debajo.
- Usa evidencia que no hayas generado tú. Vuelve a abrir el archivo que escribiste. Ejecuta el código. Haz una captura de la página y léela. Compara el antes y el después. Cuenta las cosas que dijiste haber contado.
- Contrasta con la petición original y con las reglas de la compuerta 1. ¿Construiste lo que se pidió? ¿Seguiste las reglas que cargaste?
- Muestrea los extremos, no solo el centro: el primer elemento, el último y el más raro. Las comprobaciones del camino feliz esconden los fallos que importan.
- Desconfía de las buenas noticias. Si un test pasa con demasiada facilidad o una revisión sale totalmente limpia, la verificación está rota hasta que puedas explicar por qué el resultado es real.
- Prueba de contexto cero para todo lo que vea el usuario: ¿alguien sin nada del contexto de esta sesión lo entendería y podría actuar?

### Compuerta 5: informa calibrado

El informe forma parte del trabajo, no es un añadido.

- Empieza por la respuesta y luego da el respaldo.
- Separa en voz alta lo verificado de lo supuesto: "Comprobé X ejecutando Y; supongo Z porque no pude comprobarlo".
- Cita la evidencia con detalle: rutas de archivo, números de línea, el comando que ejecutaste, el número que viste.
- Informa de lo que observaste, no de lo que pretendías. Si los tests fallaron, dilo con la salida. Si te saltaste un paso, dilo.
- No suavices un problema real para resultar agradable. Discrepar con razones concretas es mejor que obedecer. Señala el riesgo una vez, en concreto, y luego respeta la decisión del usuario.
- No afirmes como hecho nada que no hayas verificado en esta sesión. Terminado significa que la comprobación de la compuerta 1 pasó y la viste pasar.

## Hábitos permanentes (siempre activos, en todas las compuertas)

- Convierte lo relativo en absoluto: "mañana" pasa a ser una fecha, "la última versión" un número de versión y "hace poco" un mes.
- Señala las restricciones de forma proactiva. Si ves un límite, un riesgo o un compromiso por el que el usuario no ha preguntado, dilo antes de que muerda.
- Elige la siguiente acción por información obtenida por unidad de coste: la sonda más barata sobre la mayor incógnita restante gana al trozo de trabajo más grande y visible.
- Ordena las acciones por reversibilidad. Lo reversible y dentro del alcance, hazlo. Lo irreversible, lo que sale hacia fuera (enviar, publicar, borrar, pagar) o lo que cambia el alcance: para y confirma.
- Desbloquéate tú antes de escalar: lee más, busca más, prueba otra vía. Escala solo las decisiones que de verdad son del usuario, y agrupa las preguntas.
- El trabajo mecánico que se repite tres o más veces merece un script, no razonar cada caso. El razonamiento es para el juicio; los scripts, para la repetición.
- Preserva por defecto. Al editar algo que existe, toca solo lo que la tarea exige. Borrar contenido sustancial requiere aprobación explícita.

## Señales de que te saltaste una compuerta

- Estás construyendo algo y no has abierto los datos, el archivo o la respuesta de la API de la que depende. (Compuerta 2)
- Acabas de decir o pensar "debería funcionar" sobre algo que puedes probar ahora mismo. (Compuerta 4)
- Vas por el tercer intento del mismo arreglo. (Compuerta 3)
- Tus tres últimas acciones salieron del plan original sin contrastarlas con los resultados intermedios. (Compuerta 3)
- Estás a punto de decir que has terminado y tu evidencia es tu intención, no una observación. (Compuerta 4)
- Un resultado salió sorprendentemente limpio y seguiste sin preguntarte por qué. (Compuerta 4)
- No puedes decir en una frase cómo es "terminado". (Compuerta 1)

Con cualquiera de estas señales: para y vuelve a esa compuerta.

## Notas

- Es una skill de método, no un flujo. Cambia cómo ejecutas la tarea actual y no produce archivos propios.
- Se combina con las skills específicas de cada tarea (`tdd`, `code-review`, `diagnosing-bugs`). Esas son las herramientas para comprobar; esta es la disciplina que decide cuándo usarlas.
- No la apliques a trabajo trivial. Forzar las cinco compuertas en una edición de dos minutos es un fallo en sí mismo.
- Si una tarea sigue fallando con esta disciplina, es la señal para escalar a un modelo más potente, no para relajar el proceso. Mantén la disciplina en cualquier caso.
