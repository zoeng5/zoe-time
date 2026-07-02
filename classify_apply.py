#!/usr/bin/env python3
"""用 classify-brain.json 给标题归类：overrides > rules(顺序) > fallback。供 refresh.py 调用。"""
import json, re, os
BASE=os.path.dirname(os.path.abspath(__file__))
BRAIN=json.load(open(f"{BASE}/classify-brain.json",encoding="utf-8"))
RULES=BRAIN["rules"]; OVR=BRAIN["overrides"]; FB=BRAIN["fallback"]
def classify(title):
    t=title.strip()
    if t in OVR: return OVR[t]["cat"], OVR[t]["sub"]
    low=t.lower()
    for r in RULES:
        hit=False
        lowns=low.replace(' ','')
        for kw in r.get("any",[]):
            if kw.lower() in low or kw.lower().replace(' ','') in lowns: hit=True; break
        if not hit and r.get("regex"):
            if re.search(r["regex"], t, re.I): hit=True
        if hit: return r["cat"], r["sub"]
    return FB["cat"], FB["sub"]
if __name__=="__main__":
    import re as _re
    h=open(f"{BASE}/index.html",encoding="utf-8").read()
    m=_re.search(r'const REAL_EVENTS = (\{.*?\n\});',h,_re.S).group(1)
    EVP=_re.compile(r'\{cat:"(\w+)",sub:"([^"]*)",title:"((?:[^"\\]|\\.)*?)",start:')
    LAB={k:v["label"] for k,v in BRAIN["categories"].items()}; LAB["unclassified"]="❓未分类"
    rows=[(t.replace('\\"','"'),) for _,_,t in EVP.findall(m)]
    from collections import Counter
    newc=Counter(); uncl=[]
    for (t,) in rows:
        c,s=classify(t); newc[c]+=1
        if c=="unclassified": uncl.append(t)
    print("=== 新分布（共%d条）==="%sum(newc.values()))
    for c,n in newc.most_common(): print(f"  {LAB.get(c,c):8} {n:3}  {'█'*int(n/3)}")
    print(f"\n=== 需 AI 兜底的（未命中规则）: {len(uncl)} 条 ===")
    for t in uncl[:40]: print("  ·", t[:50])
