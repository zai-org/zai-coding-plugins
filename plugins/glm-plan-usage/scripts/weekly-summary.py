#!/usr/bin/env python3
"""
GLM Weekly Trend Report — queries two weeks of usage and sends a Discord DM
with week-over-week comparison. Designed to run as a cron job (zero Hermes token cost).

Usage:
    python3 weekly-summary.py                 # Full run (query + send DM)
    python3 weekly-summary.py --dry-run       # Print report without sending DM
"""

import json
import logging
import os
import sys
import time
import ssl
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# Force Asia/Shanghai
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

# --- Config ---
GLM_CONFIG_PATH = os.path.expanduser("~/.glm-config")
DISCORD_CONFIG_PATH = os.path.expanduser("~/.discord-config")
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "weekly-summary.log")

log = logging.getLogger("weekly-summary")


def setup_logging():
    """Configure logging to both file and stdout."""
    os.makedirs(LOG_DIR, exist_ok=True)
    log.setLevel(logging.DEBUG)

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S"))

    log.addHandler(fh)
    log.addHandler(sh)


def load_key_value_file(path: str) -> dict:
    config = {}
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                eq = line.find("=")
                if eq == -1:
                    continue
                config[line[:eq].strip()] = line[eq + 1:].strip()
    except FileNotFoundError:
        log.error("[ERROR] Config file not found: %s", path)
        sys.exit(1)
    return config


def api_get(url: str, auth_token: str) -> dict:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={
        "Authorization": auth_token,
        "Accept-Language": "en-US,en",
        "Content-Type": "application/json",
        "User-Agent": "GLM-WeeklySummary/1.0",
    })
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        return data.get("data", data)


def send_discord_dm(bot_token: str, user_id: str, messages: list[str]) -> bool:
    """Send one or more DM messages (split if too long for Discord 2000 char limit)."""
    ctx = ssl.create_default_context()
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
        "User-Agent": "GLM-WeeklySummary/1.0",
    }
    try:
        # Create DM channel
        dm_payload = json.dumps({"recipient_id": user_id}).encode()
        dm_req = urllib.request.Request(
            "https://discord.com/api/v10/users/@me/channels",
            data=dm_payload, headers=headers, method="POST",
        )
        with urllib.request.urlopen(dm_req, context=ctx, timeout=15) as resp:
            channel_id = json.loads(resp.read().decode())["id"]

        for msg in messages:
            msg_payload = json.dumps({"content": msg}).encode()
            msg_req = urllib.request.Request(
                f"https://discord.com/api/v10/channels/{channel_id}/messages",
                data=msg_payload, headers=headers, method="POST",
            )
            with urllib.request.urlopen(msg_req, context=ctx, timeout=15) as resp:
                pass
        log.info("[DISCORD] %d DM message(s) sent to %s", len(messages), user_id)
        return True
    except Exception as e:
        log.error("[ERROR] Discord DM failed: %s", e)
        return False


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def pct_change(curr: float, prev: float) -> str:
    if prev == 0:
        return "🆕" if curr > 0 else "—"
    change = (curr - prev) / prev * 100
    if abs(change) < 1:
        return "→ 0%"
    if change > 0:
        return f"↑ {change:.0f}%"
    return f"↓ {abs(change):.0f}%"


def get_week_range(reference_date: datetime = None) -> tuple[datetime, datetime, int, int]:
    """Get last week's Monday 00:00 to Sunday 23:59:59 and ISO week number."""
    if reference_date is None:
        reference_date = datetime.now()

    # Find last Monday (start of last week)
    today_weekday = reference_date.weekday()  # 0=Monday
    days_since_monday = today_weekday
    this_monday = reference_date - timedelta(days=days_since_monday)
    this_monday = this_monday.replace(hour=0, minute=0, second=0, microsecond=0)

    last_monday = this_monday - timedelta(days=7)
    last_sunday_end = this_monday - timedelta(seconds=1)

    iso = last_monday.isocalendar()
    week_num = iso[1]
    year = iso[0]

    return last_monday, last_sunday_end, week_num, year


