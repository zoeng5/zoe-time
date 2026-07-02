#!/usr/bin/env python3
"""Patch 2: Interactive timeline events + gap fill + color legend + localStorage"""

SRC = "/Users/zoe/mt-sites/bi-dashboards/mt-time-tracker/index.html"
with open(SRC, encoding="utf-8") as f:
    html = f.read()

# ── 1. ADD CSS for new elements ─────────────────────────────────────────────
NEW_CSS = """
/* ── INTERACTIVE EVENT ROWS ── */
.ev-row { transition: background 0.15s; border-radius: 6px; padding: 9px 6px; margin: 0 -6px; }
.ev-row:active { background: var(--sand); }
.ev-row-main { display: flex; align-items: center; gap: 10px; }
.ev-src { font-size: 7.5px; letter-spacing:.04em; color: var(--label); opacity:.7; font-weight:400; text-transform:none; margin-left:4px; }
.ev-confirm { font-size: 12px; margin-left: 4px; }
.ev-edit { display:none; padding: 8px 0 4px 22px; }
.ev-edit.open { display: block; }
.ev-edit-cats { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
.cat-chip { font-size: 10px; padding: 3px 8px; border-radius: 12px; cursor: pointer; border: 1.5px solid transparent; transition: all .15s; white-space: nowrap; }
.cat-chip.active { border-color: #1D1D1D; font-weight: 600; }
.ev-edit-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.ev-act-btn { font-size: 11px; padding: 5px 12px; border-radius: 14px; border: 1px solid var(--line); background: var(--cloud); color: var(--ink); cursor: pointer; font-family: var(--font-body); transition: background .15s; }
.ev-act-btn:active { background: var(--sand); }
.ev-act-btn.danger { color: #c0392b; border-color: #f5c6c2; }
.ev-act-btn.primary { background: var(--ink); color: var(--cloud); border-color: var(--ink); }

/* ── GAP FILL BUTTON ── */
.ev-gap-btn { display: flex; align-items: center; gap: 6px; padding: 5px 6px; margin: 0 -6px;
  color: var(--label); font-size: 10.5px; cursor: pointer; border-radius: 6px;
  border: 1px dashed var(--line); background: transparent; transition: all .15s; }
.ev-gap-btn:active { background: var(--sand); border-color: var(--body); }
.ev-gap-time { font-size: 9px; color: var(--label); font-variant-numeric: tabular-nums; width: 88px; flex-shrink: 0; font-family: var(--font-display); }
.ev-gap-plus { width: 16px; height: 16px; border-radius: 50%; background: var(--line); display: flex; align-items: center; justify-content: center; font-size: 13px; color: var(--label); flex-shrink: 0; }

/* ── ARC COLOR LEGEND ── */
.arc-cat-legend { display: flex; flex-wrap: wrap; gap: 5px 10px; padding: 10px 16px 6px; justify-content: center; }
.arc-cat-pip { display: flex; align-items: center; gap: 4px; font-size: 9.5px; color: var(--label); }
.arc-cat-pip-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }

/* ── ADD ENTRY MODAL ── */
.add-modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 200; display: none; align-items: flex-end; }
.add-modal-overlay.open { display: flex; }
.add-modal { background: var(--milk); border-radius: 16px 16px 0 0; padding: 20px 18px 32px; width: 100%; max-width: 500px; margin: 0 auto; box-shadow: 0 -4px 24px rgba(0,0,0,0.1); }
.add-modal-title { font-size: 15px; font-weight: 600; color: var(--ink); margin-bottom: 14px; }
.add-modal-row { margin-bottom: 12px; }
.add-modal-label { font-size: 10px; color: var(--label); letter-spacing: .08em; text-transform: uppercase; margin-bottom: 5px; }
.add-modal input[type=text] { width: 100%; box-sizing: border-box; font-size: 14px; padding: 8px 10px; border: 1px solid var(--line); border-radius: 8px; background: var(--cloud); color: var(--ink); font-family: var(--font-body); }
.add-modal-times { display: flex; gap: 8px; align-items: center; }
.time-sel { flex: 1; font-size: 13px; padding: 7px 8px; border: 1px solid var(--line); border-radius: 8px; background: var(--cloud); color: var(--ink); font-family: var(--font-display); font-variant-numeric: tabular-nums; cursor: pointer; }
.add-modal-cats { display: flex; flex-wrap: wrap; gap: 6px; }
.add-modal-actions { display: flex; gap: 8px; margin-top: 16px; }
.add-modal-actions button { flex: 1; padding: 11px; border-radius: 12px; font-size: 14px; font-family: var(--font-body); cursor: pointer; border: none; }
.btn-cancel { background: var(--sand); color: var(--label); }
.btn-save { background: var(--ink); color: var(--cloud); font-weight: 600; }
"""

