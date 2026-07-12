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
FREEZE_F = os.path.join(BASE, "frozen_events.json")  # 历史日程快照：定格后飞书同步不再覆盖
GRACE_DAYS = 2  # 过去 >2 天的日期视为「历史」，冻结不被覆盖；近 2 天+未来仍随飞书更新
CAL_ID = "feishu.cn_hRTVlzvwWkrNRH4nSmIELg@group.calendar.feishu.cn"
APP_ID = "app_178sw3xwu14"
TODAY = datetime.datetime.now(TZ).date()
WIN_BACK, WIN_FWD = 190, 10   # 回看到年初（配合助理补全今年数据 + 洞察"年"维度）

# ── 亲子陪伴同步：把「近30天·按孩子」陪伴时长写进「孩子成长记录」底座，供成长站实时读取 ──
KIDS_BASE  = "GkJrbJ5RHayVd5smEqxczeDvnWh"      # 数据底座「小朋友成长记录」
KIDS_TABLE = "tblactGVwPWxKjbv"                 # 🧡 亲子陪伴时长
COMP_STATE = os.path.join(BASE, ".companion_sync.json")  # 存单行 record_id，保证更新同一行不堆积
COMP_PEOPLE = ["Olivia", "George", "Max", "Donald", "父母"]

ENV = {**os.environ, "NO_PROXY": "*", "no_proxy": "*"}
for k in ("HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","http_proxy","https_proxy","all_proxy"):
    ENV.pop(k, None)

# 行程不再当噪音（归差旅）；只丢真·非时间块的标记
NOISE = ["入住", "checked in", "确认号", "✅", "订阅号转号池"]

def save_brain(brain):
    """原子写 + 滚动备份：这份手工语义层最贵，绝不能被半截写/并发写坏。"""
    try:
        import shutil
        if os.path.exists(BRAIN_F): shutil.copy(BRAIN_F, BRAIN_F + ".bak")
    except Exception: pass
    tmp = BRAIN_F + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fp:
        json.dump(brain, fp, ensure_ascii=False, indent=2)
    os.replace(tmp, BRAIN_F)

# ── 0. 合并 App 回流修正进语义层 overrides ───────────────────
SYNC_URL = "https://zoe-time-sync.zoe-mt.workers.dev"
ZT_TOKEN = "41326c953ec9ceb6227a27adc2cc83e583b9db05454e77f0"  # Worker 静态口令（与 itime_build.py 前端 / worker.js 同一值）

def _cloud_corrections():
    """拉云端(多维表格)里 Zoe+助理在 App 的改类修正——「越用越准」的回流源。"""
    try:
        import urllib.request
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # 绕过本机代理
        req = urllib.request.Request(SYNC_URL + "/sync",
            headers={"User-Agent": "Mozilla/5.0 zoe-time-refresh",   # 默认 UA 会被 Cloudflare 403
                     "X-ZT-Token": ZT_TOKEN})                        # Worker 已加鉴权，必须带口令
        d = json.load(opener.open(req, timeout=30))
        return {t: v for t, v in (d.get("corrections") or {}).items() if v.get("cat")}
    except Exception as e:
        print("  ! 云端修正拉取失败(跳过):", e); return {}

def merge_corrections():
    corr = _cloud_corrections()                     # 云端为主
    if os.path.exists(CORR_F):                      # 本地文件为辅(兼容旧通道)
        try: corr.update(json.load(open(CORR_F, encoding="utf-8")))
        except Exception: pass
    if not corr: return 0
    brain = json.load(open(BRAIN_F, encoding="utf-8"))
    n = 0
    for title, v in corr.items():
        if not v.get("cat"): continue
        prev = brain["overrides"].get(title)
        if prev and prev.get("cat") == v["cat"] and prev.get("sub") == v.get("sub",""): continue
        brain["overrides"][title] = {"cat": v["cat"], "sub": v.get("sub",""), "_note": "App 回流"}
        n += 1
    if n:
        save_brain(brain)
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
        for raw0 in (r.stdout, r.stdout + r.stderr):   # 先纯 stdout；stderr 有升级提示等噪音
            raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','?', raw0)
            try:
                d = json.loads(raw)
                if d.get("ok"): return d.get("data") or []
            except Exception: pass
        time.sleep(2)
    return None   # 4 次都失败 → 返回 None（区别于「该段确实没日程」的 []），供上层判定不完整

