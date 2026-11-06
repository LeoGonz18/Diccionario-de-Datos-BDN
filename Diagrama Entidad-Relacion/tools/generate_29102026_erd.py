"""Build the Archify ERD candidate from the 29/10/2026 MySQL dump."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".archify" / "erd-respaldo-29102026-20261029-223217"
DATA = json.loads((OUT / "source-schema.json").read_text(encoding="utf-8"))
SQL = ROOT.parent / "Practica 03" / "backups" / "Respaldo_29102026.sql"

def count_insert_rows(sql):
    counts = collections.Counter()
    start_re = re.compile(r"INSERT INTO `([^`]+)`(?:\s*\([^)]*\))?\s+VALUES\s+", re.S)
    for match in start_re.finditer(sql):
        table, index = match.group(1), match.end()
        quote = escaped = False
        depth = rows = 0
        while index < len(sql):
            char = sql[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "'":
                    if index + 1 < len(sql) and sql[index + 1] == "'":
                        index += 1
                    else:
                        quote = False
            elif char == "'":
                quote = True
            elif char == "(":
                if depth == 0:
                    rows += 1
                depth += 1
            elif char == ")":
                depth -= 1
            elif char == ";" and depth == 0:
                break
            index += 1
        counts[table] += rows
    return counts

ROW_COUNTS = count_insert_rows(SQL.read_text(encoding="utf-8", errors="replace"))

groups = {
    "Identidad": ["tb_users", "tb_people", "tb_user_addresses", "tbd_user_payment_methods", "tbd_address_components", "tbd_users_wishlist_products", "tbd_cart_items", "tb_carts"],
    "Catálogo": ["tb_products", "tbc_categories", "tbd_products_categories", "tbd_products_users_providers"],
    "Operaciones": ["tb_orders", "tbd_order_items", "tb_payments", "tb_payment_methods", "tbc_payment_methods_types", "tb_payment_transaction", "tb_refunds", "tb_shipments", "tb_returns", "tbd_return_items", "tb_order_cancellations", "tbd_cancellation_items"],
    "Auditoría": ["tb_logs"],
}
positions = {name: (row, 0) for row, name in enumerate(groups["Operaciones"])}
for row, name in enumerate(groups["Identidad"]):
    positions[name] = (row, 1)
for row, name in enumerate(groups[next(k for k in groups if k.startswith("Cat"))]):
    positions[name] = (row, 2)
positions["tb_logs"] = (4, 2)
entities, relationships, cards = [], [], []

def text_units(value):
    return sum(2 if ord(char) >= 0x2E80 else 1 for char in value)

def required_width(attributes, label):
    roles_by_attribute = []
    for attribute in attributes:
        keys = attribute.get("key", [])
        roles_by_attribute.append({keys} if isinstance(keys, str) else set(keys))
    max_roles = max((len(roles) for roles in roles_by_attribute), default=0)
    key_width = max(30, max_roles * 22 + max(max_roles - 1, 0) * 3 - 2 + 5) if max_roles else 30
    max_text = max((
        text_units(attribute["name"]) * 11 * 0.6
        + (text_units(attribute.get("type", "")) * 10.5 * 0.6 + 8 if attribute.get("type") else 0)
        for attribute in attributes
    ), default=0)
    header_width = text_units(label) * 13 * 0.6 + 42
    return max(360, int(max(max_text + 24 + key_width, header_width) + 0.999))

for table in DATA["tables"]:
    row, col = positions[table["name"]]
    attributes = []
    for column in table["columns"]:
        roles = []
        if "PK" in column["keys"]:
            roles.append("pk")
        if any(key.startswith("FK ") for key in column["keys"]):
            roles.append("fk")
        if any(key.startswith("UNIQUE ") for key in column["keys"]):
            roles.append("uk")
        attribute = {"name": column["name"], "type": column["type"]}
        if roles:
            attribute["key"] = roles[0] if len(roles) == 1 else roles
        if column["references"]:
            attribute["references"] = column["references"][0]
        attributes.append(attribute)
    domain = next(name for name, members in groups.items() if table["name"] in members)
    row_count = ROW_COUNTS[table["name"]]
    label = f"{table['name']} · {row_count:,} filas".replace(",", " ")
    entities.append({
        "id": table["name"], "label": label, "tag": domain,
        "row": row, "col": col,
        "sublabel": f"{row_count:,} registros INSERT · {len(attributes)} columnas".replace(",", " "),
        "width": required_width(attributes, label), "attributes": attributes,
    })

    for fk in table["foreignKeys"]:
        if fk["selfReference"]:
            cards.append({"dot": "amber", "title": f"Relación autorreferente · {table['name']}", "items": [
                f"{fk['name']}: ({', '.join(fk['columns'])}) referencia ({', '.join(fk['targetColumns'])}); DELETE {fk['onDelete']}; UPDATE {fk['onUpdate']}."
            ]})
            continue
        target = next(item for item in DATA["tables"] if item["name"] == fk["target"])
        target_unique = fk["targetColumns"] == target["primaryKey"] or any(
            set(index["columns"]) == set(fk["targetColumns"]) and index["unique"] for index in target["indexes"]
        )
        source_unique = fk["columns"] == table["primaryKey"] or any(
            set(index["columns"]) == set(fk["columns"]) and index["unique"] for index in table["indexes"]
        )
        nullable = any(next(column for column in table["columns"] if column["name"] == name)["nullable"] for name in fk["columns"])
        relationships.append({
            "id": re.sub(r"[^A-Za-z0-9_-]", "_", fk["name"]),
            "from": table["name"], "to": fk["target"],
            "label": f"{fk['name']} · {', '.join(fk['columns'])} → {', '.join(fk['targetColumns'])}",
            "fromCardinality": "one" if source_unique else "many",
            "toCardinality": "one" if target_unique else "many",
            "fromOptional": nullable, "toOptional": False,
            "identifying": all(name in table["primaryKey"] for name in fk["columns"]),
        })
        if fk["name"] == "fk_payment_transaction_refund_payment":
            relationships[-1]["labelDy"] = 24

for table in DATA["tables"]:
    for fk in table["foreignKeys"]:
        source_unique = fk["columns"] == table["primaryKey"] or any(
            set(index["columns"]) == set(fk["columns"]) and index["unique"] for index in table["indexes"]
        )
        if not source_unique and any(name in table["primaryKey"] for name in fk["columns"]):
            cards.append({"dot": "amber", "title": f"Revisar unicidad · {table['name']}", "items": [
                f"La FK {fk['name']} comparte parte de la PK compuesta. La cardinalidad de origen depende de la combinación completa de columnas."
            ]})

cards.append({"dot": "violet", "title": "Convenciones", "items": [
    "PK: clave primaria; FK: clave foránea; UK: clave única.",
    "Cada relación muestra la cardinalidad en ambos extremos; el círculo indica participación opcional.",
]})
cards.append({"dot": "emerald", "title": "Conteos", "items": [
    "La cifra junto al nombre de cada tabla cuenta las tuplas INSERT encontradas en este respaldo.",
]})
cards.append({"dot": "cyan", "title": "Procedencia y alcance", "items": [
    f"Esquema leído de {DATA['source']} sin ejecutar instrucciones.",
    f"DDL declara {len(entities)} tablas, {sum(len(table['columns']) for table in DATA['tables'])} columnas y {len(relationships)} claves foráneas.",
    f"El respaldo contiene {len(DATA['views'])} vistas y {len(DATA['triggers'])} triggers; no se detectaron procedimientos, funciones ni eventos.",
    "Las relaciones dibujadas son FOREIGN KEY declaradas. Los nombres funcionales y el significado de negocio requieren confirmación cuando no se desprenden directamente del SQL.",
]})

candidate = {
    "schema_version": 1,
    "diagram_type": "erd",
    "meta": {
        "title": "Modelo de datos · respaldo db_test 29/10/2026",
        "locale": "es",
        "output": "Diagrama Entidad-Relacion/.archify/erd-respaldo-29102026-20261029-223217/modelo-db-test-29102026.html",
        "quality_profile": "standard",
        "views": [
            {"id": "commerce", "label": "Compras y pagos", "focus": ["tb_orders", "tbd_order_items", "tb_payments", "tb_payment_transaction", "tb_shipments", "tb_returns", "tb_order_cancellations"]},
            {"id": "catalog", "label": "Catálogo", "focus": ["tb_products", "tbc_categories", "tbd_products_categories", "tbd_products_users_providers"]},
            {"id": "identity", "label": "Usuarios", "focus": ["tb_users", "tb_people", "tb_user_addresses", "tb_carts", "tbd_users_wishlist_products"]},
            {"id": "audit", "label": "Auditoría", "focus": ["tb_logs"], "note": "Registro de actividad incluido en el respaldo."},
        ],
    },
    "layout": {"mode": "grid", "gapX": 110, "gapY": 50, "entityW": 360, "headerH": 54, "rowH": 24},
    "entities": entities,
    "relationships": relationships,
    "cards": cards,
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "candidate.json").write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{OUT / 'candidate.json'} · {len(entities)} entidades · {len(relationships)} relaciones")
