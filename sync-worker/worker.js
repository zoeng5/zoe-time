// Zoe 时间 · 云端持久化代理（Cloudflare Worker）
// App ⇄ 这个 Worker（藏飞书密钥）⇄ 飞书多维表格
const APP = 'SWhDb2O44a7rnrskSBRcl177nvg';
const T = { manual:'tblylYDLAard5ZlZ', corr:'tbl2yVHGoZ8jtECk', del:'tblueeOFzLoukVvO', goal:'tblrYVZLzJ06BJyZ', edit:'tblNosebNwXPQJNP' };
const BASE = 'https://open.feishu.cn/open-apis';
const CORS = { 'Access-Control-Allow-Origin':'*', 'Access-Control-Allow-Methods':'GET,POST,OPTIONS', 'Access-Control-Allow-Headers':'Content-Type,X-ZT-Token' };
// 静态口令：优先读 Cloudflare secret ZT_TOKEN，未设则用此兜底常量（与前端 App / refresh.py 同一值）
const ZT_TOKEN_FALLBACK = '41326c953ec9ceb6227a27adc2cc83e583b9db05454e77f0';
const txt = v => Array.isArray(v) ? v.map(s => s.text ?? s).join('') : (v ?? '');

async function token(env){
  const r = await fetch(`${BASE}/auth/v3/tenant_access_token/internal`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ app_id: env.LARK_APP_ID, app_secret: env.LARK_APP_SECRET }) });
  return (await r.json()).tenant_access_token;
}
async function listAll(tk, table){
  let items=[], pt;
  do{
    const u = new URL(`${BASE}/bitable/v1/apps/${APP}/tables/${table}/records`);
    u.searchParams.set('page_size','500'); if(pt) u.searchParams.set('page_token', pt);
    const j = await (await fetch(u, { headers:{ Authorization:'Bearer '+tk } })).json();
    items = items.concat(j.data?.items || []); pt = j.data?.has_more ? j.data.page_token : null;
  } while(pt);
  return items;
}
const create = (tk,table,fields) => fetch(`${BASE}/bitable/v1/apps/${APP}/tables/${table}/records`,
  { method:'POST', headers:{ Authorization:'Bearer '+tk, 'Content-Type':'application/json' }, body: JSON.stringify({ fields }) });
const update = (tk,table,rid,fields) => fetch(`${BASE}/bitable/v1/apps/${APP}/tables/${table}/records/${rid}`,
  { method:'PUT', headers:{ Authorization:'Bearer '+tk, 'Content-Type':'application/json' }, body: JSON.stringify({ fields }) });
const del = (tk,table,rid) => fetch(`${BASE}/bitable/v1/apps/${APP}/tables/${table}/records/${rid}`,
  { method:'DELETE', headers:{ Authorization:'Bearer '+tk } });
const J = o => new Response(JSON.stringify(o), { headers:{ ...CORS, 'Content-Type':'application/json' } });