def _dt(node):
    if not node: return None
    if node.get("datetime"): return datetime.datetime.fromisoformat(node["datetime"]).astimezone(TZ)
    if node.get("timestamp"): return datetime.datetime.fromtimestamp(int(node["timestamp"]), TZ)
    return None

def fetch_events():
    seen, evs, incomplete = set(), [], False
    start = datetime.datetime.combine(TODAY - datetime.timedelta(days=WIN_BACK), datetime.time(0,0,tzinfo=TZ))
    end   = datetime.datetime.combine(TODAY + datetime.timedelta(days=WIN_FWD), datetime.time(23,59,tzinfo=TZ))
    cur = start
    while cur < end:
        seg = min(cur + datetime.timedelta(days=20), end)
        res = fetch_window(cur, seg)
        if res is None:            # 该段拉取失败（非空日程）→ 标记不完整，不能当没有数据
            incomplete = True
            print(f"  ! 日历段 {cur.date()}~{seg.date()} 拉取失败", file=sys.stderr)
            cur = seg; continue
        for it in res:
            st = it.get("start_time",{}) or {}
            if st.get("date") or not (st.get("datetime") or st.get("timestamp")): continue
            summ = (it.get("summary") or "").strip()
            if not summ or summ[0] in "⏰💸": continue
            # 噪音过滤豁免真航班：值机工具会给航班本体加【Checked in✅】前缀,但它是真差旅时间块
            _is_trip = ("→" in summ) or any(x in summ for x in ("机场","航空","航班","高铁","火车"))
            if any(x in summ.lower() for x in NOISE) and not _is_trip: continue
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
    return evs, incomplete

