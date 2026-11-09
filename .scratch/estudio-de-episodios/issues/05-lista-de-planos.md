# 05: Lista de planos

**What to build:** Formato de la lista de planos (un plano por idea, con la palabra del guion en la que empieza, escenario, encuadre y movimiento de cámara con su motivo, personajes y gesto, objeto protagonista y sonido físico) y sus comprobaciones. La línea de tiempo coloca cada plano en el fotograma en que empieza su palabra, así que la duración de los planos nunca se escribe a mano.

**Blocked by:** 04 (Voces de prueba y cronometraje)

**Status:** done

- [x] El formato de la lista de planos está documentado.
- [x] Cada plano tiene inicio y final en fotogramas en la línea de tiempo, y empieza justo en su palabra.
- [x] Error si alguna frase del guion queda sin cubrir o si hay planos fuera de orden.
- [x] Error si un escenario no está en la biblioteca y no va marcado como nuevo.
- [x] Aviso por planos de menos de 45 o más de 90 fotogramas, y por más de 5 escenarios en el episodio.
- [x] Probado a través de la herramienta sobre carpetas de episodio de ejemplo.

## Comments

**2026-11-09, agente.** Hecho.

- La lista de planos es `planos.toml` en la carpeta del episodio. Formato: [docs/lista-de-planos.md](../../../docs/lista-de-planos.md).
- Se comprueba al cronometrar (`uv run estudio cronometrar <carpeta>`), y sus planos entran en `linea-de-tiempo.json` con `id`, `inicio` y `final`.
- Ejemplo completo: [tests/episodios/001-olfato/planos.toml](../../../tests/episodios/001-olfato/planos.toml), con 29 planos y 4 escenarios (uno nuevo).
- 39 casos de test en `tests/test_lista_de_planos.py`, todos a través de la herramienta.

Decidido por el agente, además de lo que pedía el ticket:

- **`empieza` copia las primeras palabras del plano** (`empieza = "Tengo hasta"`), en lugar de un número de línea y de palabra. Así se lee sin contar nada. No cuentan las mayúsculas, la puntuación, los asteriscos ni las marcas de fuente. Tiene que aparecer una sola vez en el guion.
- **Las comprobaciones van dentro de `cronometrar`**, sin orden nueva. La spec pone la lista de planos como entrada del cronometraje, y las duraciones solo se conocen con la línea de tiempo.
- **Sin `planos.toml` se puede cronometrar**: la línea de tiempo sale sin planos y la orden lo dice. Así los subtítulos (ticket 06) no esperan a la lista de planos.
- **Como los planos van seguidos, sin huecos, "frase sin cubrir" solo puede pasar al principio**: el primer plano tiene que empezar en la primera palabra del guion.
- **El primer plano empieza en el fotograma 0** aunque la voz tarde en arrancar, para que no quede imagen sin plano. Los demás empiezan justo en su palabra.
- **El último plano puede pasar de 90 fotogramas si empieza dentro del CTA.** La spec pide a la vez planos de 1,5-3 s, un CTA de unos 5 s y un último plano que muestre la App mientras el Perro dice el CTA. Si el creador prefiere que ese plano también avise, es cambiar una línea de `src/estudio/cronometraje.py`.
- **La biblioteca es la carpeta `biblioteca/` junto a `estudio.toml`**, y un escenario está en ella si existe `biblioteca/escenarios/<nombre>/`. Los escenarios nuevos se marcan una vez, en `escenarios_nuevos`, no plano a plano.
- **Errores de formato** para que nada se ignore en silencio: campos que faltan o que no existen (`camera` en lugar de `camara`), `id` repetido, `id` o escenario con espacios y campos vacíos. Se dan antes que las comprobaciones entre planos, para no encadenar errores.
- **Error si dos planos empiezan en la misma palabra**: el primero duraría cero fotogramas.

Pendiente, con su motivo:

- **La línea de tiempo solo lleva `id`, `inicio` y `final` de cada plano.** `leer_planos` (`src/estudio/planos.py`) da hoy el escenario de cada plano; los tickets que necesiten la cámara (18) o el sonido (16) los añaden a `Plano`.
- **`camara` es texto libre.** Que la cámara solo haga acercamientos lentos o desplazamientos con motivo lo comprueba el ticket 18.
- **Dos frases idénticas** (por ejemplo, dos "¡Exacto!") no se pueden distinguir con `empieza`, porque no cruza de una frase a otra. Si llega a pasar, se añade un campo opcional con la línea del guion.
- **Qué hay dentro de la carpeta de un escenario** (el archivo de Blender, texturas, hojas de vistas) lo decide el ticket 14.
