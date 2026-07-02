#!/usr/bin/env python3
"""Fetch June 2026 calendar events via POST search API"""
import subprocess, json, datetime, re, sys

CAL_ID = "feishu.cn_hRTVlzvwWkrNRH4nSmIELg@group.calendar.feishu.cn"
TZ = datetime.timezone(datetime.timedelta(hours=8))
TARGET_START = datetime.datetime(2026, 5, 1, tzinfo=TZ)
TARGET_END   = datetime.datetime(2026, 6, 25, 23, 59, tzinfo=TZ)
OUT_FILE = "/tmp/cal_jun2026.json"

all_events = []
seen_ids = set()
page_token = ""
page = 0

while True:
    page += 1
    body = {
        "query": "",
        "filter": {
            "start_time": {"timestamp": "1746028800"},  # 2026-05-01 CST
            "end_time": {"timestamp": "1750809600"}      # 2026-06-25 CST
        },
        "page_size": 100
    }
    if page_token:
        body["page_token"] = page_token

    body_str = json.dumps(body)
    r = subprocess.run(
        ["lark-cli", "api", "POST",
         f"/open-apis/calendar/v4/calendars/{CAL_ID}/events/search",
         "--as", "user", "--data", body_str],
        capture_output=True, text=True, timeout=45
    )
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '?', r.stdout)
    try:
        d = json.loads(raw)
    except Exception as e:
        print(f"Parse error page {page}: {e}")
        break

    items = d.get("data", {}).get("items", [])
    next_pt = d.get("data", {}).get("page_token", "")
    has_more = d.get("data", {}).get("has_more", False)

    batch = 0
    for ev in items:
        eid = ev.get("event_id", "")
        if eid in seen_ids:
            continue
        s_ts = int(ev.get("start_time", {}).get("timestamp", 0) or 0)
        e_ts = int(ev.get("end_time",   {}).get("timestamp", 0) or 0)
        if not s_ts:  # skip all-day or missing timestamp events
            continue
        s_dt = datetime.datetime.fromtimestamp(s_ts, tz=TZ)
        e_dt = datetime.datetime.fromtimestamp(e_ts, tz=TZ) if e_ts else None
        if not (TARGET_START <= s_dt <= TARGET_END):
            continue
        if ev.get("status") == "cancelled":
            continue
        seen_ids.add(eid)
        batch += 1
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

    print(f"Page {page}: {len(items)} items → {batch} in-range | total={len(all_events)} | has_more={has_more}")
    if not has_more or not next_pt:
        break
    page_token = next_pt

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print(f"\n=== DONE: {len(all_events)} events → {OUT_FILE} ===")
by_date = {}
for ev in sorted(all_events, key=lambda e: e["start"]):
    d = ev["date"]
    by_date.setdefault(d, []).append(ev)

for date in sorted(by_date):
    print(f"\n{date}:")
    for ev in by_date[date]:
        t = ev["start"][11:]
        dur = ev["duration_min"]
        print(f"  {t}-{ev['end']} [{dur}min] {ev['summary'][:60]}")