def tags_of(s):
    sl, out = s.lower(), []
    w = lambda pat: re.search(r"(?<![a-z])(?:%s)(?![a-z])" % pat, sl)  # 英文词边界，防 London→Don、maximum→Max
    if w("ai|claude|gpt|llm|chatgpt|copilot|midjourney") or any(k in sl for k in ("智能体","大模型","妙搭")): out.append("AI")
    if w("don|donald"): out.append("Donald")
    if any(k in sl for k in ("父母","爸妈","爸爸","妈妈","父亲","母亲")): out.append("父母")
    if w("olivia") or "小柚" in sl: out.append("Olivia")
    if w("george") or "小白" in sl: out.append("George")
    if w("max") or "小宝" in sl: out.append("Max")
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
    _valid = set(classify_apply.BRAIN["categories"].keys()) | {"travel"}
    for e in evs:
        e["cat"], e["sub"] = classify_apply.classify(e["title"])
        if e["cat"] not in _valid and e["cat"] != "unclassified":
            e["cat"], e["sub"] = "operations", "日常运营"   # 脏 cat 防线：绝不让未知类别进发布版
    # 收集未命中 → AI 兜底 → 写回 brain 缓存
    unc = sorted({e["title"] for e in evs if e["cat"]=="unclassified"})
    if unc:
        print(f"  语义层未命中 {len(unc)} 条 → AI 兜底")
        ai = ai_classify(unc)
        if ai:
            brain = json.load(open(BRAIN_F, encoding="utf-8"))
            valid = set(brain["categories"].keys())
            good = {t:(c,s) for t,(c,s) in ai.items() if c in valid}   # 只缓存合法类别，杜绝 AI 返回垃圾 key 污染语义层
            if len(good) != len(ai):
                print(f"  ! AI 返回 {len(ai)-len(good)} 条非法类别，已丢弃不缓存", file=sys.stderr)
            if good:
                for t,(c,s) in good.items():
                    brain["overrides"][t] = {"cat": c, "sub": s, "_note": "AI 判定"}
                save_brain(brain)
                classify_apply.OVR = brain["overrides"]
            ai = good
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
    # ── 历史冻结：过去 >GRACE_DAYS 天的日期一旦定格，飞书同步不再覆盖 ──
    # （保护 Zoe 人工修正过的历史；近端/未来仍随飞书刷新）
    cutoff = (TODAY - datetime.timedelta(days=GRACE_DAYS)).strftime("%Y-%m-%d")
    frozen = {}
    if os.path.exists(FREEZE_F):
        try: frozen = json.load(open(FREEZE_F, encoding="utf-8"))
        except Exception: frozen = {}
    out, changed, n_frozen = {}, False, 0
    for d in (set(by) | set(frozen)):
        if d < cutoff:                       # 历史：优先冻结版；没冻过就把当前版定格
            if d in frozen:
                out[d] = frozen[d]; n_frozen += 1
            else:
                out[d] = by[d]; frozen[d] = by[d]; changed = True; n_frozen += 1
        else:                                # 近端/未来：用最新飞书版，并持续刷新其快照基线
            if d in by:
                out[d] = by[d]
                if frozen.get(d) != by[d]: frozen[d] = by[d]; changed = True
            elif d in frozen:
                # 该日在飞书里已被整天清空（取消/改期）→ 冻结库同步删除，防止幽灵日程复活
                del frozen[d]; changed = True
    if changed:                              # 原子写冻结库
        json.dump(frozen, open(FREEZE_F+".tmp","w",encoding="utf-8"), ensure_ascii=False)
        os.replace(FREEZE_F+".tmp", FREEZE_F)
    print(f"  历史冻结 {n_frozen} 天（飞书同步不覆盖；如需重拉用 --rebaseline）")
    lines = ["const REAL_EVENTS = {"]
    for d in sorted(out):
        # 近重复去重：同标题且起点差<=0.35h(约21分钟)视为同一个会被挪动过的新旧两版，保留一条
        dedup = []
        for ev in sorted(out[d], key=lambda x:x["start"]):
            if any(p["title"]==ev["title"] and abs(p["start"]-ev["start"])<=0.35 for p in dedup): continue
            dedup.append(ev)
        out[d] = dedup
        lines.append(f'  "{d}": [')
        for ev in sorted(out[d], key=lambda x:x["start"]):
            lines.append(f'    {{cat:"{ev["cat"]}",sub:"{ev["sub"]}",title:"{ev["title"]}",'
                         f'start:{ev["start"]},end:{ev["end"]},tags:{json.dumps(ev["tags"])}}},')
        lines.append("  ],")
    lines.append("};")
    try:
        sync_companions(out)            # 顺手把按孩子陪伴时长同步进成长站底座（失败绝不影响主流程）
    except Exception as e:
        print("  ! 亲子陪伴同步失败(不影响发布):", e, file=sys.stderr)
    return "\n".join(lines), sum(len(v) for v in out.values()), len(out)

def _cloud_sync():
    """拉云端全量同步数据（manual/corrections/deleted/edits），复用前端 genDay 的合并口径。"""
    import urllib.request
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(SYNC_URL + "/sync",
        headers={"User-Agent": "Mozilla/5.0 zoe-time-refresh", "X-ZT-Token": ZT_TOKEN})
    return json.load(opener.open(req, timeout=30))

def _jsnum(x):
    """把小时数格式化成与前端 JS `''+start` 一致的字符串，用于 delKey 匹配 DELETED/EDITS。"""
    if x == int(x): return str(int(x))
    return ("%.2f" % x).rstrip("0").rstrip(".")

