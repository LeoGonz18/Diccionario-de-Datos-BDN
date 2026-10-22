# Atlas · Documentación del esquema

Atlas es una aplicación estática que documenta el esquema de `db_test` desde `Practica 03/backups/Respaldo_20102026.sql`. No ejecuta el respaldo ni consulta el servidor MySQL. `schema-docs.json` y `schema-docs.js` se generan leyendo las definiciones SQL con `python tools/analyze_schema.py`.

## Abrir la aplicación

Desde la carpeta del proyecto, ejecuta `python -m http.server 8000` y abre `http://localhost:8000`. El servidor solo entrega archivos estáticos. No es necesario instalar dependencias.

## Contenido

- Navegación y búsqueda de tablas y columnas, filtros y fichas de detalle.
- Tipos, nulabilidad, valores predeterminados, `AUTO_INCREMENT`, claves, índices y referencias extraídas del DDL.
- Notación formal, dominios técnicos y naturaleza inferida con etiquetas de confianza.
- Relaciones declaradas con acciones referenciales y datos de tablas intermedias.
- Resumen de vistas, triggers, procedimientos, funciones y eventos detectados.
- Presentación adaptable, tema oscuro y respeto a `prefers-reduced-motion`.

Las descripciones funcionales son interpretaciones de nombres, tipos y relaciones; no sustituyen documentación de negocio no presente en el respaldo. Los dominios de negocio, cardinalidades inversas y reglas condicionales no demostrables se señalan como pendientes de confirmar.
