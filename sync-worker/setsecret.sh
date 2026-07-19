#!/bin/bash
# 把飞书 App Secret 安全注入 Cloudflare Worker → 部署 → 自测
# 用法：在【真实终端 Terminal.app】里运行本脚本，按提示粘贴 secret（输入隐藏，不回显、不进任何记录）
#   bash ~/AI/Workspaces/mt-sites/bi-dashboards/mt-time-tracker/sync-worker/setsecret.sh
# secret 来源：飞书开放平台 → 开发者后台 → 应用 cli_a951fab3c6785cb1（Zoe AI 助理）→ 凭证与基础信息 → App Secret
set -e
cd "$(dirname "$0")"
APPID="cli_a951fab3c6785cb1"
SECRET="${1:-}"
if [ -z "$SECRET" ]; then
  read -r -s -p "粘贴 App Secret（隐藏输入），回车确认: " SECRET; echo
fi
if [ -z "$SECRET" ]; then echo "✗ 没拿到 secret，退出"; exit 1; fi
echo "→ 注入 Cloudflare（密钥仅存 Cloudflare，不落本地/记录）…"
printf '%s' "$APPID"  | wrangler secret put LARK_APP_ID    >/dev/null 2>&1 || true
printf '%s' "$SECRET" | wrangler secret put LARK_APP_SECRET 2>&1 | grep -iE 'success|uploaded|error' | head -1
unset SECRET
echo "→ 部署…"
wrangler deploy 2>&1 | grep -iE 'Deployed|https://|error' | head -2
echo "→ 自测（飞书 code:0 = 密钥通；若是权限类错误我再修多维表格授权）…"
sleep 3
curl -s -m 25 "https://zoe-time-sync.zoe-mt.workers.dev/test" \
 | python3 -c "import sys,json;b=json.load(sys.stdin).get('body',{});print('飞书 code:',b.get('code'),'| msg:',(b.get('msg') or '')[:80])" 2>/dev/null \
 || echo "(自测请求失败，检查网络/代理)"
