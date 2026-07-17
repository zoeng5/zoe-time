# WHOOP 数据同步中断事件总结

**日期**：2026-07-17  
**状态**：🟢 已修复

---

## 事件摘要

**症状**：
- 7/17 全天无新睡眠数据（日视图显示 "--"）
- 只有 7/16 及更早的数据可用

**根本原因**：网络故障（DNS 解析失败）→ health_archive 同步任务失败 → 数据管道断裂

**影响范围**：
- MacBook Pro 上的定期同步任务（10:30、15:30、22:30）
- morning_poll.py 早晨轮询无法找到新数据

---

## 时间线

| 时间 | 事件 | 状态 |
|------|------|------|
| 7/16 22:45 | 最后一次成功同步 | ✅ |
| 7/17 10:30 | WHOOP API 请求失败（DNS 错误） | ❌ DNS 解析失败 |
| 7/17 10:30 | morning-poll 启动，检测到无新数据 | ⏸️ 0 次轮询后退出 |
| 7/17 15:30 | 重试，DNS 仍然不通 | ❌ 再次失败 |
| 7/17 17:30 | MacBook Pro 任务延迟执行（应该 7:00） | ⚠️ launchd 调度问题 |
| 2026-07-17 09:39 | 网络恢复，DNS 恢复正常 | ✅ |
| 2026-07-17 17:39 | 手动同步 + 应用发布 | ✅ 已修复 |

---

## 技术细节

### 故障原因：网络故障

```
[2026-07-17 10:30:05] Oura daily_sleep failed: <urlopen error [Errno 8] nodename nor servname provided, or not known>
[2026-07-17 10:30:05] WHOOP refresh failed: <urlopen error [Errno 8] nodename nor servname provided, or not known>
```

**Errno 8** = DNS 解析失败（`nodename nor servname provided`）
- 系统无法将 `api.prod.whoop.com` 和 `api.ouraring.com` 解析为 IP 地址
- 可能原因：
  - WiFi 断开 / 重新连接
  - DNS 服务器不可达
  - 网络配置临时丢失
  - ISP 或运营商故障

### 为什么没有自动重试

MacBook Pro 上的 health_archive 任务在 10:30、15:30、22:30 运行，但：

1. **这些是标准的 launchd 任务**，不具备自动重试机制
2. **network_state 不被监测**，任务按时运行但失败后就停止了
3. **morning_poll 只轮询到 10:00**，10:30 的重试已经超出时间范围

### 为什么 morning-poll 没有帮助

虽然 morning_poll.py 设计用于在早上 7-10 点不断检查新数据，但它也有同样的问题：

```
[17:30:53] 🌅 晨间睡眠轮询启动 | 目标: 2026-07-17 | 运行: 7:00-10:59
[17:30:53] 初始状态: 2026-07-16 睡眠 5.5h
[17:30:53] ⏰ 已到 10:00，停止轮询
```

**问题**：任务在 17:30（下午 5:30）才启动！这是 MacBook Pro 不可靠的证据。

---

## 修复方案

### ✅ 立即修复（已完成）

1. 确认网络已恢复
2. 手动运行 `run_daily_health_archive.sh`
3. 手动发布应用 `refresh.py --publish`

**结果**：7/17 数据已生成并发布

```json
{
  "date": "2026-07-17",
  "sleep_hours": 6.12,        // WHOOP
  "recovery_score": 63.0,      // WHOOP
  "oura_steps": 1871           // Oura
}
```

### 🔄 短期改进（下一步）

**A. 在 Mac Studio 上部署 health_archive 同步任务**

Mac Studio 24/7 运行，launchd 调度更可靠，可以承担主要同步职责。

```bash
# 在 Mac Studio 上
cp /Users/zoe/Library/LaunchAgents/com.zoe.all-in-context.health.plist \
   ~/Library/LaunchAgents/

# 验证
launchctl load ~/Library/LaunchAgents/com.zoe.all-in-context.health.plist
```

**B. 禁用 MacBook Pro 上的 health_archive 任务**

避免重复、冲突和延迟执行：

```bash
# 在 MacBook Pro 上
launchctl unload ~/Library/LaunchAgents/com.zoe.all-in-context.health.plist
```

### 🛡️ 长期防护

1. **网络监测**：如果可行，修改 health_archive.py 加入网络检查和指数级退避重试
2. **告警系统**：如果 48 小时内没有新数据，发送通知
3. **同步 GitHub**：定期检查时间戳，在 CI/CD 中检测数据断裂

---

## 当前状态

- ✅ 7/17 数据已恢复并发布
- ✅ 应用已更新
- ⏳ **待做**：部署到 Mac Studio 以避免重复

---

## 参考文档

- [DEPLOY_MAC_STUDIO.md](./DEPLOY_MAC_STUDIO.md) — Mac Studio 部署指南
- [MORNING_POLL.md](./MORNING_POLL.md) — 晨间轮询系统说明
- [health_archive.py](https://github.com/zoeng5/zoe-time/blob/main/docs/WHOOP_SYNC_ARCHITECTURE.md) — WHOOP 同步架构

