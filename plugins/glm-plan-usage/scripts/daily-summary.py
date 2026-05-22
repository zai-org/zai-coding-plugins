#!/usr/bin/env python3
"""
GLM Daily Usage Summary — queries usage and sends a Discord DM report.
Designed to run as a cron job (zero Hermes token cost).

Usage:
    python3 daily-summary.py                 # Full run (query + send DM)
    python3 daily-summary.py --dry-run       # Print report without sending DM
    python3 daily-summary.py --send-only     # Send last cached report
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
from datetime import datetime, timedelta, timezone

# Force Asia/Shanghai
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

# --- Config ---
GLM_CONFIG_PATH = os.path.expanduser("~/.glm-config")
DISCORD_CONFIG_PATH = os.path.expanduser("~/.discord-config")
CACHE_PATH = os.path.expanduser("~/.glm-daily-summary.json")
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "daily-summary.log")

log = logging.getLogger("daily-summary")


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
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            eq = line.find("=")
            if eq == -1:
                continue
            config[line[:eq].strip()] = line[eq + 1:].strip()
    return config


def api_get(url: str, auth_token: str) -> dict:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={
        "Authorization": auth_token,
        "Accept-Language": "en-US,en",
        "Content-Type": "application/json",
        "User-Agent": "GLM-DailySummary/1.0",
    })
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        return data.get("data", data)


def send_discord_dm(bot_token: str, user_id: str, message: str) -> bool:
    ctx = ssl.create_default_context()
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
        "User-Agent": "GLM-DailySummary/1.0",
    }
    try:
        dm_payload = json.dumps({"recipient_id": user_id}).encode()
        dm_req = urllib.request.Request(
            "https://discord.com/api/v10/users/@me/channels",
            data=dm_payload, headers=headers, method="POST",
        )
        with urllib.request.urlopen(dm_req, context=ctx, timeout=15) as resp:
            channel_id = json.loads(resp.read().decode())["id"]

        msg_payload = json.dumps({"content": message}).encode()
        msg_req = urllib.request.Request(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            data=msg_payload, headers=headers, method="POST",
        )
        with urllib.request.urlopen(msg_req, context=ctx, timeout=15) as resp:
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


def format_duration(hours: float) -> str:
    h = int(hours)
    m = int((hours - h) * 60)
    if h > 0:
        return f"{h}h{m:02d}m"
    return f"{m}m"


def build_report(config: dict) -> str:
    base_domain = config["api_domain"]
    token = config["auth_token"]
    now = datetime.now()

    # Query yesterday's usage (00:00 - 23:59:59)
    yesterday = now - timedelta(days=1)
    start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999)

    fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")
    params = f"?startTime={urllib.parse.quote(fmt(start))}&endTime={urllib.parse.quote(fmt(end))}"

    # Fetch data
    model_data = api_get(f"{base_domain}/api/monitor/usage/model-usage{params}", token)
    tool_data = api_get(f"{base_domain}/api/monitor/usage/tool-usage{params}", token)
    quota_data = api_get(f"{base_domain}/api/monitor/usage/quota/limit", token)

    date_str = yesterday.strftime("%Y-%m-%d")

    # --- Model usage ---
    total_calls = model_data.get("totalUsage", {}).get("totalModelCallCount", 0)
    total_tokens = model_data.get("totalUsage", {}).get("totalTokensUsage", 0)

    model_lines = []
    for m in model_data.get("totalUsage", {}).get("modelSummaryList", []):
        name = m["modelName"]
        tokens = m["totalTokens"]
        pct = (tokens / total_tokens * 100) if total_tokens > 0 else 0
        model_lines.append(f"  • {name}: {format_tokens(tokens)} tokens ({pct:.0f}%)")

    # --- Peak hours ---
    x_time = model_data.get("x_time", [])
    tokens_usage = model_data.get("tokensUsage", [])
    hourly = []
    for t, u in zip(x_time, tokens_usage):
        if u > 0:
            hourly.append((t, u))
    hourly.sort(key=lambda x: x[1], reverse=True)
    peak_lines = []
    for t, u in hourly[:3]:
        hour = t.split(" ")[1] if " " in t else t
        peak_lines.append(f"  • {hour} — {format_tokens(u)}")

    # --- Tool usage ---
    tool_total = tool_data.get("totalUsage", {})
    search_count = tool_total.get("totalNetworkSearchCount", 0)
    webread_count = tool_total.get("totalWebReadMcpCount", 0)
    zread_count = tool_total.get("totalZreadMcpCount", 0)
    tool_sum = search_count + webread_count + zread_count

    # --- Quota ---
    quota_lines = []
    for item in quota_data.get("limits", []):
        if item.get("type") == "TOKENS_LIMIT":
            pct = item.get("percentage", 0)
            reset_ts = item.get("nextResetTime")
            if reset_ts:
                reset_dt = datetime.fromtimestamp(reset_ts / 1000)
                quota_lines.append(f"  • 5h Token 窗口: {pct}% (重置: {reset_dt.strftime('%H:%M')})")
            else:
                quota_lines.append(f"  • 5h Token 窗口: {pct}%")
        elif item.get("type") == "TIME_LIMIT":
            pct = item.get("percentage", 0)
            curr = item.get("currentValue", 0)
            total = item.get("usage", 0)
            remain = item.get("remaining", total - curr)
            details = item.get("usageDetails", [])
            detail_str = " / ".join(f"{d['modelCode']}: {d['usage']}" for d in details)
            quota_lines.append(f"  • MCP 月度: {pct}% ({curr}/{total}, 剩余 {remain})")
            if detail_str:
                quota_lines.append(f"    ({detail_str})")

    level = quota_data.get("level", "?")

    # --- Active hours ---
    active_hours = len(hourly)
    first_active = hourly[-1][0].split(" ")[1] if hourly else "—"
    last_active = hourly[0][0].split(" ")[1] if hourly else "—"

    # --- Build report ---
    report = (
        f"📊 **GLM 每日用量报告 — {date_str}**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**总用量**\n"
        f"  Tokens: {format_tokens(total_tokens)} | 调用: {total_calls} 次\n"
        f"  活跃时段: {active_hours} 小时 ({first_active} ~ {last_active})\n\n"
        f"**模型分布**\n"
        + "\n".join(model_lines) + "\n\n"
        f"**Peak 3 时段**\n"
        + "\n".join(peak_lines) + "\n\n"
    )

    if tool_sum > 0:
        report += (
            f"**MCP 工具**\n"
            f"  search: {search_count} | web-read: {webread_count} | zread: {zread_count}\n\n"
        )

    report += (
        f"**当前配额 (Plan: {level})**\n"
        + "\n".join(quota_lines)
    )

    return report


def main():
    parser = argparse.ArgumentParser(description="GLM Daily Usage Summary")
    parser.add_argument("--dry-run", action="store_true", help="Print report without sending DM")
    parser.add_argument("--send-only", action="store_true", help="Send last cached report")
    args = parser.parse_args()

    setup_logging()

    log.info("=" * 50)
    log.info("[%s] Daily Summary started", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("=" * 50)

    if args.send_only:
        try:
            with open(CACHE_PATH, "r") as f:
                report = json.load(f)["report"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            log.error("[ERROR] No cached report found. Run without --send-only first.")
            sys.exit(1)
    else:
        glm_config = load_key_value_file(GLM_CONFIG_PATH)
        glm_config["auth_token"] = os.environ.get("ANTHROPIC_AUTH_TOKEN", glm_config.get("ANTHROPIC_AUTH_TOKEN", ""))
        glm_config["base_url"] = os.environ.get("ANTHROPIC_BASE_URL", glm_config.get("ANTHROPIC_BASE_URL", ""))

        if not glm_config["auth_token"] or not glm_config["base_url"]:
            log.error("[ERROR] GLM config incomplete")
            sys.exit(1)

        parsed = urllib.parse.urlparse(glm_config["base_url"])
        glm_config["api_domain"] = f"{parsed.scheme}://{parsed.netloc}"

        log.info("Building daily usage report...")
        report = build_report(glm_config)

        # Cache it
        with open(CACHE_PATH, "w") as f:
            json.dump({"report": report, "generated_at": datetime.now().isoformat()}, f, indent=2)

    log.info(report)

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

    if send_discord_dm(dc_token, dc_user, report):
        log.info("✅ Daily summary sent via Discord DM!")
    else:
        log.error("❌ Failed to send DM")
        sys.exit(1)


if __name__ == "__main__":
    main()