# Insert new CSS before closing </style>
html = html.replace('</style>', NEW_CSS + '\n</style>', 1)
print("✓ CSS added")

# ── 2. ADD ADD-ENTRY MODAL HTML (before </body>) ─────────────────────────────
MODAL_HTML = """
<!-- ADD ENTRY MODAL -->
<div class="add-modal-overlay" id="addModalOverlay" onclick="closeAddModal(event)">
  <div class="add-modal" id="addModal">
    <div class="add-modal-title">添加时间记录</div>
    <div class="add-modal-row">
      <div class="add-modal-label">事项名称</div>
      <input type="text" id="addTitle" placeholder="e.g. 晨跑 / 读书 / 家庭时光" />
    </div>
    <div class="add-modal-row">
      <div class="add-modal-label">时间段</div>
      <div class="add-modal-times">
        <select class="time-sel" id="addStart"></select>
        <span style="color:var(--label);font-size:12px">→</span>
        <select class="time-sel" id="addEnd"></select>
      </div>
    </div>
    <div class="add-modal-row">
      <div class="add-modal-label">类别</div>
      <div class="add-modal-cats" id="addCats"></div>
    </div>
    <div class="add-modal-actions">
      <button class="btn-cancel" onclick="closeAddModal(null)">取消</button>
      <button class="btn-save" onclick="saveManualEntry()">保存</button>
    </div>
  </div>
</div>
"""

html = html.replace('</body>', MODAL_HTML + '\n</body>', 1)
print("✓ Modal HTML added")

