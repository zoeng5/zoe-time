# Mac Studio 部署指南

## 为什么需要迁移？

| 指标 | MacBook Pro | Mac Studio |
|------|------------|-----------|
| **运行时间** | 间歇性（sleep/关机） | 24/7 |
| **launchd 可靠性** | 低（任务被跳过） | 高（持续运行） |
| **网络稳定性** | 依赖WiFi | 有线网络 |
| **功耗** | 受限 | 不受限 |
| **后台任务** | 易中断 | 稳定 |

**症状**：7/17 下午 5:30 才运行早上 7:00 的任务 = MacBook Pro 不可靠

---

## 部署步骤

### Step 1️⃣：在 Mac Studio 上克隆项目

在 Mac Studio 的终端中运行：

```bash
# 进入 App 目录
mkdir -p /Users/zoe/AI/Workspaces/APP/Health
cd /Users/zoe/AI/Workspaces/APP/Health

# 克隆 GitHub 仓库（或从 MacBook 拷贝）
git clone https://github.com/zoeng5/zoe-time.git
# 或从 MacBook 拷贝
rsync -avz /Users/zoe/AI/Workspaces/APP/Health/zoe-time/ zoe@mac-studio.local:/Users/zoe/AI/Workspaces/APP/Health/zoe-time/
```

### Step 2️⃣：验证依赖

```bash
# 检查 Python 3
python3 --version

# 检查 lark-cli
lark-cli --version

# 检查 claude CLI
which claude
```

### Step 3️⃣：在 Mac Studio 上配置 launchd

**创建任务文件**（Mac Studio 上）：

```bash
# 创建目录
mkdir -p /Users/zoe/Library/LaunchAgents

# 复制配置文件
cp /Users/zoe/AI/Workspaces/APP/Health/zoe-time/launchd/*.plist \
   /Users/zoe/Library/LaunchAgents/
```

**如果没有 plist 文件，创建新的**：

```bash
cat > /Users/zoe/Library/LaunchAgents/com.zoe.time-morning-poll.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.zoe.time-morning-poll</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>-u</string>
    <string>/Users/zoe/AI/Workspaces/APP/Health/zoe-time/morning_poll.py</string>
    <string>--start-hour</string>
    <string>7</string>
    <string>--end-hour</string>
    <string>10</string>
    <string>--interval</string>
    <string>5</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/zoe/AI/Workspaces/APP/Health/zoe-time</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>NO_PROXY</key>
    <string>*</string>
    <key>no_proxy</key>
    <string>*</string>
  </dict>
  <key>StartCalendarInterval</key>
  <array>
    <dict>
      <key>Hour</key>
      <integer>7</integer>
      <key>Minute</key>
      <integer>0</integer>
    </dict>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/zoe/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/zoe/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.err</string>
</dict>
</plist>
EOF
```

### Step 4️⃣：启动任务

```bash
# Mac Studio 上
launchctl load ~/Library/LaunchAgents/com.zoe.time-morning-poll.plist
launchctl load ~/Library/LaunchAgents/com.moodytiger.timetracker-refresh.plist

# 验证
launchctl list | grep zoe
```

### Step 5️⃣：禁用 MacBook Pro 上的任务

```bash
# MacBook Pro 上
launchctl unload ~/Library/LaunchAgents/com.zoe.time-morning-poll.plist
launchctl unload ~/Library/LaunchAgents/com.moodytiger.timetracker-refresh.plist

# 验证（应该显示为空）
launchctl list | grep zoe
```

---

## 跨机器文件同步

由于两台机器需要共享代码和数据，建议设置：

### 方案 A：GitHub 为中心（推荐）

```bash
# 任何机器上有更新：
cd /Users/zoe/AI/Workspaces/APP/Health/zoe-time
git add .
git commit -m "..."
git push

# 另一台机器上：
git pull
```

### 方案 B：rsync 实时同步

```bash
# MacBook Pro 定时同步到 Mac Studio
# 在 MacBook Pro 的 crontab 中添加
0 * * * * rsync -avz /Users/zoe/AI/Workspaces/APP/Health/zoe-time/ zoe@mac-studio.local:/Users/zoe/AI/Workspaces/APP/Health/zoe-time/
```

### 方案 C：iCloud Drive

```bash
# 如果代码放在 iCloud Drive 同步目录
# 优点：自动同步
# 缺点：不适合 git 仓库
```

---

## 数据目录配置

**WHOOP 数据同步**的几个问题：

1. **检查数据来源**
   ```bash
   # Mac Studio 上检查
   ls -la ~/AI/DataLake/健康/normalized/daily/2026/
   ```

2. **诊断为什么 WHOOP 没有更新**
   ```bash
   # 检查是否有相关的后台任务
   launchctl list | grep -i whoop
   launchctl list | grep -i health
   launchctl list | grep -i oura
   
   # 查看最近的日志
   tail -100 ~/AI/DataLake/健康/logs/*.log
   ```

3. **重新启动 WHOOP 同步**（如果有的话）
   ```bash
   # 通常的路径
   launchctl start com.whoop.sync
   # 或者手工运行同步脚本
   ```

---

## 监控和故障排查

### 在 Mac Studio 上监控

```bash
# 查看任务是否在运行
launchctl list | grep zoe.time

# 查看日志
tail -f /Users/zoe/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log

# 手工测试轮询
cd /Users/zoe/AI/Workspaces/APP/Health/zoe-time
python3 morning_poll.py --start-hour 7 --end-hour 10 --interval 5
```

### 跨机器测试

```bash
# MacBook Pro
ssh zoe@mac-studio.local

# 在 Mac Studio 上
launchctl list | grep zoe.time
tail -50 ~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log
```

---

## 常见问题

### Q1：两台机器同时修改会冲突吗？

**A**：使用 GitHub 作为中心是最安全的：
- MacBook Pro：开发和测试新功能 → git push
- Mac Studio：拉取最新代码 → 生产运行

### Q2：能否从 MacBook Pro 远程触发 Mac Studio 的任务？

**A**：可以，用 SSH：
```bash
ssh zoe@mac-studio.local launchctl start com.zoe.time-morning-poll
```

### Q3：如何验证 Mac Studio 上的任务真的在运行？

**A**：
```bash
# 检查最近的日志修改时间
ls -l ~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log

# 应该显示今天的时间（如果任务有运行过）
```

### Q4：WHOOP 数据什么时候才能再次更新？

**A**：需要诊断 WHOOP 数据同步脚本：
1. 找出哪个程序负责同步 WHOOP 数据
2. 确认它也部署在 Mac Studio 上
3. 检查日志看是否有错误

---

## 部署检查清单

- [ ] Mac Studio 上已克隆项目
- [ ] 检查 Python 3、lark-cli、claude CLI 已安装
- [ ] launchd 配置文件已复制到 Mac Studio
- [ ] Mac Studio 上的任务已加载：`launchctl load ~/Library/LaunchAgents/com.zoe.time-*.plist`
- [ ] MacBook Pro 上的任务已卸载：`launchctl unload ...`
- [ ] 验证 Mac Studio 上任务在 7:00 运行（查看日志）
- [ ] 诊断 WHOOP 数据同步问题

---

## 后续步骤

1. **立即**：在 Mac Studio 上部署，禁用 MacBook Pro
2. **短期**：诊断 WHOOP 数据为什么停止同步
3. **长期**：建立自动化测试，确保数据源持续更新

---

**部署日期**：2026-07-17  
**目标**：从 MacBook Pro 迁移到 Mac Studio（24/7 可靠性）