export default {
  async fetch(req, env){
    if(req.method==='OPTIONS') return new Response(null,{ headers:CORS });
    const url = new URL(req.url);
    // 鉴权：/sync 与 /save 必须带匹配的 X-ZT-Token（此前完全无鉴权，任何人可读写 Zoe 的时间数据）
    if(url.pathname==='/sync' || url.pathname==='/save' || url.pathname==='/html'){
      const need = env.ZT_TOKEN || ZT_TOKEN_FALLBACK;
      if((req.headers.get('X-ZT-Token')||'') !== need)
        return new Response(JSON.stringify({ error:'unauthorized' }), { status:401, headers:{ ...CORS, 'Content-Type':'application/json' } });
    }
    let tk;
    try { tk = await token(env); } catch(e){ return J({ error:'auth' }); }

    if(url.pathname==='/html'){
      if(req.method==='PUT'){ await env.ZT_KV.put('index_html', await req.text()); await env.ZT_KV.put('index_ts', String(Date.now())); return J({ok:true}); }
      const ts=await env.ZT_KV.get('index_ts');
      const h=await env.ZT_KV.get('index_html');
      if(!h) return new Response('no html yet',{status:404,headers:CORS});
      return new Response(h,{headers:{...CORS,'Content-Type':'text/html; charset=utf-8','X-ZT-TS':ts||''}});
    }
    if(url.pathname==='/sync'){
      const [mn,co,de,go,ed] = await Promise.all([listAll(tk,T.manual),listAll(tk,T.corr),listAll(tk,T.del),listAll(tk,T.goal),listAll(tk,T.edit)]);
      const manual={}; mn.forEach(r=>{const f=r.fields,d=txt(f['日期']);(manual[d]=manual[d]||[]).push({cat:txt(f['类别']),sub:txt(f['子类']),kids:txt(f['孩子']),note:txt(f['备注']),start:+f['开始'],end:+f['结束'],_rid:r.record_id});});
      const corrections={}; co.forEach(r=>{const f=r.fields;corrections[txt(f['标题'])]={cat:txt(f['类别']),sub:txt(f['子类']),kids:txt(f['孩子'])};});
      const deleted = de.map(r=>txt(r.fields['标识']));
      const goals={}; go.forEach(r=>{const f=r.fields;goals[txt(f['类别'])]={period:txt(f['周期']),target:+f['目标值']};});
      const edits={}; ed.forEach(r=>{const f=r.fields;edits[txt(f['标识'])]={title:txt(f['新标题']),start:+f['开始'],end:+f['结束']};});
      return J({ manual, corrections, deleted, goals, edits });
    }
    if(url.pathname==='/save' && req.method==='POST'){
      const b = await req.json(); const dev = b.device||'';
      if(b.kind==='manual') await create(tk,T.manual,{'日期':b.ds,'类别':b.cat,'子类':b.sub||'','开始':b.start,'结束':b.end,'孩子':b.kids||'','备注':b.note||'','设备':dev});
      else if(b.kind==='delete') await create(tk,T.del,{'标识':b.key,'日期':b.ds||'','标题':b.title||''});
      else if(b.kind==='correction'){ const hit=(await listAll(tk,T.corr)).find(r=>txt(r.fields['标题'])===b.title); const f={'标题':b.title,'类别':b.cat,'子类':b.sub||'','孩子':b.kids||'','设备':dev}; hit?await update(tk,T.corr,hit.record_id,f):await create(tk,T.corr,f); }
      else if(b.kind==='goal'){ const hit=(await listAll(tk,T.goal)).find(r=>txt(r.fields['类别'])===b.key); const f={'类别':b.key,'周期':b.period,'目标值':b.target}; hit?await update(tk,T.goal,hit.record_id,f):await create(tk,T.goal,f); }
      else if(b.kind==='edit'){ const hit=(await listAll(tk,T.edit)).find(r=>txt(r.fields['标识'])===b.key); const f={'标识':b.key,'日期':b.ds||'','新标题':b.title||'','开始':b.start,'结束':b.end,'设备':dev}; hit?await update(tk,T.edit,hit.record_id,f):await create(tk,T.edit,f); }
      else if(b.kind==='undelete'){ const hit=(await listAll(tk,T.del)).find(r=>txt(r.fields['标识'])===b.key); if(hit)await del(tk,T.del,hit.record_id); }
      else if(b.kind==='delManual'){ const hit=(await listAll(tk,T.manual)).find(r=>txt(r.fields['日期'])===b.ds && +r.fields['开始']===+b.start && txt(r.fields['类别'])===b.cat); if(hit)await del(tk,T.manual,hit.record_id); }
      // 原子改手动条目：单请求内按旧三元组(日期,开始,类别)定位→就地 update；找不到则 create（替代前端 delManual→manual 两发无序竞态）
      else if(b.kind==='editManual'){ const hit=(await listAll(tk,T.manual)).find(r=>txt(r.fields['日期'])===b.ds && +r.fields['开始']===+b.start && txt(r.fields['类别'])===b.cat);
        const f={'日期':b.ds,'类别':b.ncat,'子类':b.nsub||'','开始':b.nstart,'结束':b.nend,'孩子':b.nkids||'','备注':b.nnote||'','设备':dev};
        hit?await update(tk,T.manual,hit.record_id,f):await create(tk,T.manual,f); }
      return J({ ok:true });
    }
    return new Response('Zoe time sync worker');
  }
};
