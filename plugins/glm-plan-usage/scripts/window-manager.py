#!/usr/bin/env python3
"""
GLM Coding Plan Window Manager

Manages the 5-hour token window refresh cycle for Zhipu GLM Coding Plan.
Runs as a long-lived background process, self-scheduling the next refresh.

Time slots (active hours):
  06:00 - 11:00  Window 1 (covers morning peak)
  11:00 - 16:00  Window 2 (covers midday peak)
  16:00 - 21:00  Window 3 (covers afternoon peak)
  21:00 - 02:00  Window 4 (late night tail)
  02:00 - 06:00  SILENT — no refresh, leave as buffer

Usage:
    python3 window-manager.py [--once] [--config CONFIG_PATH]

Options:
    --once       Run once and exit (useful for testing or manual trigger)
    --config     Path to config file (default: ~/.glm-config)
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
import urllib.error
from datetime import datetime, timedelta, timezone

# --- Timezone ---
# All API responses use Beijing time; force Asia/Shanghai throughout.
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()
TZ_SHANGHAI = timezone(timedelta(hours=8))

# --- Config ---

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.glm-config")
DISCORD_CONFIG_PATH = os.path.expanduser("~/.discord-config")
STATE_FILE_PATH = os.path.expanduser("~/.glm-window-state.json")
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "window-manager.log")

log = logging.getLogger("window-manager")

# Time slots: (refresh_hour, label)
SLOTS = [
    (6,  "Morning  [06:00-11:00]"),
    (11, "Midday   [11:00-16:00]"),
    (16, "Afternoon[16:00-21:00]"),
    (21, "Night    [21:00-02:00]"),
]
# Silent period: 02:00 - 06:00, no refresh


def setup_logging():
    """Configure logging to both file and stdout."""
    os.makedirs(LOG_DIR, exist_ok=True)
    log.setLevel(logging.DEBUG)

    # File handler — append, keep detailed logs
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    # Stdout handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S"))

    log.addHandler(fh)
    log.addHandler(sh)


def load_config(config_path: str) -> dict:
    """Load API credentials from config file."""
    config = {}
    try:
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                eq = line.find("=")
                if eq == -1:
                    continue
                key = line[:eq].strip()
                value = line[eq + 1 :].strip()
                config[key] = value
    except FileNotFoundError:
        log.error("[ERROR] Config file not found: %s", config_path)
        sys.exit(1)

    # Env vars override config file
    config["auth_token"] = os.environ.get("ANTHROPIC_AUTH_TOKEN", config.get("ANTHROPIC_AUTH_TOKEN", ""))
    config["base_url"] = os.environ.get("ANTHROPIC_BASE_URL", config.get("ANTHROPIC_BASE_URL", ""))

    if not config["auth_token"]:
        log.error("[ERROR] ANTHROPIC_AUTH_TOKEN not set")
        sys.exit(1)
    if not config["base_url"]:
        log.error("[ERROR] ANTHROPIC_BASE_URL not set")
        sys.exit(1)

    # Determine platform
    if "api.z.ai" in config["base_url"]:
        config["platform"] = "ZAI"
    elif "open.bigmodel.cn" in config["base_url"] or "dev.bigmodel.cn" in config["base_url"]:
        config["platform"] = "ZHIPU"
    else:
        log.error("[ERROR] Unrecognized base URL: %s", config['base_url'])
        sys.exit(1)

    # Build API domain
    parsed = urllib.parse.urlparse(config["base_url"])
    config["api_domain"] = f"{parsed.scheme}://{parsed.netloc}"

    return config


def load_state() -> dict:
    """Load window state from file."""
    try:
        with open(STATE_FILE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: dict):
    """Save window state to file."""
    with open(STATE_FILE_PATH, "w") as f:
        json.dump(state, f, indent=2, default=str)
        f.write("\n")


def api_request(url: str, auth_token: str) -> dict:
    """Make an authenticated GET request to the API."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": auth_token,
            "Accept-Language": "en-US,en",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        return json.loads(resp.read().decode())


