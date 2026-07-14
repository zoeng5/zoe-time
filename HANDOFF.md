# Zoe's Time · 技术交接文档

**项目**：Zoe's Time（个人时间管理 & 健康追踪系统）  
**版本**：v0.8（2026-07-14 正式发布）  
**维护者**：Zoe + Claude Code  

---

## 📋 项目状态

| 指标 | 状态 |
|------|------|
| **开发阶段** | ✅ 已完成（生产可用） |
| **用户规模** | 1 人（Zoe 个人系统） |
| **日活** | 每日自动刷新 |
| **关键依赖** | Oura/WHOOP + 飞书日历 + lark-cli |
| **运行环境** | macOS + launchd 后台任务 |
| **上线时间** | 2026-06-01 |

---

## 🏗️ 核心模块速查

### 1. **后端数据管道** (`refresh.py` 主脚本)

**职责**：每日同步数据、渲染前端

**关键流程**：
1. 拉飞书日历（`fetch_events()`）→ 分段获取日程
2. 日程分类（`build_real()`）→ 调用 `classify_apply` 应用规则
3. Oura/WHOOP 聚合（`build_oura()`）→ 读 `~/AI/DataLake/健康/normalized/daily/`
4. 前端渲染（`itime_build.render()`）→ 生成 `index.html`
5. 飞书发布（`--publish` 标志）

**入口**：
```bash
python3 refresh.py [--publish]
```

**常见问题**：
- 日历拉取超时 → 自动重试 4 次
- 日历拉取部分失败 → 保留上次结果，退出（防止贫血）
- 健康数据 <30 天 → 拒绝发布（防止数据不全）

**监控点**：
- `logs/` 目录的最新 log 文件
- `frozen_events.json` 是否最新（历史冻结，若过期表示拉取异常）

---

### 2. **前端构建** (`itime_build.py` 渲染引擎)

**职责**：生成交互式 HTML（爱时间 iTime 复刻）

**关键参数**：
```python
# L652-656 时间维度目标（核心配置）
{key:'sleep', period:'每天', target:7},      # ⭐ 睡眠：每天 7h = 29%
{key:'family', period:'每天', target:3},     # 家庭：每天 3h = 12.5%
{key:'strategy', period:'每周', target:10},  # 战略：每周 10h
# ... 其他维度
```

**输出**：
- `index.html`（400KB，包含内联所有数据）
- 支持 JS 的浏览器直接打开即用

**前端特性**：
- 24h 时间轮盘 + 时间线 + 统计面板
- 支持编辑/补录/删除日程
- localStorage 存储用户编辑（App 回流到云端）
- 响应式设计（手机友好）

---

### 3. **日程分类引擎** (`classify_apply.py` + `classify_events.py`)

**职责**：把日历事件自动分类到 11 个时间维度

**分类方式**：
1. **手工规则**（`classify-brain.json` 中的 `rules`）
   - 基于标题关键词匹配（正则 + 中英文支持）
   - 命中优先级最高
   
2. **用户修正**（`corrections.json` + App 回流）
   - 用户在 App 中改过的分类
   - 下次拉取会自动应用
   
3. **AI 兜底**（claude CLI）
   - 无规则可用 → 调用 Claude Sonnet 分类
   - 结果缓存到 `classify-brain.json` 防重复

**11 个时间维度**：
```
strategy(战略)
people(组织人才)
product(产品)
operations(日常运营)
external(对外关系)
global(全球事务)
growth(进修成长)
family(家庭)
self(自我时间)
travel(差旅)
sleep(睡眠)
```

**调整分类规则**：
```json
// classify-brain.json
{
  "rules": {
    "战略": {"pattern": ["规划|战略|季度目标"], "cat": "strategy"},
    "会议": {"pattern": ["同步|会议|sync"], "cat": "operations"}
  },
  "overrides": {
    "某个具体日程标题": {"cat": "strategy", "sub": "财务规划", "_note": "手工改"}
  }
}
```

---

### 4. **健康数据聚合** (`build_oura()` 函数)

**源**：`~/AI/DataLake/健康/normalized/daily/2026/*.json`

**优先级**：WHOOP > Oura > 无

**关键字段**：
```python
rows[date] = {
  "hrs": 7.3,         # 睡眠小时数（float）
  "hrv": 52,          # 心率变异度（ms）
  "rec": 90,          # 恢复分（0-100）
  "wake": 9.68,       # 起床时刻（24h 制）
  "bs": 2.07,         # 入睡时刻（24h 制）
  "nb": None          # 小睡时刻（可选）
}
```

**特殊处理**：
- UTC 时区问题：起床早于北京 08:00 的晚上数据从前一天 normalized 提取
- 原始数据补齐：用 raw/whoop 中的真实分期数据补充 normalized 缺失部分

---

## 🔑 关键文件地图

| 文件 | 用途 | 修改频率 |
|------|------|--------|
| `refresh.py` | 主同步脚本 | 低（新增依赖时） |
| `itime_build.py` | 前端渲染 + **目标定义** | 中（调目标时） |
| `classify_events.py` | 分类规则执行 | 低 |
| `classify_apply.py` | 规则应用逻辑 | 低 |
| `classify-brain.json` | 日程分类规则库 | 高（App 回流时） |
| `frozen_events.json` | 历史日程快照 | 自动（冻结机制） |
| `corrections.json` | 本地改类记录 | 中（用户编辑时） |
| `index.html` | 最终产物 | 每日更新 |

---

## ⚡ 常见维护任务

