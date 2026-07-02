#!/usr/bin/env python3
"""Paginate Feishu calendar to find June 2026 events, save to /tmp/cal_jun2026.json"""
import subprocess, json, datetime, re, sys, time

CAL_ID = "feishu.cn_hRTVlzvwWkrNRH4nSmIELg@group.calendar.feishu.cn"
TZ = datetime.timezone(datetime.timedelta(hours=8))
TARGET_START = datetime.datetime(2026, 5, 1, 0, 0, tzinfo=TZ)
TARGET_END   = datetime.datetime(2026, 6, 25, 23, 59, tzinfo=TZ)
OUT_FILE = "/tmp/cal_jun2026.json"

def call_api(url, retries=3):
    for attempt in range(retries):
        try:
            r = subprocess.run(["lark-cli","api","GET",url,"--as","user"],
                               capture_output=True, text=True, timeout=45)
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '?', r.stdout)
            d = json.loads(text)
            return d
        except Exception as e:
            print(f"  attempt {attempt+1} error: {e}", flush=True)
            time.sleep(2)
    return {}

all_events = []
seen_ids = set()
sync_token = ""
page = 0
done = False

while not done:
    page += 1
    if sync_token:
        url = f"/open-apis/calendar/v4/calendars/{CAL_ID}/events?sync_token={sync_token}"
    else:
        url = f"/open-apis/calendar/v4/calendars/{CAL_ID}/events"

    d = call_api(url)
    items = d.get("data", {}).get("items", [])
    new_sync_token = d.get("data", {}).get("sync_token", "")
    has_more = d.get("data", {}).get("has_more", False)

    batch_events = []
    last_ts = 0
    first_ts = 0
    for ev in items:
        s_ts = int(ev.get("start_time", {}).get("timestamp", 0) or 0)
        e_ts = int(ev.get("end_time",   {}).get("timestamp", 0) or 0)
        eid  = ev.get("event_id", "")
        if not first_ts and s_ts: first_ts = s_ts
        if s_ts: last_ts = s_ts
        s_dt = datetime.datetime.fromtimestamp(s_ts, tz=TZ) if s_ts else None
        e_dt = datetime.datetime.fromtimestamp(e_ts, tz=TZ) if e_ts else None
        if s_dt and TARGET_START <= s_dt <= TARGET_END:
            if eid not in seen_ids and ev.get("status") != "cancelled":
                seen_ids.add(eid)
                batch_events.append({
                    "event_id": eid,
                    "summary": ev.get("summary", "(无标题)"),
                    "start_ts": s_ts,
                    "end_ts": e_ts,
                    "start": s_dt.strftime("%Y-%m-%d %H:%M") if s_dt else "",
                    "end":   e_dt.strftime("%H:%M") if e_dt else "",
                    "date":  s_dt.strftime("%Y-%m-%d") if s_dt else "",
                    "status": ev.get("status",""),
                })

    all_events.extend(batch_events)
    first_str = datetime.datetime.fromtimestamp(first_ts, tz=TZ).strftime("%Y-%m-%d") if first_ts else "?"
    last_str  = datetime.datetime.fromtimestamp(last_ts,  tz=TZ).strftime("%Y-%m-%d") if last_ts else "?"
    last_dt   = datetime.datetime.fromtimestamp(last_ts,  tz=TZ) if last_ts else None

    print(f"Page {page}: {len(items)} items | {first_str}→{last_str} | found={len(batch_events)} in-range | total={len(all_events)} | has_more={has_more}", flush=True)

    if not new_sync_token and not has_more:
        done = True
    elif not has_more:
        done = True
    elif last_dt and last_dt > TARGET_END:
        done = True
    elif new_sync_token:
        sync_token = new_sync_token
    else:
        done = True

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print(f"\n=== DONE: {len(all_events)} events saved to {OUT_FILE} ===", flush=True)
for ev in sorted(all_events, key=lambda e: e["start"]):
    print(f"  {ev['date']} {ev['start'][11:]} -{ev['end']} | {ev['summary'][:50]}")
