# J.A.R.V.I.S. · Diccionario de datos

Aplicación estática para explorar el esquema de `db_test` extraído de `Practica 03/backups/Respaldo_29102026.sql`. La interfaz toma referencias visuales de las pantallas HUD de J.A.R.V.I.S.: fondo azul noche, trazos cian, acentos ámbar y un núcleo gráfico animado. No ejecuta el SQL ni requiere conexión a MySQL.

## Abrir

Desde esta carpeta, ejecuta `python -m http.server 8000` y abre `http://localhost:8000`. También puedes abrir `index.html` directamente.

## Contenido

- 25 tablas y 243 columnas, con tipos, nulabilidad, defaults, claves, índices y referencias del DDL.
- Búsqueda de tablas y columnas, navegación, filtros, detalles técnicos, semántica inferida y notación formal.
- Descripción contextual de cada columna, derivada de su tabla, sus claves, referencias y dominios ENUM; las reglas que el respaldo no define se señalan como inferencias o pendientes de confirmar.
- Relaciones declaradas, acciones referenciales y resumen de vistas, triggers y otros objetos SQL.
- Mapa de dependencias con selector MAP/LIST, resaltado de conexiones y acceso directo a la ficha de una tabla.
- Tema oscuro inspirado en J.A.R.V.I.S. y alternancia a tema claro.

Las descripciones de negocio no presentes en el respaldo se indican como inferencias y requieren confirmación con documentación del dominio.
