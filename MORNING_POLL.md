# 晨间睡眠数据智能轮询系统

## 问题背景

在早上打开 Zoe's Time 应用时，用户经常看不到昨晚的睡眠数据，因为：
- WHOOP 数据需要在用户起床后 30-120 分钟才能同步到系统
- 原先的刷新计划是 6:40、11:00、16:00，无法及时捕捉早起的情况
- 用户需要手工刷新或等待 11:00 的定时刷新

## 解决方案

**晨间智能轮询**（`morning_poll.py`）：

```
每天 7:00 启动
    ↓
每 5 分钟检查一次 WHOOP 数据
    ↓
检测到今天有新的睡眠数据？
    ├─ 是 → 立即发布更新 → 退出轮询 ✅
    └─ 否 → 继续等待
    
到达 10:00？
    ├─ 是 → 无论是否有数据都做最后一次刷新 → 退出轮询
    └─ 否 → 继续
```

**工作流**：

| 时间 | 事件 | 说明 |
|------|------|------|
| 7:00 | 启动晨间轮询 | 开始每 5 分钟检查一次 |
| 7:00-7:30 | 轮询中... | 等待 WHOOP 数据到达 |
| 7:35 | ✅ 检测到睡眠数据 | 立即发布应用 → 应用更新 → 轮询退出 |
| | | 用户打开应用即可看到最新睡眠记录 |
| 11:00 | 定时刷新 | 独立的定时任务 |
| 16:00 | 定时刷新 | 独立的定时任务 |

---

## 配置细节

### launchd 任务

**文件**：`~/.LaunchAgents/com.zoe.time-morning-poll.plist`

```xml
<key>StartCalendarInterval</key>
<array>
  <dict>
    <key>Hour</key>
    <integer>7</integer>           <!-- 每天 7:00 启动 -->
    <key>Minute</key>
    <integer>0</integer>
  </dict>
</array>
```

### 轮询参数（可配置）

```bash
# 查看当前配置
cat ~/.LaunchAgents/com.zoe.time-morning-poll.plist

# 参数说明
--start-hour 7      # 开始轮询的小时（默认 7）
--end-hour 10       # 停止轮询的小时（默认 10）
--interval 5        # 轮询间隔（分钟，默认 5）
```

### 日志位置

- **标准输出**：`~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log`
- **错误日志**：`~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.err`

**查看日志**：
```bash
tail -f ~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log
```

---

## 工作原理

### 1. 睡眠数据检测

```python
# 检查数据源
~/AI/DataLake/健康/normalized/daily/2026/2026-07-14.json

# 优先级：WHOOP > Oura
{
  "whoop_sleep_hours": 7.98,        # 优先用这个
  "oura_sleep_hours": 8.03,         # 备选
}
```

### 2. 智能停止逻辑

轮询会在以下情况停止：

✅ **主动退出**（找到新数据）：
- 检测到今天有睡眠数据（`whoop_sleep_hours` 或 `oura_sleep_hours` 不为空）
- 这个数据在之前的轮询中不存在（新数据）
- 立即调用 `refresh.py --publish` 发布

⏰ **时间结束**（到达 10:00）：
- 无论是否有数据都执行最后一次刷新
- 防止轮询无限进行

❌ **异常退出**：
- 刷新脚本失败（会打印错误并继续）
- launchd 进程被中断

### 3. 与现有系统集成

```
morning_poll.py
    ↓
调用 refresh.py --publish
    ↓
├─ 拉飞书日历
├─ 拉 Oura/WHOOP 数据
├─ 分类日程
├─ 渲染 HTML
└─ 发布到飞书妙搭

（完全复用现有的 refresh.py 逻辑）
```

---

## 使用手册

### 手工运行（测试）

```bash
cd /Users/zoe/AI/Workspaces/APP/Health/zoe-time

# 默认参数（7-10 点，5 分钟间隔）
python3 morning_poll.py

# 自定义参数
python3 morning_poll.py --start-hour 6 --end-hour 11 --interval 3
```

### 查看运行状态

```bash
# 检查是否在运行
ps aux | grep morning_poll.py

# 查看日志
tail -50 ~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log

# 实时监听
tail -f ~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log
```

### 管理 launchd 任务

