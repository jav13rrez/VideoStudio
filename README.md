# Plantilla de proyectos con IA

Un punto de partida para crear cualquier app o proyecto con código, trabajando con un agente de IA. **No hace falta saber programar**: el agente hace de equipo técnico, te guía paso a paso y solo te pregunta lo que de verdad te corresponde decidir (qué quieres construir, para quién y con qué presupuesto).

Funciona con Claude Code, Codex, Gemini CLI, Cursor, GitHub Copilot y otras herramientas de agentes, con cualquier modelo (Anthropic, OpenAI, Google…).

## Cómo empezar un proyecto nuevo

### 1. Crea tu proyecto desde la plantilla

En la página de este repositorio en GitHub, pulsa **Use this template** → **Create a new repository**, ponle nombre a tu proyecto y créalo. Luego ábrelo en tu herramienta de agentes (clónalo, o ábrelo directamente si tu herramienta trabaja en la nube).

### 2. Instalar las skills de Matt Pocock (una vez por ordenador)

La plantilla sigue la metodología de [Matt Pocock](https://github.com/mattpocock/skills). Sus skills se instalan una sola vez por ordenador, como plugin, y se actualizan solas. Elige **una sola** vía: si instalas por dos, tendrás cada skill dos veces.

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin install mattpocock-skills@claude-plugins-official
```

Se actualiza sola.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add mattpocock/skills
```

```bash
codex plugin add mattpocock-skills@mattpocock
```

Se actualiza sola al arrancar.

</details>

<details>
<summary><strong>GitHub Copilot</strong> (CLI y VS Code)</summary>

```bash
copilot plugin marketplace add mattpocock/skills
```

```bash
copilot plugin install mattpocock-skills@mattpocock
```

Después, una sola vez, añade esto a `~/.copilot/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "mattpocock": { "source": { "source": "github", "repo": "mattpocock/skills" }, "autoUpdate": true }
  }
}
```

En VS Code: ejecuta **Chat: Install Plugin From Source** e introduce `https://github.com/mattpocock/skills`. Se actualiza a diario.

</details>

<details>
<summary><strong>Gemini CLI</strong> (actualización manual)</summary>

```bash
gemini skills install https://github.com/mattpocock/skills.git --path skills/engineering
```

```bash
gemini skills install https://github.com/mattpocock/skills.git --path skills/productivity
```

Para actualizar, vuelve a ejecutar los dos comandos.

</details>

<details>
<summary><strong>Cursor y cualquier otra herramienta</strong> (actualización manual)</summary>

```bash
npx skills@latest add mattpocock/skills -a <herramienta>
```

Cambia `<herramienta>` por `cursor`, `opencode`, `windsurf`, `amp`, etc. (sin `-a`, te deja elegir). Para actualizar: `npx skills@latest update`.

</details>

**No hace falta ejecutar `/setup-matt-pocock-skills`**: esta plantilla ya viene configurada (tickets en archivos locales dentro de `.scratch/`).

Si tu herramienta tiene un chat y no sabes dónde escribir estos comandos, ábrela en tu proyecto y dile: *"Instala las skills de Matt Pocock siguiendo el README"*. El agente te guiará.

### 3. Saluda al agente

Abre tu proyecto en la herramienta y escribe algo como *"Hola, quiero empezar"*. El agente lee `PROGRESS.md`, ve que el proyecto está recién creado, te explica cómo vais a trabajar y te pide que le cuentes tu idea. A partir de ahí, al final de cada paso te dice cuál es el siguiente.

## Cómo se trabaja

Todo proyecto recorre el mismo camino. El agente lo conduce y te avisa en cada cambio de fase:

1. **Entender la idea.** El agente te entrevista hasta que los dos tenéis claro qué se construye. Tú respondes las preguntas de producto y él decide y te explica las técnicas.
2. **Planificar.** Si el trabajo es grande, se convierte en una spec (qué se construye y por qué) y en tickets pequeños.
3. **Construir.** Ticket a ticket, con tests automáticos y una revisión al final de cada uno.
4. **Enseñar.** El agente te muestra el resultado funcionando, no solo "está hecho".
5. **Aprender.** Al terminar, repasáis qué mejorar para la próxima vez.

Algunos pasos solo los puedes lanzar tú escribiendo un comando, por ejemplo `/to-spec`. Cuando toque, el agente te dirá exactamente qué escribir.

El agente **siempre te pedirá permiso** antes de publicar algo, borrar datos, gastar dinero, enviar mensajes en tu nombre o dar accesos. Las contraseñas y claves nunca se escriben en el chat: el agente te guía para guardarlas tú mismo en un archivo `.env` privado.

## Qué incluye

| Archivo o carpeta | Para qué sirve |
| --- | --- |
| `AGENTS.md` | Las instrucciones del agente: metodología, flujo, reglas. Es la única fuente de verdad. |
| `CLAUDE.md`, `GEMINI.md` | Redirigen a `AGENTS.md` para Claude Code y Gemini CLI. |
| `PROGRESS.md` | Dónde está el proyecto y cuál es el siguiente paso. |
| `docs/adr/` | Decisiones importantes y su porqué. Las 0001 a 0004 explican el diseño de esta plantilla. |
| `docs/agents/` | Configuración de las skills de Matt Pocock (ya hecha). |
| `.agents/skills/` | Skills propias de la plantilla (abajo). |
| `.claude/skills/` | Copia de las anteriores para Claude Code (`scripts/sincronizar-skills.sh` la mantiene). |

### Skills propias

| Skill | Para qué |
| --- | --- |
| `crear-loop` | Convierte una tarea repetitiva en un bucle que el agente ejecuta solo hasta que una comprobación automática pasa. |
| `crear-grafo` | Diseña una revisión en paralelo de muchas cosas independientes (auditar todas las páginas, todas las rutas…), con verificación independiente de cada hallazgo. |
| `modo-riguroso` | Disciplina de trabajo para tareas difíciles: delimitar, reunir evidencia, atacar la propia respuesta, verificar e informar con honestidad. |

No hace falta invocarlas: el agente las usa cuando tocan. También puedes pedirlas por su nombre.

## Para quien mantiene la plantilla

- Para que aparezca el botón **Use this template**, activa en GitHub **Settings → General → Template repository**.
- Si cambias una skill propia, edítala en `.agents/skills/` y ejecuta:

  ```bash
  bash scripts/sincronizar-skills.sh
  ```

- Para llevar las skills actualizadas a un proyecto ya creado, copia la carpeta `.agents/skills/` de la plantilla a ese proyecto y ejecuta allí el mismo script, o pídeselo al agente.

## Créditos

- Metodología y skills de ingeniería: [Matt Pocock, *Skills for Real Engineers*](https://github.com/mattpocock/skills) (MIT). Los archivos de `docs/agents/` están adaptados de su skill `setup-matt-pocock-skills`.
- Principios de comportamiento ("pensar antes de programar", "simplicidad primero", "cambios quirúrgicos", "ejecución guiada por objetivos"): [Karpathy-Inspired Guidelines](https://github.com/multica-ai/andrej-karpathy-skills) (MIT), a partir de las [observaciones de Andrej Karpathy](https://x.com/karpathy/status/2015883857489522876).
