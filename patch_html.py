#!/usr/bin/env python3
"""Patch index.html: replace logo + inject real data + update genDay/genOura"""
import re, json

SRC = "/Users/zoe/mt-sites/bi-dashboards/mt-time-tracker/index.html"

with open(SRC, encoding="utf-8") as f:
    html = f.read()

# ── 1. Replace header logo (img → inline SVG) ──────────────────────────────
LOGO_SVG = '''<svg class="hdr-logo" viewBox="0 0 128 28" height="28" width="128" xmlns="http://www.w3.org/2000/svg">
      <circle cx="14" cy="14" r="9.5" fill="none" stroke="#EAE1D2" stroke-width="2.2"/>
      <path d="M 14 4.5 A 9.5 9.5 0 0 1 22.2 18.75" fill="none" stroke="#F37434" stroke-width="2.2" stroke-linecap="round"/>
      <line x1="14" y1="14" x2="9.2" y2="9.2" stroke="#1D1D1D" stroke-width="1.6" stroke-linecap="round"/>
      <line x1="14" y1="14" x2="14" y2="6.5" stroke="#1D1D1D" stroke-width="1.1" stroke-linecap="round"/>
      <circle cx="14" cy="14" r="1.4" fill="#1D1D1D"/>
      <text x="30" y="19" font-family="'Hanken Grotesk','Helvetica Neue',sans-serif" font-weight="600" font-size="15" letter-spacing="-0.4" fill="#1D1D1D">Zoe</text>
      <circle cx="61" cy="14" r="1.6" fill="#F37434"/>
      <text x="66" y="19" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-weight="300" font-size="13" letter-spacing="1.5" fill="#818A7D">时间</text>
    </svg>'''

# Replace <img class="hdr-logo" ... > (the whole img tag, which ends at the >)
html = re.sub(
    r'<img class="hdr-logo"[^>]+>',
    LOGO_SVG,
    html,
    count=1
)
print("✓ Header logo replaced")

# ── 2. Replace sidebar logo (img → inline SVG, white version) ──────────────
SB_LOGO_SVG = '''<svg class="sb-logo" viewBox="0 0 128 28" height="22" width="110" xmlns="http://www.w3.org/2000/svg">
    <circle cx="14" cy="14" r="9.5" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2.2"/>
    <path d="M 14 4.5 A 9.5 9.5 0 0 1 22.2 18.75" fill="none" stroke="#F37434" stroke-width="2.2" stroke-linecap="round"/>
    <line x1="14" y1="14" x2="9.2" y2="9.2" stroke="white" stroke-width="1.6" stroke-linecap="round"/>
    <line x1="14" y1="14" x2="14" y2="6.5" stroke="white" stroke-width="1.1" stroke-linecap="round"/>
    <circle cx="14" cy="14" r="1.4" fill="white"/>
    <text x="30" y="19" font-family="'Hanken Grotesk','Helvetica Neue',sans-serif" font-weight="600" font-size="15" letter-spacing="-0.4" fill="white">Zoe</text>
    <circle cx="61" cy="14" r="1.6" fill="#F37434"/>
    <text x="66" y="19" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-weight="300" font-size="13" letter-spacing="1.5" fill="rgba(255,255,255,0.7)">时间</text>
  </svg>'''

html = re.sub(
    r'<img class="sb-logo"[^>]*>',
    SB_LOGO_SVG,
    html,
    count=1
)
print("✓ Sidebar logo replaced")

# ── 3. Inject REAL_EVENTS + OURA_DATA constants before MOCK DATA section ───

# Load real events from classifier output
import subprocess, sys
result = subprocess.run(
    ["python3", "/Users/zoe/mt-sites/bi-dashboards/mt-time-tracker/classify_events.py"],
    capture_output=True, text=True
)
real_events_js = result.stdout.strip()

# Build OURA_DATA constant
import glob, os
oura_lines = ["const OURA_DATA = {"]
files = sorted(glob.glob(os.path.expanduser("~/AI/DataLake/健康/normalized/daily/2026/202*.json")))
for fp in files:
    date = os.path.basename(fp).replace(".json", "")
    try:
        with open(fp) as f2:
            d = json.load(f2)
        hrs = round(d.get("sleep_hours", 7.0), 1)
        hrv = round(d.get("hrv_ms", 50))
        rec = round(d.get("recovery_score", 70))
        oura_lines.append(f'  "{date}": {{hrs:{hrs},hrv:{hrv},rec:{rec}}},')
    except:
        pass
