#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SETTINGS_PATH = CLAUDE_DIR / "settings.json"
BACKUP_DIR = CLAUDE_DIR / "backups"
SKILL_DIR = Path(__file__).resolve().parents[1]
SEND_SCRIPT = (SKILL_DIR / "scripts" / "send_notification.py").resolve()
TOAST_SCRIPT = (Path.home() / ".claude" / "hooks" / "send-toast.ps1").resolve()
MARKER = "managed-by claude-notify-hook-manager"
LEGACY_MANAGER_MARKER = "--managed-by claude-notify-manager"
DEFAULT_MANAGER_PATH = Path("/Applications/Claude Notify Manager.app/Contents/MacOS/claude-notify-manager")
MANAGER_PATTERN = re.compile(r'"([^"]*claude-notify-manager[^"]*)"|([^\s]*claude-notify-manager[^\s]*)')


@dataclass(frozen=True)
class HookSpec:
    key: str
    event_name: str
    matcher: str
    event_type: str
    title: str
    message: str


HOOK_SPECS: tuple[HookSpec, ...] = (
    HookSpec(
        key="permission_request",
        event_name="PermissionRequest",
        matcher="*",
        event_type="permission_required",
        title="Claude Code - 需要确认",
        message="Claude 即将请求工具权限或应用编辑",
    ),
    HookSpec(
        key="permission_prompt",
        event_name="Notification",
        matcher="permission_prompt",
        event_type="permission_required",
        title="Claude Code - 需要权限确认",
        message="Claude 请求工具使用权限",
    ),
    HookSpec(
        key="elicitation_dialog",
        event_name="Notification",
        matcher="elicitation_dialog",
        event_type="input_needed",
        title="Claude Code - 需要输入",
        message="Claude 需要你填写输入或确认信息",
    ),
    HookSpec(
        key="idle_prompt",
        event_name="Notification",
        matcher="idle_prompt",
        event_type="input_needed",
        title="Claude Code - 请注意",
        message="Claude 正在等待你的输入",
    ),
    HookSpec(
        key="task_done",
        event_name="Stop",
        matcher="*",
        event_type="task_done",
        title="Claude Code - 本轮结束",
        message="Claude 当前这一轮已结束",
    ),
    HookSpec(
        key="task_failed",
        event_name="StopFailure",
        matcher="*",
        event_type="task_failed",
        title="Claude Code - 异常结束",
        message="Claude 当前这一轮异常结束",
    ),
)


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


def status_label(spec: HookSpec) -> str:
    return f"{spec.event_name}:{spec.matcher}"


def event_items(settings: dict, event_name: str) -> list[dict]:
    hooks = settings.get("hooks", {})
    items = hooks.get(event_name, [])
    return items if isinstance(items, list) else []


def command_hooks(item: dict) -> list[dict]:
    hooks = item.get("hooks", [])
    if not isinstance(hooks, list):
        return []
    return [
        hook
        for hook in hooks
        if hook.get("type") == "command" and isinstance(hook.get("command"), str)
    ]


def all_commands(settings: dict) -> list[str]:
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        return []
    return [
        hook["command"]
        for items in hooks.values()
        if isinstance(items, list)
        for item in items
        if isinstance(item, dict)
        for hook in command_hooks(item)
    ]


def find_manager_binary(settings: dict) -> str | None:
    for command in all_commands(settings):
        match = MANAGER_PATTERN.search(command)
        if match:
            return match.group(1) or match.group(2)
    if DEFAULT_MANAGER_PATH.exists():
        return str(DEFAULT_MANAGER_PATH)
    return shutil.which("claude-notify-manager")


def engine_name(settings: dict) -> str:
    if platform.system().lower() == "windows" and TOAST_SCRIPT.exists():
        return "windows-toast"
    if find_manager_binary(settings):
        return "claude-notify-manager"
    return "python-fallback"


def build_manager_command(binary: str, event_type: str) -> str:
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


def build_windows_toast_command(spec: HookSpec) -> str:
    return (
        f'powershell -ExecutionPolicy Bypass -NoProfile -File "{TOAST_SCRIPT}" '
        f'-Title "{spec.title}" -Message "{spec.message}" -Persistent'
    )