def get_prev_week_range(last_monday: datetime) -> tuple[datetime, datetime]:
    """Get the week before last week."""
    prev_monday = last_monday - timedelta(days=7)
    prev_sunday_end = last_monday - timedelta(seconds=1)
    return prev_monday, prev_sunday_end


def query_week(config: dict, start: datetime, end: datetime) -> dict:
    """Query model + tool usage for a time range."""
    fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")
    params = f"?startTime={urllib.parse.quote(fmt(start))}&endTime={urllib.parse.quote(fmt(end))}"

    model_data = api_get(f"{config['api_domain']}/api/monitor/usage/model-usage{params}", config["auth_token"])
    tool_data = api_get(f"{config['api_domain']}/api/monitor/usage/tool-usage{params}", config["auth_token"])

    return {"model": model_data, "tool": tool_data}


def aggregate_daily(model_data: dict) -> dict:
    """Aggregate hourly data by day."""
    x_time = model_data.get("x_time", [])
    tokens_usage = model_data.get("tokensUsage", [])
    call_counts = model_data.get("modelCallCount", [])

    daily = {}
    for t, tok, calls in zip(x_time, tokens_usage, call_counts):
        date_str = t.split(" ")[0]  # "2026-05-05"
        short = date_str[5:]  # "05-05"
        weekday_idx = datetime.strptime(date_str, "%Y-%m-%d").weekday()
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        if short not in daily:
            daily[short] = {"date": short, "weekday": weekday_names[weekday_idx], "tokens": 0, "calls": 0}
        daily[short]["tokens"] += tok
        daily[short]["calls"] += calls
    return daily


def aggregate_models(model_data: dict) -> dict:
    """Aggregate by model."""
    result = {}
    total = model_data.get("totalUsage", {}).get("totalTokensUsage", 0)
    for m in model_data.get("totalUsage", {}).get("modelSummaryList", []):
        name = m["modelName"]
        tokens = m["totalTokens"]
        pct = (tokens / total * 100) if total > 0 else 0
        result[name] = {"tokens": tokens, "pct": pct}
    return result


def aggregate_tools(tool_data: dict) -> dict:
    """Aggregate tool usage."""
    total = tool_data.get("totalUsage", {})
    return {
        "search": total.get("totalNetworkSearchCount", 0),
        "web-read": total.get("totalWebReadMcpCount", 0),
        "zread": total.get("totalZreadMcpCount", 0),
        "search-mcp": total.get("totalSearchMcpCount", 0),
    }


def find_peak_hours(model_data: dict, top_n: int = 5) -> list[tuple[str, str, int]]:
    """Find top N peak hours."""
    x_time = model_data.get("x_time", [])
    tokens_usage = model_data.get("tokensUsage", [])
    hourly = [(t, tok) for t, tok in zip(x_time, tokens_usage) if tok > 0]
    hourly.sort(key=lambda x: x[1], reverse=True)
    result = []
    for t, tok in hourly[:top_n]:
        parts = t.split(" ")
        date_short = parts[0][5:] if len(parts) > 1 else ""
        hour = parts[1][:5] if len(parts) > 1 else t
        result.append((date_short, hour, tok))
    return result


