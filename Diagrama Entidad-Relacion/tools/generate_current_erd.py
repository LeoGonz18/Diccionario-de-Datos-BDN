"""Build a current Archify ERD from the parsed 20/10/2026 DDL metadata."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT.parent/'Diccionario de Datos'/'schema-docs.json').read_text(encoding='utf-8'))
OUT=ROOT/'.archify'/'erd-respaldo-20102026-20261020-120000'
groups={
 'Identidad':['tb_users','tb_carts','tb_user_addresses','tbd_address_components','tbd_user_payment_methods','tbd_users_wishlist_products'],
 'Catálogo':['tb_products','tbc_categories','tbd_products_categories','tbd_products_users_providers'],
 'Operaciones':['tb_orders','tb_payments','tb_payment_methods','tbc_payment_methods_types','tbd_buyer_orders','tbd_cart_items','tbd_order_items'],
 'Auditoría':['tb_logs']}
positions={name:(i,group) for group,names in enumerate(groups.values()) for i,name in enumerate(names)}
entities=[];rels=[];cards=[]
for table in DATA['tables']:
 row, col=positions[table['name']]; attrs=[]
 for c in table['columns']:
  roles=[]
  if 'PK' in c['keys']: roles.append('pk')
  if any(k.startswith('FK ') for k in c['keys']): roles.append('fk')
  if any(k.startswith('UNIQUE ') for k in c['keys']): roles.append('uk')
  a={'name':c['name'],'type':c['declaration']}
  if roles:a['key']=roles[0] if len(roles)==1 else roles
  if c['references']:a['references']=c['references'][0]
  attrs.append(a)
 entities.append({'id':table['name'],'label':table['name'],'tag':list(groups)[col],'row':row,'col':col,'sublabel':f"{len(attrs)} columnas · {table['engine'].split()[0]}",'attributes':attrs})
 for fk in table['foreignKeys']:
  target=next(t for t in DATA['tables'] if t['name']==fk['target'])
  target_unique=fk['targetColumns']==target['primaryKey'] or any(set(ix['columns'])==set(fk['targetColumns']) and ix['unique'] for ix in target['indexes'])
  src_unique=fk['columns']==table['primaryKey'] or any(set(ix['columns'])==set(fk['columns']) and ix['unique'] for ix in table['indexes'])
  nullable=any(next(c for c in table['columns'] if c['name']==col)['nullable'] for col in fk['columns'])
  rels.append({'id':re.sub(r'[^A-Za-z0-9_-]','_',fk['name']),'from':table['name'],'to':fk['target'],'label':f"{fk['name']} · {', '.join(fk['columns'])} → {', '.join(fk['targetColumns'])}",'fromCardinality':'one' if src_unique else 'many','toCardinality':'one' if target_unique else 'many','fromOptional':nullable,'toOptional':False,'identifying':all(c in table['primaryKey'] for c in fk['columns'])})
  if fk['selfReference']:cards.append({'dot':'amber','title':f"Relación autorreferente · {table['name']}",'items':[f"{fk['name']}: ({', '.join(fk['columns'])}) referencia ({', '.join(fk['targetColumns'])}); DELETE {fk['onDelete']}; UPDATE {fk['onUpdate']}."]})
for t in DATA['tables']:
 for fk in t['foreignKeys']:
  if fk['columns']!=t['primaryKey'] and not any(set(ix['columns'])==set(fk['columns']) and ix['unique'] for ix in t['indexes']) and any(c in t['primaryKey'] for c in fk['columns']):
   cards.append({'dot':'amber','title':f"Revisar unicidad · {t['name']}",'items':[f"La FK {fk['name']} comparte parte de la PK compuesta. La cardinalidad de origen depende de la combinación completa de columnas."]})
cards.append({'dot':'cyan','title':'Procedencia y alcance','items':[f"Esquema leído de {DATA['source']} sin ejecutar instrucciones.",f"DDL declara {len(entities)} tablas, {sum(len(t['columns']) for t in DATA['tables'])} columnas y {len(rels)} claves foráneas.",f"El respaldo contiene {len(DATA['views'])} vistas y {len(DATA['triggers'])} triggers; no se detectaron procedimientos, funciones ni eventos.","Las relaciones dibujadas son FOREIGN KEY declaradas. Los nombres funcionales y el significado de negocio requieren confirmación cuando no se desprenden directamente del SQL."]})
candidate={'schema_version':1,'diagram_type':'erd','meta':{'title':'Modelo de datos · respaldo db_test 20/10/2026','locale':'es','output':'modelo-db-test.html','quality_profile':'standard'},'layout':{'mode':'grid','gapX':70,'gapY':38,'entityW':340,'rowH':22},'entities':entities,'relationships':rels,'cards':cards}
OUT.mkdir(parents=True,exist_ok=True);(OUT/'candidate.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2),encoding='utf-8')
print(f"{OUT/'candidate.json'} · {len(entities)} entidades · {len(rels)} relaciones")
