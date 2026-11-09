---
name: crear-grafo
description: >-
  Diseña y redacta "grafos" (fan-out paralelo → reduce en código → verificación
  independiente → síntesis; el patrón diamante) para trabajo ancho, apoyándose en los
  documentos de flujo del proyecto (AGENTS.md, PROGRESS.md, specs y tickets) y en lo que
  indique el usuario. Usar cuando el usuario pida "crea un grafo", "paraleliza esto",
  "audita todos los X", "revisa cada archivo/ruta/página", "lanza varios agentes a la
  vez", o cuando una tarea contenga 2 o más trabajos independientes sin arista real de
  datos entre ellos. Si la tarea es iterativa sobre un solo frente (repetir hasta que un
  test pase), usar crear-loop en su lugar; si es puntual y acotada, no usar ninguna de
  las dos; si lo que se quiere es implementar en paralelo los tickets de una spec, eso
  es /implement-spec, no un grafo. El usuario puede no tener experiencia técnica: la
  skill resuelve los detalles por él y solo pregunta lo estrictamente necesario antes de
  dar el grafo por terminado.
---

# Crear Grafo

Un grafo no es "muchos agentes". Es: **trabajo ancho demostrado (fake-edge test)
+ contrato por nodo + verificador con contexto limpio + límite de coste**. Esta
skill no ejecuta el grafo — produce su especificación (un GRAPH SPEC listo para
lanzar) y confirma con el usuario todo lo que un agente no podría resolver solo
a mitad de la ejecución.

Fundamento (no lo repitas al usuario salvo que pregunte "por qué así"): el
patrón es el **diamante** — split → fan out → reduce → verify → synthesize. El
fan-out compra anchura; el reduce es código, no un agente; el verificador nunca
comparte contexto con el que hizo el trabajo; la síntesis solo ve lo que
sobrevivió. Un grafo compra anchura, **no** compra mejor juicio: si el trabajo
no es ancho, el grafo solo multiplica coste.

## Proceso

### 0. Descubrir el contexto del proyecto actual

Igual que en [[crear-loop]]: antes de preguntar nada, lee lo que ya existe en el
directorio de trabajo (y la raíz del repo si es distinta):

- `AGENTS.md` (y `CLAUDE.md`/`GEMINI.md` si añaden algo) — reglas del proyecto.
- `PROGRESS.md` — fase actual, trabajo en curso, pendientes.
- **Specs y tickets** en el gestor configurado en `docs/agents/issue-tracker.md`
  (por defecto `.scratch/`): sus listas de archivos, rutas o páginas afectadas son
  candidatas naturales a unidades de un grafo. Ojo: si lo que se quiere es
  *implementar* en paralelo los tickets que no se bloquean entre sí, eso ya lo
  hace `/implement-spec` (la lanza el usuario escribiéndola): díselo y no diseñes
  un grafo para eso. Esta skill es para trabajo ancho de revisión, auditoría o
  verificación.
- `README.md`, `package.json` / `pyproject.toml` / etc. — cómo se testea, lintea
  y compila aquí: de ahí saldrán las **anclas** del VERIFY.

Si no encuentras nada de esto, dilo y sigue con lo que aporte el usuario.

### 1. Determinar el trabajo ancho

**Si el usuario ya describe la tarea** ("audita todas las rutas del API"), pasa
directamente al filtro del punto 2.

