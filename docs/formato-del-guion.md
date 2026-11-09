# Formato del guion y de las fuentes

El guion y las fuentes de cada episodio son dos archivos de texto dentro de la carpeta del episodio: `guion.md` y `fuentes.md`. El creador los puede leer tal cual, y la herramienta del estudio los comprueba. La salida de la skill de diálogo del creador se adapta a este formato (ver [spec](../.scratch/estudio-de-episodios/spec.md), "Guion y fuentes").

Hay un ejemplo completo en [`tests/episodios/001-olfato/`](../tests/episodios/001-olfato/).

## `guion.md`

Una frase por línea, en el orden en que se dicen:

```text
[marcas] Personaje: texto de la frase
```

```markdown
# Guion: por qué te huelo los zapatos

[gancho] Perro: ¿Sabes por qué te huelo los zapatos cuando vuelves a casa?
Tutor: ¿Porque huelen fatal?
Perro: Tengo hasta *trescientos millones* de receptores de olor. [fuente: nova]
…
[remate] Tutor: Pues a partir de hoy, tú marcas el ritmo y yo leo contigo.
[cta] Perro: Pídele a la App un plan de paseos hecho para tu perro.
```

- **Personaje**: solo `Perro` o `Tutor`, escritos así.
- **Marcas de frase**, delante del personaje y en minúsculas:
  - `[gancho]`: la primera frase.
  - `[remate]`: la última frase de la conversación.
  - `[cta]`: cada frase del CTA (1 o 2, siempre del Perro y siempre al final, justo después del remate).
- **Palabras acentuadas**: entre asteriscos, `*así*`. Si son varias seguidas, `*trescientos millones*`. Marcan dónde mueve la boca el Tutor y qué subtítulos se animan.
- **Marcas de fuente**: `[fuente: id]` dentro del texto, detrás del dato que se afirma. Una marca por fuente; si un dato tiene dos fuentes, dos marcas. El `id` es el de `fuentes.md`. Dentro del texto no puede ir ningún otro corchete.
- Las líneas que empiezan por `#` son títulos y las líneas en blanco se ignoran. Cualquier otra línea tiene que ser una frase.

Las marcas de fuente y los asteriscos no cuentan como palabras.

## `fuentes.md`

Una fuente por línea, como una lista de casillas:

```markdown
# Fuentes

- [x] nova: Receptores olfativos del perro frente a los de las personas. — PBS NOVA (2012). Dogs' Dazzling Sense of Smell.
- [ ] craven: El aire que exhala el perro sale por los lados de la nariz. — Craven, B. A. et al. (2010). Journal of the Royal Society Interface.
```

- `[x]` si el creador ya ha revisado la fuente; `[ ]` si no.
- `id`: letras, números, guiones o guiones bajos, sin espacios. Es lo que va en las marcas `[fuente: id]` del guion.
- Después de los dos puntos (obligatorio): qué dato respalda, una raya (`—`) y el enlace o la referencia.

Si el episodio no tiene `fuentes.md`, la herramienta lo trata como una lista vacía.

## Comprobarlo

```bash
uv run estudio comprobar-guion ruta/a/la/carpeta-del-episodio
```

**Errores**: el guion no puede pasar a la parada 1 hasta corregirlos. La orden termina entonces con código de salida 1, que es como un programa le dice al agente que algo ha fallado; sin errores, termina con 0.

- Habla un personaje que no es el Perro ni el Tutor.
- El CTA no va al final, o lo dice el Tutor.
- Una marca apunta a una fuente que no está en `fuentes.md`.
- Falta `guion.md` o no tiene frases, una línea no sigue el formato, hay una marca mal escrita o un asterisco de acento sin pareja.

**Avisos**: no impiden pasar, pero el creador los revisa en la parada 1.

- La conversación (sin el CTA) se sale de 150-170 palabras, lo que cabe en 55-70 segundos.
- El CTA pasa de unas 15 palabras (unos 5 segundos), o el guion no tiene CTA.
- La primera frase no lleva `[gancho]`, o la última de la conversación no lleva `[remate]`.
- Una fuente no la usa ninguna frase, o el creador no la ha revisado.

Detectar qué frases afirman datos es trabajo del agente; la herramienta solo comprueba que las marcas y las fuentes cuadran.

Con el guion aprobado, los siguientes pasos son la lista de planos ([lista-de-planos.md](lista-de-planos.md)) y las voces y la línea de tiempo ([voces-y-linea-de-tiempo.md](voces-y-linea-de-tiempo.md)).