```bash
# 加载任务
launchctl load ~/Library/LaunchAgents/com.zoe.time-morning-poll.plist

# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.zoe.time-morning-poll.plist

# 检查任务状态
launchctl list | grep "zoe.time"

# 手工启动（用于测试）
launchctl start com.zoe.time-morning-poll
```

---

## 日志示例

### 成功场景

```
[07:00:15] 🌅 晨间睡眠轮询启动 | 目标: 2026-07-14 | 运行: 7:00-10:59 | 间隔: 5分钟
[07:00:20] 📊 初始状态: 暂无睡眠数据
[07:00:21] ⏳ 轮询 #1 (07:00): 等待数据，5 分钟后重试
[07:05:22] ⏳ 轮询 #2 (07:05): 等待数据，5 分钟后重试
[07:10:23] ⏳ 轮询 #3 (07:10): 等待数据，5 分钟后重试
[07:15:24] ✅ 轮询 #4 (07:15): 检测到新睡眠数据 2026-07-14 7.98h
[07:15:25] 🔄 立即发布更新...
[07:15:45] 🎉 发布成功！今日睡眠已更新为 7.98h
[07:15:46] ✨ 晨间轮询完成，共轮询 4 次
```

### 超时场景

```
[07:00:15] 🌅 晨间睡眠轮询启动 | 目标: 2026-07-14 | 运行: 7:00-10:59 | 间隔: 5分钟
...
[09:55:00] ⏳ 轮询 #56 (09:55): 等待数据，5 分钟后重试
[10:00:01] ⏰ 已到 10:00，停止轮询
[10:00:02] 🔄 时间范围结束，执行最后一次刷新...
[10:00:25] ✨ 晨间轮询结束，共轮询 56 次
```

---

## 故障排查

### 问题 A：任务没有启动

**症状**：7:00 时没有日志生成

**诊断**：
```bash
launchctl list | grep zoe.time
# 如果输出 PID 为 0，表示上次运行失败

# 查看错误
tail -20 ~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.err
```

**解决**：
```bash
# 重新加载
launchctl unload ~/Library/LaunchAgents/com.zoe.time-morning-poll.plist
launchctl load ~/Library/LaunchAgents/com.zoe.time-morning-poll.plist
```

### 问题 B：轮询不停止（无限循环）

**症状**：任务一直运行，没有停止

**可能原因**：
1. refresh.py 失败 → 轮询继续等待
2. 睡眠数据目录不可达

**检查**：
```bash
tail -100 ~/AI/Workspaces/APP/Health/zoe-time/logs/morning-poll.log | grep -E "❌|⚠️"

# 验证数据目录
ls ~/AI/DataLake/健康/normalized/daily/2026/$(date +%Y-%m-%d).json
```

### 问题 C：脚本找不到路径

**症状**：日志显示"找不到 refresh.py"

**原因**：路径硬编码在脚本中，如果项目迁移需要更新

**解决**：
```python
# morning_poll.py 中的路径定义
BASE = os.path.dirname(os.path.abspath(__file__))  # 自动相对当前脚本
OURA_DIR = os.path.join(HOME, "AI/DataLake/健康/normalized/daily")

# 确保都是绝对路径，无需修改
```

---

## 性能考量

### 资源消耗

- **CPU**：每次刷新 ~2-3%（持续 10-30 秒）
- **网络**：每次刷新 ~5MB（日历 + 数据拉取）
- **磁盘**：日志文件 ~1MB/月

### 优化建议

1. **减少轮询频率**：从 5 分钟改为 10 分钟
   ```bash
   # 编辑 plist 文件的 --interval 参数
   ```

2. **早期停止**：如果 8:00 还没数据，跳过继续轮询
   ```python
   # 可在 morning_poll.py 中添加逻辑
   if hour >= 8 and not has_new_data:
       log("数据未到，降级到下次定时刷新")
       break
   ```

3. **仅在需要时启动**：改为手工触发而非自动
   ```bash
   # 移除 StartCalendarInterval，用手工命令替代
   launchctl start com.zoe.time-morning-poll
   ```

---

## 未来改进

- [ ] 支持自定义轮询时间窗口（UI 中添加设置）
- [ ] 睡眠数据变化时发送通知
- [ ] 轮询统计仪表板（轮询次数、平均等待时间）
- [ ] 支持其他健康指标（HRV、恢复分等）

---

**最后更新**：2026-07-14  
**功能新增版本**：v0.9