# ── 3. ADD LOCALSTORAGE HELPERS + EVENT HANDLERS ────────────────────────────
# Find the catMins function to insert before it
LS_JS = """
// ─────────────────────────────────────────
//  LOCALSTORAGE & EDIT HELPERS
// ─────────────────────────────────────────
function lsKey(ds) { return 'ZT_' + ds; }
function loadDayData(ds) {
  try { return JSON.parse(localStorage.getItem(lsKey(ds)) || '{}'); } catch(e) { return {}; }
}
function saveDayData(ds, data) {
  localStorage.setItem(lsKey(ds), JSON.stringify(data));
}
function getOverrides(ds) { return loadDayData(ds).overrides || {}; }
function getManuals(ds) { return loadDayData(ds).manuals || []; }
function saveOverride(ds, evId, patch) {
  const data = loadDayData(ds);
  data.overrides = data.overrides || {};
  data.overrides[evId] = Object.assign(data.overrides[evId] || {}, patch);
  saveDayData(ds, data);
}
function saveManualEvsArr(ds, manuals) {
  const data = loadDayData(ds);
  data.manuals = manuals;
  saveDayData(ds, data);
}

// Apply localStorage overrides to genDay events
function applyOverrides(dateStr, evs) {
  const ov = getOverrides(dateStr);
  const mans = getManuals(dateStr);
  let result = evs.map(ev => {
    const ovr = ov[ev._id];
    if (!ovr) return ev;
    if (ovr.deleted) return null;
    return Object.assign({}, ev, ovr);
  }).filter(Boolean);
  result = result.concat(mans.map(m => Object.assign({_source:'manual'}, m)));
  return result.sort((a,b) => a.start - b.start);
}

let _openEditId = null;
function toggleEvEdit(evId) {
  const panel = document.getElementById('evEdit_' + evId);
  if (!panel) return;
  if (_openEditId && _openEditId !== evId) {
    const prev = document.getElementById('evEdit_' + _openEditId);
    if (prev) prev.classList.remove('open');
  }
  panel.classList.toggle('open');
  _openEditId = panel.classList.contains('open') ? evId : null;
}

function confirmEv(ds, evId) {
  saveOverride(ds, evId, {confirmed: true});
  renderDay();
}

function deleteEv(ds, evId) {
  saveOverride(ds, evId, {deleted: true});
  _openEditId = null;
  renderDay();
}

function changeCat(ds, evId, newCat, newSub, el) {
  el.closest('.ev-edit-cats').querySelectorAll('.cat-chip').forEach(c=>c.classList.remove('active'));
  el.classList.add('active');
  saveOverride(ds, evId, {cat: newCat, sub: newSub});
  renderDay();
}

// GAP / ADD MODAL
let _addGapStart = 0, _addGapEnd = 0, _addDateStr = '';
let _addCatSel = 'self';

function showAddModal(ds, gapStart, gapEnd) {
  _addDateStr = ds; _addGapStart = gapStart; _addGapEnd = gapEnd; _addCatSel = 'self';
  // Build time options (30-min increments)
  const opts = [];
  for (let h = 0; h < 24; h += 0.5) {
    const hh = Math.floor(h), mm = h % 1 === 0.5 ? 30 : 0;
    opts.push(`<option value="${h}">${String(hh).padStart(2,'0')}:${String(mm).padStart(2,'0')}</option>`);
  }
  const startSel = document.getElementById('addStart');
  const endSel = document.getElementById('addEnd');
  startSel.innerHTML = opts.join('');
  endSel.innerHTML = opts.join('');
  startSel.value = gapStart;
  endSel.value = Math.min(gapEnd, 23.5);
  document.getElementById('addTitle').value = '';
  // Build cat chips
  const catsEl = document.getElementById('addCats');
  catsEl.innerHTML = CATS.filter(c=>c.key!=='sleep').map(c =>
    `<div class="cat-chip ${c.key===_addCatSel?'active':''}" style="background:${c.color}22;color:${c.color}"
      onclick="this.closest('.add-modal-cats').querySelectorAll('.cat-chip').forEach(x=>x.classList.remove('active'));this.classList.add('active');_addCatSel='${c.key}'">
      ${c.icon} ${c.label}</div>`
  ).join('');
  document.getElementById('addModalOverlay').classList.add('open');
  setTimeout(()=>document.getElementById('addTitle').focus(), 100);
}

function closeAddModal(e) {
  if (e && e.target !== document.getElementById('addModalOverlay')) return;
  document.getElementById('addModalOverlay').classList.remove('open');
}

function saveManualEntry() {
  const title = document.getElementById('addTitle').value.trim();
  if (!title) { document.getElementById('addTitle').focus(); return; }
  const start = parseFloat(document.getElementById('addStart').value);
  const end   = parseFloat(document.getElementById('addEnd').value);
  if (end <= start) { alert('结束时间需晚于开始时间'); return; }
  const cat = CATS.find(c=>c.key===_addCatSel) || CATS[8];
  const manuals = getManuals(_addDateStr);
  manuals.push({
    _id: 'm_' + Date.now(), _source: 'manual',
    cat: cat.key, sub: cat.sub[0]||'', title, start, end, tags: []
  });
  saveManualEvsArr(_addDateStr, manuals);
  document.getElementById('addModalOverlay').classList.remove('open');
  renderDay();
}

"""

# Insert before catMins function
if 'function catMins(evs)' in html:
    html = html.replace('function catMins(evs)', LS_JS + '\nfunction catMins(evs)', 1)
    print("✓ LS helpers + handlers added")
else:
    print("✗ Could not find catMins!")

# ── 4. UPDATE genDay to assign _id and _source ──────────────────────────────
# In the genDay function, we need to:
# a) Assign _id to each event
# b) Mark source: 'cal', 'auto', 'mock'
# After the final return statement, intercept

# Replace the real events section in genDay
OLD_REAL_SECTION = """    realEvs.forEach(ev => push(ev.cat, ev.sub, ev.title, ev.start, ev.end, ev.tags));"""
NEW_REAL_SECTION = """    realEvs.forEach(ev => push(ev.cat, ev.sub, ev.title, ev.start, ev.end, ev.tags, 'cal'));"""
html = html.replace(OLD_REAL_SECTION, NEW_REAL_SECTION, 1)

# Update push function to include source
OLD_PUSH = """  const push = (cat, subCat, title, start, end, tags=[]) =>
    evs.push({cat, subCat, title, start, end, tags});"""
NEW_PUSH = """  const push = (cat, subCat, title, start, end, tags=[], _source='mock') =>
    evs.push({cat, subCat, title, start, end, tags, _source,
               _id: start+'_'+cat+'_'+title.slice(0,8).replace(/\\s/g,'')});"""
html = html.replace(OLD_PUSH, NEW_PUSH, 1)

