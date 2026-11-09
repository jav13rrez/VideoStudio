# Grafo: <nombre-corto-del-grafo>

> Generado por la skill `crear-grafo` el <fecha>. Fuente: <qué documentos del
> proyecto y qué indicaciones del usuario se usaron>.

## GOAL

<Objetivo final, en una frase verificable. Ej: "todas las rutas bajo src/routes/
están auditadas para comprobación de auth, y cada hallazgo confirmado por un
verificador independiente aparece en el informe con su archivo y línea".>

## CONTEXTO QUE TODO AGENTE DEBE LEER ANTES DE EMPEZAR

- <documento 1 del proyecto, p. ej. AGENTS.md o convenciones>
- <documento 2, p. ej. la spec o el ticket del que nace este grafo>
- <credenciales/accesos ya confirmados como disponibles, y dónde viven>

## SPLIT — enumeración de unidades

<Cómo se obtiene la lista exacta de unidades, de forma determinista.
Ej: "glob src/routes/**/*.ts", "los tickets #12-#19 sin dependencias entre sí",
"las 9 fuentes listadas abajo".>

## FAN OUT — contrato de nodo

- UN NODO = <una unidad: un archivo / una ruta / una fuente / un ticket>
- ENTRADA:  <lo que recibe cada agente, pasado explícitamente>
- TRABAJO:  <el único trabajo del nodo, sin ambigüedad>
- SALIDA:   <forma definida con campos concretos. Ej: { hallazgo, archivo,
  linea, severidad: alta|media|baja, evidencia }. Nunca texto libre.>
- MODELO:   <barato para trabajo repetitivo; anota cuál>
- AISLAMIENTO: <"worktree por agente" si los nodos escriben archivos;
  "no necesario, solo lectura" si no. Si comparten una API con rate limit,
  indica la concurrencia máxima.>

## REDUCE — solo código, sin agentes

<Qué se hace con las salidas antes de verificar: aplanar, deduplicar por
<clave>, filtrar <criterio>. Si el fan-out supera ~20-30 unidades: fan-in por
capas — lotes de <N>, resumen por lote, síntesis sobre resúmenes.>

## VERIFY — verificador con contexto limpio

- ENTRADA: solo el hallazgo (nunca el chat del worker).
- LENTES:  <1. ¿es correcto? 2. ¿es vigente/reproducible? 3. ¿la fuente/el
  archivo citado existe y dice eso?>
- ANCLA:   <la comprobación objetiva que no puede discutir. Ej: "el test se
  ejecuta y falla como el hallazgo predice", "el link resuelve", "la línea
  citada contiene el patrón".>
- PASA si: <mayoría de lentes lo mantiene / el ancla lo confirma>.
- MODELO:  <fuerte; anota cuál>

## DEDUPE

<Contra qué se deduplica: contra TODO lo visto (incluido lo rechazado), no solo
contra lo confirmado. Clave de dedupe: <campo(s)>.>

## CAP — doble límite

- Primera pasada: <N unidades, empezar en 10-20>.
- Límite duro total: <máx agentes / máx coste / máx tiempo>. Al alcanzarlo, el
  grafo para y reporta lo que tenga.

## SYNTHESIZE

<Qué produce el agente final, solo con los supervivientes del verify: formato
del informe, orden (por severidad/confianza), dónde se guarda.>

## REPORT — conteo obligatorio

- Declarar: "volvieron <X> de <Y> nodos lanzados; <Z> hallazgos descartados en
  verify". Si X < Y, avisar del hueco — nunca presentar un conjunto parcial
  como completo.

## COMPUERTAS HUMANAS (si aplica)

<Puntos donde el grafo se detiene a esperar aprobación humana explícita
(desplegar, publicar, borrar, enviar, gastar más del CAP). Si no hay ninguna,
escribe "Ninguna — el grafo es de solo lectura y termina en un informe".>

## ON STOP

<Qué hace el agente al terminar, con éxito o sin él: dónde queda el informe,
qué quedó sin cubrir, referencia cruzada en PROGRESS.md/tickets si existen.>

## CÓMO LANZARLO

```
Ejecuta este grafo: @grafos/<nombre>.md
```

Primera vez: con el CAP de primera pasada. Revisa el coste del run antes de
ensanchar.
