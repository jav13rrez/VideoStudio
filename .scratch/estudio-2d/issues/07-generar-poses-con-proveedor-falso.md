# 07 — `generar-poses` con proveedor falso y confirmación

Spec: [estudio-2d](../spec.md).

**What to build:** una orden para generar las ilustraciones de pose a partir de las hojas de personaje del creador. Recibe el personaje y la pose, lee la hoja, comprueba que trae la vista que necesita la pose y construye el texto con una plantilla fija del estilo de la casa (plano, contorno uniforme, dos tonos). Antes de gastar muestra cuántas imágenes va a generar y cuánto costarían, y no genera nada sin una confirmación explícita. Después deja las ilustraciones y anota en la ficha qué modelo las hizo, con qué texto y cuándo. Hay un proveedor `falso` que genera ilustraciones de prueba sin gastar; los tests solo usan ese.

**Blocked by:** 01 — Un plano fijo en 2D.

**Status:** ready-for-agent

- [x] `generar-poses` recibe un personaje y una pose y construye el texto con una plantilla fija del estilo de la casa.
- [x] Antes de generar muestra cuántas imágenes y cuánto costarían, y no hace nada sin una confirmación explícita.
- [x] Deja las ilustraciones y anota en la ficha el modelo, el texto y la fecha (formato AAAA-MM-DD).
- [x] Avisa antes de generar si a la hoja le falta la vista que necesita la pose.
- [x] El proveedor `falso` genera ilustraciones de prueba sin gastar y sin clave.
- [x] La clave del proveedor real se lee solo de `.env` y no se escribe nunca en pantalla ni en archivos.
- [x] Los tests usan solo el proveedor falso y comprueban todo lo anterior.
