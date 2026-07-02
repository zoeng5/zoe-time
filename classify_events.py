#!/usr/bin/env python3
"""Classify calendar events into v3 categories and generate JS REAL_EVENTS constant"""
import json, datetime, re

TZ = datetime.timezone(datetime.timedelta(hours=8))

with open("/tmp/cal_jun2026.json", encoding="utf-8") as f:
    events = json.load(f)

# Remove exact duplicates (same summary + same start)
seen = set()
unique = []
for ev in events:
    key = (ev["summary"].strip(), ev["start"])
    if key not in seen:
        seen.add(key)
        unique.append(ev)
events = unique

def classify(summary, duration_min):
    s = summary.lower()
    # SLEEP
    if any(x in s for x in ["sleep", "nap", "入睡"]):
        return "sleep", ""
    # FAMILY
    if any(x in s for x in ["school", "george", "max", "olivia", "xventure", "play date",
                              "kellett", "yvette", "mediterranean", "children", "孩子", "kids",
                              "child", "学期末", "欢送会"]):
        # check if it's yvette and george/max context
        if "yvette" in s or "george" in s or "max" in s or "kellett" in s or "school" in s:
            return "family", "亲子居家"
        return "family", "亲子居家"
    # GROWTH / learning
    if any(x in s for x in ["湖畔", "ypo", "ypoi", "研修班", "工作坊", "mot ", "腾讯咨询",
                              "课程", "游学", "胖东来", "案例交流", "风变", "消费者洞察",
                              "声誉与传播"]):
        if "湖畔" in s or "ypo" in s.lower():
            return "growth", "湖畔/YPO"
        if any(x in s for x in ["研修班", "工作坊", "课程", "游学", "胖东来", "案例交流",
                                  "消费者洞察", "声誉与传播", "腾讯咨询"]):
            return "growth", "课程学习"
        return "growth", "行业交流"
    # EXTERNAL relations
    if any(x in s for x in ["innoven", "nicef", "unicef", "morris mak", "鑫磊", "班主任",
                              "kpmg", "德勤", "deloitte", "simon", "fundraising", "行权",
                              "investor", "wind", "行业"]):
        if any(x in s for x in ["nicef", "unicef", "fundraising"]):
            return "external", "社会责任"
        if any(x in s for x in ["innoven", "行权", "investor"]):
            return "external", "投资人"
        if any(x in s for x in ["kpmg", "德勤", "deloitte"]):
            return "external", "合作伙伴"
        if "morris mak" in s or "ypo" in s:
            return "external", "合作伙伴"
        return "external", "合作伙伴"
    # PEOPLE / org talent
    if any(x in s for x in ["面试", "interview", "hiring", "招聘", "offer", "1 on 1", "1on1",
                              "1-1 with", "shirley", "judy", "touch base", "hey zoe",
                              "团建", "欢送"]):
        if any(x in s for x in ["面试", "interview", "hiring", "招聘", "offer"]):
            return "people", "招聘"
        if any(x in s for x in ["1 on 1", "1on1", "1-1", "shirley", "judy"]):
            return "people", "1-1"
        if any(x in s for x in ["hey zoe", "团建", "欢送"]):
            return "people", "团队文化"
        return "people", "高管团队"
    # GLOBAL business
    if any(x in s for x in ["mti", "global ec", "weekly mti", "international", "海外",
                              "us retail", "uk", "europe"]):
        return "global", "MTI EC"
    # PRODUCT / brand
    if any(x in s for x in ["mkt", "品牌", "营销", "产品", "拍摄", "内容", "creative",
                              "设计", "门店", "store bd", "发展历程", "retail bd"]):
        if any(x in s for x in ["mkt", "品牌", "营销", "拍摄", "内容", "发展历程"]):
            return "product", "品牌营销"
        if "产品" in s:
            return "product", "产品评审"
        return "product", "门店体验"
    # OPERATIONS / finance
    if any(x in s for x in ["财务", "finance", "bp ", "kpmg", "税务", "税", "会计",
                              "bi ", "数智化", "数字化", "ec电商", "电商周会", "运营",
                              "审批", "决策", "费控", "行权事项"]):
        if any(x in s for x in ["财务", "finance", "税务", "会计", "bp ", "行权事项"]):
            return "operations", "财务"
        if any(x in s for x in ["bi ", "数智化", "数字化"]):
            return "operations", "跨部门协同"
        if "ec电商" in s or "电商周会" in s:
            return "operations", "日常运营"
        return "operations", "日常运营"
    # STRATEGY (default for high-level meetings)
    if any(x in s for x in ["战略", "strategy", "ceo", "董事", "股东", "ai", "鞋", "reset",
                              "update", "weekly update", "ai 实战", "ai update", "ai catch",
                              "数智", "meet with jerry", "meeting with jerry"]):
        if "鞋战略" in s:
            return "strategy", "公司战略"
        if any(x in s for x in ["ai 实战", "ai实战", "ai update", "ai catch", "ai岗位"]):
            return "strategy", "战略研究"  # AI strategy is strategic work
        if "战略" in s:
            return "strategy", "公司战略"
        return "strategy", "战略研究"
    # Default: strategy/general work meeting
    return "strategy", "公司战略"

