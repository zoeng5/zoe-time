#!/usr/bin/env python3
"""
晨间睡眠数据轮询 — 从早上开始频繁刷新，直到获得 WHOOP 睡眠数据为止
==========================================================

背景：WHOOP 数据通常在起床后 30-120 分钟到达，用户希望早上打开应用时能立即看到睡眠数据。
解决方案：从 7:00 开始，每 5 分钟刷新一次，一旦检测到新的睡眠数据就立即发布并退出。

用法：python3 morning_poll.py [--start-hour 7] [--end-hour 10] [--interval 5]
"""
import json, datetime, time, os, subprocess, sys, glob

TZ = datetime.timezone(datetime.timedelta(hours=8))
HOME = os.path.expanduser("~")
BASE = os.path.dirname(os.path.abspath(__file__))
OURA_DIR = os.path.join(HOME, "AI/DataLake/健康/normalized/daily")

def log(msg):
    ts = datetime.datetime.now(TZ).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def get_latest_sleep_date():
    """获取最新有睡眠数据的日期"""
    try:
        today = datetime.datetime.now(TZ).date()
        for offset in range(3):  # 检查今天往前 3 天
            check_date = today - datetime.timedelta(days=offset)
            path = os.path.join(OURA_DIR, check_date.strftime("%Y"), f"{check_date.isoformat()}.json")
            if os.path.exists(path):
                try:
                    data = json.load(open(path, encoding="utf-8"))
                    # 检查是否有睡眠数据（WHOOP 优先）
                    if data.get("whoop_sleep_hours") or data.get("oura_sleep_hours"):
                        return check_date, data
                except Exception:
                    pass
        return None, None
    except Exception as e:
        log(f"❌ 获取睡眠数据失败: {e}")
        return None, None

def refresh_app():
    """调用 refresh.py 刷新应用"""
    try:
        result = subprocess.run(
            ["python3", os.path.join(BASE, "refresh.py"), "--publish"],
            cwd=BASE,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def morning_poll(start_hour=7, end_hour=10, interval=5):
    """
    晨间轮询主逻辑

    Args:
        start_hour: 开始轮询的小时（默认 7）
        end_hour: 停止轮询的小时（默认 10）
        interval: 轮询间隔（分钟，默认 5）
    """
    today = datetime.datetime.now(TZ).date()
    log(f"🌅 晨间睡眠轮询启动 | 目标: {today} | 运行: {start_hour}:00-{end_hour}:59 | 间隔: {interval}分钟")

    # 记录初始状态
    initial_date, initial_data = get_latest_sleep_date()
    if initial_data:
        initial_sleep = initial_data.get("whoop_sleep_hours") or initial_data.get("oura_sleep_hours")
        log(f"📊 初始状态: {initial_date} 睡眠 {initial_sleep:.1f}h")
    else:
        log(f"📊 初始状态: 暂无睡眠数据")

    poll_count = 0
    while True:
        now = datetime.datetime.now(TZ)
        hour = now.hour

        # 检查时间范围
        if hour >= end_hour:
            log(f"⏰ 已到 {end_hour}:00，停止轮询")
            break

        if hour < start_hour:
            # 还没到开始时间，等待
            wait_mins = (start_hour - hour) * 60 - now.minute
            log(f"⏳ 未到开始时间 ({start_hour}:00)，待机 {wait_mins} 分钟")
            time.sleep(min(wait_mins * 60, 600))  # 最多等 10 分钟后重新检查
            continue

        # 检查是否有新的睡眠数据
        latest_date, latest_data = get_latest_sleep_date()
        latest_sleep = latest_data.get("whoop_sleep_hours") or latest_data.get("oura_sleep_hours") if latest_data else None

        # 判断是否有新数据
        has_new_data = False
        if latest_data and latest_date == today:
            # 今天有睡眠数据
            if not initial_data or initial_date != today:
                # 之前没有或不是今天的
                has_new_data = True
            elif initial_data and latest_sleep and latest_data.get("whoop_sleep_hours") and initial_data.get("whoop_sleep_hours"):
                # 都有，但 WHOOP 数据可能更新了
                has_new_data = latest_sleep != (initial_data.get("whoop_sleep_hours") or initial_data.get("oura_sleep_hours"))

        poll_count += 1
        ts = now.strftime("%H:%M")

        if has_new_data and latest_sleep:
            log(f"✅ 轮询 #{poll_count} ({ts}): 检测到新睡眠数据 {latest_date} {latest_sleep:.1f}h")
            log(f"🔄 立即发布更新...")
            success, output = refresh_app()
            if success:
                log(f"🎉 发布成功！今日睡眠已更新为 {latest_sleep:.1f}h")
                log(f"✨ 晨间轮询完成，共轮询 {poll_count} 次")
                return True
            else:
                log(f"⚠️ 发布失败: {output[:200]}")
                # 继续轮询
        else:
            status = "等待数据" if not latest_sleep else f"数据检查中 ({latest_sleep:.1f}h)"
            log(f"⏳ 轮询 #{poll_count} ({ts}): {status}，{interval} 分钟后重试")

        # 等待下一轮
        time.sleep(interval * 60)

    # 时间范围结束，一律刷新一次确保应用是最新的
    log(f"🔄 时间范围结束，执行最后一次刷新...")
    success, output = refresh_app()
    if success:
        log(f"✨ 晨间轮询结束，共轮询 {poll_count} 次")
        return True
    else:
        log(f"⚠️ 最后一次刷新失败")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="晨间睡眠数据智能轮询")
    parser.add_argument("--start-hour", type=int, default=7, help="开始轮询的小时（默认 7）")
    parser.add_argument("--end-hour", type=int, default=10, help="停止轮询的小时（默认 10）")
    parser.add_argument("--interval", type=int, default=5, help="轮询间隔（分钟，默认 5）")

    args = parser.parse_args()

    try:
        success = morning_poll(args.start_hour, args.end_hour, args.interval)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("⛔ 轮询被中断")
        sys.exit(130)
    except Exception as e:
        log(f"❌ 轮询异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
