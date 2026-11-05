(() => {
  const root = document.documentElement;
  const key = 'jarvis-theme';
  const saved = localStorage.getItem(key);
  root.dataset.theme = saved === 'light' ? 'light' : 'dark';
  const button = document.querySelector('#theme');
  if (button) button.onclick = () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(key, root.dataset.theme);
  };

  const esc = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const overview = document.querySelector('#overview');
  const db = window.SCHEMA_DOCS;

  function addNetworkConsole() {
    if (!overview || overview.hidden || overview.querySelector('.net-map') || !db) return;
    const list = overview.querySelector('.relation-list');
    if (!list) return;
    const card = list.closest('.card');
    if (!card) return;

    const toolbar = document.createElement('div');
    toolbar.className = 'net-toolbar';
    toolbar.innerHTML = '<span class="net-mode"><i></i> DEPENDENCY MAP</span><div class="net-switch"><button class="active" data-mode="map">MAP</button><button data-mode="list">LIST</button></div>';
    const map = document.createElement('div');
    map.className = 'net-map';
    const stats = new Map(db.tables.map(table => [table.name, 0]));
    const edges = db.tables.flatMap(source => source.foreignKeys.map(fk => ({from:source.name,to:fk.target,field:fk.columns.join(', ')})));
    edges.forEach(edge => {
      if (stats.has(edge.from)) stats.set(edge.from, stats.get(edge.from) + 1);
      if (stats.has(edge.to)) stats.set(edge.to, stats.get(edge.to) + 1);
    });
    const nodes = [...db.tables].sort((a,b) => stats.get(b.name)-stats.get(a.name) || a.name.localeCompare(b.name)).slice(0,8);
    const positions = new Map(nodes.map((node,index) => {
      const angle = -Math.PI/2 + index * (2*Math.PI/nodes.length);
      return [node.name,{x:300+195*Math.cos(angle),y:165+105*Math.sin(angle)}];
    }));
    const visibleEdges = edges.filter(edge => positions.has(edge.from) && positions.has(edge.to));
    const paths = visibleEdges.map(edge => {
      const from=positions.get(edge.from),to=positions.get(edge.to);
      return `<path class="net-edge" data-from="${esc(edge.from)}" data-to="${esc(edge.to)}" d="M ${from.x} ${from.y} L ${to.x} ${to.y}"><title>${esc(edge.from)}.${esc(edge.field)} → ${esc(edge.to)}</title></path>`;
    }).join('');
    const nodeMarkup = nodes.map((node,index) => {
      const {x,y}=positions.get(node.name), count=stats.get(node.name);
      const shortName=node.name.replace(/^tbd?_/, '');
      return `<g class="net-node" data-table="${esc(node.name)}" tabindex="0" role="button" aria-label="Abrir ${esc(node.name)}"><title>${esc(node.name)} · ${count} dependencias</title><rect x="${x-77}" y="${y-17}" width="154" height="34" rx="3"/><circle cx="${x-65}" cy="${y}" r="3"/><text x="${x-55}" y="${y+3}">${esc(shortName)}</text><text class="net-count" x="${x+70}" y="${y+3}" text-anchor="end">${count}</text></g>`;
    }).join('');
    map.innerHTML = `<svg viewBox="0 0 600 330" role="img" aria-label="Mapa interactivo de las tablas con más dependencias"><defs><filter id="net-glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><g class="net-grid"><circle cx="300" cy="165" r="52"/><circle cx="300" cy="165" r="104"/><circle cx="300" cy="165" r="154"/><path d="M 42 165 H 558 M 300 18 V 312"/></g><g class="net-links">${paths}</g><g class="net-nodes">${nodeMarkup}</g></svg><div class="net-foot"><span>8 MOST CONNECTED TABLES</span><span>${visibleEdges.length} DECLARED LINKS</span><span>SELECT A NODE TO INSPECT</span></div>`;
    list.before(toolbar,map);
    list.hidden = true;

    toolbar.querySelectorAll('[data-mode]').forEach(control => control.addEventListener('click', () => {
      const useMap=control.dataset.mode==='map';
      map.hidden=!useMap; list.hidden=useMap;
      toolbar.querySelectorAll('[data-mode]').forEach(item=>item.classList.toggle('active',item===control));
      toolbar.querySelector('.net-mode').innerHTML=useMap?'<i></i> DEPENDENCY MAP':'<i></i> RELATION INDEX';
    }));
    map.querySelectorAll('.net-node').forEach(node => {
      const openTable=()=>document.querySelectorAll('.table-card').forEach(card=>{if(card.dataset.table===node.dataset.table)card.click()});
      node.addEventListener('click',openTable);
      node.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();openTable()}});
      node.addEventListener('pointerenter',()=>map.querySelectorAll('.net-edge').forEach(edge=>edge.classList.toggle('dim',edge.dataset.from!==node.dataset.table&&edge.dataset.to!==node.dataset.table)));
      node.addEventListener('pointerleave',()=>map.querySelectorAll('.net-edge').forEach(edge=>edge.classList.remove('dim')));
    });
  }

  const observer = new MutationObserver(addNetworkConsole);
  if (overview) observer.observe(overview,{childList:true,subtree:true});
  addNetworkConsole();

  const jump=document.querySelector('#diagram-jump');
  if(jump) jump.onclick=()=>{
    if(overview?.hidden) document.querySelector('#back')?.click();
    window.setTimeout(()=>document.querySelector('.net-toolbar')?.scrollIntoView({behavior:'smooth',block:'center'}),30);
  };
})();
