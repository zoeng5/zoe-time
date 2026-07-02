#!/usr/bin/env python3
"""Patch 3: Pulse trend cards (sleep/exercise/family) in week view + overrides in aggregates"""

SRC = "/Users/zoe/mt-sites/bi-dashboards/mt-time-tracker/index.html"
with open(SRC, encoding="utf-8") as f:
    html = f.read()

# ── 1. CSS for trend cards ──────────────────────────────────────────────────
NEW_CSS = """
/* ── PULSE TREND CARDS ── */
.trend-card { background: var(--cloud); border: 1px solid var(--sand); border-radius: 14px; padding: 14px 15px 10px; margin-bottom: 12px; }
.trend-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 3px; }
.trend-name { font-size: 13px; font-weight: 700; letter-spacing: -0.01em; color: var(--ink); }
.trend-name .tn-icon { margin-right: 5px; }
.trend-avg { font-size: 18px; font-weight: 700; color: var(--ink); font-family: var(--font-display); font-variant-numeric: tabular-nums; }
.trend-avg .tn-unit { font-size: 11px; color: var(--label); font-weight: 500; margin-left: 1px; }
.trend-sub { display: flex; align-items: center; gap: 8px; font-size: 10px; color: var(--label); margin-bottom: 10px; font-family: var(--font-display); }
.trend-delta { font-weight: 600; }
.trend-delta.up { color: #5A8A70; }
.trend-delta.down { color: var(--tang); }
.trend-target { color: var(--label); }
.trend-chart { width: 100%; }
.trend-status { display:inline-block; font-size: 9px; padding: 1px 7px; border-radius: 9px; font-weight: 600; letter-spacing:.04em; }
.ts-good { background: #EAF7D4; color: #3A6B1A; }
.ts-warn { background: #FEF3E2; color: #9A5000; }
.ts-neutral { background: #EEF0EE; color: var(--moss); }
"""
html = html.replace('</style>', NEW_CSS + '\n</style>', 1)
print("✓ CSS added")

# ── 2. Add trends section to week view HTML (after the stack bar section) ────
OLD_WEEK_HTML = """  <div class="divider"></div>
  <div class="wk-bottom-section">
    <div class="sec-title">健康 · Oura</div>
    <div class="wk-cards-grid" id="wkHealth"></div>
  </div>"""
NEW_WEEK_HTML = """  <div class="divider"></div>
  <div class="section">
    <div class="sec-title">专题趋势 · 睡眠 / 运动 / 家庭</div>
    <div id="wkTrends"></div>
  </div>
  <div class="divider"></div>
  <div class="wk-bottom-section">
    <div class="sec-title">健康 · Oura</div>
    <div class="wk-cards-grid" id="wkHealth"></div>
  </div>"""
if OLD_WEEK_HTML in html:
    html = html.replace(OLD_WEEK_HTML, NEW_WEEK_HTML, 1)
    print("✓ Week trends section HTML added")
else:
    print("✗ Week HTML section not found!")