def sync_companions(out):
    """完全复刻 Zoe·时间 前端 genDay 的合并口径：REAL_EVENTS(日历)去掉 DELETED、套 CORR(改类/点名孩子)
    与 EDITS(改时段)、再并入 MANUAL(App 补录)，近30天按人累计(今天截到此刻、多标签各记一遍)。"""
    now = datetime.datetime.now(TZ)
    win_start = TODAY - datetime.timedelta(days=29)   # 近30天（含今天）
    CORR, DELETED, EDITS, MANUAL = {}, set(), {}, {}
    try:
        d = _cloud_sync()
        for t, v in (d.get("corrections") or {}).items():
            CORR[t] = {"kids": [x for x in str(v.get("kids") or "").split(",") if x]}
        DELETED = set(d.get("deleted") or [])
        for k, v in (d.get("edits") or {}).items():
            EDITS[k] = {"start": (float(v["start"]) if v.get("start") is not None else None),
                        "end":   (float(v["end"])   if v.get("end")   is not None else None)}
        for ds, evs in (d.get("manual") or {}).items():
            for e in (evs or []):
                try: s, en = float(e["start"]), float(e["end"])
                except Exception: continue
                MANUAL.setdefault(ds, []).append(
                    {"start": s, "end": en, "tags": [x for x in str(e.get("kids") or "").split(",") if x]})
    except Exception as e:
        print("  ! 陪伴同步：拉取云端修正/补录失败，仅用日历:", e, file=sys.stderr)

    kh = {p: 0.0 for p in COMP_PEOPLE}
    days = [TODAY - datetime.timedelta(days=i) for i in range(30)]   # 近30天
    for d0 in days:
        dstr = d0.isoformat()
        bound = 24.0 if d0 < TODAY else (now.hour + now.minute / 60)   # 今天只算到此刻，未来不计
        if bound <= 0: continue
        merged = []
        for e in out.get(dstr, []):                                    # 日历事件：去删除 + 套 CORR/EDITS
            title, start = e.get("title", ""), e["start"]
            if f"{dstr}|{title}|{_jsnum(start)}" in DELETED: continue
            cr = CORR.get(title)
            tags = set(e.get("tags") or [])
            if cr and cr["kids"]: tags |= set(cr["kids"])
            ed = EDITS.get(f"{dstr}|{title}|{_jsnum(start)}", {})
            st = ed["start"] if ed.get("start") is not None else start
            en = ed["end"]   if ed.get("end")   is not None else e["end"]
            merged.append((st, en, tags))
        for e in MANUAL.get(dstr, []):                                 # App 补录事件
            merged.append((e["start"], e["end"], set(e["tags"])))
        for st, en, tags in merged:
            if st >= bound: continue
            du = min(en, bound) - st
            if du <= 0: continue
            for t in tags:
                if t in kh: kh[t] += du
    epoch = int(datetime.datetime.combine(TODAY, datetime.time(0, 0, tzinfo=TZ)).timestamp() * 1000)
    fields = {"截止日期 Date": epoch, "窗口天数 Window": 30,
              "Olivia": round(kh["Olivia"], 1), "George": round(kh["George"], 1), "Max": round(kh["Max"], 1),
              "Donald": round(kh["Donald"], 1), "父母 Parents": round(kh["父母"], 1),
              "备注 Notes": f"自动同步自 Zoe·时间 (refresh.py) · 近30天截至 {now:%Y-%m-%d %H:%M}"}
    rid = None
    if os.path.exists(COMP_STATE):
        try: rid = json.load(open(COMP_STATE, encoding="utf-8")).get("record_id")
        except Exception: pass

    def _upsert(with_rid):
        args = ["lark-cli", "base", "+record-upsert", "--base-token", KIDS_BASE,
                "--table-id", KIDS_TABLE, "--as", "user", "--json", json.dumps(fields, ensure_ascii=False)]
        if with_rid: args += ["--record-id", with_rid]
        r = subprocess.run(args, capture_output=True, text=True, env=ENV, timeout=60, stdin=subprocess.DEVNULL)
        try: j = json.loads(r.stdout)
        except Exception: j = {}
        return j

    j = _upsert(rid)
    ok = bool(j.get("ok"))
    if not ok and rid:                 # 存的 record_id 已失效（被删）→ 新建一行并回存
        j = _upsert(None); ok = bool(j.get("ok"))
    if ok:
        # 从返回里取 record_id 回存（新建时才变；更新时保持不变）
        rec = (j.get("data") or {}).get("record") or {}
        new_rid = rec.get("record_id") or rid
        if new_rid and new_rid != rid:
            json.dump({"record_id": new_rid}, open(COMP_STATE, "w", encoding="utf-8"))
        print(f"  ✓ 亲子陪伴已同步成长站底座：" + " / ".join(f"{p} {round(kh[p],1)}h" for p in COMP_PEOPLE))
    else:
        print("  ! 亲子陪伴同步未成功:", json.dumps(j, ensure_ascii=False)[:200], file=sys.stderr)