# Mark auto-filled events in genDay real events section
OLD_AUTO = """    const hasEarlyMtg = realEvs.some(e => e.start < 9.5);
    if (!hasEarlyMtg) {
      if (!wknd && rand() > 0.4) push('self', '健身运动', '晨练', wake + 0.25, Math.min(9.0, wake + 1.0), []);
      if (!wknd && rand() > 0.5) push('growth', '读书', '早读', 8.0, 8.5, ['Zoe']);
    }
    // Lunch break if gap around noon
    const hasNoon = realEvs.some(e => e.start >= 11.5 && e.start <= 13 && e.end <= 14);
    if (!hasNoon) push('self', '休闲放松', '午间休息', 12.5, 13.25, ['Zoe']);
    // Evening filler after last event
    const lastEnd = realEvs.reduce((m,e) => Math.max(m,e.end), 0);
    if (lastEnd < 19 && !wknd) {
      const tf = Math.max(18.0, lastEnd);
      if (rand() > 0.4) push('family', '亲子居家', '家庭晚餐', tf, tf + 0.75 + rand()*0.5, ['Don','George','Max','Olivia']);
      if (rand() > 0.5) push('self', '休闲放松', '个人时间', tf + 1.0, tf + 1.75, ['Zoe']);
    }
    const nightSleep = Math.max(lastEnd + 0.5, 21.5 + rand() * 1.0);
    push('sleep', '', '入睡', Math.min(nightSleep, 23.5), 24);"""
NEW_AUTO = """    const hasEarlyMtg = realEvs.some(e => e.start < 9.5);
    if (!hasEarlyMtg) {
      if (!wknd && rand() > 0.4) push('self', '健身运动', '晨练', wake + 0.25, Math.min(9.0, wake + 1.0), [], 'auto');
      if (!wknd && rand() > 0.5) push('growth', '读书', '早读', 8.0, 8.5, ['Zoe'], 'auto');
    }
    const hasNoon = realEvs.some(e => e.start >= 11.5 && e.start <= 13 && e.end <= 14);
    if (!hasNoon) push('self', '休闲放松', '午间休息', 12.5, 13.25, ['Zoe'], 'auto');
    const lastEnd = realEvs.reduce((m,e) => Math.max(m,e.end), 0);
    if (lastEnd < 19 && !wknd) {
      const tf = Math.max(18.0, lastEnd);
      if (rand() > 0.4) push('family', '亲子居家', '家庭晚餐', tf, tf + 0.75 + rand()*0.5, ['Don','George','Max','Olivia'], 'auto');
      if (rand() > 0.5) push('self', '休闲放松', '个人时间', tf + 1.0, tf + 1.75, ['Zoe'], 'auto');
    }
    const nightSleep = Math.max(lastEnd + 0.5, 21.5 + rand() * 1.0);
    push('sleep', '', '入睡', Math.min(nightSleep, 23.5), 24, [], 'auto');"""
html = html.replace(OLD_AUTO, NEW_AUTO, 1)
print("✓ genDay updated with _id and _source")

# ── 5. UPDATE renderDay to use applyOverrides + interactive rows ─────────────
OLD_LIST_RENDER = """  const list = document.getElementById('dayEvList');
  list.innerHTML = evs.map(ev => {
    const cat = CM[ev.cat] || {label:'?',color:'#CCC'};
    return `<div class="ev-row">
      <div class="ev-row-time">${h2t(ev.start)}<br>${h2t(ev.end)}</div>
      <div class="ev-row-dot" style="background:${cat.color}"></div>
      <div class="ev-row-info">
        <div class="ev-row-cat">${cat.label}</div>
        <div class="ev-row-title">${ev.title}</div>
      </div>
      <div class="ev-row-dur">${fmtM((ev.end-ev.start)*60)}</div>
    </div>`;
  }).join('');
}"""