# ── 3. Helper: svgMetricTrend (single metric 7-day bars + avg line) ─────────
TREND_HELPER = """
// Apply localStorage edits to a day's events (used by aggregates)
function dayEvents(ds) {
  return applyOverrides(ds, genDay(ds));
}
// Sum minutes of a specific sub-category across a day
function subCatMins(evs, catKey, subName) {
  return evs.filter(e => e.cat === catKey && (e.subCat === subName || e.sub === subName))
            .reduce((s,e) => s + (e.end - e.start) * 60, 0);
}

// Single-metric 7-day trend: bars + dashed average line + optional target line
function svgMetricTrend(container, values, opts) {
  const o = opts || {};
  const color = o.color || '#1D1D1D';
  const labels = o.labels || values.map((_,i)=>i+1);
  const unit = o.unit || '';
  const target = o.target;
  const W = container.clientWidth || 320, H = 96;
  const PL = 6, PR = 24, PT = 10, PB = 18;
  const cW = W - PL - PR, cH = H - PT - PB;
  const avg = values.length ? values.reduce((s,v)=>s+v,0)/values.length : 0;
  const maxV = Math.max(1, ...values, avg, target || 0) * 1.12;
  const bW = cW / values.length;
  const bw = bW * 0.56;
  const today = new Date(); today.setHours(0,0,0,0);

  let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}">`;

  // Target line (faint)
  if (target != null) {
    const yT = PT + cH * (1 - target/maxV);
    svg += `<line x1="${PL}" y1="${yT}" x2="${PL+cW}" y2="${yT}" stroke="#C5C8C2" stroke-width="1" stroke-dasharray="2 3"/>`;
    svg += `<text x="${PL+cW+3}" y="${yT+3}" font-size="8" fill="#A9ADA4">目标</text>`;
  }

  // Bars
  values.forEach((v,i) => {
    const x = PL + i*bW + (bW-bw)/2;
    const h = Math.max(0, (v/maxV)*cH);
    const y = PT + cH - h;
    const isWeekend = (i===5 || i===6);
    svg += `<rect x="${x}" y="${y}" width="${bw}" height="${h}" fill="${color}" rx="2.5" opacity="${isWeekend?0.55:0.92}"/>`;
    // value label on top of bar
    const vLabel = o.decimals ? v.toFixed(o.decimals) : Math.round(v);
    if (v > 0) svg += `<text x="${x+bw/2}" y="${y-3}" text-anchor="middle" font-size="8" fill="#818A7D" font-family="var(--font-display)">${vLabel}</text>`;
    // day label
    svg += `<text x="${x+bw/2}" y="${H-5}" text-anchor="middle" font-size="9" fill="#818A7D">${labels[i]}</text>`;
  });

  // Average line (solid accent, drawn on top)
  const yAvg = PT + cH * (1 - avg/maxV);
  svg += `<line x1="${PL}" y1="${yAvg}" x2="${PL+cW}" y2="${yAvg}" stroke="${color}" stroke-width="1.2" stroke-dasharray="5 3" opacity="0.65"/>`;
  svg += `<text x="${PL+cW+3}" y="${yAvg+3}" font-size="8" fill="${color}" font-family="var(--font-display)">均</text>`;

  svg += '</svg>';
  container.innerHTML = svg;
}
"""
# Insert before svgStackBar
html = html.replace("function svgStackBar(container, days, cats) {",
                    TREND_HELPER + "\nfunction svgStackBar(container, days, cats) {", 1)
print("✓ svgMetricTrend helper added")

# ── 4. Render the 3 trend cards inside renderWeek ───────────────────────────
# Insert render logic right after wkHealth innerHTML assignment block.
# We'll inject after the avgRec computation block; simplest: after the line that
# sets document.getElementById('wkBarLegend').innerHTML ... we add trend render.

ANCHOR = """  document.getElementById('wkBarLegend').innerHTML = activeCats.map(c=>
    `<div style="display:flex;align-items:center;gap:5px;font-size:9px;color:var(--label);font-family:var(--font-display)"><div style="width:9px;height:9px;background:${c.color};border-radius:2px"></div>${c.label}</div>`
  ).join('');"""

