#!/bin/bash
# 从 macOS 钥匙串读飞书 app secret → 注入 Cloudflare Worker → 部署 → 自测
# 运行时若弹出"security 想访问钥匙串"，点【始终允许】
set -e
cd "$(dirname "$0")"
ACCT="appsecret:cli_a951fab3c6785cb1"
SECRET=""
for svc in lark-cli lark-mcp larksuite-cli ""; do
  if [ -n "$svc" ]; then
    SECRET=$(security find-generic-password -s "$svc" -a "$ACCT" -w 2>/dev/null) || true
  else
    SECRET=$(security find-generic-password -a "$ACCT" -w 2>/dev/null) || true
  fi
  [ -n "$SECRET" ] && { echo "✓ 从钥匙串(service=${svc:-auto})读到密钥，长度 ${#SECRET}"; break; }
done
if [ -z "$SECRET" ]; then
  echo "✗ 钥匙串里没找到。请改为手动：去飞书开放平台复制 cli_a951fab3c6785cb1 的 App Secret，然后运行："
  echo "    echo '你的secret' | wrangler secret put LARK_APP_SECRET"
  exit 1
fi
# 注入 + 同时确保 app_id
printf '%s' "cli_a951fab3c6785cb1" | wrangler secret put LARK_APP_ID >/dev/null 2>&1 || true
printf '%s' "$SECRET" | wrangler secret put LARK_APP_SECRET 2>&1 | grep -iE 'success|error' | head -1
echo "→ 部署…"
wrangler deploy 2>&1 | grep -iE 'Deployed|https://|error' | head -3
echo "→ 自测 /test（应返回 success:true）…"
sleep 3
curl -s -m 25 "https://zoe-time-sync.zoe-mt.workers.dev/test" | python3 -c "import sys,json;d=json.load(sys.stdin);b=d.get('body',{});print('飞书返回 code:', b.get('code'), '| msg:', b.get('msg'))" 2>/dev/null || echo "(自测请求失败)"