def bar_chart(daily: dict, width: int = 10) -> list[str]:
    """Generate ASCII bar chart for daily usage."""
    if not daily:
        return ["  (无数据)"]

    sorted_days = sorted(daily.items())
    max_val = max(d["tokens"] for d in daily.values())
    lines = []

    max_tokens = max_val
    min_tokens = min(d["tokens"] for d in daily.values())
    annotations = {}
    if max_tokens > 0:
        for k, v in daily.items():
            if v["tokens"] == max_tokens:
                annotations[k] = " ← 最高"
            elif min_tokens == max_tokens:
                pass
            elif v["tokens"] == min_tokens:
                annotations[k] = " ← 最低"

    for day, data in sorted_days:
        ratio = data["tokens"] / max_val if max_val > 0 else 0
        filled = round(ratio * width)
        bar = "█" * filled + "░" * (width - filled)
        ann = annotations.get(day, "")
        lines.append(f"  {data['weekday']} {day}  {bar}  {format_tokens(data['tokens'])}  {data['calls']}次{ann}")

    return lines


def build_report(config: dict) -> list[str]:
    """Build the weekly trend report. Returns list of messages (split for Discord 2000 char limit)."""
    now = datetime.now()
    last_monday, last_sunday_end, week_num, year = get_week_range(now)
    prev_monday, prev_sunday_end = get_prev_week_range(last_monday)

    log.info("Querying last week: %s ~ %s", last_monday.strftime("%Y-%m-%d"), last_sunday_end.strftime("%Y-%m-%d"))
    log.info("Querying prev week: %s ~ %s", prev_monday.strftime("%Y-%m-%d"), prev_sunday_end.strftime("%Y-%m-%d"))

    # Query both weeks
    last_week = query_week(config, last_monday, last_sunday_end)
    prev_week = query_week(config, prev_monday, prev_sunday_end)

    # Query current quota
    quota_data = api_get(f"{config['api_domain']}/api/monitor/usage/quota/limit", config["auth_token"])

    # Aggregate
    lw_daily = aggregate_daily(last_week["model"])
    pw_daily = aggregate_daily(prev_week["model"])

    lw_models = aggregate_models(last_week["model"])
    pw_models = aggregate_models(prev_week["model"])

    lw_tools = aggregate_tools(last_week["tool"])
    pw_tools = aggregate_tools(prev_week["tool"])

    lw_total_tokens = sum(d["tokens"] for d in lw_daily.values())
    lw_total_calls = sum(d["calls"] for d in lw_daily.values())
    pw_total_tokens = sum(d["tokens"] for d in pw_daily.values())
    pw_total_calls = sum(d["calls"] for d in pw_daily.values())

    # --- Build report ---
    date_range = f"{last_monday.strftime('%m.%d')} - {last_sunday_end.strftime('%m.%d')}"

    lines = []
    lines.append(f"📈 **GLM 每周趋势报告 — {year}-W{week_num:02d} ({date_range})**")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # Overview
    lines.append("**本周概览**")
    lines.append(f"  Tokens: {format_tokens(lw_total_tokens)} | 调用: {lw_total_calls:,} 次")
    lines.append(f"  vs 上周: {pct_change(lw_total_tokens, pw_total_tokens)} tokens, {pct_change(lw_total_calls, pw_total_calls)} 调用")
    lines.append("")

    # Daily distribution
    lines.append("**每日分布**")
    lines.extend(bar_chart(lw_daily))
    lines.append("")

    # Model distribution
    lines.append("**模型分布**")
    for name in sorted(lw_models.keys(), key=lambda n: lw_models[n]["tokens"], reverse=True):
        m = lw_models[name]
        prev_tok = pw_models.get(name, {}).get("tokens", 0)
        lines.append(f"  • {name}: {format_tokens(m['tokens'])} ({m['pct']:.0f}%)  {pct_change(m['tokens'], prev_tok)}")
    lines.append("")

    # Peak hours
    peaks = find_peak_hours(last_week["model"], 5)
    if peaks:
        lines.append("**峰值时段 Top 5**")
        for date_short, hour, tok in peaks:
            lines.append(f"  • {date_short} {hour} — {format_tokens(tok)}")
        lines.append("")

    # MCP tools
    lw_tool_sum = sum(lw_tools.values())
    pw_tool_sum = sum(pw_tools.values())
    if lw_tool_sum > 0 or pw_tool_sum > 0:
        tool_details = [f"{k}: {v}" for k, v in lw_tools.items() if v > 0]
        lines.append("**MCP 工具**")
        lines.append(f"  {' | '.join(tool_details)}")
        lines.append(f"  vs 上周: {pct_change(lw_tool_sum, pw_tool_sum)}")
        lines.append("")

    # Quota
    level = quota_data.get("level", "?")
    lines.append(f"**当前配额 (Plan: {level})**")
    for item in quota_data.get("limits", []):
        if item.get("type") == "TOKENS_LIMIT":
            pct = item.get("percentage", 0)
            reset_ts = item.get("nextResetTime")
            if reset_ts:
                reset_dt = datetime.fromtimestamp(reset_ts / 1000)
                lines.append(f"  • 5h Token 窗口: {pct}% (重置: {reset_dt.strftime('%m.%d %H:%M')})")
            else:
                lines.append(f"  • 5h Token 窗口: {pct}%")
        elif item.get("type") == "TIME_LIMIT":
            pct = item.get("percentage", 0)
            curr = item.get("currentValue", 0)
            total = item.get("usage", 0)
            remain = item.get("remaining", total - curr)
            lines.append(f"  • MCP 月度: {pct}% ({curr}/{total}, 剩余 {remain})")

    # Split into messages (Discord 2000 char limit)
    full_text = "\n".join(lines)
    messages = []
    if len(full_text) <= 2000:
        messages.append(full_text)
    else:
        # Split at section boundaries
        current_msg = []
        current_len = 0
        for line in lines:
            line_len = len(line) + 1  # +1 for newline
            if current_len + line_len > 1950 and current_msg:
                messages.append("\n".join(current_msg))
                current_msg = []
                current_len = 0
            current_msg.append(line)
            current_len += line_len
        if current_msg:
            messages.append("\n".join(current_msg))

    return messages


