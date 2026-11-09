# El agente decide lo técnico; el usuario decide el producto

La plantilla está pensada para personas sin conocimientos de desarrollo. La regla original de `grilling` (Matt Pocock) es "los hechos los busca el agente, las decisiones son del usuario", pero un usuario no técnico no puede juzgar decisiones técnicas (lenguaje, base de datos, arquitectura, cómo testear). Por eso el agente toma las decisiones técnicas por defecto, las explica en lenguaje llano y deja abierta la posibilidad de que el usuario las cambie. Al usuario solo se le preguntan las decisiones de producto, negocio y dinero, y las acciones irreversibles. Es una desviación deliberada del flujo de Matt.

## Opciones consideradas

- **Preguntarlo todo (Matt puro)**: rechazada. Bloquea al usuario con preguntas que no puede responder.
- **Decidirlo todo y solo informar**: rechazada. El usuario pierde el control del qué y el porqué.

## Consecuencias

- Las decisiones técnicas difíciles de revertir (stack, base de datos, proveedor de despliegue o de autenticación) quedan registradas como ADR, para que el usuario y los agentes futuros sepan por qué se eligieron.
- Las acciones irreversibles o que salen hacia fuera (publicar, borrar datos, pagar, enviar, dar accesos) siempre pasan por una **compuerta humana**.
