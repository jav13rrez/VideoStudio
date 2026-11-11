# 01: Aportaciones del creador

**What to build:** El creador deja en el proyecto lo que solo él puede dar: su skill de diálogo (la que convierte el contenido en una conversación Perro–Tutor), un contenido para el episodio piloto, las hojas de personaje del Tutor y del Perro, y la documentación de la App (nombre, enlace, logo, colores y funcionalidades para tutores y para educadores caninos). El agente lo revisa todo y señala lo que falte.

**Blocked by:** None (can start immediately)

**Status:** ready-for-human

- [x] La skill de diálogo está en el proyecto y el agente la ha leído y ha resumido su formato de salida.
- [x] Hay un contenido para el piloto en su sitio.
- [ ] Las hojas de personaje traen vistas (frente, tres cuartos y perfil) y juegos de ojos y bocas, o el agente ha listado lo que falta.
- [ ] La documentación de la App tiene nombre, enlace, logo, colores y la lista de funcionalidades, separadas para tutores y para educadores caninos.
- [ ] Los puntos de "Pendiente de aportar por el usuario" de `DEBT_TECH.md` están marcados.

## Comments

**2026-11-09, agente (desde el ticket 07).** La documentación de la App va en una carpeta `app/` junto a `estudio.toml`, en la raíz del proyecto. El creador deja ahí el logo (PNG o SVG) y lo demás. El agente escribe `app/app.toml` con el nombre y el archivo del logo (`nombre = "…"` y `logo = "logo.png"`). Mientras no esté, el cierre del CTA de los episodios lleva un marcador. Ver "El cierre del CTA" en `docs/montaje.md`.

**2026-11-11, agente.** El creador aportó dos skills de diálogo (divulgación científica y estilo Caserza, en `C:\Users\Usuario\Documents\VideoStudio\skills-de-dialogo\`). Decidió fusionarlas en una: `.agents/skills/dialogo-perro-tutor/`, que escribe directamente `guion.md`, `fuentes.md` y `acotaciones.md`, con el estilo Caserza como una dinámica más entre cinco. Las transcripciones de Caserza no entran en el proyecto (el repositorio es público y son contenido de otra persona); la skill describe sus técnicas con palabras propias.
