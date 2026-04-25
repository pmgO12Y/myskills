#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SETTINGS_PATH = CLAUDE_DIR / "settings.json"
BACKUP_DIR = CLAUDE_DIR / "backups"
SKILL_DIR = Path(__file__).resolve().parents[1]
SEND_SCRIPT = (SKILL_DIR / "scripts" / "send_notification.py").resolve()
MARKER = "managed-by claude-notify-hook-manager"
DEFAULT_MANAGER_PATH = Path("/Applications/Claude Notify Manager.app/Contents/MacOS/claude-notify-manager")
EVENT_TYPES = {
    "PermissionRequest": "permission_required",
    "Elicitation": "input_needed",
    "Stop": "task_done",
    "StopFailure": "task_failed",
}
FALLBACK_EVENTS = {
    "PermissionRequest": [("Notification", "permission_required")],
    "Elicitation": [],
    "Stop": [],
    "StopFailure": [],
}


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return {}
    with SETTINGS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_settings(settings: dict) -> None:
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    with SETTINGS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(settings, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def backup_settings() -> Path | None:
    if not SETTINGS_PATH.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"settings.notify-backup.{timestamp}.json"
    shutil.copy2(SETTINGS_PATH, backup_path)
    return backup_path


def all_commands(settings: dict, event_name: str) -> list[str]:
    hooks = settings.get("hooks", {})
    event_items = hooks.get(event_name, [])
    commands: list[str] = []
    for item in event_items:
        for hook in item.get("hooks", []):
            if hook.get("type") == "command" and isinstance(hook.get("command"), str):
                commands.append(hook["command"])
    return commands


def find_manager_binary(settings: dict) -> str | None:
    pattern = re.compile(r'"([^"]*claude-notify-manager[^"]*)"|([^\s]*claude-notify-manager[^\s]*)')
    for hooks in settings.get("hooks", {}).values():
        for item in hooks:
            for hook in item.get("hooks", []):
                command = hook.get("command")
                if not isinstance(command, str):
                    continue
                match = pattern.search(command)
                if match:
                    return match.group(1) or match.group(2)
    if DEFAULT_MANAGER_PATH.exists():
        return str(DEFAULT_MANAGER_PATH)
    found = shutil.which("claude-notify-manager")
    return found


def build_command(settings: dict, event_type: str) -> str:
    binary = find_manager_binary(settings)
    if binary:
        return (
            f'"{binary}" send --type {event_type} '
            '--managed-by claude-notify-hook-manager '
            '--source global-hook '
            '--pid $PPID '
            '--project-path "$PWD" '
            '--session-id "${CLAUDE_SESSION_ID:-}" '
            '--claude-version "${CLAUDE_VERSION:-}" '
            '--claude-agent "${CLAUDE_AGENT:-}"'
        )

    script_path = str(SEND_SCRIPT)
    return f'python3 "{script_path}" {event_type} || python "{script_path}" {event_type}'


def command_covers(command: str, event_type: str) -> bool:
    return event_type in command or MARKER in command or str(SEND_SCRIPT) in command


def event_is_covered(settings: dict, event_name: str, event_type: str) -> bool:
    if any(command_covers(command, event_type) for command in all_commands(settings, event_name)):
        return True
    for fallback_event, fallback_type in FALLBACK_EVENTS.get(event_name, []):
        if any(command_covers(command, fallback_type) for command in all_commands(settings, fallback_event)):
            return True
    return False


def install_or_repair(settings: dict) -> tuple[dict, list[str], list[str]]:
    changed: list[str] = []
    kept: list[str] = []

    if "preferredNotifChannel" not in settings:
        settings["preferredNotifChannel"] = "auto"
        changed.append("preferredNotifChannel=auto")

    hooks = settings.setdefault("hooks", {})

    for event_name, event_type in EVENT_TYPES.items():
        if event_is_covered(settings, event_name, event_type):
            kept.append(event_name)
            continue

        hooks.setdefault(event_name, []).append(
            {
                "matcher": "*",
                "hooks": [
                    {
                        "type": "command",
                        "command": build_command(settings, event_type),
                        "timeout": 10,
                        "async": True,
                    }
                ],
            }
        )
        changed.append(event_name)

    return settings, changed, kept


def remove_managed_hooks(settings: dict) -> tuple[dict, list[str]]:
    removed: list[str] = []
    hooks = settings.get("hooks", {})
    updated_hooks: dict = {}

    for event_name, items in hooks.items():
        kept_items = []
        for item in items:
            kept_commands = []
            for hook in item.get("hooks", []):
                command = hook.get("command", "")
                if hook.get("type") == "command" and isinstance(command, str) and (MARKER in command or str(SEND_SCRIPT) in command):
                    removed.append(f"{event_name}:{command}")
                    continue
                kept_commands.append(hook)

            if kept_commands:
                next_item = dict(item)
                next_item["hooks"] = kept_commands
                kept_items.append(next_item)

        if kept_items:
            updated_hooks[event_name] = kept_items

    if updated_hooks:
        settings["hooks"] = updated_hooks
    else:
        settings.pop("hooks", None)

    return settings, removed


def print_status(settings: dict) -> int:
    print(f"settings: {SETTINGS_PATH}")
    print(f"preferredNotifChannel: {settings.get('preferredNotifChannel', '<unset>')}")
    print(f"engine: {find_manager_binary(settings) or 'python-fallback'}")
    for event_name, event_type in EVENT_TYPES.items():
        covered = event_is_covered(settings, event_name, event_type)
        state = "covered" if covered else "missing"
        print(f"{event_name}: {state}")
    return 0


def main(argv: list[str]) -> int:
    action = argv[1] if len(argv) > 1 else "status"
    if action not in {"status", "install", "repair", "remove"}:
        print("usage: manage_notify_hooks.py [status|install|repair|remove]", file=sys.stderr)
        return 2

    settings = load_settings()

    if action == "status":
        return print_status(settings)

    backup_path = backup_settings()

    if action in {"install", "repair"}:
        settings, changed, kept = install_or_repair(settings)
        save_settings(settings)
        print(f"backup: {backup_path or '<new file>'}")
        print(f"changed: {', '.join(changed) if changed else '<none>'}")
        print(f"kept: {', '.join(kept) if kept else '<none>'}")
        return 0

    settings, removed = remove_managed_hooks(settings)
    save_settings(settings)
    print(f"backup: {backup_path or '<new file>'}")
    print(f"removed: {len(removed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
