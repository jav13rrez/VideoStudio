# Crear un episodio y seguir su estado

Cada episodio vive en su propia carpeta, con número y nombre corto (`001-olfato`). La carpeta lleva el estado del episodio: en qué paso está, qué ha aprobado el creador y cuándo, qué escenarios o personajes nuevos esperan su aprobación y cuántas horas lleva cada etapa. Con eso se retoma el episodio otro día, en una conversación nueva, sin explicar nada. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Carpeta de episodio" y "Paradas".

## Crear un episodio

```bash
uv run estudio crear-episodio episodios/paseo
```

Crea `episodios/002-paseo` si la última carpeta numerada de `episodios/` es la `001-…`. El número es el siguiente al más alto de las carpetas que empiezan por tres cifras y un guion; las demás carpetas no cuentan. Si no hay ninguna, empieza en `001`. El nombre corto va en minúsculas sin tildes, con números y guiones, sin espacios y sin número delante: el número lo pone la herramienta.

La carpeta nueva lleva:

| Archivo | Qué es |
| --- | --- |
| `contenido.md` | Donde el creador deja el tema y la información del episodio, con sus palabras. |
| `guion.md` | El guion, vacío; lo escribe el agente ([formato-del-guion.md](formato-del-guion.md)). |
| `fuentes.md` | Las fuentes, vacías; las escribe el agente o las aporta el creador. |
| `estado.toml` | El estado del episodio, sin nada aprobado. |

El resto (`planos.toml`, `sonido.toml`, las voces, las versiones, las hojas de revisión, la exportación y la hoja de publicación) aparece cuando lo escribe el agente o lo genera su orden.

La configuración del estudio (`estudio.toml`) se busca subiendo desde la carpeta del episodio, así que la carpeta de episodios tiene que estar dentro del estudio: si no encuentra un `estudio.toml` por encima, la herramienta no crea el episodio.

## Ver el estado

```bash
uv run estudio estado episodios/002-paseo
```

Dice, en lenguaje llano:

- **Paso**: en cuál de los cuatro está el episodio. El paso no se guarda: sale de las paradas aprobadas.
  1. El guion. Espera la parada 1: el guion, las fuentes y el CTA.
  2. La lista de planos, los escenarios y personajes, las voces y la versión previa. Espera la parada 2: el ritmo de la versión previa.
  3. El render y el montaje final. Espera la parada 3: el episodio final con su hoja de contactos.
  4. La exportación y la publicación. No hay más paradas: se comprueba la exportación, se saca la hoja de publicación y el creador lo sube a mano.
- **Esperando**: la parada siguiente y, si quedan escenarios o personajes nuevos por aprobar, también ellos.
- **Paradas aprobadas**, cada una con su fecha.
- **Escenarios nuevos por aprobar**: los de `escenarios_nuevos` de `planos.toml` que el creador aún no ha aprobado.
- **Personajes nuevos por aprobar**: los personajes que salen en `planos.toml` y que no tienen carpeta en `biblioteca/personajes/<nombre>/` ni están aprobados. Igual que con los escenarios, un personaje está en la biblioteca si existe su carpeta.
- **Escenarios y personajes aprobados**, cada uno con su fecha.
- **Horas por etapa** y el **total**.

Sin lista de planos no hay escenarios ni personajes que esperen. Un episodio sin `estado.toml` (como el de ejemplo de los tests) es un episodio sin nada aprobado.

## Anotar una aprobación

Cuando el creador aprueba algo, el agente lo anota con la fecha de hoy:

```bash
uv run estudio aprobar episodios/002-paseo parada 1
uv run estudio aprobar episodios/002-paseo escenario parque
uv run estudio aprobar episodios/002-paseo personaje Tutor
```

- Las paradas son la 1, la 2 y la 3, y van en orden: no se aprueba la 2 sin la 1.
- Solo se aprueban los escenarios y personajes que esperan aprobación (los de la lista de arriba).
- Aprobar otra vez lo mismo no cambia la fecha de la primera vez; la herramienta lo avisa.

## Registrar las horas

```bash
uv run estudio registrar-horas episodios/002-paseo guion 1,5
```

Suma las horas a las que ya tenía la etapa (vale `1,5` y `1.5`). Las etapas son `guion`, `escenarios`, `personajes`, `animacion`, `voces`, `sonido` y `revision`. Las horas tienen que ser un número mayor que cero.

## `estado.toml`

Lo escribe la herramienta; no se edita a mano. Si alguien lo estropea (también si las paradas aprobadas no van en orden), las órdenes dicen que no lo entienden y no lo sobrescriben: se recupera con git.

```toml
# Estado del episodio. Lo escribe la herramienta del estudio: no lo edites a mano.

[paradas]
"1" = 2026-11-11

[escenarios]
"parque" = 2026-11-11

[personajes]
"Tutor" = 2026-11-11

[horas]
"guion" = 1.5
"voces" = 2.0
```