NEW_LIST_RENDER = r"""  // Color legend below arc (only visible categories)
  const legendCats = CATS.filter(c => (m[c.key]||0)>0);
  const arcLegendEl = document.getElementById('arcCatLegend');
  if (arcLegendEl) arcLegendEl.innerHTML = legendCats.map(c =>
    `<div class="arc-cat-pip"><div class="arc-cat-pip-dot" style="background:${c.color}"></div>${c.label}</div>`
  ).join('');

  // Apply localStorage overrides
  const ds = dateStr(d);
  const mergedEvs = applyOverrides(ds, evs);
  const overrides = getOverrides(ds);

  const list = document.getElementById('dayEvList');
  let rows = '';

  // Helper: source label
  const srcLabel = (ev) => {
    if (ev._source==='cal') return '<span class="ev-src">日历</span>';
    if (ev._source==='auto') return '<span class="ev-src">自动填充</span>';
    if (ev._source==='manual') return '<span class="ev-src">手动</span>';
    return '';
  };

  for (let i = 0; i < mergedEvs.length; i++) {
    const ev = mergedEvs[i];
    const cat = CM[ev.cat] || {label:'?',color:'#CCC',sub:[]};
    const ovr = overrides[ev._id] || {};
    const confirmed = ovr.confirmed;
    const isSleep = ev.cat === 'sleep';
    const eid = (ev._id || ev.start+'_'+ev.cat).replace(/[^\w]/g,'_');

    rows += `<div class="ev-row" onclick="${isSleep?'':('toggleEvEdit(\''+eid+'\')')}">
      <div class="ev-row-main">
        <div class="ev-row-time">${h2t(ev.start)}<br>${h2t(ev.end)}</div>
        <div class="ev-row-dot" style="background:${cat.color}"></div>
        <div class="ev-row-info">
          <div class="ev-row-cat">${cat.label}${srcLabel(ev)}</div>
          <div class="ev-row-title">${ev.title}${confirmed?'<span class="ev-confirm">✅</span>':''}</div>
        </div>
        <div class="ev-row-dur">${fmtM((ev.end-ev.start)*60)}</div>
      </div>`;

    if (!isSleep) {
      rows += `<div class="ev-edit" id="evEdit_${eid}">
        <div class="add-modal-label" style="font-size:9px;margin-bottom:6px">改分类</div>
        <div class="ev-edit-cats">${CATS.filter(c=>c.key!=='sleep').map(c=>`
          <div class="cat-chip ${c.key===ev.cat?'active':''}" style="background:${c.color}22;color:${c.color}"
            onclick="event.stopPropagation();changeCat('${ds}','${eid}','${c.key}','${c.sub[0]||''}',this)">
            ${c.icon} ${c.label}</div>`).join('')}
        </div>
        <div class="ev-edit-actions">
          ${!confirmed?`<button class="ev-act-btn primary" onclick="event.stopPropagation();confirmEv('${ds}','${eid}')">✅ 确认</button>`:''}
          <button class="ev-act-btn danger" onclick="event.stopPropagation();deleteEv('${ds}','${eid}')">🗑️ 删除</button>
        </div>
      </div>`;
    }
    rows += '</div>';

    // Gap detection: show "+" if next event is > 20 min away
    const nextEv = mergedEvs[i+1];
    const gapStart = ev.end;
    const gapEnd = nextEv ? nextEv.start : 24;
    if (gapEnd - gapStart >= 0.33 && ev.cat !== 'sleep' && (!nextEv || nextEv.cat !== 'sleep')) {
      rows += `<div class="ev-gap-btn" onclick="showAddModal('${ds}',${gapStart},${gapEnd})">
        <div class="ev-gap-time">${h2t(gapStart)}<br>${h2t(gapEnd)}</div>
        <div class="ev-gap-plus">+</div>
        <span style="flex:1;color:var(--label);font-size:10px">${fmtM((gapEnd-gapStart)*60)} 空白 · 点击添加</span>
      </div>`;
    }
  }

  list.innerHTML = rows;
}"""

if OLD_LIST_RENDER in html:
    html = html.replace(OLD_LIST_RENDER, NEW_LIST_RENDER, 1)
    print("✓ renderDay updated with interactive rows")
else:
    print("✗ renderDay list block not found - trying partial match...")
    if "list.innerHTML = evs.map(ev =>" in html:
        print("  Found the map line - need to check surrounding context")

# ── 6. ADD arcCatLegend div in the HTML ─────────────────────────────────────
# Find the arc SVG container and add legend below it
OLD_ARC_CONTAINER = '<div id="dayArcSvg"></div>'
NEW_ARC_CONTAINER = '<div id="dayArcSvg"></div>\n    <div class="arc-cat-legend" id="arcCatLegend"></div>'
if OLD_ARC_CONTAINER in html:
    html = html.replace(OLD_ARC_CONTAINER, NEW_ARC_CONTAINER, 1)
    print("✓ Arc legend div added")
else:
    # Try alternative
    if 'id="dayArcSvg"' in html:
        print("  dayArcSvg found but container context different - skipping arc legend")

with open(SRC, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n✓ Saved. File size: {len(html):,} bytes")