**Si es vago** ("paraleliza algo", "qué grafos puedo montar aquí"): extrae de los
documentos del proyecto los pendientes que sean *enumerables* — listas de
archivos, rutas, páginas, dependencias, tickets sin dependencias entre sí — y
preséntale, con preguntas cerradas y tu recomendación primero (con `AskUserQuestion` si tu herramienta la tiene; si no, en texto con opciones numeradas), los 2-4 mejores candidatos que sobrevivan el
filtro del punto 2, cada uno en una frase ("qué se revisa en paralelo" + "cómo
se verifica cada hallazgo"). Si ningún pendiente es ancho, dilo: probablemente
lo que necesita es un loop ([[crear-loop]]) o trabajo directo, no un grafo.

### 2. Filtro fake-edge — "¿esto merece ser un grafo?"

La prueba central: recorre la tarea paso a paso y pregunta en cada transición
**¿este paso lee la salida del anterior?** Si sí, la arista es real y el orden
se respeta. Si no, no hay arista: esos trabajos pueden correr a la vez.

Condiciones para seguir (si falla alguna, dilo explícitamente y redirige — a
`crear-loop` si es iterativo, a trabajo normal si es puntual; ofrece igualmente
"aun así, quiero el grafo" si el usuario insiste):

- Hay **2 o más unidades de trabajo sin arista real** entre ellas (archivos,
  rutas, fuentes, tickets independientes). Si no encuentras dos trabajos sin
  arista, no hay grafo que construir.
- Cada hallazgo individual se puede **verificar automáticamente o con un
  criterio objetivo** (el link resuelve, el test corre, la regla se cumple). Si
  nada puede reprobar un hallazgo, el grafo solo producirá volumen, no verdad.
- El trabajo es de **anchura, no de juicio**: explorar N cosas a la vez, no
  decidir mejor una cosa. Para decidir mejor, un solo agente fuerte gana.
- El usuario acepta el **coste**: un grafo gasta más que un chat normal — la
  coordinación es lo que sale gratis, el trabajo de cada agente no.
- No es trabajo exploratorio que el usuario quiera dirigir paso a paso: el
  grafo corre ancho *sin* él; una correa corta lo anula.

### 3. Dibujar el diamante

Con el trabajo validado, define las cinco piezas. Cada una tiene una regla no
negociable:

1. **SPLIT** — cómo se enumeran las unidades. Debe ser una enumeración
   determinista (un glob, una lista de tickets, una query), no "el agente
   decide qué mirar".
2. **FAN OUT** — un agente por unidad, con **contrato de nodo**: entrada
   acotada pasada explícitamente (nunca asumida de un contexto compartido), un
   solo trabajo, y salida con forma definida (campos concretos; cada hallazgo
   con su fuente/ubicación). Un nodo cuya salida es texto libre es un nodo que
   solo un humano puede leer — no se puede cablear.
3. **REDUCE** — aplanar, deduplicar, filtrar: **código, no agente**. Si
   "combinar resultados" significa juntar listas y quitar duplicados, eso no
   gasta tokens. Reserva agentes para el juicio, no para la fontanería.
4. **VERIFY** — un verificador **con contexto limpio** por hallazgo (o por
   lote): no ha visto el trabajo que juzga, recibe solo el hallazgo, e intenta
   matarlo. Si sobrevive, pasa; si no, muere ahí. Con presupuesto, usa lentes
   diversas (¿es correcto? ¿es vigente? ¿la fuente existe?) — tres lentes
   distintas cazan lo que diez idénticas no ven.
5. **SYNTHESIZE** — un solo agente escribe la respuesta final **solo con lo que
   sobrevivió**, ordenado por confianza/severidad.

### 4. Barrido de riesgos — la parte que NO se puede saltar

Los tres fallos clásicos de un grafo, y su mitigación obligatoria en el spec:

- **Falsa independencia**: dos nodos parecen independientes pero escriben el
  mismo archivo o golpean la misma API con rate limit. Regla: dos nodos que
  escriben el mismo recurso necesitan una arista, no paralelismo. Si los nodos
  escriben archivos en paralelo, exige **aislamiento por worktree**; si
  comparten una API limitada, baja la concurrencia. Audita recursos
  compartidos, no solo datos compartidos.
- **Colapso de contexto**: N salidas crudas no caben en la síntesis final. Si
  el fan-out supera ~20-30 unidades, impón **fan-in por capas**: lotes →
  resumen por lote → síntesis sobre resúmenes, nunca sobre la pila cruda.
- **Fallo silencioso**: un nodo muere y el informe parece completo. Regla: todo
  merge **cuenta los resultados recibidos contra los esperados** y declara el
  hueco ("volvieron 17 de 20") — nunca sintetizar sobre un conjunto parcial
  llamándolo completo. Diseña cada fan-in para tolerar entradas ausentes.

Y el barrido genérico, igual que en crear-loop: credenciales y accesos que el
agente necesitará (compruébalos, no los supongas), decisiones de negocio que no
se derivan del código (se resuelven ahora o se declaran compuerta humana), y
aprobaciones obligatorias (desplegar, publicar, borrar, enviar — SIEMPRE
compuerta humana explícita, nunca decisión del agente). Si hay algo bloqueante,
**para y pregunta** antes de redactar; la especificación final no lleva ningún
"TODO: pedir luego".

### 5. Redactar el GRAPH SPEC

Usa la plantilla [templates/graph-spec-template.md](templates/graph-spec-template.md).
Puntos no negociables:

- **CAP doble**: límite de unidades en la primera pasada (empieza pequeño:
  10-20) y límite duro de agentes/coste total. La primera pasada barata es la
  que decide si se ensancha.
- **VERIFY con ancla**: la comprobación final se apoya en algo que no puede
  discutir — un test que corrió, un build que compiló, un link que resuelve.
  Nunca "el agente confirma que está bien": un modelo que califica su propio
  trabajo es demasiado blando consigo mismo.
- **MODELOS por nivel**: nodos repetitivos del fan-out en modelo barato; verify
  y synthesize en modelo fuerte. Es la palanca que abarata el grafo sin tocar
  su forma.
- **REPORT con conteo**: el informe final declara cuántos nodos volvieron de
  cuántos lanzados, y qué se descartó en verify.
- Cada nodo debe quedar redactado de forma que un agente que nunca ha hablado
  contigo pueda ejecutarlo solo con el spec y los documentos del proyecto.

### 6. Guardar y explicar cómo lanzarlo

- Guarda el spec en `grafos/<nombre>.md` (crea la carpeta si no existe), junto
  al código y versionado.
- Añade una línea en `PROGRESS.md` (sección "Trabajo en curso") que enlace al
  grafo, y en el ticket del que nace, si lo hay.
- Explica al usuario, en lenguaje simple, cómo arrancarlo: abrir su herramienta de
  agentes en el proyecto y pedir literalmente **"Ejecuta este grafo: @grafos/<nombre>.md"**
  — el agente lanza los subagentes en paralelo siguiendo el spec (con worktrees
  si el spec lo exige) y entrega un solo informe. Si su instalación soporta
  workflows dinámicos (prompts que empiezan por "workflow"), el mismo spec
  sirve tal cual; no dependas de esa función sin comprobarla.
- Recomienda siempre la primera pasada con el CAP bajo, revisar el coste, y
  solo entonces ensanchar.

### 7. Cierre

Resume en 3-4 líneas, sin jerga: qué revisará el grafo y en cuántas unidades,
cómo se verifica cada hallazgo, cuánto puede costar como máximo (el CAP), y qué
compuertas humanas quedaron. Pregunta si quiere lanzarlo ya o ajustar antes.

## Reglas invariables

- El que hace el trabajo **nunca** verifica el trabajo. Worker y verificador no
  comparten contexto jamás — un verificador que vio el chat del worker no está
  comprobando nada, está asintiendo con otra letra.
- Sin fake-edge test no hay grafo: si no encuentras dos trabajos sin arista
  real, redirige a `crear-loop` o a trabajo directo. No grafiques por moda.
- Todo spec lleva CAP doble (primera pasada + total). Un grafo sin límite es
  una factura sin límite.
- Todo merge cuenta sus entradas contra las esperadas y declara el hueco.
- El reduce es código; los agentes son para el juicio.
- Nunca inventes que una credencial o acceso existe: compruébalo, y si falta,
  pregunta antes de seguir.
- Prioriza encajar en los documentos de flujo que el proyecto ya tiene
  (`PROGRESS.md`, specs y tickets) en vez de crear un sistema paralelo.