def get_tags(summary):
    tags = []
    s = summary.lower()
    if "ai" in s or "claude" in s:
        tags.append("AI")
    if "don" in s:
        tags.append("Don")
    if "olivia" in s:
        tags.append("Olivia")
    if "george" in s or "小白" in s:
        tags.append("George")
    if "max" in s or "小宝" in s:
        tags.append("Max")
    return tags

# Group and deduplicate by date + approximate time
classified = []
for ev in events:
    # Skip pure reminders (⏰ / 💸)
    if ev["summary"].startswith("⏰") or ev["summary"].startswith("💸"):
        continue
    cat, sub = classify(ev["summary"], ev["duration_min"])
    tags = get_tags(ev["summary"])

    # Convert timestamps to decimal hours
    s_dt = datetime.datetime.fromtimestamp(ev["start_ts"], tz=TZ)
    e_dt = datetime.datetime.fromtimestamp(ev["end_ts"], tz=TZ) if ev["end_ts"] else None

    start_h = s_dt.hour + s_dt.minute / 60
    end_h   = e_dt.hour + e_dt.minute / 60 if e_dt else start_h + ev["duration_min"]/60

    classified.append({
        "date": ev["date"],
        "cat": cat,
        "sub": sub,
        "title": ev["summary"],
        "start": round(start_h, 2),
        "end": round(end_h, 2),
        "tags": tags,
    })

# Group by date
by_date = {}
for ev in classified:
    by_date.setdefault(ev["date"], []).append(ev)

# Generate JS REAL_EVENTS constant
lines = ["const REAL_EVENTS = {"]
for date in sorted(by_date.keys()):
    evs = sorted(by_date[date], key=lambda e: e["start"])
    lines.append(f'  "{date}": [')
    for ev in evs:
        tags_str = json.dumps(ev["tags"])
        title = ev["title"].replace('"', '\\"').replace('\n', ' ')
        # Truncate long titles
        if len(title) > 50:
            title = title[:47] + "..."
        lines.append(f'    {{cat:"{ev["cat"]}",sub:"{ev["sub"]}",title:"{title}",start:{ev["start"]},end:{ev["end"]},tags:{tags_str}}},')
    lines.append("  ],")
lines.append("};")

js_output = "\n".join(lines)

with open("/tmp/real_events.js", "w", encoding="utf-8") as f:
    f.write(js_output)

print(js_output)
print(f"\n// Total: {len(classified)} events across {len(by_date)} days")
print(f"\n// Category breakdown:")
from collections import Counter
cats = Counter(ev["cat"] for ev in classified)
for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"//   {cat}: {cnt}")