oura_lines.append("};")
oura_js = "\n".join(oura_lines)

injection = f"""
// ─────────────────────────────────────────
//  REAL DATA (calendar + Oura)
// ─────────────────────────────────────────
{real_events_js}

{oura_js}

"""

# Insert before "// ─────... MOCK DATA"
marker = "// ─────────────────────────────────────────\n//  MOCK DATA"
if marker in html:
    html = html.replace(marker, injection + marker, 1)
    print("✓ Real data injected")
else:
    print("✗ Could not find MOCK DATA marker!")

# ── 4. Update genOura to use real OURA_DATA ────────────────────────────────
OLD_GENOURA = """function genOura(dateStr) {
  const rand = seeded('o' + dateStr);
  return {
    hrs: +(7.0 + rand()*1.4 - 0.3).toFixed(1),
    hrv: 40 + Math.floor(rand()*24),
    rec: 65 + Math.floor(rand()*25),
  };
}"""

NEW_GENOURA = """function genOura(dateStr) {
  if (OURA_DATA[dateStr]) return OURA_DATA[dateStr];
  const rand = seeded('o' + dateStr);
  return {
    hrs: +(7.0 + rand()*1.4 - 0.3).toFixed(1),
    hrv: 40 + Math.floor(rand()*24),
    rec: 65 + Math.floor(rand()*25),
  };
}"""

if OLD_GENOURA in html:
    html = html.replace(OLD_GENOURA, NEW_GENOURA, 1)
    print("✓ genOura updated")
else:
    print("✗ genOura not found exactly")

# ── 5. Update genDay to use REAL_EVENTS ────────────────────────────────────
OLD_GENDAY_OPEN = """function genDay(dateStr) {
  const rand = seeded(dateStr);
  const d = new Date(dateStr + 'T00:00:00');
  const dow = d.getDay();
  const wknd = dow === 0 || dow === 6;
  const evs = [];

  const push = (cat, subCat, title, start, end, tags=[]) =>
    evs.push({cat, subCat, title, start, end, tags});

  const wake = 6.25 + rand() * 0.75;
  push('sleep', '', '睡眠', 0, wake);

  if (!wknd) {"""

NEW_GENDAY_OPEN = """function genDay(dateStr) {
  const rand = seeded(dateStr);
  const d = new Date(dateStr + 'T00:00:00');
  const dow = d.getDay();
  const wknd = dow === 0 || dow === 6;
  const evs = [];

  const push = (cat, subCat, title, start, end, tags=[]) =>
    evs.push({cat, subCat, title, start, end, tags});

  // Use real Oura sleep data when available
  const oura = OURA_DATA[dateStr];
  const sleepHrs = oura ? oura.hrs : (6.5 + rand() * 1.2);
  // Estimate wake time: typical bedtime ~22:30, wake = bedtime + sleepHrs - 24
  const wake = Math.min(9.5, Math.max(5.0, 6.0 + (7 - sleepHrs) * 0.3));
  push('sleep', '', '睡眠', 0, Math.round(wake * 4) / 4);

  // If real calendar events exist for this date, use them
  const realEvs = REAL_EVENTS[dateStr];
  if (realEvs && realEvs.length > 0) {
    // Add real events
    realEvs.forEach(ev => push(ev.cat, ev.sub, ev.title, ev.start, ev.end, ev.tags));
    // Morning filler if no early events
    const hasEarlyMtg = realEvs.some(e => e.start < 9.5);
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
    push('sleep', '', '入睡', Math.min(nightSleep, 23.5), 24);
    return evs.sort((a,b) => a.start - b.start);
  }

  if (!wknd) {"""

if OLD_GENDAY_OPEN in html:
    html = html.replace(OLD_GENDAY_OPEN, NEW_GENDAY_OPEN, 1)
    print("✓ genDay updated with real events support")
else:
    print("✗ genDay open block not found exactly - checking...")
    # Check for partial match
    if "const wake = 6.25 + rand() * 0.75;" in html:
        print("  Found wake line at some position")
    if "function genDay(dateStr)" in html:
        print("  Found function signature")

with open(SRC, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n✓ Saved. File size: {len(html):,} bytes")
