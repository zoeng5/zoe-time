#!/usr/bin/env python3
"""复刻「爱时间」：24h 时钟盘 + 时间线 + 统计 + 目标，用 Zoe 的真实数据。
   输出 demos/itime.html（验证用）；满意后 promote 到 index.html。"""
import re, os, base64
HOME=os.path.expanduser("~"); BASE=os.path.dirname(os.path.abspath(__file__))  # 脚本自身目录，抗迁移
src=open(f"{BASE}/index.pre-redesign.html",encoding="utf-8").read()
def g(p):
    m=re.search(p,src,re.S)
    if not m: raise SystemExit("miss "+p[:30])
    return m.group(1)
FAV="data:image/png;base64,"+base64.b64encode(open(f"{BASE}/icon.png","rb").read()).decode()  # 新 logo B
CATS=g(r'(const CATS = \[.*?\n\];)')
REAL=g(r'(const REAL_EVENTS = \{.*?\n\};)')
OURA=g(r'(const OURA_DATA = \{.*?\n\};)')

HTML=r'''<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="时间">
<meta name="theme-color" content="#1D1D1D">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0">
<title>Zoe · 时间</title>
<link rel="icon" type="image/png" href="__FAV__"><link rel="apple-touch-icon" href="__FAV__">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600;700;800&family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
:root{--mid:#1D1D1D;--tang:#F37434;--lime:#BEDA6E;--sand:#EAE1D2;
 --ink:#1D1D1D;--mut:#8A8475;--mut2:#C2BCAD;--line:#ECE4D8;--bg:#FBFAF6;--soft:#F2ECE0}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{font-family:'Hanken Grotesk','Noto Sans SC',-apple-system,'PingFang SC',sans-serif;background:#E6E0D3;color:var(--ink);-webkit-font-smoothing:antialiased}
.phone{max-width:440px;margin:0 auto;min-height:100vh;background:var(--bg);display:flex;flex-direction:column;position:relative;box-shadow:0 0 40px rgba(29,29,29,.08)}
/* header */
.hdr{background:var(--mid);color:#FAFBF9;padding:calc(14px + env(safe-area-inset-top)) 16px 14px;display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:10}
.hdr .nav{display:flex;align-items:center;gap:14px;margin:0 auto}
.hdr .nav b{font-size:17px;font-weight:800;min-width:78px;text-align:center}
.hdr .nav span{font-size:11px;opacity:.85;display:block;font-weight:500}
.hdr .a{width:30px;height:30px;border-radius:9px;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;border:0;color:#fff}
.hdr .a:active{background:rgba(255,255,255,.3)}
.body{flex:1;padding-bottom:76px;overflow-x:hidden}
/* clock */
.clockwrap{display:flex;flex-direction:column;align-items:center;padding:18px 0 6px}
.clock{position:relative;width:300px;height:300px}
.clock svg{width:300px;height:300px;display:block}
.clock .ctr{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;pointer-events:none}
.clock .ctr .rg{font-size:14px;color:var(--mut);font-variant-numeric:tabular-nums;font-weight:600}
.clock .ctr .lb{font-size:12px;color:var(--mut);margin-top:9px}
.clock .ctr .big{font-size:26px;font-weight:800;margin-top:2px;letter-spacing:-.01em}
/* health + role overview */
.ov{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-top:8px}
.ovi{background:var(--bg);padding:13px 6px;text-align:center}
.ovi b{font-size:21px;font-weight:800;letter-spacing:-.01em;display:block;line-height:1}
.ovi b i{font-size:13px;font-style:normal;color:var(--mut);font-weight:700}
.ovi span{font-size:11px;color:var(--mut);font-weight:600;margin-top:4px;display:block}
.rcheck{display:flex;align-items:center;gap:10px 14px;flex-wrap:wrap;padding:11px 18px;background:var(--soft);border-bottom:1px solid var(--line);font-size:12.5px;font-weight:600;color:var(--ink)}
.rcheck .rlab{font-weight:800;font-size:10px;letter-spacing:.05em;color:var(--mut)}
.rcheck .rc-i b{font-weight:800;font-variant-numeric:tabular-nums}
.rcheck .rc-i b.g{color:#5E9C6B}.rcheck .rc-i b.w{color:#C2562F}
/* timeline list */
.tl{padding:6px 0 10px}
.tli{display:flex;align-items:center;gap:13px;padding:13px 18px;border-top:1px solid var(--line);cursor:pointer}
.tli:active{background:var(--soft)}
.tli .tm{font-size:12px;color:var(--mut);font-variant-numeric:tabular-nums;width:48px;line-height:1.5;font-weight:600}
.tli .dot{width:11px;height:11px;border-radius:50%;flex:none}
.tli .nm{font-size:15px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tli .du{font-size:12.5px;color:var(--mut);font-weight:600;white-space:nowrap}
.tli .ch{color:var(--mut2);font-size:16px}
.tl .empty{text-align:center;color:var(--mut2);font-size:14px;padding:36px 0}
.tl .gap{margin:6px 16px;padding:11px 14px;border:1.5px dashed var(--sand);border-radius:12px;color:#A99C86;font-size:12.5px;font-weight:600;cursor:pointer;text-align:center}
.tl .gap:active{background:var(--soft)}
.tli .mtag{font-size:9.5px;font-weight:800;color:var(--tang);background:#FBEEE3;padding:1px 6px;border-radius:6px;margin-left:6px;vertical-align:middle}
.fab{position:fixed;right:calc(50% - 220px + 18px);bottom:90px;width:54px;height:54px;border-radius:50%;border:0;background:var(--tang);color:#fff;font-size:28px;font-weight:300;line-height:1;cursor:pointer;box-shadow:0 6px 18px rgba(243,116,52,.42);z-index:25;display:flex;align-items:center;justify-content:center}
.fab:active{transform:scale(.94)}
@media(max-width:472px){.fab{right:18px}}
/* stats */
.seg2{display:flex;gap:6px;padding:14px 16px 4px}
.seg2 button{flex:1;border:0;background:var(--soft);color:var(--mut);font-family:inherit;font-weight:700;font-size:14px;padding:9px 0;border-radius:11px;cursor:pointer}
.seg2 button.on{background:var(--mid);color:#FAFBF9}
.sthdr{display:flex;justify-content:space-between;padding:14px 18px 6px;font-size:12.5px;color:var(--mut);font-weight:600}
.srow{padding:13px 18px;border-top:1px solid var(--line)}
.srow .t{display:flex;align-items:center;gap:9px;margin-bottom:9px}
.srow .dot{width:11px;height:11px;border-radius:50%}.srow .nm{font-size:15px;font-weight:700}
.srow .du{font-size:12.5px;color:var(--mut);font-weight:500;margin-left:2px}
.srow .pc{margin-left:auto;font-size:15px;font-weight:800;font-variant-numeric:tabular-nums}
.srow .bar{height:7px;border-radius:5px;background:var(--soft);overflow:hidden}
.srow .bar i{display:block;height:100%;border-radius:5px}
.srow-u{cursor:pointer}.srow-u:active{background:var(--soft)}
.srow-u .uadd{font-size:9.5px;font-weight:800;color:var(--tang);background:#FBEEE3;padding:1px 7px;border-radius:6px;margin-left:7px;vertical-align:middle}
.snote{font-size:12px;color:var(--mut);line-height:1.65;margin:14px 18px 4px;padding-top:12px;border-top:1px solid var(--line)}
.snote b{color:var(--ink);font-weight:800}
/* goals */
.goals{padding:14px 16px}
.gcard{border-radius:18px;padding:16px 18px;margin-bottom:12px;color:#fff;position:relative;overflow:hidden}
.gcard .gn{font-size:17px;font-weight:800}
.gcard .gg{font-size:12.5px;opacity:.92;margin-top:4px;font-weight:600;display:flex;align-items:center;gap:8px}
.gcard .now{font-size:12.5px;opacity:.92;font-weight:600}
.gcard .ring{position:absolute;right:18px;top:50%;transform:translateY(-50%);width:54px;height:54px}
.gcard .ring .pv{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800}
.gcard{cursor:pointer}
.goalhint{font-size:12px;color:var(--mut);padding:14px 18px 2px;font-weight:600}
.ge-row{display:flex;gap:8px;margin-bottom:14px}
.ge-p{flex:1;padding:11px;border:1px solid var(--line);border-radius:12px;background:var(--bg);font-family:inherit;font-weight:700;font-size:14px;color:var(--mut);cursor:pointer}
.ge-p.on{background:var(--mid);color:#FAFBF9;border-color:var(--mid)}
.ge-stepper{display:flex;align-items:center;gap:14px;margin-bottom:14px}
.ge-stepper button{width:52px;height:52px;border-radius:14px;border:1px solid var(--line);background:var(--soft);font-size:26px;font-weight:300;color:var(--ink);cursor:pointer}
.ge-stepper button:active{background:var(--sand)}
.ge-val{flex:1;text-align:center;font-size:22px;font-weight:800;font-variant-numeric:tabular-nums}
/* 类别详情 + 趋势 */
.detail{position:fixed;inset:0;max-width:440px;margin:0 auto;background:var(--bg);z-index:50;display:flex;flex-direction:column;animation:up .2s ease}
.detail .dhead{display:flex;align-items:center;background:var(--mid);color:#FAFBF9;padding:calc(14px + env(safe-area-inset-top)) 14px 14px}
.detail .dhead b{margin:0 auto;font-size:16px;font-weight:800}
.detail .dhead button{background:none;border:0;color:#FAFBF9;font-family:inherit;font-size:14px;font-weight:700;cursor:pointer;opacity:.92}
.detail .dbody{padding:18px 18px 30px;overflow-y:auto}
.dstat{display:flex;gap:10px;margin-bottom:22px}
.dstat .ds{flex:1;background:var(--soft);border-radius:13px;padding:13px 8px;text-align:center}
.dstat .ds b{font-size:19px;font-weight:800;display:block;font-variant-numeric:tabular-nums}
.dstat .ds b.up{color:#5E9C6B}.dstat .ds b.dn{color:#C2562F}
.dstat .ds span{font-size:10.5px;color:var(--mut);font-weight:600;margin-top:3px;display:block}
.dtt{font-size:12.5px;color:var(--mut);font-weight:600;margin-bottom:10px}
.trend{position:relative;height:200px;display:flex;align-items:flex-end;gap:5px;border-bottom:1px solid var(--line);padding-bottom:0}
.trend .goalline{position:absolute;left:0;right:0;border-top:1.5px dashed var(--mid);opacity:.55;z-index:1}
.trend .tcol{flex:1;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:4px}
.trend .tval{font-size:9.5px;color:var(--mut);font-weight:700;font-variant-numeric:tabular-nums}
.trend .tbar{width:100%;max-width:26px;border-radius:5px 5px 0 0}
.trend .tlb{font-size:9px;color:var(--mut2);font-weight:600;white-space:nowrap}
/* 30天每日趋势：柱更密、标签稀疏、均值线 */
.trend.d30{gap:2px}
.trend.d30 .tbar{max-width:12px}
.trend.d30 .tval{display:none}
.trend.d30 .tlb{font-size:8px;transform:rotate(0)}
.trend .avgline{position:absolute;left:0;right:0;border-top:1.5px solid var(--tang);opacity:.7;z-index:1}
.trend .avgtag{position:absolute;right:2px;font-size:9px;font-weight:800;color:var(--tang);background:var(--bg);padding:0 3px;transform:translateY(-100%)}
.trend .goaltag{position:absolute;right:2px;font-size:9px;font-weight:800;color:var(--mid);background:var(--bg);padding:0 3px;transform:translateY(-100%)}
.dnote{font-size:12.5px;color:var(--mut);margin-top:16px;line-height:1.6}
/* bottom tabs */
.tabs{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:440px;background:rgba(255,255,255,.94);backdrop-filter:blur(12px);border-top:1px solid var(--line);display:flex;padding:8px 0 calc(8px + env(safe-area-inset-bottom));z-index:20}
.tabs button{flex:1;border:0;background:none;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--mut2);font-family:inherit}
.tabs button .ic{font-size:21px;line-height:1}.tabs button .tx{font-size:10.5px;font-weight:700}
.tabs button.on{color:var(--tang)}
/* 改类弹层 */
.mask{position:fixed;inset:0;background:rgba(29,29,29,.42);z-index:40;display:flex;align-items:flex-end;justify-content:center}
.sheet{width:100%;max-width:440px;background:var(--bg);border-radius:20px 20px 0 0;padding:18px 16px calc(18px + env(safe-area-inset-bottom));animation:up .18s ease}
@keyframes up{from{transform:translateY(100%)}to{transform:translateY(0)}}
.sheet .sh-t{font-size:13px;color:var(--mut);font-weight:600;margin-bottom:4px}
.sheet .sh-n{font-size:15px;font-weight:800;margin-bottom:14px;line-height:1.3}
.sheet .grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.addtime{display:flex;gap:10px;margin-bottom:14px}
.att{flex:1;background:var(--soft);border-radius:13px;padding:9px 10px;text-align:center}
.att>span{font-size:11px;color:var(--mut);font-weight:600;display:block;margin-bottom:5px}
.att .stp{display:flex;align-items:center;justify-content:space-between;gap:6px}
.att .stp button{width:34px;height:34px;border-radius:10px;border:1px solid var(--line);background:var(--bg);font-size:19px;font-weight:300;color:var(--ink);cursor:pointer}
.att .stp b{font-size:17px;font-weight:800;font-variant-numeric:tabular-nums}
.sheet .cb{display:flex;align-items:center;gap:9px;padding:12px 13px;border:1px solid var(--line);border-radius:13px;background:var(--bg);font-family:inherit;font-size:14px;font-weight:700;cursor:pointer;color:var(--ink)}
.sheet .cb .d{width:12px;height:12px;border-radius:50%;flex:none}
.sheet .cb:active{background:var(--soft)}
.sheet .del{width:100%;margin-top:12px;padding:13px;border:1px solid #E7C3B6;border-radius:13px;background:#FBEEE9;color:#C2562F;font-family:inherit;font-weight:800;font-size:14px;cursor:pointer}
.sheet .del:active{background:#F6E0D7}
.sheet .cancel{width:100%;margin-top:8px;padding:13px;border:0;border-radius:13px;background:var(--soft);color:var(--mut);font-family:inherit;font-weight:700;font-size:14px;cursor:pointer}
/* 洞察 */
.ins{padding:14px 16px}
.icard{background:var(--bg);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:12px}
.icard .it{font-size:13px;font-weight:800;letter-spacing:.02em;margin-bottom:3px}
.icard .isub{font-size:11.5px;color:var(--mut);margin-bottom:14px;font-weight:500}
.verdict{background:var(--mid);color:#FAFBF9;border-radius:16px;padding:16px 18px;margin-bottom:12px}
.verdict .vt{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--lime);font-weight:700;margin-bottom:8px}
.verdict .vc{font-size:15px;font-weight:700;line-height:1.5}
.verdict .vc b{color:var(--lime)}
/* 本周建议 */
.sugg{background:var(--bg);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:12px}
.sugg .st{font-size:13px;font-weight:800;letter-spacing:.02em;margin-bottom:3px}
.sugg .ssub{font-size:11.5px;color:var(--mut);margin-bottom:12px;font-weight:500}
.sugg ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.sugg li{display:flex;gap:10px;align-items:flex-start;font-size:13px;line-height:1.55;color:var(--ink);font-weight:600}
.sugg li .si{flex:none;width:24px;height:24px;border-radius:8px;background:var(--soft);display:flex;align-items:center;justify-content:center;font-size:13px;margin-top:1px}
.sugg li b{font-weight:800}
.sugg li em{font-style:normal;color:var(--tang);font-weight:800;font-variant-numeric:tabular-nums}
.sugg .sempty{font-size:12.5px;color:var(--mut);font-weight:600;line-height:1.6}
.alloc2{display:flex;height:12px;border-radius:7px;overflow:hidden;gap:1.5px;background:var(--soft);margin-bottom:12px}
.alloc2 i{height:100%}
.leg2{display:flex;flex-wrap:wrap;gap:6px 14px;margin-bottom:13px}
.leg2 span{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--ink);font-weight:600}
.leg2 em{width:9px;height:9px;border-radius:3px;display:inline-block}
.famnudge{font-size:13px;color:var(--ink);padding-top:13px;border-top:1px solid var(--line);line-height:1.65;font-weight:600}
.famnudge b{font-weight:800}
.up{color:#5E9C6B;font-weight:800}.dn{color:#C2562F;font-weight:800}
.brow{margin-bottom:13px}
.brow .bl{display:flex;align-items:baseline;font-size:13px;margin-bottom:6px}
.brow .bl .nm{font-weight:700}.brow .bl .vv{margin-left:auto;font-weight:800;font-variant-numeric:tabular-nums}
.brow .bl .vv em{font-style:normal;color:var(--mut);font-weight:600;font-size:11.5px;margin-left:5px}
.brow .tk{position:relative;height:8px;border-radius:5px;background:var(--soft);overflow:visible}
.brow .tk i{display:block;height:100%;border-radius:5px}
.brow .tk .tgt{position:absolute;top:-3px;width:2px;height:14px;background:var(--mid);border-radius:1px}
.mgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.mcell{background:var(--soft);border-radius:13px;padding:12px 13px}
.mcell b{font-size:20px;font-weight:800;display:block;line-height:1.1;font-variant-numeric:tabular-nums}
.mcell b.warn{color:#C2562F}
.mcell span{font-size:11px;color:var(--mut);font-weight:600;margin-top:3px;display:block}
.ecorr{display:flex;gap:10px}
.ecorr .ec{flex:1;background:var(--soft);border-radius:13px;padding:13px;text-align:center}
.ecorr .ec b{font-size:24px;font-weight:800;display:block;line-height:1}
.ecorr .ec b.g{color:#5E9C6B}.ecorr .ec b.r{color:#C2562F}
.ecorr .ec span{font-size:11px;color:var(--mut);font-weight:600;margin-top:4px;display:block}
.inote{font-size:12px;color:var(--mut);line-height:1.6;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
.inote b{color:var(--ink)}
/* 洞察维度切换 */
.segI{display:flex;gap:6px;padding:14px 16px 2px}
.segI button{flex:1;border:0;background:var(--soft);color:var(--mut);font-family:inherit;font-weight:700;font-size:13.5px;padding:8px 0;border-radius:10px;cursor:pointer}
.segI button.on{background:var(--mid);color:#FAFBF9}
/* 工作×生活 圆环 */
.balwrap{display:flex;align-items:center;gap:18px;margin-bottom:14px}
.donut{width:104px;height:104px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center}
.donut .dhole{width:62px;height:62px;border-radius:50%;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center}
.donut .dhole b{font-size:20px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums}
.donut .dhole span{font-size:10px;color:var(--mut);font-weight:700;margin-top:2px}
.ballist{flex:1;display:flex;flex-direction:column;gap:10px}
.balrow{display:flex;align-items:center;font-size:13px}
.balrow em{width:10px;height:10px;border-radius:3px;margin-right:9px;flex:0 0 auto}
.balrow .bn{font-weight:700;color:var(--ink)}
.balrow .bp{margin-left:auto;font-weight:800;font-variant-numeric:tabular-nums}
.balrow .bh{width:52px;text-align:right;color:var(--mut);font-weight:600;font-variant-numeric:tabular-nums}
/* 家庭·自身 页 */
.fam{padding:14px 16px}
.fcard{background:var(--bg);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:12px}
.fcard .fhd{display:flex;align-items:center;margin-bottom:10px}
.fcard .ft{font-size:14px;font-weight:800;letter-spacing:.02em}
.fbadge{margin-left:auto;font-size:12px;font-weight:800;color:#7A6A3C;background:#FBEED9;border:1px solid #EDD9AE;padding:4px 10px;border-radius:20px;font-variant-numeric:tabular-nums}
.fbadge.warn{color:#B4531F;background:#FBE6D8;border-color:#F0C7AC}
.sleepsvg{width:100%;height:auto;display:block;margin:2px 0 4px}
.fnote{font-size:12px;color:var(--mut);line-height:1.6;margin-top:10px}
.kgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:4px}
.kcell{background:var(--soft);border-radius:13px;padding:13px 10px}
.kcell .kn{display:flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;color:var(--ink)}
.kcell .kn em{width:8px;height:8px;border-radius:50%;display:inline-block}
.kcell .kh{font-size:24px;font-weight:800;margin-top:8px;font-variant-numeric:tabular-nums}
.kcell .kh i{font-size:13px;font-style:normal;color:var(--mut);font-weight:700}
/* 说明弹窗 */
.amask{position:fixed;inset:0;background:rgba(29,29,29,.42);z-index:40;display:flex;align-items:flex-end;justify-content:center}
.asheet{background:var(--bg);width:100%;max-width:440px;max-height:88vh;border-radius:20px 20px 0 0;display:flex;flex-direction:column;overflow:hidden}
.asheet .ahd{display:flex;align-items:center;padding:18px 18px 12px;border-bottom:1px solid var(--line)}
.asheet .ahd b{font-size:16px;font-weight:800}
.asheet .aclose{margin-left:auto;border:0;background:var(--soft);width:30px;height:30px;border-radius:50%;font-size:15px;cursor:pointer;color:var(--mut)}
.abody{overflow-y:auto;padding:6px 18px 30px}
.asec{padding:14px 0;border-bottom:1px solid var(--line)}
.asec:last-child{border-bottom:0}
.asec h4{font-size:13.5px;font-weight:800;margin:0 0 6px}
.asec p{font-size:13px;color:var(--ink);line-height:1.72;margin:5px 0;font-weight:500}
.asec p b{font-weight:800}
.asec .amut{color:var(--mut);font-size:12px;font-weight:500}
</style></head><body><div class="phone">
<div class="hdr">
  <button class="a" id="todayB" title="今天">●</button>
  <div class="nav"><button class="a" id="prevB" style="background:none;font-size:20px">‹</button>
   <div><b id="dlab">今天</b><span id="dsub"></span></div>
   <button class="a" id="nextB" style="background:none;font-size:20px">›</button></div>
  <button class="a" id="aboutB" title="说明">ⓘ</button>
  <button class="a" id="reloadB" title="刷新">⟳</button>
  <div style="font-size:14px;font-weight:800;letter-spacing:.02em;opacity:.95;text-align:right;min-width:24px">Zoe</div>
</div>
<div class="body" id="body"></div>
<div class="tabs">
  <button data-v="clock" class="on"><span class="ic">🕘</span><span class="tx">时钟</span></button>
  <button data-v="stats"><span class="ic">📊</span><span class="tx">统计</span></button>
  <button data-v="insights"><span class="ic">💡</span><span class="tx">洞察</span></button>
  <button data-v="family"><span class="ic">🏡</span><span class="tx">家庭</span></button>
  <button data-v="goals"><span class="ic">🎯</span><span class="tx">目标</span></button>
</div>
</div>
<script>
__CATS__
__REAL_EVENTS__
__OURA_DATA__
// 全新调色板（明快、克制、区分度高），覆盖旧的发闷棕黑灰
const PAL={strategy:'#F37434',people:'#818A7D',product:'#C56B4A',operations:'#D69A3C',external:'#B4643E',global:'#8C6E45',growth:'#A6C061',family:'#E3A868',self:'#C98F7E',travel:'#A79E8C',sleep:'#B9BEAD'};
if(!CATS.find(c=>c.key==='travel')) CATS.splice(CATS.length-1,0,{key:'travel',label:'差旅',color:PAL.travel,icon:'✈️',sub:['出差飞行','通勤接送']});
CATS.forEach(c=>{if(PAL[c.key])c.color=PAL[c.key];});
const CM=Object.fromEntries(CATS.map(c=>[c.key,c]));
// 改类回流：本地修正表（title -> {cat,sub}），长按时间线一条即可改
const CORR=JSON.parse(localStorage.getItem('ztCorrections')||'{}');
function applyCorr(title,cat,sub){return CORR[title]?[CORR[title].cat,CORR[title].sub]:[cat,sub];}
function saveCorr(title,cat,sub){CORR[title]={cat,sub};localStorage.setItem('ztCorrections',JSON.stringify(CORR));}
// 删除/不参加：按"日期|标题|开始"记一条实例，不计入任何统计
const DELETED=new Set(JSON.parse(localStorage.getItem('ztDeleted')||'[]'));
function delKey(ds,t,s){return ds+'|'+t+'|'+s;}
function saveDel(k){DELETED.add(k);localStorage.setItem('ztDeleted',JSON.stringify([...DELETED]));}
// 手动补录：{ds:[{cat,sub,title,start,end}]}
const MANUAL=JSON.parse(localStorage.getItem('ztManual')||'{}');
function saveManual(ds,ev){(MANUAL[ds]=MANUAL[ds]||[]).push(ev);localStorage.setItem('ztManual',JSON.stringify(MANUAL));}
function delManual(ds,i){if(MANUAL[ds]){MANUAL[ds].splice(i,1);localStorage.setItem('ztManual',JSON.stringify(MANUAL));}}
const WORK=['strategy','people','product','operations','external','global','growth'];
const ACTIVE=CATS.filter(c=>c.key!=='sleep');
function genDay(ds){const evs=[];const push=(cat,sub,t,s,e,tg=[],man=false,mi=-1)=>evs.push({cat,sub,title:t,start:s,end:e,tags:tg,man,mi});
 const ou=OURA_DATA[ds];
 if(ou&&ou.hrs>0){const hrs=ou.hrs,wake=Math.min(9.5,Math.max(5,6+(7-hrs)*0.3));push('sleep','','睡眠',0,Math.round(wake*4)/4);
  const bed=24-Math.max(0,hrs-wake);if(bed<24)push('sleep','','入睡',Math.round(bed*4)/4,24);}
 (REAL_EVENTS[ds]||[]).forEach(e=>{if(DELETED.has(delKey(ds,e.title,e.start)))return;
   const[c,s]=applyCorr(e.title,e.cat,e.sub);push(c,s,e.title,e.start,e.end,e.tags);});
 (MANUAL[ds]||[]).forEach((e,i)=>push(e.cat,e.sub,e.title,e.start,e.end,[],true,i));
 return evs.sort((a,b)=>a.start-b.start);}
function genOura(ds){return OURA_DATA[ds]||null;}
function catMins(evs){const m={};evs.forEach(e=>{m[e.cat]=(m[e.cat]||0)+(e.end-e.start)*60;});return m;}
function fmtDur(min){min=Math.round(min);const h=Math.floor(min/60),m=min%60;return h&&m?h+'小时'+m+'分':h?h+'小时':m+'分';}
function fmtShort(min){min=Math.round(min);const h=Math.floor(min/60),m=min%60;return h&&m?h+'h'+m+'m':h?h+'h':m+'m';}
function fmtU(min){min=Math.round(min);const h=Math.floor(min/60),m=min%60;return h&&m?h+'<i>h</i>'+m+'<i>m</i>':h?h+'<i>h</i>':m+'<i>m</i>';}
function h2t(h){h=((h%24)+24)%24;const hh=Math.floor(h),mm=Math.round((h-hh)*60);return String(hh).padStart(2,'0')+':'+String(mm===60?0:mm).padStart(2,'0');}
function addDays(d,n){const r=new Date(d);r.setDate(r.getDate()+n);return r;}
function dateStr(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function weekStart(d){const r=new Date(d);r.setDate(r.getDate()-((r.getDay()+6)%7));r.setHours(0,0,0,0);return r;}
function today(){const d=new Date();d.setHours(0,0,0,0);return d;}
const WKD=['周日','周一','周二','周三','周四','周五','周六'];
// 若真实"今天"无任何事件，则演示用最忙的一天
let TBASE=today(); if(genDay(dateStr(TBASE)).filter(e=>e.cat!=='sleep').length===0){
  const busy=Object.keys(REAL_EVENTS).sort((a,b)=>REAL_EVENTS[b].length-REAL_EVENTS[a].length)[0];
  if(busy) TBASE=new Date(busy+'T00:00:00');
}

/* ---------- 24h 时钟盘 ---------- */
function polar(cx,cy,r,h){const a=(h/24*360-90)*Math.PI/180;return[cx+r*Math.cos(a),cy+r*Math.sin(a)];}
function sector(cx,cy,r1,r2,h1,h2,fill){
 if(h2-h1<=0.001)return'';
 const[x1o,y1o]=polar(cx,cy,r2,h1),[x2o,y2o]=polar(cx,cy,r2,h2),[x2i,y2i]=polar(cx,cy,r1,h2),[x1i,y1i]=polar(cx,cy,r1,h1);
 const lg=(h2-h1)>12?1:0;
 return `<path d="M${x1o} ${y1o} A${r2} ${r2} 0 ${lg} 1 ${x2o} ${y2o} L${x2i} ${y2i} A${r1} ${r1} 0 ${lg} 0 ${x1i} ${y1i} Z" fill="${fill}"/>`;}
function clock(evs,d){
 const cx=150,cy=150,R=128,ri=96;let s='';
 s+=`<circle cx="${cx}" cy="${cy}" r="${(R+ri)/2}" fill="none" stroke="#EEE7DB" stroke-width="${R-ri}"/>`;
 evs.forEach(e=>{const col=CM[e.cat].color;let a=e.start,b=Math.min(e.end,24);
   if(e.end>24){s+=sector(cx,cy,ri,R,a,24,col);s+=sector(cx,cy,ri,R,0,e.end-24,col);}else s+=sector(cx,cy,ri,R,a,b,col);});
 // 今天：剩余时间灰色 + now 指针
 const isToday=dateStr(d)===dateStr(today());
 if(isToday){const now=new Date();const nh=now.getHours()+now.getMinutes()/60;
   s+=sector(cx,cy,ri,R,nh,24,'rgba(138,132,117,.14)');
   const[px,py]=polar(cx,cy,R+4,nh),[ix,iy]=polar(cx,cy,ri-4,nh);
   s+=`<line x1="${ix}" y1="${iy}" x2="${px}" y2="${py}" stroke="#1D1D1D" stroke-width="2"/><circle cx="${px}" cy="${py}" r="3.4" fill="#1D1D1D"/>`;}
 // 刻度 + 数字
 for(let h=0;h<24;h++){const[tx,ty]=polar(cx,cy,R+2,h),[tx2,ty2]=polar(cx,cy,R+ (h%6===0?9:6),h);
   s+=`<line x1="${tx}" y1="${ty}" x2="${tx2}" y2="${ty2}" stroke="#C9CFD6" stroke-width="${h%6===0?1.4:0.8}"/>`;
   if(h%3===0){const[nx,ny]=polar(cx,cy,R+20,h);s+=`<text x="${nx}" y="${ny}" font-size="12" fill="#9AA0A8" font-weight="700" text-anchor="middle" dominant-baseline="central">${h}</text>`;}}
 return `<svg viewBox="-16 -16 332 332">${s}</svg>`;
}

/* ---------- 视图 ---------- */
let view='clock', off=0, statScope='day', insScope='week';
const INS_WIN={week:7,month:30,quarter:90,year:365};
function scopeName(){return {week:'本周',month:'近30天',quarter:'近一季',year:'近一年'}[insScope];}
function insDays(){ // 洞察当前维度的天数组（week=周一起，其它=截至锚点的滚动窗口）
 if(insScope==='week'){const ws=weekStart(curDay());return Array.from({length:7},(_,i)=>addDays(ws,i));}
 const N=INS_WIN[insScope],a=curDay();return Array.from({length:N},(_,i)=>addDays(a,-(N-1-i)));}
function curDay(){return addDays(TBASE,off);}

function vClock(){
 const d=curDay(),ds=dateStr(d),evs=genDay(ds),ou=OURA_DATA[ds];
 const m=catMins(evs),work=WORK.reduce((s,k)=>s+(m[k]||0),0),logged=Object.values(m).reduce((a,b)=>a+b,0);
 const isToday=ds===dateStr(today());
 let ctr;
 if(isToday){const now=new Date(),nh=now.getHours()+now.getMinutes()/60,rem=(24-nh)*60;
   ctr=`<div class="rg">${h2t(nh)}–24:00</div><div class="lb">今日剩余</div><div class="big">${fmtDur(rem)}</div>`;}
 else ctr=`<div class="rg">${ds.slice(5)} · ${WKD[d.getDay()]}</div><div class="lb">已记录</div><div class="big">${fmtDur(logged)}</div>`;
 window._evs=evs;
 // 时间线：事件行 + 可点的"空白补录"行
 let list='';
 if(!evs.length){list='<div class="gap" data-s="9" data-e="10">＋ 这天还没有记录 · 点此补录</div>';}
 else{let prev=null;
  evs.forEach((e,i)=>{
   if(prev!=null && e.start-prev>=0.5 && prev>=6 && e.start<=23.5)
     list+=`<div class="gap" data-s="${prev}" data-e="${e.start}">＋ ${h2t(prev)}–${h2t(e.start)} 空白 · 点此补录</div>`;
   const c=CM[e.cat];
   list+=`<div class="tli" data-i="${i}"><div class="tm">${h2t(e.start)}<br>${h2t(e.end)}</div>
    <span class="dot" style="background:${c.color}"></span><span class="nm">${e.title}${e.man?' <span class="mtag">手动</span>':''}</span>
    <span class="du">${fmtShort((e.end-e.start)*60)}</span><span class="ch">›</span></div>`;
   prev=Math.max(prev==null?0:prev,e.end);});
  const isT=ds===dateStr(today()),nowH=new Date().getHours()+new Date().getMinutes()/60,lim=isT?nowH:24;
  if(prev!=null && lim-prev>=0.5 && prev>=6 && prev<23.5)
   list+=`<div class="gap" data-s="${prev}" data-e="${Math.min(lim,prev+1).toFixed(2)}">＋ ${h2t(prev)} 起 · 点此补录</div>`;}
 // 健康 + 双角色概览（爱时间没有，你的数据独有）
 const fam=(m.family||0)+(m.self||0), rec=ou?ou.rec:null, sh=ou?ou.hrs:null;
 const GRN='#5E9C6B',AMB='#E0922A',RED='#D2553A';
 const sleepC=sh==null?'#C2B8A6':sh>=8?GRN:sh<5?RED:'#1D1D1D';      // 睡眠：≥8绿 <5红 中间黑
 const recC=rec==null?'#C2B8A6':rec>=67?GRN:rec>=34?AMB:RED;        // 恢复分：≥67绿 34-66黄 <34红
 const ov=`<div class="ov">
   <div class="ovi"><b style="color:${sleepC}">${sh!=null?sh+'<i>h</i>':'--'}</b><span>睡眠</span></div>
   <div class="ovi"><b style="color:${recC}">${rec!=null?rec:'--'}</b><span>恢复分</span></div>
   <div class="ovi"><b>${fmtU(work)||'0<i>m</i>'}</b><span>工作</span></div>
   <div class="ovi"><b>${fmtU(fam)||'0<i>m</i>'}</b><span>家庭·自我</span></div>
 </div>`;
 // 角色体检：一开 App（时钟页）就看清本周——战略被挤压？家庭够不够？（全用已流逝口径）
 const _ws=weekStart(today()),_wd=Array.from({length:7},(_,i)=>addDays(_ws,i));
 let _wk=0,_st=0,_fa=0;_wd.forEach(dd=>{const mm=catMinsElapsed(dateStr(dd));WORK.forEach(k=>_wk+=(mm[k]||0));_st+=(mm.strategy||0)+(mm.global||0);_fa+=(mm.family||0);});
 const _stP=_wk?Math.round(_st/_wk*100):0,_faH=_fa/60;
 const _fg=goals().find(x=>x.key==='family'),_df=_fg?(_fg.period==='每周'?_fg.target/7:_fg.target):3;
 const _ed=_wd.filter(dd=>dateStr(dd)<=dateStr(today())).length||1,_fgoal=_df*_ed;
 const rc=`<div class="rcheck"><span class="rlab">本周体检</span>`
   +`<span class="rc-i">战略 <b class="${_stP<20?'w':'g'}">${_stP}%</b>${_stP<20?'·被挤压':''}</span>`
   +`<span class="rc-i">陪家庭 <b class="${_faH>=_fgoal?'g':'w'}">${_faH.toFixed(1)}h</b>${_faH>=_fgoal?'·✓':'·目标'+_fgoal.toFixed(0)+'h'}</span></div>`;
 return `<div class="clockwrap"><div class="clock">${clock(evs,d)}<div class="ctr">${ctr}</div></div></div>${ov}${rc}<div class="tl">${list}</div>
  <button class="fab" id="fab">＋</button>`;
}

// 单日已流逝分钟：过去=1440，今天=到此刻，未来=0（分母只算真实发生过的时间）
function elapsedMin(ds){
 const tds=dateStr(today());
 if(ds<tds)return 1440;
 if(ds>tds)return 0;
 const n=new Date();return Math.round((n.getHours()*60+n.getMinutes()));
}
// 该日「到此刻」的边界（小时）：过去=24，今天=当前时刻，未来=0。
// 事件只在 [start, min(end, 边界)] 范围内算作已发生，绝不把未来排程当既成事实。
function nowBound(ds){const tds=dateStr(today());if(ds<tds)return 24;if(ds>tds)return 0;const n=new Date();return n.getHours()+n.getMinutes()/60;}
// 只计已发生部分的 catMins：把每条事件截到「到此刻」边界内（诚实口径，与统计页一致）
function catMinsElapsed(ds){const b=nowBound(ds),m={};if(b<=0)return m;
 genDay(ds).forEach(e=>{const s=Math.min(e.start,b),en=Math.min(e.end,b);if(en>s)m[e.cat]=(m[e.cat]||0)+(en-s)*60;});return m;}
// 只计已发生部分的孩子陪伴时长（截到「到此刻」）
function kidHrsElapsed(ds,key){const b=nowBound(ds);if(b<=0)return 0;let t=0;
 genDay(ds).forEach(e=>{if((e.tags||[]).includes(key)){const s=Math.min(e.start,b),en=Math.min(e.end,b);if(en>s)t+=en-s;}});return t;}
// 窗口是否含「今天或未来」——用于给标题打「截至此刻」标记
function winPartial(days){const tds=dateStr(today());return days.some(d=>dateStr(d)>=tds);}
function aggregate(scope){
 const d=curDay();const m={};let totalSpan=0,partial=false;
 // 分子也只算「已发生」部分：事件截到「到此刻」边界，避免今天满额排程 / 未来事件把占比冲到 >100%
 const add=ds=>{const x=catMinsElapsed(ds);for(const k in x)m[k]=(m[k]||0)+x[k];
   const el=elapsedMin(ds);totalSpan+=el;if(el<1440)partial=true;};
 if(scope==='day'){add(dateStr(d));}
 else if(scope==='week'){const ws=weekStart(d);for(let i=0;i<7;i++)add(dateStr(addDays(ws,i)));}
 else{const b=new Date(d.getFullYear(),d.getMonth(),1),dim=new Date(d.getFullYear(),d.getMonth()+1,0).getDate();
   for(let i=1;i<=dim;i++)add(dateStr(new Date(d.getFullYear(),d.getMonth(),i)));}
 // partial=分母含今天(未走完)或未来天，说明是"截至此刻"口径
 return {m,totalSpan:totalSpan||1,partial};
}
function vStats(){
 const {m,totalSpan,partial}=aggregate(statScope);
 const span=totalSpan; // 已=elapsed 分母，>=1
 const logged=Object.values(m).reduce((a,b)=>a+b,0),unrec=Math.max(0,span-logged);
 const hasData=Object.keys(m).some(k=>m[k]>0);
 const rows=Object.keys(m).filter(k=>m[k]>0).map(k=>({k,v:m[k],c:CM[k]})).sort((a,b)=>b.v-a.v);
 if(unrec>5)rows.push({k:'unrec',v:unrec,c:{label:'未记录',color:'#E2DACB',icon:''}});
 const scopeTxt={day:'全天',week:'本周 7 天',month:'本月'}[statScope]+(partial?' · 截至此刻':'');
 const seg=`<div class="seg2">
   <button data-s="day" class="${statScope==='day'?'on':''}">日</button>
   <button data-s="week" class="${statScope==='week'?'on':''}">周</button>
   <button data-s="month" class="${statScope==='month'?'on':''}">月</button></div>`;
 if(!hasData) return seg+`<div class="tl"><div class="empty" style="padding:48px 24px;line-height:1.7">
   这段还没有任何记录<br><span style="font-size:12.5px;color:var(--mut2)">点右下角 <b style="color:var(--tang)">＋</b> 或时钟页空白段补录</span></div></div>
   <button class="fab" id="fabS">＋</button>`;
 return seg+
  `<div class="sthdr"><span>${scopeTxt}</span><span>已记录 ${fmtShort(logged)} · 占 ${Math.round(logged/span*100)}%</span></div>
  ${rows.map(r=>{const isU=r.k==='unrec';
   return `<div class="srow${isU?' srow-u':''}"${isU?' data-unrec="1"':` data-cat="${r.k}" style="cursor:pointer"`}><div class="t"><span class="dot" style="background:${r.c.color}"></span>
   <span class="nm">${r.c.icon?r.c.icon+' ':''}${r.c.label}${isU?' <span class="uadd">＋ 补录</span>':''}</span><span class="du">${fmtShort(r.v)}</span>
   <span class="pc">${Math.round(r.v/span*100)}%</span></div>
   <div class="bar"><i style="width:${Math.min(100,r.v/span*100)}%;background:${r.c.color}"></i></div></div>`;}).join('')}
  <div class="snote"><b>未记录</b>＝这段时间里没有日历日程、也没有手动补录覆盖的部分${partial?'（分母只算到此刻，未来时间不计）':''}。点「未记录」这一行即可补录。</div>
  <button class="fab" id="fabS">＋</button>`;
}

// 目标：可编辑（存 localStorage 'ztGoals'），家庭默认提到 每天3h
const GOAL_DEF=[
 {key:'family',period:'每天',target:3},{key:'sleep',period:'每天',target:7},{key:'self',period:'每天',target:1},
 {key:'strategy',period:'每周',target:10},{key:'growth',period:'每周',target:5},{key:'people',period:'每周',target:6},
];
const GOV=JSON.parse(localStorage.getItem('ztGoals')||'{}');
function goals(){return GOAL_DEF.map(g=>({...g,...(GOV[g.key]||{})}));}
function saveGoal(key,patch){GOV[key]={...(GOV[key]||{}),...patch};localStorage.setItem('ztGoals',JSON.stringify(GOV));}
// 目标进度只算「已发生」的时间——未来排程不算达成（诚实口径，与统计/洞察一致）
function goalActual(g,d){if(g.period==='每天')return (catMinsElapsed(dateStr(d))[g.key]||0)/60;
 const ws=weekStart(d);let a=0;for(let i=0;i<7;i++)a+=(catMinsElapsed(dateStr(addDays(ws,i)))[g.key]||0)/60;return a;}
function vGoals(){
 const d=curDay(),isWk=dateStr(d)>=dateStr(weekStart(today()))&&dateStr(d)<=dateStr(addDays(weekStart(today()),6));
 const daysLeft=isWk?Math.max(1,7-((today().getDay()+6)%7)):7;  // 含今天
 return `<div class="goalhint">点任一目标卡可改数值 · 想多陪孩子？把「家庭」目标调高</div>
  <div class="goals">${goals().map(g=>{const c=CM[g.key];
  const act=goalActual(g,d),pct=Math.min(100,Math.round(act/g.target*100)),r=22,cc=2*Math.PI*r;
  const gapH=g.target-act;
  let nudge;
  if(gapH<=0) nudge=`✓ 已达标，超额 ${(-gapH).toFixed(1)}h`;
  else if(g.period==='每天') nudge=`今天还差 ${gapH.toFixed(1)}h`;
  else nudge=`本周还差 ${gapH.toFixed(1)}h${isWk?` · 剩 ${daysLeft} 天，日均再 ${(gapH/daysLeft).toFixed(1)}h`:''}`;
  return `<div class="gcard" style="background:${c.color}" data-g="${g.key}">
   <div class="gn">${c.icon} ${c.label}</div>
   <div class="gg">${g.period} ≥ ${g.target}小时 ✎</div>
   <div class="now">${g.period==='每天'?'今日':'本周'} ${act.toFixed(1)}h · ${nudge}</div>
   <div class="ring"><svg viewBox="0 0 54 54"><circle cx="27" cy="27" r="${r}" fill="none" stroke="rgba(255,255,255,.3)" stroke-width="5"></circle>
    <circle cx="27" cy="27" r="${r}" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-dasharray="${cc}" stroke-dashoffset="${cc*(1-pct/100)}" transform="rotate(-90 27 27)"></circle></svg>
    <div class="pv">${pct}%</div></div></div>`;}).join('')}</div>`;
}
function openGoalEdit(key){const g=goals().find(x=>x.key===key);if(!g)return;const c=CM[key];
 const mask=document.createElement('div');mask.className='mask';
 const render2=()=>{const gg=goals().find(x=>x.key===key);
  mask.querySelector('.ge-val').textContent=gg.target+' 小时';
  mask.querySelectorAll('.ge-p').forEach(b=>b.classList.toggle('on',b.dataset.p===gg.period));};
 mask.innerHTML=`<div class="sheet"><div class="sh-t">设定目标</div><div class="sh-n">${c.icon} ${c.label}</div>
  <div class="ge-row"><button class="ge-p" data-p="每天">每天</button><button class="ge-p" data-p="每周">每周</button></div>
  <div class="ge-stepper"><button class="ge-m">−</button><div class="ge-val">${g.target} 小时</div><button class="ge-pl">＋</button></div>
  <button class="cancel">完成</button></div>`;
 mask.onclick=ev=>{
  if(ev.target===mask||ev.target.classList.contains('cancel')){mask.remove();render();return;}
  const p=ev.target.closest('.ge-p');if(p){saveGoal(key,{period:p.dataset.p});render2();}
  if(ev.target.classList.contains('ge-pl')){saveGoal(key,{target:Math.min(24,(goals().find(x=>x.key===key).target)+0.5)});render2();}
  if(ev.target.classList.contains('ge-m')){saveGoal(key,{target:Math.max(0.5,(goals().find(x=>x.key===key).target)-0.5)});render2();}};
 document.body.appendChild(mask);render2();}
// 类别详情：近 10 周趋势 + 目标参考线 + 改目标
function openCatDetail(key){const c=CM[key],g=goals().find(x=>x.key===key);
 const thisWS=weekStart(curDay());
 const weeks=[];for(let w=9;w>=0;w--){const ws=addDays(thisWS,-7*w);let t=0;
  for(let i=0;i<7;i++)t+=(catMins(genDay(dateStr(addDays(ws,i))))[key]||0)/60;weeks.push({ws,t});}
 const maxT=Math.max(...weeks.map(w=>w.t),g?(g.period==='每周'?g.target:g.target*7):0,1);
 const wgoal=g?(g.period==='每周'?g.target:g.target*7):null;
 const avg=weeks.reduce((s,w)=>s+w.t,0)/10, cur=weeks[9].t, prev=weeks[8].t;
 const bars=weeks.map(w=>{const hh=w.t/maxT*100,isC=dateStr(w.ws)===dateStr(thisWS);
  return `<div class="tcol"><div class="tval">${w.t>0?w.t.toFixed(0):''}</div><div class="tbar" style="height:${Math.max(2,hh)}%;background:${c.color};opacity:${isC?1:.5}"></div><div class="tlb">${w.ws.getMonth()+1}/${w.ws.getDate()}</div></div>`;}).join('');
 const ov=document.createElement('div');ov.className='detail';
 const dlt=cur-prev;
 ov.innerHTML=`<div class="dhead"><button class="dback">‹ 返回</button><b>${c.icon} ${c.label}</b><button class="dedit">改目标</button></div>
  <div class="dbody">
   <div class="dstat"><div class="ds"><b>${cur.toFixed(1)}h</b><span>本周</span></div>
    <div class="ds"><b class="${dlt>=0?'up':'dn'}">${dlt>=0?'↑':'↓'}${Math.abs(dlt).toFixed(1)}h</b><span>较上周</span></div>
    <div class="ds"><b>${avg.toFixed(1)}h</b><span>10周周均</span></div>
    ${g?`<div class="ds"><b>${wgoal}h</b><span>周目标</span></div>`:''}</div>
   <div class="dtt">每周时长趋势 · 近 10 周${wgoal?' · 虚线=目标':''}</div>
   <div class="trend">${wgoal?`<div class="goalline" style="bottom:${Math.min(98,wgoal/maxT*100)}%"></div>`:''}${bars}</div>
   <div class="dnote">${cur>=avg?'近期高于自己的均值，保持。':'近期低于自己的均值，可以多投入。'}</div>
  </div>`;
 ov.onclick=ev=>{if(ev.target.classList.contains('dback')||ev.target===ov){ov.remove();return;}
  if(ev.target.classList.contains('dedit')){ov.remove();openGoalEdit(key);}};
 document.body.appendChild(ov);}
// ── 通用「近30天·每日」趋势下钻（复用 .detail/.trend 全套样式）──
function trendSeries(kind,key){ // 返回 {days,vals,goal|null,title,icon}
 const end=today(),N=30,days=Array.from({length:N},(_,i)=>addDays(end,-(N-1-i)));
 let vals,goal=null,title='',icon='';
 if(kind==='sleep'){
   vals=days.map(d=>{const h=(OURA_DATA[dateStr(d)]||{}).hrs;return h&&h>0?h:0;});
   goal=7;title='平均睡眠';icon='😴';
 }else if(kind==='kid'){
   vals=days.map(d=>{let t=0;genDay(dateStr(d)).forEach(e=>{if((e.tags||[]).includes(key))t+=(e.end-e.start);});return t;});
   title='陪 '+key;icon='🧒';
 }else if(kind==='bucket'){
   const b=BUCKETS.find(x=>x.key===key);
   vals=days.map(d=>{const m=catMins(genDay(dateStr(d)));return b.cats.reduce((a,k)=>a+(m[k]||0),0)/60;});
   title=b.label;icon='🎯';
 }else{ // cat（含 family/self）
   const c=CM[key];
   vals=days.map(d=>(catMins(genDay(dateStr(d)))[key]||0)/60);
   const g=goals().find(x=>x.key===key);
   if(g)goal=g.period==='每周'?g.target/7:g.target;
   title=c?c.label:key;icon=c&&c.icon?c.icon:'';
 }
 return {days,vals,goal,title,icon};
}
function openTrend(kind,key){
 const {days,vals,goal,title,icon}=trendSeries(kind,key);
 const N=days.length;
 const have=vals.filter(v=>v>0);
 const avg=have.length?have.reduce((a,b)=>a+b,0)/have.length:0;
 const sum=vals.reduce((a,b)=>a+b,0);
 const cur=vals[N-1], prev=vals[N-2]||0, dlt=cur-prev;
 const maxV=Math.max(...vals,goal||0,avg,0.1);
 const fmtH=v=>v>=10?Math.round(v)+'h':v.toFixed(1)+'h';
 const bars=vals.map((v,i)=>{
   const hh=v/maxV*100, isC=i===N-1, dt=days[i];
   const lbl=(i%5===0||i===N-1)?`${dt.getMonth()+1}/${dt.getDate()}`:'';
   const col=kind==='sleep'?(v>=7?'#7FA64B':v>0?'#E07A3C':'#E2DACB'):(CM[key]?CM[key].color:'#F37434');
   return `<div class="tcol"><div class="tbar" style="height:${v>0?Math.max(2,hh):0}%;background:${col};opacity:${isC?1:.55}"></div><div class="tlb">${lbl}</div></div>`;
 }).join('');
 const avgPct=Math.min(97,avg/maxV*100), goalPct=goal?Math.min(97,goal/maxV*100):0;
 const ov=document.createElement('div');ov.className='detail';
 ov.innerHTML=`<div class="dhead"><button class="dback">‹ 返回</button><b>${icon} ${title}</b><span style="width:44px"></span></div>
  <div class="dbody">
   <div class="dstat">
     <div class="ds"><b>${fmtH(cur)}</b><span>昨日/今日</span></div>
     <div class="ds"><b class="${dlt>=0?'up':'dn'}">${dlt>=0?'↑':'↓'}${Math.abs(dlt).toFixed(1)}h</b><span>较前一天</span></div>
     <div class="ds"><b>${fmtH(avg)}</b><span>30天日均</span></div>
     ${goal?`<div class="ds"><b>${goal.toFixed(goal>=10?0:1)}h</b><span>每日目标</span></div>`:`<div class="ds"><b>${fmtH(sum)}</b><span>30天合计</span></div>`}
   </div>
   <div class="dtt">近 30 天每日趋势 · 实线=日均${goal?' · 虚线=目标':''}</div>
   <div class="trend d30">
     ${goal?`<div class="goalline" style="bottom:${goalPct}%"></div><div class="goaltag" style="bottom:${goalPct}%">目标 ${goal.toFixed(goal>=10?0:1)}h</div>`:''}
     <div class="avgline" style="bottom:${avgPct}%"></div><div class="avgtag" style="bottom:${avgPct}%">均 ${avg.toFixed(1)}h</div>
     ${bars}
   </div>
   <div class="dnote">${have.length?(cur>=avg?'昨日高于近30天日均，保持。':'昨日低于近30天日均，可以多投入。'):'近30天暂无该项记录。'}${kind==='kid'?'<br>仅统计日历中点名到该孩子的事件；多数「家庭」时间未点名。':''}</div>
  </div>`;
 ov.onclick=ev=>{if(ev.target.classList.contains('dback')||ev.target===ov)ov.remove();};
 document.body.appendChild(ov);
}

/* ---------- 洞察层 ---------- */
const BUCKETS=[
 {key:'strategy',cats:['strategy','global'],label:'战略方向',tgt:35},
 {key:'ops',cats:['operations','product'],label:'运营执行',tgt:25},
 {key:'people',cats:['people'],label:'组织人才',tgt:20},
 {key:'external',cats:['external'],label:'对外关系',tgt:2},
 {key:'growth',cats:['growth'],label:'进修成长',tgt:8},
];
const BCOLOR={strategy:'#F37434',ops:'#D69A3C',people:'#818A7D',external:'#B4643E',growth:'#A6C061'};
function vInsights(){
 const days=insDays();
 const partial=winPartial(days); // 窗口含今天/未来 → 只算到此刻，标题打「截至此刻」
 // 诚实口径：每天只统计「已发生」部分，未来排程不计（与统计页 elapsed 一致）
 const dms=days.map(d=>catMinsElapsed(dateStr(d)));
 const bsum={};let workTot=0;
 BUCKETS.forEach(b=>{bsum[b.key]=dms.reduce((s,m)=>s+b.cats.reduce((a,k)=>a+(m[k]||0),0),0);workTot+=bsum[b.key];});
 const wt=workTot||1;
 const dev=BUCKETS.map(b=>({b,act:bsum[b.key]/wt*100,gap:bsum[b.key]/wt*100-b.tgt}));
 const over=dev.slice().sort((a,b)=>b.gap-a.gap)[0],under=dev.slice().sort((a,b)=>a.gap-b.gap)[0];
 let verdict;
 if(workTot<60) verdict=scopeName()+'记录的工作时间还太少，多记几天配比更准。';
 else verdict=`${scopeName()}时间最偏向 <b>${over.b.label}</b>（${Math.round(over.act)}% vs 目标 ${over.b.tgt}%），而 <b>${under.b.label}</b> 偏少（仅 ${Math.round(under.act)}%）。`+
   (under.b.key==='strategy'?'CEO 最该守住的战略时间被挤压了。':under.b.key==='growth'?'记得给自己留充电时间。':over.b.key==='ops'?'警惕困在运营救火。':'');
 const bars=BUCKETS.map(b=>{const act=bsum[b.key]/wt*100;
  return `<div class="brow" data-bucket="${b.key}" style="cursor:pointer"><div class="bl"><span class="nm">${b.label}</span><span class="vv">${Math.round(act)}%<em>${fmtShort(bsum[b.key])} · 目标${b.tgt}%</em></span></div>
   <div class="tk"><i style="width:${Math.min(100,act)}%;background:${BCOLOR[b.key]}"></i><div class="tgt" style="left:${b.tgt}%"></div></div></div>`;}).join('');
 // 会议负荷（只看工作类；重叠去重；分清"撞车"与"背靠背"）
 let mtg=0,b2b=0,gaps=0,eve=0,longest=0,conflicts=0,mergedMin=0;
 days.forEach(d=>{const ds=dateStr(d),bd=nowBound(ds); // 只看已发生的会议：把事件截到「到此刻」，未来的会不算负荷
  const evs=genDay(ds).filter(e=>WORK.includes(e.cat)&&e.start<bd).map(e=>({...e,end:Math.min(e.end,bd)})).sort((a,b)=>a.start-b.start);
  mtg+=evs.length;let mS=null,mE=null,cs=null,ce=null;
  evs.forEach((e,i)=>{
   if(e.end>19)eve+=(Math.min(e.end,24)-Math.max(e.start,19));
   if(i>0){const g=e.start-evs[i-1].end;
     if(g<-0.001)conflicts++; else {gaps++; if(g<=0.25)b2b++;}}
   if(mE===null){mS=e.start;mE=e.end;}
   else if(e.start<=mE+0.001){mE=Math.max(mE,e.end);}
   else {mergedMin+=(mE-mS)*60;mS=e.start;mE=e.end;}
   if(ce!==null&&e.start-ce<=0.25)ce=Math.max(ce,e.end);
   else {if(ce!==null)longest=Math.max(longest,ce-cs);cs=e.start;ce=e.end;}});
  if(mE!==null)mergedMin+=(mE-mS)*60;
  if(ce!==null)longest=Math.max(longest,ce-cs);});
 const b2bP=gaps?Math.round(b2b/gaps*100):0;
 // 精力 × 时间
 const dayWork=days.map((d,i)=>BUCKETS.reduce((s,b)=>s+b.cats.reduce((a,k)=>a+(dms[i][k]||0),0),0)/60);
 const wr=days.map((d,i)=>({wh:dayWork[i],rec:(OURA_DATA[dateStr(d)]||{}).rec})).filter(x=>x.rec!=null);
 let ec;
 if(wr.length>=4){const so=wr.slice().sort((a,b)=>b.wh-a.wh),half=Math.ceil(so.length/2);
  const avg=a=>Math.round(a.reduce((s,x)=>s+x.rec,0)/a.length);
  const hi=avg(so.slice(0,half)),lo=avg(so.slice(half));
  ec=`<div class="ecorr"><div class="ec"><b class="${hi<lo?'r':'g'}">${hi}</b><span>开会多的日子<br>平均恢复分</span></div>
   <div class="ec"><b class="${lo>=hi?'g':'r'}">${lo}</b><span>开会少的日子<br>平均恢复分</span></div></div>
   <div class="inote">${hi<lo?`开会多的日子恢复分平均低 <b>${lo-hi} 分</b> —— 身体在替你记账。考虑给最满的几天之后留恢复缓冲。`:'本周会议量和恢复分没明显负相关，状态稳。'}</div>`;
 } else ec='<div class="inote">本周 Oura 数据不足（需 ≥4 天）来算精力×时间相关性。</div>';
 // 工作 × 生活平衡（家庭是重点）
 const wkW=workTot/60, famW=dms.reduce((s,m)=>s+(m.family||0),0)/60,
   selfW=dms.reduce((s,m)=>s+(m.self||0),0)/60, sleepW=dms.reduce((s,m)=>s+(m.sleep||0),0)/60;
 // 上一周期做同口径对比：本窗口截到「到此刻」，上一窗口就按对应天数截同一时刻，避免拿满额比已发生
 const N=days.length,pStart=addDays(days[0],-N);let famPrev=0;
 for(let i=0;i<N;i++){const cd=days[i],pd=addDays(pStart,i),cb=nowBound(dateStr(cd));if(cb<=0)continue;
   genDay(dateStr(pd)).forEach(e=>{if(e.cat!=='family')return;const s=Math.min(e.start,cb),en=Math.min(e.end,cb);if(en>s)famPrev+=en-s;});}
 // 目标只按「已发生天数」折算（已过完的天算满、今天算到此刻、未来不算），达标与否只看真实已发生
 let famGoalDays=0;days.forEach(d=>{famGoalDays+=Math.min(1,nowBound(dateStr(d))/24);});
 const fg=goals().find(x=>x.key==='family'),dailyFam=fg?(fg.period==='每周'?fg.target/7:fg.target):3,famGoal=dailyFam*famGoalDays,famD=famW-famPrev;
 const segB=[['工作',wkW,'#F37434',0],['家庭',famW,CM.family.color,1],['自我',selfW,CM.self.color,1],['睡眠',sleepW,CM.sleep.color,0]];
 const totB=segB.reduce((s,x)=>s+x[1],0)||1;
 let _ac=0; const _stops=segB.filter(x=>x[1]>0.05).map(x=>{const p=x[1]/totB*100,s=`${x[2]} ${_ac.toFixed(2)}% ${(_ac+p).toFixed(2)}%`;_ac+=p;return s;}).join(',');
 const balCard=`<div class="icard"><div class="it">⚖️ 工作 × 生活</div><div class="isub">${scopeName()}时间去向占比 · 家庭是你最在意的</div>
   <div class="balwrap"><div class="donut" style="background:conic-gradient(${_stops||'var(--soft) 0 100%'})"><div class="dhole"><b>${Math.round(wkW/totB*100)}%</b><span>工作</span></div></div>
   <div class="ballist">${segB.map(x=>`<div class="balrow"><em style="background:${x[2]}"></em><span class="bn">${x[0]}</span><span class="bp">${Math.round(x[1]/totB*100)}%</span><span class="bh">${x[1].toFixed(x[3])}h</span></div>`).join('')}</div></div>
   <div class="famnudge">👨‍👩‍👧 陪伴家庭 <b>${famW.toFixed(1)}h</b>${partial?'（截至此刻）':''} · 较上一周期 ${famD>=0?'<span class="up">↑'+famD.toFixed(1)+'h</span>':'<span class="dn">↓'+Math.abs(famD).toFixed(1)+'h</span>'} · ${partial?'进度目标':'目标'} ${famGoal.toFixed(0)}h ${famW>=famGoal?`<span class="up">✓ ${partial?'进度达标':'已达标'}</span>`:`· <span class="dn">还差 ${(famGoal-famW).toFixed(1)}h</span>`}</div></div>`;
 // ---- 本周建议：按真实数据触发，克制取前 5 条 ----
 const N2=days.length;
 // 真实睡眠均值（用 WHOOP hrs，不是 genDay 的睡眠事件）
 const slH=days.map(d=>(OURA_DATA[dateStr(d)]||{}).hrs).filter(h=>h!=null&&h>0);
 const slAvg=slH.length?slH.reduce((a,b)=>a+b,0)/slH.length:null;
 const slBelow=slH.filter(h=>h<7).length;
 const stratDev=dev.find(x=>x.b.key==='strategy');   // {b,act,gap}
 const opsDev=dev.find(x=>x.b.key==='ops');
 const growthDev=dev.find(x=>x.b.key==='growth');
 const S=[];  // {ic,html,pr} pr=优先级(小=靠前)
 // 战略被挤压
 if(workTot>=60 && stratDev && stratDev.act < stratDev.b.tgt-15){
  const wkNeed = insScope==='week' ? (stratDev.b.tgt-stratDev.act)/100*(workTot/60) : null;
  const blk = wkNeed!=null ? Math.max(1,Math.round(wkNeed*2)/2) : 2;
  S.push({ic:'🧭',pr:1,html:`${scopeName()}战略仅 <em>${Math.round(stratDev.act)}%</em>（目标 ${stratDev.b.tgt}%），本周在日历 block 一段 <b>${blk}h</b> 深度战略时间，先占坑再排会。`});}
 // 运营救火
 if(workTot>=60 && opsDev && opsDev.act > opsDev.b.tgt+15){
  S.push({ic:'🪃',pr:2,html:`运营执行占 <em>${Math.round(opsDev.act)}%</em>（目标 ${opsDev.b.tgt}%），像困在执行里——挑 1–2 类高频事务授权出去，把手抽回战略。`});}
 // 睡眠护栏
 if(slAvg!=null && slAvg<7){
  S.push({ic:'😴',pr:1,html:`近期睡眠均 <em>${slAvg.toFixed(1)}h</em>，低于 7h 护栏 <b>${slBelow}</b> 晚；把最满的几天之后留一晚恢复缓冲，别连排。`});}
 // 背靠背
 if(b2bP>=60){
  S.push({ic:'⛓️',pr:2,html:`会议背靠背 <em>${b2bP}%</em>，几乎连轴转——两会之间默认留 <b>15 分钟</b>缓冲，给自己喘息和消化。`});}
 // 家庭低于目标（用已算好的 famW/famGoal）
 if(famGoal>0 && famW < famGoal*0.8){
  const gap=famGoal-famW;
  S.push({ic:'👨‍👩‍👧',pr:2,html:`陪伴家庭 <em>${famW.toFixed(1)}h</em>，距目标 ${famGoal.toFixed(0)}h 还差 <b>${gap.toFixed(1)}h</b>；本周固定 1–2 段亲子时间，写进日历当会议守。`});}
 // 进修成长被挤没
 if(workTot>=60 && growthDev && growthDev.act < growthDev.b.tgt-5){
  S.push({ic:'📚',pr:3,html:`进修成长仅 <em>${Math.round(growthDev.act)}%</em>（目标 ${growthDev.b.tgt}%），给自己留一段充电时间，别让学习永远排在最后。`});}
 // 记录太少
 if(workTot<60){
  S.push({ic:'✍️',pr:1,html:`${scopeName()}只记录了 <em>${fmtShort(workTot)}</em> 工作时间，样本还太少；多记几天，建议才够准。`});}
 S.sort((a,b)=>a.pr-b.pr);
 const top=S.slice(0,5);
 const suggBody = top.length
  ? `<ul>${top.map(s=>`<li><span class="si">${s.ic}</span><span>${s.html}</span></li>`).join('')}</ul>`
  : `<div class="sempty">✓ ${scopeName()}各项都在护栏内——战略在线、睡眠达标、会议不挤、家庭有陪伴。保持节奏就好。</div>`;
 const suggCard=`<div class="sugg"><div class="st">🧩 本周建议</div><div class="ssub">按你的真实数据生成 · 具体、可落地、点到为止</div>${suggBody}</div>`;
 return `<div class="segI">${['week','month','quarter','year'].map(s=>`<button data-i="${s}" class="${insScope===s?'on':''}">${({week:'周',month:'月',quarter:'季',year:'年'})[s]}</button>`).join('')}</div>
 <div class="ins">
  <div class="verdict"><div class="vt">${scopeName()}一句话</div><div class="vc">${verdict}</div></div>
  ${suggCard}
  ${balCard}
  <div class="icard"><div class="it">⚖️ CEO 时间配比</div><div class="isub">工作时间在各方向的占比 · 竖线＝参考目标（可调）</div>${bars}</div>
  <div class="icard"><div class="it">🔋 精力 × 时间</div><div class="isub">把 Oura 恢复分叠到时间分配上 —— 只有你的合并数据能看出</div>${ec}</div>
  <div class="icard"><div class="it">📋 会议负荷体检</div><div class="isub">${scopeName()} · 只看工作类、重叠已去重</div>
   <div class="mgrid">
    <div class="mcell"><b>${mtg}</b><span>工作会议数</span></div>
    <div class="mcell"><b>${fmtShort(mergedMin)}</b><span>实际工作时长</span></div>
    <div class="mcell"><b class="${longest>=4?'warn':''}">${longest?longest.toFixed(1)+'h':'—'}</b><span>最长无歇时段</span></div>
    <div class="mcell"><b class="${b2bP>=60?'warn':''}">${b2bP}%</b><span>会议背靠背</span></div>
    <div class="mcell"><b class="${eve>=5?'warn':''}">${fmtShort(eve*60)}</b><span>19:00 后工作</span></div>
    <div class="mcell"><b class="${conflicts>0?'warn':''}">${conflicts}</b><span>日程撞车</span></div>
   </div>
   <div class="inote"><b>最长无歇</b>＝首尾相接、中间没 ≥15分钟休息的最长时段（含工作午餐）。<b>背靠背</b>＝两个会间隔<15分钟就接上的占比，越高越"连轴转"。<b>撞车</b>＝同一时段订了多个日程。</div></div>
 </div>`;
}

/* ---------- 家庭 · 自身 页 ---------- */
function vFamily(){
 const end=today(),N=30,ds=Array.from({length:N},(_,i)=>addDays(end,-(N-1-i)));
 // 睡眠趋势 30 天
 const sl=ds.map(d=>({d,h:(OURA_DATA[dateStr(d)]||{}).hrs}));
 const have=sl.filter(x=>x.h!=null&&x.h>0);
 const avg=have.length?have.reduce((s,x)=>s+x.h,0)/have.length:0;
 const below=have.filter(x=>x.h<7).length;
 const W=328,H=118,pad=10,maxH=Math.max(9,...have.map(x=>x.h));
 const xs=i=>pad+i*((W-2*pad)/(N-1)), ys=h=>H-pad-(h/maxH)*(H-2*pad);
 let path='',dots='',prev=null;
 sl.forEach((x,i)=>{if(x.h==null||x.h<=0){prev=null;return;}const X=xs(i),Y=ys(x.h);
   path+=(prev===null?`M${X} ${Y}`:` L${X} ${Y}`);prev=X;
   dots+=`<circle cx="${X}" cy="${Y}" r="3.1" fill="${x.h>=7?'#7FA64B':'#E07A3C'}"/>`;});
 const gy=ys(7);
 const sleepCard=`<div class="fcard"><div class="fhd"><div class="ft">睡眠 · 30天</div><div class="fbadge ${avg<7?'warn':''}">均 ${avg.toFixed(1)}h${avg<7?' ⚠':''}</div></div>
   <svg viewBox="0 0 ${W} ${H}" class="sleepsvg"><line x1="${pad}" y1="${gy}" x2="${W-pad}" y2="${gy}" stroke="#C9C2B4" stroke-width="1" stroke-dasharray="4 4"/><text x="${pad+2}" y="${gy-5}" text-anchor="start" font-size="10" font-weight="700" fill="#B7AE9C" font-family="inherit">7h 护栏</text><path d="${path}" fill="none" stroke="#6B6257" stroke-width="1.6" stroke-linejoin="round"/>${dots}</svg>
   <div class="fnote">虚线＝7h 睡眠护栏。<b>${below}</b> 晚低于护栏（共 ${have.length} 晚有记录）。睡眠是你最该补的护栏——WHOOP 数据每天 11:00 后更新。</div></div>`;
 // 陪每个孩子（近30天，来自日历点名到具体孩子的事件）
 const kids=[['George','#E07A3C'],['Olivia','#C0846A'],['Max','#7FA64B']];
 const kh={George:0,Olivia:0,Max:0};
 ds.forEach(d=>genDay(dateStr(d)).forEach(e=>(e.tags||[]).forEach(t=>{if(kh[t]!=null)kh[t]+=(e.end-e.start);})));
 const kidCards=`<div class="fcard"><div class="ft">陪每个孩子（近30天）</div>
   <div class="kgrid">${kids.map(([k,c])=>`<div class="kcell" data-kid="${k}" style="cursor:pointer"><div class="kn"><em style="background:${c}"></em>${k}</div><div class="kh">${kh[k]<10?kh[k].toFixed(1):Math.round(kh[k])}<i>h</i></div></div>`).join('')}</div>
   <div class="fnote">仅统计日历中点名到具体孩子的事件；多数「家庭」时间未点名。<b>口径</b>：同一段同时陪 2–3 个孩子时，这段时长会给每个在场孩子各记一遍（不平摊），因此各娃相加可能大于总陪伴时长。想更准：点时间线某条改类，或右下角 + 补录。</div></div>`;
 // 家庭·自身 汇总（近30天）
 let famH=0,selfH=0;ds.forEach(d=>{const m=catMins(genDay(dateStr(d)));famH+=(m.family||0)/60;selfH+=(m.self||0)/60;});
 const sumCard=`<div class="fcard"><div class="ft">家庭 · 自身（近30天）</div>
   <div class="kgrid">
     <div class="kcell" data-trend="family" style="cursor:pointer"><div class="kn"><em style="background:${CM.family.color}"></em>陪伴家庭</div><div class="kh">${Math.round(famH)}<i>h</i></div></div>
     <div class="kcell" data-trend="self" style="cursor:pointer"><div class="kn"><em style="background:${CM.self.color}"></em>自我时间</div><div class="kh">${Math.round(selfH)}<i>h</i></div></div>
     <div class="kcell" data-trend="sleep" style="cursor:pointer"><div class="kn"><em style="background:${CM.sleep.color}"></em>平均睡眠</div><div class="kh">${avg.toFixed(1)}<i>h</i></div></div>
   </div></div>`;
 return `<div class="fam">${sleepCard}${kidCards}${sumCard}</div>`;
}
/* ---------- 说明 ---------- */
function openAbout(){
 const m=document.createElement('div');m.className='amask';
 m.innerHTML=`<div class="asheet"><div class="ahd"><b>关于「Zoe · 时间」</b><button class="aclose">✕</button></div>
   <div class="abody">
    <div class="asec"><h4>🎯 它在做什么</h4><p>把你的真实时间——飞书日程 + WHOOP 睡眠恢复——自动归类、统计、给出洞察。<b>全部真实数据，零编造填充。</b></p></div>
    <div class="asec"><h4>🧠 怎么归类</h4><p>日程按语义层规则自动分到 10 类（战略 / 运营 / 对外 / 人才 / 深度 / 家庭 / 健康 / 自我 / 差旅 / 睡眠）。规则没命中的用 AI 兜底判断。<b>你改一次，它记住一次——越用越准。</b></p></div>
    <div class="asec"><h4>🔄 多久更新一次</h4>
      <p><b>日程</b>：每天 <b>6:40 / 11:00 / 16:00</b> 三次，自动拉飞书日历、重建并发布。</p>
      <p><b>睡眠 / 恢复（WHOOP）</b>：手环数据由健康归档在 <b>10:30 / 15:30 / 22:30</b> 落盘。所以当天睡眠通常在 <b>11:00</b> 那次刷新后出现，最迟 <b>16:00</b> 补齐；偶尔 WHOOP 云端定稿晚会拖到下午。<b>前一晚的睡眠不会在清晨立刻出现，属正常。</b></p></div>
    <div class="asec"><h4>✍️ 你可以怎么调</h4><p>· 点时间线某条 → 改类别 / 删除（不参加）<br>· 右下角 <b>+</b> → 手动补录一段时间<br>· 目标页 → 改每类目标、点卡片看趋势<br><span class="amut">你的修改先存在本机；跨设备云同步开发中。</span></p></div>
    <div class="asec"><h4>🧭 背后的原则</h4><p>· 只呈现真实、绝不编造填充<br>· 睡眠是第一护栏，健康优先<br>· 家庭时间是重点守护的指标<br>· CEO 时间对标理想配比（洞察页竖线＝参考目标，可调）</p></div>
   </div></div>`;
 document.body.appendChild(m);
 m.onclick=e=>{if(e.target===m||e.target.classList.contains('aclose'))m.remove();};
}
function render(){
 const d=curDay();
 if(view==='insights'){const dd=insDays(),a=dd[0],b=dd[dd.length-1];
   document.getElementById('dlab').textContent=scopeName()+'洞察';
   document.getElementById('dsub').textContent=`${a.getMonth()+1}.${a.getDate()} – ${b.getMonth()+1}.${b.getDate()}`+(winPartial(dd)?' · 截至此刻':'');
 } else if(view==='clock'||view==='stats'){
   document.getElementById('dlab').textContent=off===0?'今天':`${d.getMonth()+1}月${d.getDate()}日`;
   document.getElementById('dsub').textContent=`${dateStr(d)} ${WKD[d.getDay()]}`;
 } else if(view==='family'){document.getElementById('dlab').textContent='家庭 · 自身';document.getElementById('dsub').textContent='睡眠趋势 · 陪伴每个孩子';
 } else {document.getElementById('dlab').textContent='目标';document.getElementById('dsub').textContent='点卡片看趋势 · 可改目标';}
 document.getElementById('nextB').style.visibility=off>=0?'hidden':'visible';
 document.getElementById('body').innerHTML = view==='clock'?vClock():view==='stats'?vStats():view==='insights'?vInsights():view==='family'?vFamily():vGoals();
 if(view==='stats'){document.querySelectorAll('.seg2 button').forEach(b=>b.onclick=()=>{statScope=b.dataset.s;render();});
  wireStatsAdd();
  document.querySelectorAll('.srow[data-cat]').forEach(el=>el.onclick=()=>openTrend('cat',el.dataset.cat));}
 if(view==='insights'){document.querySelectorAll('.segI button').forEach(b=>b.onclick=()=>{insScope=b.dataset.i;off=0;render();});
  document.querySelectorAll('.brow[data-bucket]').forEach(el=>el.onclick=()=>openTrend('bucket',el.dataset.bucket));}
 if(view==='clock')wireEdit();
 if(view==='family'){
   document.querySelectorAll('.kcell[data-kid]').forEach(el=>el.onclick=()=>openTrend('kid',el.dataset.kid));
   document.querySelectorAll('.kcell[data-trend]').forEach(el=>el.onclick=()=>{const t=el.dataset.trend;openTrend(t==='sleep'?'sleep':'cat',t);});
 }
 if(view==='goals')document.querySelectorAll('.gcard').forEach(el=>el.onclick=()=>openCatDetail(el.dataset.g));
}
// 点一条时间线 → 改类别 / 删除（不参加）
function wireEdit(){
 document.querySelectorAll('.tli').forEach(el=>{el.onclick=()=>openPicker(+el.dataset.i);});
 document.querySelectorAll('.gap').forEach(el=>{el.onclick=()=>openAdd(parseFloat(el.dataset.s),parseFloat(el.dataset.e));});
 const fab=document.getElementById('fab');if(fab)fab.onclick=()=>{const n=new Date(),nh=n.getHours()+n.getMinutes()/60;
  const e=Math.min(24,Math.round(nh*2)/2),s=Math.max(0,e-1);openAdd(s,e);};}
// 统计页：点"未记录"行 or FAB → 补录（智能选默认时段）
function suggestGap(){ // 返回当前锚点日一个"最近的空白"[s,e]，无则给近1h
 const ds=dateStr(curDay()),evs=genDay(ds).filter(e=>e.cat!=='sleep').sort((a,b)=>a.start-b.start);
 const isT=ds===dateStr(today()),nowH=new Date().getHours()+new Date().getMinutes()/60,lim=isT?nowH:24;
 let prev=6; // 从早6点起找第一段>=0.5h空白
 for(const e of evs){if(e.start-prev>=0.5&&prev>=6)return[Math.round(prev*4)/4,Math.round(e.start*4)/4];prev=Math.max(prev,e.end);}
 if(lim-prev>=0.5&&prev>=6)return[Math.round(prev*4)/4,Math.round(Math.min(lim,prev+1)*4)/4];
 const e=Math.min(24,Math.round((isT?nowH:12)*2)/2);return[Math.max(0,e-1),e]; // 兜底近1h
}
function wireStatsAdd(){
 const go=()=>{const[s,e]=suggestGap();openAdd(s,e);};
 document.querySelectorAll('.srow-u').forEach(el=>el.onclick=go);
 const fb=document.getElementById('fabS');if(fb)fb.onclick=go;
}
function catSheet(title,sub,onpick,extra){
 const cats=CATS.filter(c=>c.key!=='sleep');
 const btns=cats.map(c=>`<button class="cb" data-k="${c.key}"><span class="d" style="background:${c.color}"></span>${c.icon} ${c.label}</button>`).join('');
 const mask=document.createElement('div');mask.className='mask';
 mask.innerHTML=`<div class="sheet"><div class="sh-t">${sub}</div><div class="sh-n">${title}</div><div class="grid">${btns}</div>${extra||''}<button class="cancel">取消</button></div>`;
 mask.onclick=ev=>{
  if(ev.target===mask||ev.target.classList.contains('cancel')){mask.remove();return;}
  if(ev.target.classList.contains('del')){onpick('__del__');mask.remove();render();return;}
  const b=ev.target.closest('.cb');if(b){onpick(b.dataset.k);mask.remove();render();}};
 document.body.appendChild(mask);}
function openPicker(i){const e=window._evs[i];if(!e||e.cat==='sleep')return;const ds=dateStr(curDay());
 catSheet(e.title, e.man?'手动记录 · 改类别或删除':'改归类（点一下记住，下次自动）', k=>{
  if(k==='__del__'){ if(e.man) delManual(ds,e.mi); else saveDel(delKey(ds,e.title,e.start)); return; }
  const c=CM[k]; if(e.man){MANUAL[ds][e.mi].cat=k;MANUAL[ds][e.mi].sub=(c.sub&&c.sub[0])||'';localStorage.setItem('ztManual',JSON.stringify(MANUAL));}
  else saveCorr(e.title,k,(c.sub&&c.sub[0])||'');
 }, '<button class="del">🗑 '+(e.man?'删除这条补录':'不参加 · 从记录中删除')+'</button>');}
function openAdd(gs,ge){const ds=dateStr(curDay());let s=gs,e=ge;
 const cats=CATS.filter(c=>c.key!=='sleep');
 const btns=cats.map(c=>`<button class="cb" data-k="${c.key}"><span class="d" style="background:${c.color}"></span>${c.icon} ${c.label}</button>`).join('');
 const mask=document.createElement('div');mask.className='mask';
 mask.innerHTML=`<div class="sheet"><div class="sh-t">补录一段时间 · 调好时间点类别保存</div>
  <div class="addtime">
   <div class="att"><span>开始</span><div class="stp"><button data-a="s-">−</button><b id="as">${h2t(s)}</b><button data-a="s+">＋</button></div></div>
   <div class="att"><span>结束</span><div class="stp"><button data-a="e-">−</button><b id="ae">${h2t(e)}</b><button data-a="e+">＋</button></div></div>
  </div>
  <div class="grid">${btns}</div><button class="cancel">取消</button></div>`;
 const upd=()=>{mask.querySelector('#as').textContent=h2t(s);mask.querySelector('#ae').textContent=h2t(e);};
 mask.onclick=ev=>{
  if(ev.target===mask||ev.target.classList.contains('cancel')){mask.remove();return;}
  const st=ev.target.closest('[data-a]');
  if(st){const a=st.dataset.a;
   if(a==='s-')s=Math.max(0,Math.round((s-0.25)*100)/100);
   if(a==='s+')s=Math.min(e-0.25,Math.round((s+0.25)*100)/100);
   if(a==='e-')e=Math.max(s+0.25,Math.round((e-0.25)*100)/100);
   if(a==='e+')e=Math.min(24,Math.round((e+0.25)*100)/100);
   upd();return;}
  const b=ev.target.closest('.cb');if(b){const k=b.dataset.k,c=CM[k];
   saveManual(ds,{cat:k,sub:(c.sub&&c.sub[0])||'',title:c.label,start:s,end:e});mask.remove();render();}};
 document.body.appendChild(mask);}
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{view=b.dataset.v;off=0;
  document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x===b));render();});
function insStep(){return view==='insights'?INS_WIN[insScope]:1;}
document.getElementById('prevB').onclick=()=>{off-=insStep();render();};
document.getElementById('nextB').onclick=()=>{const st=insStep();if(off<0){off=Math.min(0,off+st);render();}};
document.getElementById('todayB').onclick=()=>{off=0;render();};
document.getElementById('reloadB').onclick=()=>location.reload();
document.getElementById('aboutB').onclick=openAbout;
render();
</script></body></html>'''

def render(real_js, oura_js):
    """供 refresh.py 调用：注入最新数据，返回完整 App HTML。"""
    return (HTML.replace("__FAV__",FAV).replace("__CATS__",CATS)
            .replace("__REAL_EVENTS__",real_js).replace("__OURA_DATA__",oura_js))

if __name__=="__main__":
    out=render(REAL,OURA)
    os.makedirs(f"{BASE}/demos",exist_ok=True)
    open(f"{BASE}/demos/itime.html","w",encoding="utf-8").write(out)
    print("wrote demos/itime.html", len(out))