TREND_RENDER = ANCHOR + """

  // ── PULSE TREND CARDS: sleep / exercise / family ──
  const dayLbls = ['一','二','三','四','五','六','日'];
  const dayEvsArr = Array.from({length:7},(_,i)=>dayEvents(dateStr(addDays(ws,i))));
  const prevEvsArr = Array.from({length:7},(_,i)=>dayEvents(dateStr(addDays(wsPrev,i))));

  // Sleep (Oura hours)
  const sleepVals = ouras.map(o=>o.hrs);
  const sleepAvg = sleepVals.reduce((a,b)=>a+b,0)/7;
  const prevSleep = Array.from({length:7},(_,i)=>genOura(dateStr(addDays(wsPrev,i))).hrs);
  const prevSleepAvg = prevSleep.reduce((a,b)=>a+b,0)/7;

  // Exercise (健身运动 minutes/day)
  const exVals = dayEvsArr.map(evs=>subCatMins(evs,'self','健身运动'));
  const exAvg = exVals.reduce((a,b)=>a+b,0)/7;
  const prevEx = prevEvsArr.map(evs=>subCatMins(evs,'self','健身运动'));
  const prevExAvg = prevEx.reduce((a,b)=>a+b,0)/7;

  // Family (minutes/day)
  const famVals = dayEvsArr.map(evs=>catMins(evs).family||0);
  const famAvg = famVals.reduce((a,b)=>a+b,0)/7;
  const famTotH = famVals.reduce((a,b)=>a+b,0)/60;
  const prevFam = prevEvsArr.map(evs=>catMins(evs).family||0);
  const prevFamTotH = prevFam.reduce((a,b)=>a+b,0)/60;

  const deltaSpan = (cur, prev, fmt, invert) => {
    const d = cur - prev;
    const good = invert ? d < 0 : d >= 0;
    const sign = d >= 0 ? '+' : '−';
    return `<span class="trend-delta ${good?'up':'down'}">${sign}${fmt(Math.abs(d))} vs 上周</span>`;
  };

  const trends = [
    {
      icon:'😴', name:'睡眠', color:'#7C9AAE',
      avg: sleepAvg.toFixed(1), unit:'h',
      vals: sleepVals, target: 7, decimals: 1,
      delta: deltaSpan(sleepAvg, prevSleepAvg, v=>v.toFixed(1)+'h'),
      status: sleepAvg>=7 ? ['ts-good','达标'] : sleepAvg>=6 ? ['ts-neutral','偏少'] : ['ts-warn','不足'],
      targetTxt: '目标 7h/晚',
    },
    {
      icon:'🏃', name:'运动', color:'#BEDA6E',
      avg: Math.round(exAvg), unit:'min',
      vals: exVals, target: 30, decimals: 0,
      delta: deltaSpan(exAvg, prevExAvg, v=>Math.round(v)+'m'),
      status: exAvg>=30 ? ['ts-good','达标'] : exAvg>=15 ? ['ts-neutral','偏少'] : ['ts-warn','需加强'],
      targetTxt: '目标 30min/天',
    },
    {
      icon:'👨‍👩‍👧', name:'家庭', color:'#C08060',
      avg: famTotH.toFixed(1), unit:'h/周',
      vals: famVals.map(v=>v/60), target: 10/7, decimals: 1,
      delta: deltaSpan(famTotH, prevFamTotH, v=>v.toFixed(1)+'h'),
      status: famTotH>=10 ? ['ts-good','达标'] : famTotH>=6 ? ['ts-neutral','尚可'] : ['ts-warn','偏少'],
      targetTxt: '目标 10h/周',
    },
  ];

  document.getElementById('wkTrends').innerHTML = trends.map((t,ti)=>{
    return `<div class="trend-card">
      <div class="trend-head">
        <div class="trend-name"><span class="tn-icon">${t.icon}</span>${t.name}</div>
        <div class="trend-avg">${t.avg}<span class="tn-unit">${t.unit}</span></div>
      </div>
      <div class="trend-sub">
        ${t.delta}
        <span class="trend-status ${t.status[0]}">${t.status[1]}</span>
        <span class="trend-target">${t.targetTxt}</span>
      </div>
      <div class="trend-chart" id="wkTrend_${ti}"></div>
    </div>`;
  }).join('');

  trends.forEach((t,ti)=>{
    const el = document.getElementById('wkTrend_'+ti);
    if (el) svgMetricTrend(el, t.vals, {color:t.color, unit:t.unit, labels:dayLbls, target:t.target, decimals:t.decimals});
  });
"""

if ANCHOR in html:
    html = html.replace(ANCHOR, TREND_RENDER, 1)
    print("✓ Trend cards render added to renderWeek")
else:
    print("✗ renderWeek anchor not found!")

# ── 5. Make week aggregates respect overrides (use dayEvents not genDay) ────
# Update days7/prev7 in renderWeek to apply overrides for accuracy
OLD_AGG = """  const days7 = Array.from({length:7},(_,i)=>({lbl:lbls[i], m:catMins(genDay(dateStr(addDays(ws,i))))}));
  const prev7 = Array.from({length:7},(_,i)=>catMins(genDay(dateStr(addDays(wsPrev,i)))));"""
NEW_AGG = """  const days7 = Array.from({length:7},(_,i)=>({lbl:lbls[i], m:catMins(dayEvents(dateStr(addDays(ws,i))))}));
  const prev7 = Array.from({length:7},(_,i)=>catMins(dayEvents(dateStr(addDays(wsPrev,i)))));"""
if OLD_AGG in html:
    html = html.replace(OLD_AGG, NEW_AGG, 1)
    print("✓ Week aggregates now respect overrides")

with open(SRC, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\n✓ Saved. File size: {len(html):,} bytes")
