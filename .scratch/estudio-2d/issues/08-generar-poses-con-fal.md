# 08 — `generar-poses` con Fal de verdad

Spec: [estudio-2d](../spec.md).

**What to build:** el proveedor `fal` para `generar-poses`, con un modelo de edición de imagen. Cuando la hoja no trae la cabeza de la pose (el Tutor de pie, de perfil), usa como segunda referencia la cabeza ya ilustrada de otra pose. Valida lo que sale: avisa si la ilustración viene sin cabeza, sin cola o con un fondo que no se puede recortar, para repetirla antes de seguir. Generar de verdad gasta dinero, así que pasa siempre por la confirmación del creador al ejecutarlo.

**Blocked by:** 07 — `generar-poses` con proveedor falso y confirmación.

**Status:** ready-for-agent. La ejecución real contra Fal es una compuerta humana: el agente no la lanza sin la confirmación explícita del creador.

- [ ] El proveedor `fal` genera una ilustración a partir de la hoja, leyendo la clave solo de `.env`.
- [ ] Si la hoja no trae la cabeza de la pose, usa como segunda referencia la cabeza ya ilustrada de otra pose.
- [ ] Valida cada ilustración generada y avisa si falta la cabeza o la cola, o si el fondo no se puede recortar.
- [ ] Muestra el coste estimado antes de gastar y exige la confirmación del creador para generar de verdad.
- [ ] El código se prueba con el proveedor falso; una generación real se hace una vez, con el visto bueno del creador, y se anota lo que costó.
