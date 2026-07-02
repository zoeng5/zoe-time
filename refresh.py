#!/usr/bin/env python3
"""
Zoe 时间管理 App · 每日真实数据刷新（语义层归类版）
  1. 合并 App 回流的修正(corrections.json) 进语义层
  2. 拉飞书日历真实日程
  3. 归类：语义层(classify-brain.json) → AI 兜底(claude CLI) → 缓存回写
  4. 读 Oura/WHOOP 真实健康
  5. 渲染 itime App（爱时间 MTVI 复刻）→ index.html → 发布妙搭
用法：python3 refresh.py [--publish]
"""
import json, datetime, re, subprocess, glob, os, sys, time
import classify_apply, itime_build

TZ = datetime.timezone(datetime.timedelta(hours=8))
HOME = os.path.expanduser("~")
BASE = os.path.dirname(os.path.abspath(__file__))  # 脚本自身目录，抗迁移（勿写死 ~/mt-sites，已迁 ~/AI/Workspaces）
HTML = os.path.join(BASE, "index.html")
OURA_DIR = os.path.join(HOME, "AI/DataLake/健康/normalized/daily")
BRAIN_F = os.path.join(BASE, "classify-brain.json")
CORR_F = os.path.join(BASE, "corrections.json")
CAL_ID = "feishu.cn_hRTVlzvwWkrNRH4nSmIELg@group.calendar.feishu.cn"
APP_ID = "app_178sw3xwu14"
TODAY = datetime.datetime.now(TZ).date()
WIN_BACK, WIN_FWD = 190, 10   # 回看到年初（配合助理补全今年数据 + 洞察"年"维度）

ENV = {**os.environ, "NO_PROXY": "*", "no_proxy": "*"}
for k in ("HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","http_proxy","https_proxy","all_proxy"):
    ENV.pop(k, None)

# 行程不再当噪音（归差旅）；只丢真·非时间块的标记
NOISE = ["入住", "checked in", "确认号", "✅", "订阅号转号池"]

