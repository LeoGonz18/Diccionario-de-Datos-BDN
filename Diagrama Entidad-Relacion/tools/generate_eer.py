#!/usr/bin/env python3
"""Build an Archify ERD candidate from the checked-in MySQL dump."""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SQL = WORKSPACE / "Practica 03" / "backups" / "Respaldo_14102026.sql"
OUT = ROOT / ".archify" / "erd-respaldo-14102026-20261014-174859" / "candidate.json"


def count_insert_rows(sql: str) -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    start_re = re.compile(r"INSERT INTO `([^`]+)`(?:\s*\([^)]*\))?\s+VALUES\s+", re.S)
    for match in start_re.finditer(sql):
        table, i = match.group(1), match.end()
        quote = escaped = False
        depth = rows = 0
        while i < len(sql):
            char = sql[i]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "'":
                    if i + 1 < len(sql) and sql[i + 1] == "'":
                        i += 1
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
            i += 1
        counts[table] += rows
    return counts


def split_columns(text: str) -> list[str]:
    """Split a comma-delimited SQL expression without splitting nested syntax."""
    parts, start, depth, quote, escaped = [], 0, 0, None, False
    for i, char in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    parts.append(text[start:].strip())
    return parts


def main() -> None:
    sql = SQL.read_text(encoding="utf-8", errors="replace")
    counts = count_insert_rows(sql)
    blocks = re.findall(r"CREATE TABLE `([^`]+)`\s*\((.*?)\) ENGINE=", sql, re.S)
    tables = {name: body for name, body in blocks}
    fk_re = re.compile(
        r"CONSTRAINT `([^`]+)` FOREIGN KEY \(([^)]+)\) REFERENCES `([^`]+)` \(([^)]+)\)"
    )
    unique_re = re.compile(r"UNIQUE KEY `([^`]+)` \(([^)]+)\)")
    pk_re = re.compile(r"PRIMARY KEY \(([^)]+)\)")
    col_re = re.compile(r"^`([^`]+)`\s+(.+)$")

    keys: dict[str, dict[str, set]] = {}
    refs: dict[tuple[str, str], tuple[str, str, str]] = {}
    constraints: dict[str, list[str]] = {}
    for table, body in blocks:
        info = collections.defaultdict(set)
        notes = []
        for item in split_columns(body.replace("\n", " ")):
            if item.startswith("PRIMARY KEY"):
                m = pk_re.search(item)
                if m:
                    for col in re.findall(r"`([^`]+)`", m.group(1)):
                        info[col].add("pk")
            elif item.startswith("UNIQUE KEY"):
                m = unique_re.search(item)
                if m:
                    cols = re.findall(r"`([^`]+)`", m.group(2))
                    if len(cols) == 1:
                        info[cols[0]].add("uk")
                    notes.append(f"UNIQUE {m.group(1)} ({', '.join(cols)})")
            elif item.startswith("CONSTRAINT"):
                m = fk_re.search(item)
                if m:
                    cname, child_cols, parent, parent_cols = m.groups()
                    ccols = re.findall(r"`([^`]+)`", child_cols)
                    pcols = re.findall(r"`([^`]+)`", parent_cols)
                    for child_col, parent_col in zip(ccols, pcols):
                        info[child_col].add("fk")
                        refs[(table, child_col)] = (parent, parent_col, cname)
                    notes.append(f"FOREIGN KEY {cname}: ({', '.join(ccols)}) → {parent}({', '.join(pcols)})")
                else:
                    notes.append(item.rstrip(";"))
            elif item.startswith(("KEY ", "INDEX ")):
                notes.append(item.rstrip(";"))
            else:
                col = col_re.match(item)
                if col:
                    # MySQL column clauses carry nullability/default/generated rules;
                    # preserve the complete declaration as Archify's displayed type text.
                    pass
        keys[table] = info
        constraints[table] = notes

    # Column definitions are read from the original line records to retain exact SQL.
    entities = []
    column_details: dict[str, list[str]] = collections.defaultdict(list)
    table_order = list(tables)
    domains = {
        "Usuarios": ["tb_users", "tb_carts", "tbd_users_wishlist_products", "tbd_products_users_providers"],
        "Catálogo": ["tb_products", "tbc_categories", "tbd_products_categories"],
        "Compras y pagos": ["tb_orders", "tbd_order_items", "tb_payment_methods", "tb_payments", "tbd_cart_items"],
        "Auditoría": ["tb_logs"],
    }
    positions = {}
    for col, names in enumerate(domains.values()):
        for row, name in enumerate(names):
            positions[name] = (row, col)

    fk_to_unique = {(t, c) for t, cs in keys.items() for c, roles in cs.items() if "uk" in roles}
    for table in table_order:
        body = tables[table]
        attrs = []
        for line in body.splitlines():
            stripped = line.strip().rstrip(",")
            m = col_re.match(stripped)
            if not m:
                continue
            name, declaration = m.groups()
            declaration = re.sub(r"\s+", " ", declaration.strip())
            # The table lists the exact SQL base type and a compact null marker;
            # full clauses (defaults, generated/on-update, checks) live in the
            # corresponding interactive detail card to keep every row legible.
            type_match = re.match(r"([A-Za-z]+(?:\([^)]*\))?(?:\s+unsigned)?)", declaration, re.I)
            sql_type = type_match.group(1) if type_match else declaration
            if sql_type.lower().startswith("enum("):
                values = split_columns(sql_type[5:-1])
                sql_type = f"enum({len(values)} values)"
            nullable = not bool(re.search(r"\bNOT NULL\b", declaration, re.I))
            roles = sorted(keys[table].get(name, set()), key=lambda role: ["pk", "fk", "uk"].index(role))
            ref = refs.get((table, name))
            unresolved = bool(ref and ref[0] not in tables)
            displayed_type = f"{sql_type} · {'NULL' if nullable else 'NN'}"
            if unresolved:
                displayed_type += " · FK ext"
                roles = [role for role in roles if role != "fk"]
            attr = {"name": name, "type": displayed_type}
            if roles:
                attr["key"] = roles[0] if len(roles) == 1 else roles
            if ref and not unresolved:
                parent, parent_col, _ = ref
                attr["references"] = f"{parent}.{parent_col}"
            attrs.append(attr)
            key_text = ", ".join(role.upper() for role in roles) if roles else "sin clave"
            ref_text = f"; referencia {ref[0]}.{ref[1]} ({ref[2]})" if ref else ""
            column_details[table].append(f"{name}: {declaration}; {key_text}{ref_text}")
        row, col = positions[table]
        entities.append({
            "id": table,
            "label": table,
            "tag": next(tag for tag, names in domains.items() if table in names),
            "row": row,
            "col": col,
            "sublabel": f"{counts[table]:,} registros INSERT · {len(attrs)} columnas".replace(",", " "),
            "attributes": attrs,
        })

    relationships = []
    for (child, child_col), (parent, parent_col, cname) in refs.items():
        if parent not in tables or parent == child:
            continue
        unique_fk = child_col in keys[child] and "uk" in keys[child][child_col]
        nullable = any(
            re.match(rf"`{re.escape(child_col)}`\s+.*?\bDEFAULT\s+NULL", line.strip(), re.I)
            for line in tables[child].splitlines()
        )
        relationships.append({
            "id": re.sub(r"[^A-Za-z0-9_-]", "_", f"rel_{child}_{child_col}_{parent}"),
            "from": child,
            "to": parent,
            "label": f"{cname}: {child_col} → {parent_col}",
            "fromCardinality": "one" if unique_fk else "many",
            "fromOptional": nullable,
            "toCardinality": "one",
            "identifying": child_col in keys[child] and "pk" in keys[child][child_col],
        })

    cards = [{"dot": "violet", "title": f"Columnas · {table}", "items": column_details[table]}
             for table in tables]
    cards.extend({"dot": "cyan", "title": f"Restricciones · {table}", "items": notes}
                 for table, notes in constraints.items() if notes)
    cards.append({
        "dot": "amber",
        "title": "Relaciones y límites del respaldo",
        "items": [
            "Las relaciones directas corresponden únicamente a FOREIGN KEY declaradas; la cardinalidad se deriva de la unicidad y nulabilidad de la FK.",
            "Las asociaciones N:M usan entidades puente: tbd_products_categories (productos–categorías), tbd_users_wishlist_products (usuarios–productos), tbd_products_users_providers (usuarios–productos) y tbd_cart_items (carritos–ofertas).",
            "La FK autorreferente tbc_categories.sup_id_category → tbc_categories.ID se conserva en la tabla y su tarjeta de restricción; Archify no permite dibujar una relación de entidad consigo misma.",
            "El respaldo referencia tb_users_offer_products.product_offer_ID desde tbd_cart_items y tbd_order_items, pero no define esa tabla; esas dos relaciones quedan señaladas como referencias externas no resueltas.",
            "Cada conteo suma las tuplas encontradas en INSERT INTO del dump; CREATE TABLE sin INSERT se muestra como 0.",
        ],
    })
    candidate = {
        "schema_version": 1,
        "diagram_type": "erd",
        "meta": {
            "title": "Modelo EER · respaldo db_test 14/10/2026",
            "locale": "es",
            "output": ".archify/erd-respaldo-14102026-20261014-174859/respaldo-14102026.html",
            "quality_profile": "standard",
            "views": [
                {"id": "commerce", "label": "Compras y pagos", "focus": ["tb_carts", "tb_orders", "tb_payments", "tb_payment_methods", "tbd_cart_items", "tbd_order_items"], "note": "Carritos, pedidos y pagos; también señala ofertas ausentes."},
                {"id": "catalog", "label": "Catálogo", "focus": ["tb_products", "tbc_categories", "tbd_products_categories", "tbd_products_users_providers"], "note": "Productos, categorías y sus entidades puente."},
                {"id": "identity", "label": "Usuarios", "focus": ["tb_users", "tb_carts", "tbd_users_wishlist_products"], "note": "Identidades y asociaciones vinculadas a usuarios."},
                {"id": "audit", "label": "Auditoría", "focus": ["tb_logs"], "note": "Registros de actividad insertados en el dump."},
            ],
        },
        "layout": {"mode": "grid", "gapX": 68, "gapY": 40, "entityW": 360, "headerH": 54, "rowH": 24},
        "entities": entities,
        "relationships": relationships,
        "cards": cards,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidate": str(OUT), "tables": len(entities), "relationships": len(relationships),
                      "total_rows": sum(counts[t] for t in tables),
                      "counts": {t: counts[t] for t in tables},
                      "unresolved_references": sorted({p for p, _, _ in refs.values() if p not in tables})},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