def _whoop_sleep_times():
    """从原始 WHOOP 记录提取真实入睡/起床本地时刻 + 回填数据（绝不估计）。
    返回 {date: {"wake","bs","nb","hrs_raw","rec_raw","hrv_raw"}}。
    回填用途：健康归档 normalized 层按 UTC 切日，起床早于北京 08:00 的晚上会被记到前一天，
    导致当天 hrs=None（如 6/30）——这里按 +8 切日直接从 raw 算，堵住这个洞。"""
    raw_dir = os.path.join(HOME, "AI/DataLake/健康/raw/whoop")
    # 1) 按 id 去重（多导出文件重叠），updated_at 最新者胜
    def _load(sub):
        byid = {}
        for f in glob.glob(os.path.join(raw_dir, sub, "*.json")):
            try: recs = json.load(open(f, encoding="utf-8"))
            except Exception: continue
            if isinstance(recs, dict): recs = recs.get("records") or recs.get("data") or []
            for r in recs:
                k = r.get("id") or (r.get("cycle_id"), r.get("start"))
                if k not in byid or (r.get("updated_at","") > byid[k].get("updated_at","")): byid[k] = r
        return list(byid.values())
    sleeps = _load("sleep")
    recov = {}
    for r in _load("recovery"):
        sc = r.get("score") or {}
        if r.get("cycle_id") is not None and sc.get("recovery_score") is not None:
            recov[r["cycle_id"]] = (sc["recovery_score"], sc.get("hrv_rmssd_milli"))
    out = {}
    main = {}   # date -> 主觉记录(最长非小睡)
    for r in sleeps:
        if r.get("nap"): continue
        try:
            sdt = datetime.datetime.fromisoformat(r["start"].replace("Z","+00:00")).astimezone(TZ)
            edt = datetime.datetime.fromisoformat(r["end"].replace("Z","+00:00")).astimezone(TZ)
        except Exception: continue
        dE = edt.strftime("%Y-%m-%d"); dS = sdt.strftime("%Y-%m-%d")
        wh = round(edt.hour + edt.minute/60, 2); sh = round(sdt.hour + sdt.minute/60, 2)
        ent = out.setdefault(dE, {})
        if ent.get("wake") is None or wh > ent["wake"]: ent["wake"] = wh
        if dS == dE: ent["bs"] = sh
        else: out.setdefault(dS, {})["nb"] = sh
        dur = (edt - sdt).total_seconds()
        if dE not in main or dur > main[dE][0]: main[dE] = (dur, r)
    # 2) 回填：真实睡眠时长(浅+REM+深) + 恢复分/HRV(按 cycle_id 关联)
    for dE, (_, r) in main.items():
        ss = ((r.get("score") or {}).get("stage_summary")) or {}
        ms = (ss.get("total_light_sleep_time_milli",0) + ss.get("total_rem_sleep_time_milli",0)
              + ss.get("total_slow_wave_sleep_time_milli",0))
        if ms > 0: out[dE]["hrs_raw"] = round(ms/3600000, 1)
        rv = recov.get(r.get("cycle_id"))
        if rv:
            out[dE]["rec_raw"] = rv[0]
            if rv[1] is not None: out[dE]["hrv_raw"] = rv[1]
    return out