# ── 0. 合并 App 回流修正进语义层 overrides ───────────────────
def merge_corrections():
    if not os.path.exists(CORR_F): return 0
    try: corr = json.load(open(CORR_F, encoding="utf-8"))
    except Exception: return 0
    brain = json.load(open(BRAIN_F, encoding="utf-8"))
    n = 0
    for title, v in corr.items():
        if not v.get("cat"): continue
        brain["overrides"][title] = {"cat": v["cat"], "sub": v.get("sub",""), "_note": "App 回流"}
        n += 1
    if n:
        json.dump(brain, open(BRAIN_F,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
        classify_apply.BRAIN = brain
        classify_apply.RULES = brain["rules"]; classify_apply.OVR = brain["overrides"]
    return n

# ── 1. 拉日历 ────────────────────────────────────────────────
def fetch_window(s, e):
    args = ["lark-cli","calendar","+agenda","--calendar-id",CAL_ID,"--as","user",
            "--start",s.isoformat(),"--end",e.isoformat()]
    for _ in range(4):
        try:
            r = subprocess.run(args, capture_output=True, text=True, env=ENV, timeout=110, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            time.sleep(3); continue
        raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','?', r.stdout + r.stderr)
        try:
            d = json.loads(raw)
            if d.get("ok"): return d.get("data") or []
        except Exception: pass
        time.sleep(2)
    return []

def _dt(node):
    if not node: return None
    if node.get("datetime"): return datetime.datetime.fromisoformat(node["datetime"]).astimezone(TZ)
    if node.get("timestamp"): return datetime.datetime.fromtimestamp(int(node["timestamp"]), TZ)
    return None

def fetch_events():
    seen, evs = set(), []
    start = datetime.datetime.combine(TODAY - datetime.timedelta(days=WIN_BACK), datetime.time(0,0,tzinfo=TZ))
    end   = datetime.datetime.combine(TODAY + datetime.timedelta(days=WIN_FWD), datetime.time(23,59,tzinfo=TZ))
    cur = start
    while cur < end:
        seg = min(cur + datetime.timedelta(days=20), end)
        for it in fetch_window(cur, seg):
            st = it.get("start_time",{}) or {}
            if st.get("date") or not (st.get("datetime") or st.get("timestamp")): continue
            summ = (it.get("summary") or "").strip()
            if not summ or summ[0] in "⏰💸": continue
            if any(x in summ.lower() for x in NOISE): continue
            sdt, edt = _dt(it.get("start_time")), _dt(it.get("end_time"))
            if not sdt: continue
            if not edt: edt = sdt + datetime.timedelta(hours=1)
            dur = (edt - sdt).total_seconds()/3600
            if dur <= 0 or dur > 14: continue
            key = (summ, sdt.isoformat())
            if key in seen: continue
            seen.add(key)
            sh = round(sdt.hour + sdt.minute/60, 2)
            eh = 24.0 if edt.date()!=sdt.date() else round(edt.hour + edt.minute/60, 2)
            evs.append({"date": sdt.strftime("%Y-%m-%d"), "title": summ, "start": sh, "end": eh})
        cur = seg  # 推进窗口，否则死循环（曾被丢失）
    return evs

def tags_of(s):
    s, out = s.lower(), []
    if "ai" in s or "claude" in s: out.append("AI")
    if "don" in s: out.append("Don")
    if "olivia" in s: out.append("Olivia")
    if "george" in s or "小白" in s: out.append("George")
    if "max" in s or "小宝" in s: out.append("Max")
    return out

# ── 2. AI 兜底（仅未命中语义层的新标题）──────────────────────
def ai_classify(titles):
    if not titles: return {}
    brain = classify_apply.BRAIN
    desc = "\n".join(f'- {k} ({v["label"]}): {v["def"]}'
                     for k,v in brain["categories"].items() if k!="sleep")
    numbered = "\n".join(f"{i+1}. {t}" for i,t in enumerate(titles))
    prompt = ("你是 Zoe 的时间归类助手。把每个会议标题归到下面**唯一一个** key：\n"+desc+
              "\n\n只输出 JSON 数组，每项 {\"i\":序号(从1), \"cat\":\"key\", \"sub\":\"子类\"}，不要解释。\n标题：\n"+numbered)
    try:
        r = subprocess.run(["claude","-p",prompt,"--output-format","json","--model","claude-haiku-4-5-20251001"],
                           capture_output=True, text=True, env=ENV, timeout=150, stdin=subprocess.DEVNULL)
        env = json.loads(r.stdout)
        txt = env.get("result", r.stdout)
        arr = json.loads(re.search(r'\[.*\]', txt, re.S).group(0))
        out = {}
        for o in arr:
            i = int(o["i"])-1
            if 0 <= i < len(titles): out[titles[i]] = (o["cat"], o.get("sub",""))
        return out
    except Exception as e:
        print("  ! AI 兜底失败:", e, file=sys.stderr)
        return {}

# ── 3. 归类 + 组装 REAL_EVENTS ───────────────────────────────
def build_real(evs):
    # 先全部走语义层
    for e in evs:
        e["cat"], e["sub"] = classify_apply.classify(e["title"])
    # 收集未命中 → AI 兜底 → 写回 brain 缓存
    unc = sorted({e["title"] for e in evs if e["cat"]=="unclassified"})
    if unc:
        print(f"  语义层未命中 {len(unc)} 条 → AI 兜底")
        ai = ai_classify(unc)
        if ai:
            brain = json.load(open(BRAIN_F, encoding="utf-8"))
            for t,(c,s) in ai.items():
                brain["overrides"][t] = {"cat": c, "sub": s, "_note": "AI 判定"}
            json.dump(brain, open(BRAIN_F,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
            classify_apply.OVR = brain["overrides"]
        for e in evs:
            if e["cat"]=="unclassified":
                e["cat"], e["sub"] = ai.get(e["title"], ("operations","日常运营"))
    # 组 JS
    by = {}
    for e in evs:
        title = e["title"].replace('"','\\"').replace('\n',' ')
        if len(title) > 50: title = title[:47]+"..."
        by.setdefault(e["date"], []).append(
            {"cat":e["cat"],"sub":e["sub"],"title":title,"start":e["start"],"end":e["end"],"tags":tags_of(e["title"])})
    lines = ["const REAL_EVENTS = {"]
    for d in sorted(by):
        lines.append(f'  "{d}": [')
        for ev in sorted(by[d], key=lambda x:x["start"]):
            lines.append(f'    {{cat:"{ev["cat"]}",sub:"{ev["sub"]}",title:"{ev["title"]}",'
                         f'start:{ev["start"]},end:{ev["end"]},tags:{json.dumps(ev["tags"])}}},')
        lines.append("  ],")
    lines.append("};")
    return "\n".join(lines), len(evs), len(by)

def build_oura():
    rows = {}
    for f in glob.glob(f"{OURA_DIR}/20*/*.json"):
        try: d = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        date = d.get("date")
        # 用 WHOOP 数据（不用 Oura）；该日无 whoop 则跳过
        hrs = d.get("whoop_sleep_hours"); rec = d.get("whoop_recovery_score"); hrv = d.get("whoop_hrv_rmssd_ms")
        if not date or hrs is None or date < "2026-01-01": continue
        rows[date] = {"hrs":round(float(hrs),1),
                      "hrv":int(round(hrv)) if hrv is not None else 0,
                      "rec":int(round(rec)) if rec is not None else 0}
    lines = ["const OURA_DATA = {"]
    for d in sorted(rows):
        r = rows[d]; lines.append(f'  "{d}": {{hrs:{r["hrs"]},hrv:{r["hrv"]},rec:{r["rec"]}}},')
    lines.append("};")
    return "\n".join(lines), len(rows)

# ── 主流程 ──────────────────────────────────────────────────
def main():
    n = merge_corrections()
    if n: print(f"→ 合并 App 回流修正 {n} 条")
    print("→ 拉飞书日历…")
    evs = fetch_events()
    if not evs:
        print("  ! 0 事件，疑似拉取失败，放弃"); sys.exit(1)
    re_js, n_ev, n_day = build_real(evs)
    print(f"  真实事件 {n_ev} 条 / {n_day} 天")
    ou_js, n_ou = build_oura()
    print(f"  Oura/WHOOP {n_ou} 天")
    html = itime_build.render(re_js, ou_js)
    tmp = HTML + ".tmp"                       # 原子写：先落临时文件再 rename，杜绝半截/并发覆盖
    open(tmp, "w", encoding="utf-8").write(html)
    os.replace(tmp, HTML)
    print(f"✓ index.html（itime App）已生成 {len(html)} bytes")
    # 同步一份到 Mac 桌面 App 稳定路径（抗目录迁移，供原生 App 读取）
    try:
        import shutil as _sh
        appdir = os.path.expanduser("~/Library/Application Support/ZoeTime")
        os.makedirs(appdir, exist_ok=True)
        _sh.copy(HTML, os.path.join(appdir, "index.html"))
    except Exception as e:
        print("  ! 同步桌面 App 副本失败:", e)
    if "--publish" in sys.argv:
        print("→ 发布妙搭…")
        import shutil
        pub = os.path.join(BASE, ".publish"); os.makedirs(pub, exist_ok=True)
        shutil.copy(HTML, os.path.join(pub, "index.html"))
        r = subprocess.run(["lark-cli","apps","+html-publish","--app-id",APP_ID,"--path","./.publish"],
                           cwd=BASE, capture_output=True, text=True, env=ENV, timeout=120, stdin=subprocess.DEVNULL)
        print("  ", "发布成功" if '"ok": true' in r.stdout else r.stdout[:300])
        shutil.rmtree(pub, ignore_errors=True)

if __name__ == "__main__":
    # 并发锁：同一时刻只允许一个 refresh 跑，避免多进程抢写 index.html 互相覆盖
    import fcntl
    lock_path = os.path.join(BASE, ".refresh.lock")
    lock_fp = open(lock_path, "w")
    try:
        fcntl.flock(lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("⏭ 已有 refresh 在运行，本次跳过"); sys.exit(0)
    try:
        main()
    finally:
        fcntl.flock(lock_fp, fcntl.LOCK_UN); lock_fp.close()