### 任务 1️⃣：调整睡眠目标

**需求**：从 7h/天 改成 7.5h/天

**步骤**：
```python
# 1. 编辑 itime_build.py L652
{key:'sleep', period:'每天', target:7.5}  # 从 7 改

# 2. 本地测试
python3 refresh.py

# 3. 查看 index.html 中睡眠目标是否变成 31.25%（而非 29%）

# 4. 发布
python3 refresh.py --publish
```

### 任务 2️⃣：添加日程分类规则

**需求**：每次「会见 CEO」事件自动分类为「对外」而不是「运营」

**步骤**：
```json
// classify-brain.json 中的 rules 增加
"external": {
  "pattern": ["会见|CEO|投资人|董事会"],
  "cat": "external"
}
```

### 任务 3️⃣：排查今天数据缺失

**症状**：7/14 的睡眠显示 "--"

**诊断**：
1. 检查时间 → 如果今天还没睡完（正常）
2. 检查 Oura/WHOOP 是否有数据 → `~/AI/DataLake/健康/normalized/daily/2026/2026-07-14.json`
3. 查 log → `tail -50 logs/refresh_*.log`
4. 确认 lark-cli 是否能正常访问飞书 → `lark-cli api GET /open-apis/calendar/v4/calendars`

---

## 🔐 安全与隐私

### 数据存储

- **本地**：`/Users/zoe/AI/Workspaces/APP/Health/zoe-time/`（含 git 历史，未加密）
- **云端**：飞书妙搭应用（飞书企业版权限控制）
- **外网同步**：Cloudflare Worker（ZT_TOKEN 鉴权，不存储原始数据）

### 凭证管理

| 凭证 | 位置 | 风险 | 对策 |
|------|------|------|------|
| `lark-cli auth` | `~/.lark/tokens.json` | 泄露 → 任意日历访问 | 使用 macOS Keychain |
| `ZT_TOKEN` | `refresh.py` L54 | 硬编码 | 考虑迁移到环境变量 |
| `APP_ID` | `refresh.py` L24 | 半公开 | 无实质风险（只读应用） |

### 建议升级

```bash
# 改用环境变量存储 token
export ZT_TOKEN="..."
# refresh.py 改为
ZT_TOKEN = os.getenv("ZT_TOKEN", "41326...")
```

---

## 📦 部署与运维

### 本地开发环境

**依赖**：
- Python 3.9+
- `lark-cli`（飞书命令行工具）
- `claude` CLI（AI 分类兜底）

**安装**：
```bash
# 如需重新部署
pip install --upgrade lark-cli
# 确保 claude 命令可用
which claude
```

### launchd 后台任务

**配置文件**：`~/.launchd/com.zoe.time-tracker.plist`（示意，实际路径需确认）

**启用**：
```bash
launchctl load ~/.launchd/com.zoe.time-tracker.plist
launchctl start com.zoe.time-tracker
```

**监控**：
```bash
launchctl list | grep zoe-time
tail -f ~/Library/Logs/zoe-time.log
```

---

## 🆘 故障排查

### 问题 A：`refresh.py` 执行失败

**日志**：
```
! 日历段 2026-07-01~2026-07-21 拉取失败
stderr=401 Unauthorized
```

**原因**：lark-cli 认证过期

**解决**：
```bash
lark-cli auth login
```

### 问题 B：App 在飞书中显示为空白

**可能**：
1. `index.html` 生成失败（检查 `refresh.py` log）
2. 飞书妙搭缓存（清浏览器缓存）
3. JavaScript 错误（浏览器控制台查看）

**排查**：
```bash
# 本地查看产物
open index.html

# 查看 console（F12）
# 如有错误，通常是 OURA_DATA/REAL_EVENTS 未正确生成
```

### 问题 C：Oura/WHOOP 数据显示"--"

**可能**：
1. 当日数据未生成（进行中的一天正常）
2. 健康数据同步中断（检查数据源目录）
3. 构建脚本中 `build_oura()` 路径错误

**检查**：
```bash
ls ~/AI/DataLake/健康/normalized/daily/2026/2026-07-14.json
# 如无，表示 Oura/WHOOP 还未上报该日数据

# 查看最新有数据的日期
ls -lt ~/AI/DataLake/健康/normalized/daily/2026/ | head
```

---

## 📚 相关文档

| 文档 | 位置 | 说明 |
|------|------|------|
| **README** | 本目录 | 用户指南 + 功能说明 |
| **HANDOFF** | 本文件 | 技术维护指南 |
| **睡眠目标分析** | Obsidian Vault | 2026-07-14 的目标定义分析 |

---

## ✅ 交接清单

- [x] 源代码迁移完毕（git 历史保留）
- [x] GitHub 仓库创建并推送
- [x] README.md 完成
- [x] HANDOFF.md 完成
- [x] 路径引用检查（相对路径，抗迁移）
- [x] launchd 后台任务验证
- [x] 飞书妙搭应用状态检查
- [x] Obsidian Vault 归档

---

## 🎯 下次改进方向

1. **Token 安全**：将 `ZT_TOKEN` 迁移到环境变量
2. **错误恢复**：添加 `--rebaseline` 模式强制重拉历史
3. **用户界面**：在 App 中加入"数据诊断"面板
4. **多维度目标**：支持运动、水摄入等额外维度
5. **云备份**：自动备份 `classify-brain.json` 到飞书

---

**最后更新**：2026-07-14  
**负责人**：Zoe  
**技术支持**：Claude Code