def load_discord_config() -> dict:
    """Load Discord bot config for DM notifications."""
    config = {}
    try:
        with open(DISCORD_CONFIG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                eq = line.find("=")
                if eq == -1:
                    continue
                key = line[:eq].strip()
                value = line[eq + 1:].strip()
                config[key] = value
    except FileNotFoundError:
        log.warning("[WARN] Discord config not found: %s, DM notifications disabled", DISCORD_CONFIG_PATH)
        return {}
    return config


def send_discord_dm(bot_token: str, user_id: str, message: str) -> bool:
    """Send a DM via Discord Bot API."""
    ctx = ssl.create_default_context()
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
        "User-Agent": "GLM-WindowManager/1.0",
    }
    try:
        # Create DM channel
        dm_payload = json.dumps({"recipient_id": user_id}).encode()
        dm_req = urllib.request.Request(
            "https://discord.com/api/v10/users/@me/channels",
            data=dm_payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(dm_req, context=ctx, timeout=15) as resp:
            channel_data = json.loads(resp.read().decode())
            channel_id = channel_data["id"]

        # Send message
        msg_payload = json.dumps({"content": message}).encode()
        msg_req = urllib.request.Request(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            data=msg_payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(msg_req, context=ctx, timeout=15) as resp:
            log.info("[DISCORD] DM sent to %s", user_id)
            return True
    except Exception as e:
        log.error("[DISCORD] Failed to send DM: %s", e)
        return False


def query_quota(config: dict) -> dict:
    """Query current quota/limit status."""
    url = f"{config['api_domain']}/api/monitor/usage/quota/limit"
    data = api_request(url, config["auth_token"])
    return data.get("data", data)


def query_model_usage(config: dict, start_time: str, end_time: str) -> dict:
    """Query model usage for a time range."""
    params = f"?startTime={urllib.parse.quote(start_time)}&endTime={urllib.parse.quote(end_time)}"
    url = f"{config['api_domain']}/api/monitor/usage/model-usage{params}"
    data = api_request(url, config["auth_token"])
    return data.get("data", data)


def parse_quota_limits(quota_data: dict) -> dict:
    """Parse quota limits into a readable dict, preserving all API fields."""
    result = {"level": quota_data.get("level", "unknown"), "limits": {}}
    for item in quota_data.get("limits", []):
        limit_type = item.get("type", "")
        if limit_type == "TOKENS_LIMIT":
            # nextResetTime is authoritative — use it instead of manual calculation
            reset_ts = item.get("nextResetTime")
            reset_dt = datetime.fromtimestamp(reset_ts / 1000) if reset_ts else None
            result["limits"]["token_5h"] = {
                "type": item.get("type"),
                "unit": item.get("unit"),
                "number": item.get("number"),
                "percentage": item.get("percentage", 0),
                "next_reset_time": reset_ts,
                "next_reset_dt": format_dt(reset_dt) if reset_dt else None,
            }
        elif limit_type == "TIME_LIMIT":
            reset_ts = item.get("nextResetTime")
            reset_dt = datetime.fromtimestamp(reset_ts / 1000) if reset_ts else None
            result["limits"]["mcp_monthly"] = {
                "type": item.get("type"),
                "unit": item.get("unit"),
                "number": item.get("number"),
                "percentage": item.get("percentage", 0),
                "current_usage": item.get("currentValue", 0),
                "total": item.get("usage", 0),
                "remaining": item.get("remaining"),
                "next_reset_time": reset_ts,
                "next_reset_dt": format_dt(reset_dt) if reset_dt else None,
                "details": item.get("usageDetails", []),
            }
    return result


def send_refresh_request(config: dict) -> bool:
    """Send a minimal chat completion request to trigger a new window."""
    # Use the full base_url path (e.g. /api/coding/paas/v4) to hit the coding plan endpoint
    url = f"{config['base_url']}/chat/completions"
    payload = json.dumps({
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
    }).encode()

    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": config["auth_token"],
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            log.info("[REFRESH] Request sent, response OK")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        log.error("[REFRESH] HTTP %d: %s", e.code, body[:200])
        return False
    except Exception as e:
        log.error("[REFRESH] Error: %s", e)
        return False


def format_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    if seconds < 0:
        return "expired"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def get_current_slot(now_hour: int) -> dict:
    """
    Determine which time slot we're in and the next action.

    Returns:
        dict with:
          slot_index: which slot (0-3), -1 if silent period
          slot_label: human readable label
          refresh_hour: hour when this slot's refresh should happen
          next_slot_hour: hour of the next slot's refresh
          is_silent: True if in silent period (02:00-06:00)
    """
    if now_hour < 2:
        # 00:00-01:59 → still in the night slot, next is 06:00
        return {
            "slot_index": 3,
            "slot_label": "Night    [21:00-02:00]",
            "refresh_hour": 21,
            "next_slot_hour": 6,
            "is_silent": False,
            "next_is_tomorrow": True,
        }
    elif now_hour < 6:
        # 02:00-05:59 → SILENT period
        return {
            "slot_index": -1,
            "slot_label": "SILENT   [02:00-06:00]",
            "refresh_hour": None,
            "next_slot_hour": 6,
            "is_silent": True,
            "next_is_tomorrow": False,
        }
    elif now_hour < 11:
        return {
            "slot_index": 0,
            "slot_label": "Morning  [06:00-11:00]",
            "refresh_hour": 6,
            "next_slot_hour": 11,
            "is_silent": False,
            "next_is_tomorrow": False,
        }
    elif now_hour < 16:
        return {
            "slot_index": 1,
            "slot_label": "Midday   [11:00-16:00]",
            "refresh_hour": 11,
            "next_slot_hour": 16,
            "is_silent": False,
            "next_is_tomorrow": False,
        }
    elif now_hour < 21:
        return {
            "slot_index": 2,
            "slot_label": "Afternoon[16:00-21:00]",
            "refresh_hour": 16,
            "next_slot_hour": 21,
            "is_silent": False,
            "next_is_tomorrow": False,
        }
    else:
        # 21:00-23:59
        return {
            "slot_index": 3,
            "slot_label": "Night    [21:00-02:00]",
            "refresh_hour": 21,
            "next_slot_hour": 6,
            "is_silent": False,
            "next_is_tomorrow": True,
        }


def target_time_for_slot(now: datetime, hour: int) -> datetime:
    """Get the next occurrence of a specific hour."""
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target


def run_once(config: dict) -> dict:
    """
    Run one check cycle. Returns action dict with scheduling info.
    """
    now = datetime.now()
    state = load_state()
    log.info("=" * 60)
    log.info("[%s] Window Manager Check", format_dt(now))
    log.info("=" * 60)

    # 1. Query current quota
    log.info("Querying quota status...")
    try:
        quota_data = query_quota(config)
        quota = parse_quota_limits(quota_data)
    except Exception as e:
        log.error("[ERROR] Failed to query quota: %s", e)
        return {"action": "retry_later", "retry_minutes": 5}

    token_info = quota["limits"].get("token_5h", {})
    token_pct = token_info.get("percentage", -1)
    api_reset_dt = token_info.get("next_reset_dt")  # from API, authoritative
    level = quota.get("level", "unknown")
    log.info("Plan: %s | Token window: %s%%", level, token_pct)
    if api_reset_dt:
        log.info("API nextResetTime: %s", api_reset_dt)

    # 2. Determine current time slot
    slot = get_current_slot(now.hour)
    log.info("Slot: %s", slot['slot_label'])

    # 3. SILENT period (02:00-06:00)
    if slot["is_silent"]:
        next_morning = target_time_for_slot(now, 6)
        wait = (next_morning - now).total_seconds()
        log.info("[SILENT] Buffer period, skipping until 06:00")
        log.info("💤 Sleeping %s...", format_duration(wait))
        return {"action": "sleep", "seconds": wait}

    # 4. Check if someone already opened a new window (usage ≤ 1%)
    # A minimal refresh request itself consumes at least 1%, so this is the
    # practical floor for detecting a freshly opened window.
    # NOTE: 0% does NOT mean "window just created" — it only means "no tokens
    # consumed in this window yet". The window might have been alive for hours.
    # We only claim if API confirms it's truly fresh (no nextResetTime or far future).
    if token_pct == 0 and not api_reset_dt:
        # No nextResetTime + 0% = genuinely fresh window, safe to claim
        log.info("[ACTION] Token 0%% and no nextResetTime — sending request to claim new window")
        success = send_refresh_request(config)
        if success:
            log.info("[OK] Window claimed successfully")
        else:
            log.warning("[WARN] Failed to claim window, will treat as active anyway")
    elif token_pct == 0 and api_reset_dt:
        # 0% but has nextResetTime — window is old but unused, don't waste a claim
        log.info("[INFO] Token 0%% but nextResetTime=%s — window already active, skipping claim", api_reset_dt)
    if token_pct >= 0 and token_pct <= 1:
        log.info("[INFO] Token usage is %s%% — new window already active", token_pct)
        # Still sleep to next slot boundary
        next_target = target_time_for_slot(now, slot["next_slot_hour"])
        wait = (next_target - now).total_seconds()
        new_state = {
            "window_start": format_dt(now),
            "expected_expiry": format_dt(now + timedelta(hours=5)),
            "last_refresh": format_dt(now),
            "refresh_trigger": "detected_external" if token_pct > 0 else "window_manager",
            "current_slot": slot["slot_label"],
            "plan_level": level,
        }
        save_state(new_state)
        log.info("💤 Sleeping to next slot at %s (%s)...", format_dt(next_target), format_duration(wait))

        # Send Discord DM notification
        dc = load_discord_config()
        dc_token = dc.get("DISCORD_BOT_TOKEN")
        dc_user = dc.get("DISCORD_ALLOWED_USERS")
        if dc_token and dc_user:
            emoji = "🔄" if token_pct == 0 else "✅"
            action = "Refreshed" if token_pct == 0 else "Active"
            msg = (
                f"{emoji} **GLM Window {action}**\n"
                f"Slot: {slot['slot_label']}\n"
                f"Token: {token_pct}%\n"
                f"Plan: {level}\n"
                f"⏰ {format_dt(now)}"
            )
            send_discord_dm(dc_token, dc_user, msg)

        return {"action": "sleep", "seconds": wait}

    # 5. Check if old window is still alive
    state_expiry = state.get("expected_expiry")
    state_slot = state.get("current_slot")

    if state_slot == slot["slot_label"]:
        # This slot was already refreshed, sleep to next slot
        next_target = target_time_for_slot(now, slot["next_slot_hour"])
        wait = (next_target - now).total_seconds()
        log.info("Slot already refreshed, window until %s", state_expiry)
        log.info("💤 Sleeping to next slot at %s (%s)...", format_dt(next_target), format_duration(wait))
        return {"action": "sleep", "seconds": wait}

    # 6. New slot, but old window might still be alive — wait for it to expire
    # Prefer API's nextResetTime (authoritative), fall back to state file
    window_expiry_str = api_reset_dt or state_expiry
    if window_expiry_str and token_pct > 0:
        try:
            expiry_dt = datetime.strptime(window_expiry_str, "%Y-%m-%d %H:%M:%S")
            source = "API" if api_reset_dt else "state file"
            remaining = (expiry_dt - now).total_seconds()
            if remaining > 0:
                # Old window still alive, wait for it to expire
                # Add a small grace (30s) to ensure it's truly expired
                wait = remaining + 30
                log.info("[WAIT] Old window alive until %s (%s left, src: %s)", window_expiry_str, format_duration(remaining), source)
                log.info("💤 Sleeping %s until window expires, then will refresh...", format_duration(wait))
                return {"action": "wait_then_refresh", "seconds": wait}
        except ValueError:
            pass

    # 7. Old window expired or no state — refresh now
    log.info("[ACTION] Refreshing for slot: %s", slot['slot_label'])
    success = send_refresh_request(config)

    if success:
        new_expiry = now + timedelta(hours=5)
        new_state = {
            "window_start": format_dt(now),
            "expected_expiry": format_dt(new_expiry),
            "api_next_reset_dt": api_reset_dt,
            "last_refresh": format_dt(now),
            "refresh_trigger": "window_manager",
            "current_slot": slot["slot_label"],
            "plan_level": level,
        }
        save_state(new_state)
        log.info("[OK] New window: %s → %s", format_dt(now), format_dt(new_expiry))

        # Send Discord DM notification
        dc = load_discord_config()
        dc_token = dc.get("DISCORD_BOT_TOKEN")
        dc_user = dc.get("DISCORD_ALLOWED_USERS")
        if dc_token and dc_user:
            msg = (
                f"🔄 **GLM Window Refreshed**\n"
                f"Slot: {slot['slot_label']}\n"
                f"New window: {format_dt(now)} → {format_dt(new_expiry)}\n"
                f"Plan: {level}"
            )
            send_discord_dm(dc_token, dc_user, msg)

        # Sleep to next slot boundary
        next_target = target_time_for_slot(now, slot["next_slot_hour"])
        wait = (next_target - now).total_seconds()
        log.info("💤 Sleeping to next slot at %s (%s)...", format_dt(next_target), format_duration(wait))
        return {"action": "refreshed", "seconds": wait}
    else:
        log.error("[FAIL] Refresh failed, will retry in 3 minutes")
        return {"action": "retry_later", "retry_minutes": 3}


def main():
    parser = argparse.ArgumentParser(description="GLM Coding Plan Window Manager")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to config file")
    args = parser.parse_args()

    setup_logging()

    log.info("GLM Window Manager starting...")
    log.info("  Config: %s", args.config)
    log.info("  State:  %s", STATE_FILE_PATH)
    log.info("  Log:    %s", LOG_FILE)
    log.info("  Slots:")
    for h, label in SLOTS:
        log.info("    %02d:00  %s", h, label)
    log.info("    02:00-06:00  SILENT (buffer)")

    config = load_config(args.config)
    log.info("  Platform: %s", config['platform'])
    log.info("  API: %s", config['base_url'])

    if args.once:
        result = run_once(config)
        log.info("Result: %s", json.dumps(result, indent=2))
        return

    # Main loop
    while True:
        result = run_once(config)

        if result["action"] in ("sleep", "refreshed", "wait_then_refresh"):
            wait = result.get("seconds", 300)
            time.sleep(max(wait, 30))

        elif result["action"] == "retry_later":
            wait = result.get("retry_minutes", 5) * 60
            time.sleep(wait)

if __name__ == "__main__":
    main()
