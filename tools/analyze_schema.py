"""Read CREATE TABLE metadata from the checked-in dump without executing SQL."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SQL = WORKSPACE / "Practica 03" / "backups" / "Respaldo_29102026.sql"
OUT = ROOT / "schema-docs.json"

def split_items(body):
    result=[]; start=depth=0; quote=None; esc=False
    for i,ch in enumerate(body):
        if quote:
            if esc: esc=False
            elif ch == "\\": esc=True
            elif ch == quote: quote=None
        elif ch in "'\"`": quote=ch
        elif ch == "(": depth+=1
        elif ch == ")": depth-=1
        elif ch == "," and depth==0: result.append(body[start:i].strip()); start=i+1
    result.append(body[start:].strip())
    return result

def main():
    sql=SQL.read_text(encoding="utf-8",errors="replace")
    tables=[]
    for m in re.finditer(r"CREATE TABLE `([^`]+)`\s*\((.*?)\)\s*ENGINE=([^;]+);",sql,re.S|re.I):
        name,body,engine=m.groups(); cols=[]; indexes=[]; fks=[]; checks=[]; pk=[]
        for item in split_items(body):
            cm=re.match(r"`([^`]+)`\s+(.+)$",item,re.S)
            if cm:
                cn,decl=cm.groups(); typ=re.match(r"(?:enum|set)\s*\([^)]*(?:\)[^)]*)?\)|[a-z]+(?:\s+unsigned)?(?:\([^)]*\))?",decl,re.I)
                # Capture type expressions containing nested enum strings with a quote-aware prefix.
                mt=re.match(r"([a-z]+)\s*(\()",decl,re.I)
                if mt:
                    dep=0; q=None; end=0
                    for i,ch in enumerate(decl):
                        if q:
                            if ch==q and (i==0 or decl[i-1] != "\\"): q=None
                        elif ch in "'\"": q=ch
                        elif ch=="(": dep+=1
                        elif ch==")":
                            dep-=1
                            if dep==0: end=i+1; break
                    type_text=decl[:end]
                    tail=decl[end:]
                    if re.match(r"\s+unsigned",tail,re.I): type_text += " unsigned"; tail=re.sub(r"^\s+unsigned","",tail,flags=re.I)
                else:
                    mm=re.match(r"[a-z]+(?:\s+unsigned)?(?:\([^)]*\))?",decl,re.I); type_text=mm.group(0) if mm else decl.split()[0]; tail=decl[len(type_text):]
                null=not bool(re.search(r"\bNOT NULL\b",tail,re.I))
                default=re.search(r"\bDEFAULT\s+((?:'[^']*')|(?:b'[^']*')|(?:NULL|CURRENT_TIMESTAMP(?:\(\d+\))?|[-\w.]+))",tail,re.I)
                gm=re.search(r"GENERATED ALWAYS AS\s*(\(.*\))\s*(STORED|VIRTUAL)",tail,re.I)
                cols.append({"name":cn,"type":type_text,"declaration":re.sub(r"\s+"," ",decl),"nullable":null,"default":default.group(1) if default else None,"autoIncrement":bool(re.search(r"AUTO_INCREMENT",tail,re.I)),"generated":bool(gm),"generatedExpression":gm.group(1) if gm else None,"generatedKind":gm.group(2).upper() if gm else None,"onUpdate":(re.search(r"ON UPDATE\s+\w+(?:\(\d+\))?",tail,re.I).group(0) if re.search(r"ON UPDATE\s+\w+(?:\(\d+\))?",tail,re.I) else None),"keys":[],"references":[]})
            elif item.upper().startswith("PRIMARY KEY"):
                pk=re.findall(r"`([^`]+)`",item)
            elif item.upper().startswith(("UNIQUE KEY","UNIQUE INDEX")):
                mm=re.match(r"UNIQUE KEY `([^`]+)`\s*\(([^)]+)\)",item,re.I); indexes.append({"name":mm.group(1),"columns":re.findall(r"`([^`]+)`",mm.group(2)),"unique":True}) if mm else None
            elif item.upper().startswith(("KEY ","INDEX ")):
                mm=re.match(r"(?:KEY|INDEX) `([^`]+)`\s*\(([^)]+)\)",item,re.I); indexes.append({"name":mm.group(1),"columns":re.findall(r"`([^`]+)`",mm.group(2)),"unique":False}) if mm else None
            elif "FOREIGN KEY" in item.upper():
                mm=re.search(r"CONSTRAINT `([^`]+)` FOREIGN KEY\s*\(([^)]+)\) REFERENCES `([^`]+)`\s*\(([^)]+)\)(.*)",item,re.I)
                if mm:
                    cn,src,target,dst,opts=mm.groups(); fks.append({"name":cn,"columns":re.findall(r"`([^`]+)`",src),"target":target,"targetColumns":re.findall(r"`([^`]+)`",dst),"onDelete":(re.search(r"ON DELETE (RESTRICT|CASCADE|SET NULL|NO ACTION|SET DEFAULT)",opts,re.I).group(1).upper() if re.search(r"ON DELETE (RESTRICT|CASCADE|SET NULL|NO ACTION|SET DEFAULT)",opts,re.I) else "NO ACTION (implícito)"),"onUpdate":(re.search(r"ON UPDATE (RESTRICT|CASCADE|SET NULL|NO ACTION|SET DEFAULT)",opts,re.I).group(1).upper() if re.search(r"ON UPDATE (RESTRICT|CASCADE|SET NULL|NO ACTION|SET DEFAULT)",opts,re.I) else "NO ACTION (implícito)"),"selfReference":target==name})
            elif "CHECK" in item.upper():
                mm=re.search(r"CONSTRAINT `([^`]+)` CHECK\s*(\(.*\))",item,re.I)
                if mm: checks.append({"name":mm.group(1),"expression":mm.group(2)})
        for c in cols:
            if c["name"] in pk: c["keys"].append("PK")
            for idx in indexes:
                if c["name"] in idx["columns"]: c["keys"].append(("UNIQUE " if idx["unique"] else "INDEX ")+idx["name"])
            for fk in fks:
                if c["name"] in fk["columns"]: c["keys"].append("FK "+fk["name"]); c["references"].append(f"{fk['target']}.{fk['targetColumns'][fk['columns'].index(c['name'])]}")
        tables.append({"name":name,"engine":engine.strip(),"columns":cols,"primaryKey":pk,"indexes":indexes,"foreignKeys":fks,"checkConstraints":checks})
    views=re.findall(r"CREATE VIEW `([^`]+)` AS",sql,re.I)
    triggers=re.findall(r"TRIGGER `([^`]+)`",sql,re.I)
    data={"database":"db_test","source":"Practica 03/backups/Respaldo_29102026.sql","mysql":"8.0.36","tables":tables,"views":views,"triggers":triggers,"procedures":re.findall(r"CREATE PROCEDURE `([^`]+)`",sql,re.I),"functions":re.findall(r"CREATE FUNCTION `([^`]+)`",sql,re.I),"events":re.findall(r"CREATE EVENT `([^`]+)`",sql,re.I)}
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT / "schema-docs.js").write_text("window.SCHEMA_DOCS="+json.dumps(data,ensure_ascii=False,separators=(",",":"))+";",encoding="utf-8")
    print(f"{len(tables)} tablas, {sum(len(t['columns']) for t in tables)} columnas, {sum(len(t['foreignKeys']) for t in tables)} claves foráneas; {len(views)} vistas, {len(triggers)} triggers")
if __name__=="__main__": main()