def main():
    parser = argparse.ArgumentParser(description="GLM Weekly Trend Report")
    parser.add_argument("--dry-run", action="store_true", help="Print report without sending DM")
    args = parser.parse_args()

    setup_logging()

    log.info("=" * 50)
    log.info("[%s] Weekly Summary started", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("=" * 50)

    glm_config = load_key_value_file(GLM_CONFIG_PATH)
    glm_config["auth_token"] = os.environ.get("ANTHROPIC_AUTH_TOKEN", glm_config.get("ANTHROPIC_AUTH_TOKEN", ""))
    glm_config["base_url"] = os.environ.get("ANTHROPIC_BASE_URL", glm_config.get("ANTHROPIC_BASE_URL", ""))

    if not glm_config["auth_token"] or not glm_config["base_url"]:
        log.error("[ERROR] GLM config incomplete")
        sys.exit(1)

    parsed = urllib.parse.urlparse(glm_config["base_url"])
    glm_config["api_domain"] = f"{parsed.scheme}://{parsed.netloc}"

    log.info("Building weekly trend report...")
    messages = build_report(glm_config)

    for i, msg in enumerate(messages):
        log.info("=" * 40)
        log.info("Message %d/%d (%d chars)", i + 1, len(messages), len(msg))
        log.info("=" * 40)
        log.info(msg)

    if args.dry_run:
        log.info("[DRY RUN] Not sending DM.")
        return

    # Send DM
    dc = load_key_value_file(DISCORD_CONFIG_PATH)
    dc_token = dc.get("DISCORD_BOT_TOKEN")
    dc_user = dc.get("DISCORD_ALLOWED_USERS")

    if not dc_token or not dc_user:
        log.error("[ERROR] Discord config missing, cannot send DM")
        sys.exit(1)

    if send_discord_dm(dc_token, dc_user, messages):
        log.info("✅ Weekly summary sent via Discord DM!")
    else:
        log.error("❌ Failed to send DM")
        sys.exit(1)


if __name__ == "__main__":
    main()
