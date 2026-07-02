#!/usr/bin/env python3
"""Fetch recent calendar events via keyword search + freebusy for real June 2026 data"""
import subprocess, json, datetime, re

TZ = datetime.timezone(datetime.timedelta(hours=8))
TARGET_START = datetime.datetime(2026, 5, 1, tzinfo=TZ)
TARGET_END   = datetime.datetime(2026, 6, 25, 23, 59, tzinfo=TZ)
CAL_ID = "feishu.cn_hRTVlzvwWkrNRH4nSmIELg@group.calendar.feishu.cn"
OUT_FILE = "/tmp/cal_jun2026.json"

# Keywords covering common meeting types Zoe would have
KEYWORDS = [
    "",         # empty = general
    "周会", "例会", "月会", "季会",
    "touch base", "1on1", "1 on 1", "1-1", "meeting",
    "战略", "品牌", "产品", "运营", "财务",
    "MTI", "EC", "电商", "retail",
    "湖畔", "YPO", "培训", "学习",
    "孩子", "家庭", "school", "tour",
    "AI", "数智", "数字化",
    "review", "汇报", "沟通", "讨论",
    "blocked", "focus", "深度",
    "healthy", "运动", "健身",
]

def search(query):
    body = json.dumps({"query": query, "page_size": 100})
    r = subprocess.run(
        ["lark-cli", "api", "POST",
         f"/open-apis/calendar/v4/calendars/{CAL_ID}/events/search",
         "--as", "user", "--data", body],
        capture_output=True, text=True, timeout=20
    )
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '?', r.stdout + r.stderr)
    try:
        return json.loads(raw)
    except:
        return {}

seen_ids = set()
all_events = []

for kw in KEYWORDS:
    d = search(kw)
    items = d.get("data", {}).get("items", [])
    found = 0
    for ev in items:
        eid = ev.get("event_id", "")
        if eid in seen_ids:
            continue
        s_ts = int(ev.get("start_time", {}).get("timestamp", 0) or 0)
        e_ts = int(ev.get("end_time",   {}).get("timestamp", 0) or 0)
        if not s_ts:
            continue
        s_dt = datetime.datetime.fromtimestamp(s_ts, tz=TZ)
        e_dt = datetime.datetime.fromtimestamp(e_ts, tz=TZ) if e_ts else None
        if not (TARGET_START <= s_dt <= TARGET_END):
            continue
        if ev.get("status") == "cancelled":
            continue
        seen_ids.add(eid)
        found += 1
        all_events.append({
            "event_id": eid,
            "summary": ev.get("summary", "(无标题)"),
            "start_ts": s_ts,
            "end_ts":   e_ts,
            "start": s_dt.strftime("%Y-%m-%d %H:%M"),
            "end":   e_dt.strftime("%H:%M") if e_dt else "",
            "date":  s_dt.strftime("%Y-%m-%d"),
            "duration_min": (e_ts - s_ts) // 60 if e_ts else 0,
        })
    kw_label = repr(kw) if kw else '""'
    print(f'  {kw_label:20s} → {found} new | total={len(all_events)}')

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print(f"\n=== DONE: {len(all_events)} unique events ===")
by_date = {}
for ev in all_events:
    by_date.setdefault(ev["date"], []).append(ev)

for date in sorted(by_date):
    print(f"\n{date}:")
    for ev in sorted(by_date[date], key=lambda e: e["start"]):
        print(f"  {ev['start'][11:]}-{ev['end']} [{ev['duration_min']}min] {ev['summary'][:60]}")
