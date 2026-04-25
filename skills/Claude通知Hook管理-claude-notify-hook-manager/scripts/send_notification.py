#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

APP_NAME = "Claude Code"
LOG_PATH = Path.home() / ".claude" / "notify-hook-manager.log"
MANAGER_CANDIDATES = [
    "/Applications/Claude Notify Manager.app/Contents/MacOS/claude-notify-manager",
]

MESSAGES = {
    "permission_required": "Claude Code 需要你确认权限请求",
    "input_needed": "Claude Code 正在等待你的输入",
    "task_done": "Claude Code 当前这一轮已结束",
    "task_failed": "Claude Code 当前这一轮异常结束",
    "generic": "Claude Code 有新的状态更新",
}


def read_payload() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": raw}


def append_log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")


def manager_binary() -> str | None:
    for candidate in MANAGER_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    found = shutil.which("claude-notify-manager")
    return found


def send_with_manager(event_type: str) -> bool:
    binary = manager_binary()
    if not binary:
        return False

    command = [
        binary,
        "send",
        "--type",
        event_type,
        "--managed-by",
        "claude-notify-hook-manager",
        "--source",
        "global-hook",
        "--pid",
        str(os.getppid()),
        "--project-path",
        os.getcwd(),
        "--session-id",
        os.getenv("CLAUDE_SESSION_ID", ""),
        "--claude-version",
        os.getenv("CLAUDE_VERSION", ""),
        "--claude-agent",
        os.getenv("CLAUDE_AGENT", ""),
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    append_log(f"manager type={event_type} code={result.returncode}")
    return result.returncode == 0


def escape_powershell(value: str) -> str:
    return value.replace("`", "``").replace('"', '`"')


def send_native(title: str, body: str) -> bool:
    system = platform.system().lower()

    if system == "darwin" and shutil.which("osascript"):
        escaped_body = body.replace("\\", "\\\\").replace('"', '\\"')
        escaped_title = title.replace("\\", "\\\\").replace('"', '\\"')
        script = f'display notification "{escaped_body}" with title "{escaped_title}"'
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        append_log(f"native=mac code={result.returncode}")
        return result.returncode == 0

    if system == "linux" and shutil.which("notify-send"):
        result = subprocess.run(["notify-send", title, body], capture_output=True, text=True)
        append_log(f"native=linux code={result.returncode}")
        return result.returncode == 0

    if system == "windows":
        toast_xml = (
            "<toast><visual><binding template=\"ToastGeneric\">"
            f"<text>{html.escape(title)}</text>"
            f"<text>{html.escape(body)}</text>"
            "</binding></visual></toast>"
        )
        ps = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;"
            "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null;"
            f"$xml = New-Object Windows.Data.Xml.Dom.XmlDocument; $xml.LoadXml(\"{escape_powershell(toast_xml)}\");"
            "$toast = [Windows.UI.Notifications.ToastNotification]::new($xml);"
            "$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(\"Claude Code\");"
            "$notifier.Show($toast)"
        )
        result = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
        append_log(f"native=windows code={result.returncode}")
        return result.returncode == 0

    append_log(f"native=unsupported system={system}")
    return False


def ring_bell() -> None:
    try:
        sys.stderr.write("\a")
        sys.stderr.flush()
    except Exception:
        pass


def build_body(event_type: str, payload: dict) -> str:
    base = MESSAGES.get(event_type, MESSAGES["generic"])
    tool_name = payload.get("tool_name")
    if tool_name and event_type == "permission_required":
        return f"{base}：{tool_name}"
    return base


def main() -> int:
    event_type = sys.argv[1] if len(sys.argv) > 1 else "generic"
    payload = read_payload()
    title = APP_NAME
    body = build_body(event_type, payload)

    if send_with_manager(event_type):
        return 0

    if send_native(title, body):
        return 0

    ring_bell()
    append_log(f"fallback=bell type={event_type} body={body}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