def build_oura():
    rows = {}
    times = _whoop_sleep_times()
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
    for d, t in times.items():                # 真实起止时刻并入（可能比 normalized 多出当天）
        if d < "2026-01-01": continue
        row = rows.setdefault(d, {"hrs":0,"hrv":0,"rec":0})
        row.update({k:v for k,v in t.items() if v is not None and k in ("wake","bs","nb")})
        # 回填：normalized 因 UTC 切日丢掉的当天数据，用 raw 补齐（真实分期时长/恢复分，非估计）
        if not row.get("hrs") and t.get("hrs_raw"): row["hrs"] = t["hrs_raw"]
        if not row.get("rec") and t.get("rec_raw") is not None: row["rec"] = int(round(t["rec_raw"]))
        if not row.get("hrv") and t.get("hrv_raw") is not None: row["hrv"] = int(round(t["hrv_raw"]))
    lines = ["const OURA_DATA = {"]
    for d in sorted(rows):
        r = rows[d]
        ext = "".join(f',{k}:{r[k]}' for k in ("wake","bs","nb") if r.get(k) is not None)
        lines.append(f'  "{d}": {{hrs:{r["hrs"]},hrv:{r["hrv"]},rec:{r["rec"]}{ext}}},')
    lines.append("};")
    return "\n".join(lines), len(rows)

# ── 主流程 ──────────────────────────────────────────────────
def main():
    if "--rebaseline" in sys.argv and os.path.exists(FREEZE_F):
        import shutil as _sh2
        _sh2.copy(FREEZE_F, FREEZE_F + ".bak")   # 先备份，误操作可救
        os.remove(FREEZE_F); print("→ 已清空历史冻结库（已备份 .bak），本次从飞书全量重拉重建")
    n = merge_corrections()
    if n: print(f"→ 合并 App 回流修正 {n} 条")
    print("→ 拉飞书日历…")
    evs, incomplete = fetch_events()
    if not evs:
        print("  ! 0 事件，疑似拉取失败，放弃"); sys.exit(1)
    if incomplete:
        # 有分段拉取失败 → 宁可保留上次完整结果，也不用残缺数据覆盖本地/线上（对齐「只呈现真实」）
        print("  ! 日历部分段拉取失败，为避免残缺数据覆盖，保留上次结果并退出"); sys.exit(1)
    re_js, n_ev, n_day = build_real(evs)   # build_real 内部已顺带同步亲子陪伴到成长站底座
    print(f"  真实事件 {n_ev} 条 / {n_day} 天")
    if "--sync-only" in sys.argv:          # 只同步亲子陪伴、不重建 HTML / 不上传 / 不发布
        print("→ --sync-only：已完成日历拉取与陪伴同步，跳过 HTML 重建/上传/发布"); return
    ou_js, n_ou = build_oura()
    print(f"  Oura/WHOOP {n_ou} 天")
    if n_ou < 30:
        print(f"  ! 健康数据仅 {n_ou} 天(<30)，疑似本机数据不全——拒绝发布/上传，防止贫血版本覆盖线上", file=sys.stderr)
        sys.exit(1)
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
    # 上传到 Worker /html（KV）——MacBook 桌面 App 的远程数据源（管线迁 Studio 后靠这个更新）
    try:
        import urllib.request
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(SYNC_URL + "/html", data=html.encode("utf-8"), method="PUT",
            headers={"User-Agent": "Mozilla/5.0 zoe-time-refresh", "X-ZT-Token": ZT_TOKEN})
        opener.open(req, timeout=60)
        print("  ✓ 已上传 Worker /html（桌面 App 远程源）")
    except Exception as e:
        print("  ! Worker /html 上传失败(不影响发布):", e)
    if "--publish" in sys.argv:
        print("→ 发布妙搭…")
        import shutil
        pub = os.path.join(BASE, ".publish"); os.makedirs(pub, exist_ok=True)
        shutil.copy(HTML, os.path.join(pub, "index.html"))
        r = subprocess.run(["lark-cli","apps","+html-publish","--app-id",APP_ID,"--path","./.publish"],
                           cwd=BASE, capture_output=True, text=True, env=ENV, timeout=120, stdin=subprocess.DEVNULL)
        shutil.rmtree(pub, ignore_errors=True)
        ok = r.returncode == 0
        try: ok = ok and bool(json.loads(r.stdout).get("ok"))
        except Exception: ok = ok and ('"ok": true' in r.stdout)
        if ok:
            print("   发布成功")
        else:
            print("  ! 发布失败:", (r.stdout or r.stderr or "")[:300], file=sys.stderr); sys.exit(1)

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
