# Zoe's Time — 个人时间管理 & 健康追踪系统

> 24h 时间轮盘 + 日程分类 + 睡眠/恢复 + 周报统计 | 爱时间(iTime) MTVI 复刻版

## 📱 应用入口

- **飞书妙搭**：https://moodytiger.aiforce.cloud/app/app_178sw3xwu14/
- **源代码**：本仓库（`/Users/zoe/AI/Workspaces/APP/Health/zoe-time/`）

---

## 🎯 核心功能

| 功能 | 说明 |
|------|------|
| **日时间轮盘** | 24h 环形时钟，实时展示当日时间分配（战略/人才/运营/家庭/自我/睡眠等） |
| **周/月/季/年统计** | 多维度时间归类统计 + 目标达成度 |
| **睡眠追踪** | 集成 Oura/WHOOP 数据，显示睡眠时长/质量/恢复分 |
| **日程智能分类** | 飞书日历 → 语义层分类（支持 AI 兜底）→ 视觉展示 |
| **手工补录** | App 回流修正，"越用越准"的机器学习基础 |
| **亲子陪伴** | 近 30 天按孩子汇总陪伴时长，实时同步到成长记录底座 |

---

## 🏗️ 系统架构

```
数据流向：
┌─ Oura/WHOOP 设备 ─→ ~/AI/DataLake/健康/normalized/daily/{date}.json
└─ 飞书日历       ─→ lark-cli calendar +agenda
                  ↓
          refresh.py (每日同步)
                  ↓
    ┌─ 日程分类（语义层 + AI）
    ├─ 睡眠数据聚合
    └─ 亲子陪伴计算
                  ↓
          itime_build.py (前端渲染)
                  ↓
            index.html (400KB)
                  ↓
          飞书妙搭发布
                  ↓
           用户访问
```

---

## 📂 项目结构

```
zoe-time/
├── .git/                      # Git 历史（完整保留）
├── refresh.py                 # 每日数据刷新 + 渲染管线（主脚本）
├── itime_build.py             # iTime App 前端构建（目标定义在此）
├── classify_events.py         # 日程分类逻辑
├── classify_apply.py          # 分类规则执行
│
├── index.html                 # 最终产物（发布到飞书）
├── index.pre-live.html        # 版本快照（7.1版本）
├── index.pre-redesign.html    # 版本快照（重设计前）
│
├── classify-brain.json        # 语义层规则库（ML 脑）
├── frozen_events.json         # 历史日程快照（>GRACE_DAYS 被冻结）
├── corrections.json           # App 回流修正（用户改类记录）
│
├── mac-app/                   # macOS 原生应用框架
├── sync-worker/               # 云端同步 Worker（Cloudflare）
├── backups/                   # 日期归档备份
└── logs/                       # 运行日志

conf:
├── APP_ID                     飞书应用 ID: app_178sw3xwu14
├── OURA_DIR                   健康数据源: ~/AI/DataLake/健康/normalized/daily
├── CAL_ID                     飞书日历 ID
├── KIDS_BASE / KIDS_TABLE     亲子陪伴同步目标
└── SYNC_URL + ZT_TOKEN        云端同步服务器 (Cloudflare Worker)
```

---

## ⚙️ 使用说明

### 本地开发/测试

```bash
cd /Users/zoe/AI/Workspaces/APP/Health/zoe-time/

# 查看帮助
python3 refresh.py --help

# 一次性刷新（输出到 index.html，不上传）
python3 refresh.py

# 测试 dry-run（验证流程，不生成产物）
# （暂无实现，可自行扩展）
```

### 部署流程

```bash
# 1. 本地刷新（拉飞书日历 + 健康数据 → 渲染 HTML）
python3 refresh.py

# 2. 发布到飞书妙搭
python3 refresh.py --publish

# 3. 日志检查
tail -f logs/refresh_*.log
```

### 定时同步（launchd）

已配置后台同步，每日自动运行。查看状态：

```bash
launchctl list | grep zoe-time
```

---

## 🎯 关键配置

### 睡眠目标定义

**文件**：`itime_build.py` L652

```javascript
{key:'sleep', period:'每天', target:7}  // 每天 7 小时 = 周 29%
```

**可调参数**：
- `target: 7` → 改为 7.5 或 8.0（根据个人需求）
- `period: '每天'` → 固定（不支持每周目标）

### 其他时间维度目标

见 `itime_build.py` L650-656，包含：
- 家庭：3h/天（可改为 3.5）
- 自我：1h/天
- 战略：10h/周
- 成长：5h/周
- 人才：6h/周
- 等等

---

## 🔄 数据流详解

### 睡眠数据

**来源**：`~/AI/DataLake/健康/normalized/daily/2026/{date}.json`

**格式**：
```json
{
  "date": "2026-07-13",
  "sleep_hours": 7.98,
  "whoop_sleep_hours": 7.98,
  "whoop_sleep_efficiency_pct": 97.854,
  "whoop_sleep_performance_pct": 87.0,
  "whoop_recovery_score": 96.0,
  "whoop_hrv_rmssd_ms": 55.917,
  "oura_sleep_hours": 8.03,
  "oura_sleep_efficiency_pct": 96
}
```

**优先级**：WHOOP 数据优先，无则用 Oura，无则显示 "--"

### 日程数据

**来源**：飞书日历（lark-cli 拉取）

**分类规则**：
1. **语义层优先**：`classify-brain.json` 中的手工规则
2. **AI 兜底**：无规则时调用 Claude CLI 分类
3. **App 回流**：用户在应用中改类的修正会存到 corrections.json

**历史冻结**：>GRACE_DAYS (2天) 的日期冻结，飞书同步不覆盖，保护人工修正

---

## 🚀 部署记录

| 版本 | 日期 | 关键变更 |
|------|------|--------|
| v0.8 | 2026-07-14 | 迁移到 `/APP/Health/zoe-time/`；发布 GitHub |
| v0.7 | 2026-07-12 | 双语支持 + 睡眠质量显示 |
| v0.6 | 2026-07-05 | 亲子陪伴实时同步 + 日程冻结机制 |

---

## 📝 已知限制

| 限制 | 说明 | 影响 |
|-----|------|------|
| **当日睡眠延迟** | Oura/WHOOP 需要起床后才能定稿 | 进行中的一天显示"--" |
| **日历同步 30 日** | 回看最多 190 天（年初），未来 10 天 | 超出窗口的事件不可见 |
| **飞书 API 限制** | 分段拉取可能失败 → 保留上次结果 | 旧数据比新数据落后可能数小时 |
| **应用唯一用户** | 单用户系统（硬编码 Zoe） | 不支持多人使用 |

---

## 🔧 常见操作

### 调整睡眠目标

```python
# itime_build.py L652
{key:'sleep', period:'每天', target:7.5}  # 从 7 改成 7.5

# 再次运行刷新
python3 refresh.py --publish
```

### 修改日程分类规则

编辑 `classify-brain.json`，添加规则到 `rules` 或 `overrides`：

```json
{
  "overrides": {
    "我的日程标题": {"cat": "strategy", "sub": "战略梳理", "_note": "手工改类"}
  }
}
```

### 查看运行日志

```bash
tail -50 logs/refresh_*.log
# 或找最新的
ls -lt logs/ | head
```

---

## 📞 支持与联系

- **Bug 反馈**：在应用中点击「目标」页的反馈按钮
- **特性请求**：通过飞书私聊 Zoe
- **技术问题**：见 HANDOFF.md

---

**最后更新**：2026-07-14  
**维护者**：Zoe  
**许可**：Private (moodytiger)