def build_python_fallback_command(event_type: str) -> str:
    return f'python3 "{SEND_SCRIPT}" {event_type} || python "{SEND_SCRIPT}" {event_type}'


def build_command(settings: dict, spec: HookSpec) -> str:
    current_engine = engine_name(settings)
    if current_engine == "windows-toast":
        return build_windows_toast_command(spec)
    manager_binary = find_manager_binary(settings)
    if current_engine == "claude-notify-manager" and manager_binary:
        return build_manager_command(manager_binary, spec.event_type)
    return build_python_fallback_command(spec.event_type)


def build_hook_item(settings: dict, spec: HookSpec) -> dict:
    return {
        "matcher": spec.matcher,
        "hooks": [
            {
                "type": "command",
                "command": build_command(settings, spec),
                "timeout": 10,
                "async": True,
            }
        ],
    }


def event_is_covered(settings: dict, spec: HookSpec) -> bool:
    return any(
        item.get("matcher") == spec.matcher and bool(command_hooks(item))
        for item in event_items(settings, spec.event_name)
        if isinstance(item, dict)
    )


def is_managed_command(command: str) -> bool:
    toast_titles = tuple(spec.title for spec in HOOK_SPECS)
    return (
        MARKER in command
        or LEGACY_MANAGER_MARKER in command
        or str(SEND_SCRIPT) in command
        or ("send-toast.ps1" in command and any(title in command for title in toast_titles))
    )


def remove_managed_hooks(settings: dict) -> tuple[dict, list[str]]:
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        return dict(settings), []

    removed: list[str] = []
    next_hooks: dict[str, list[dict]] = {}

    for event_name, items in hooks.items():
        if not isinstance(items, list):
            continue
        kept_items: list[dict] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            remaining_hooks = []
            for hook in item.get("hooks", []):
                command = hook.get("command") if isinstance(hook, dict) else None
                if isinstance(command, str) and hook.get("type") == "command" and is_managed_command(command):
                    removed.append(f"{event_name}:{item.get('matcher', '*')}")
                    continue
                remaining_hooks.append(hook)
            if remaining_hooks:
                kept_item = dict(item)
                kept_item["hooks"] = remaining_hooks
                kept_items.append(kept_item)
        if kept_items:
            next_hooks[event_name] = kept_items

    next_settings = dict(settings)
    if next_hooks:
        next_settings["hooks"] = next_hooks
    else:
        next_settings.pop("hooks", None)
    return next_settings, removed


def install_or_repair(settings: dict) -> tuple[dict, list[str], list[str]]:
    cleaned_settings, removed = remove_managed_hooks(settings)
    hooks = {
        event_name: list(items)
        for event_name, items in cleaned_settings.get("hooks", {}).items()
        if isinstance(items, list)
    }
    changed = list(dict.fromkeys(removed))
    kept: list[str] = []

    next_settings = dict(cleaned_settings)

    for spec in HOOK_SPECS:
        if event_is_covered(next_settings, spec):
            kept.append(status_label(spec))
            continue
        hooks.setdefault(spec.event_name, []).append(build_hook_item(next_settings, spec))
        next_settings = {**next_settings, "hooks": hooks}
        changed.append(status_label(spec))

    next_settings["hooks"] = hooks
    return next_settings, changed, kept


def print_status(settings: dict) -> int:
    print(f"settings: {SETTINGS_PATH}")
    print(f"engine: {engine_name(settings)}")
    for spec in HOOK_SPECS:
        state = "covered" if event_is_covered(settings, spec) else "missing"
        print(f"{status_label(spec)}: {state}")
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
        next_settings, changed, kept = install_or_repair(settings)
        save_settings(next_settings)
        print(f"backup: {backup_path or '<new file>'}")
        print(f"changed: {', '.join(changed) if changed else '<none>'}")
        print(f"kept: {', '.join(kept) if kept else '<none>'}")
        return 0

    next_settings, removed = remove_managed_hooks(settings)
    save_settings(next_settings)
    print(f"backup: {backup_path or '<new file>'}")
    print(f"removed: {len(removed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
