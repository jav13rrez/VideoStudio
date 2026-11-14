# Actuación

Antes de animar, cada plano lleva una línea de actuación en `actuacion.toml` (junto a `planos.toml` y `tomas.toml`). La escribe el agente y el creador la puede leer. `uv run estudio renderizar-planos` no renderiza un plano sin su línea.

```toml
[[plano]]
id = "08"                                   # el plano al que corresponde
pensamiento = "El Perro cuenta algo serio."  # qué piensa el personaje
anticipacion = "Mira al Tutor antes de levantar las orejas."
accion = "Levanta las orejas."
pausa = "Quieto mientras el Tutor se inclina."
gestos = [{ pieza = "perro_sentado_frente", parte = "orejas", inicio = 6, angulo = 15 }]   # opcional
parpadeos = [24, 120]                       # opcional, solo en el dibujo 2D
```

Las cuatro frases son obligatorias. Los `gestos` son solo del Perro: `parte` es `orejas` o `cola` (la boca del Perro no se mueve nunca), `inicio` es el fotograma del plano en que empieza y `angulo`, en grados (hasta 30), a dónde llega. Con el dibujo 2D, `pieza` es el nombre de la pose del reparto (`perro_de_pie`) y las orejas y la cola son las zonas de su ficha ([dibujo-2d.md](dibujo-2d.md)); `parpadeos` son los fotogramas del plano en que empieza cada parpadeo (dura 6 y no se pisan; Blender lo rechaza). Las orejas y la cola de Blender están en `perro_sentado_frente` (orejas) y `perro_sentado_perfil` (orejas y cola); las poses de pie no los tienen.

## Qué hace la herramienta

- **Tutor:** su boca se abre solo en las palabras acentuadas (`*así*` en el guion) que dice él, con los fotogramas de la línea de tiempo; alterna `abierta_grande` y `abierta_pequena` cada 3 fotogramas y, fuera de esas palabras, vuelve a la boca de la toma (`boca`, o `cerrada`). No hay que escribirla.
- **Perro:** cada gesto dura 36 fotogramas: 6 de anticipación (tira un cuarto del ángulo hacia el otro lado), 8 de acción, 10 manteniendo y 12 de vuelta al reposo suavizada y sin pasarse, así que no rebota. Dos gestos de la misma parte no pueden pisarse, y cada uno tiene que caber en el plano.
- Un plano de cámara fija cuyos personajes se mueven deja ahora un vídeo (`planos/<id>.mp4`) en lugar de una imagen. Con la cámara quieta, Blender renderiza una sola vez cada combinación distinta de personajes y copia el resto.

## Lo que todavía no hace

- «Cada gesto empieza con una mirada» está en la línea escrita (`anticipacion`), pero no se anima: el Perro solo tiene ojos abiertos o cerrados y no hay cabeza suelta que girar.
- El Tutor solo mueve la boca. Los ojos son los de la toma.
