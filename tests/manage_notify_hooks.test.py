from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "Claude通知Hook管理-claude-notify-hook-manager"
    / "scripts"
    / "manage_notify_hooks.py"
)
SPEC = importlib.util.spec_from_file_location("manage_notify_hooks_skill", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

FIXTURES = {
    "legacy_manager_command": '"/Applications/Claude Notify Manager.app/Contents/MacOS/claude-notify-manager" send --type permission_required --managed-by claude-notify-manager --source global-hook',
    "custom_command": {"type": "command", "command": "echo custom"},
}


class ManageNotifyHooksTests(unittest.TestCase):
    def test_event_is_covered_returns_false_for_malformed_or_mismatched_items(self) -> None:
        settings = {
            "hooks": {
                "Notification": [
                    {
                        "matcher": "*",
                        "hooks": [FIXTURES["custom_command"]],
                    }
                ],
                "PermissionRequest": {"matcher": "*"},
            }
        }
        spec = next(item for item in MODULE.HOOK_SPECS if item.key == "permission_prompt")

        self.assertFalse(MODULE.event_is_covered(settings, spec))

    def test_remove_managed_hooks_preserves_custom_command(self) -> None:
        settings = {
            "hooks": {
                "PermissionRequest": [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "powershell -ExecutionPolicy Bypass -NoProfile -File \"C:/Users/test/.claude/hooks/send-toast.ps1\" -Title \"Claude Code - 需要确认\" -Message \"Claude 即将请求工具权限或应用编辑\" -Persistent",
                            },
                            FIXTURES["custom_command"],
                        ],
                    }
                ],
                "Stop": [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f'python3 "{MODULE.SEND_SCRIPT}" task_done || python "{MODULE.SEND_SCRIPT}" task_done',
                            }
                        ],
                    }
                ],
            }
        }

        cleaned, removed = MODULE.remove_managed_hooks(settings)

        self.assertEqual(removed, ["PermissionRequest:*", "Stop:*"])
        self.assertEqual(
            cleaned["hooks"]["PermissionRequest"][0]["hooks"],
            [FIXTURES["custom_command"]],
        )
        self.assertNotIn("Stop", cleaned["hooks"])

    def test_install_or_repair_adds_correct_global_hooks_on_windows(self) -> None:
        legacy_settings = {
            "hooks": {
                "Notification": [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "command",
                                "command": FIXTURES["legacy_manager_command"],
                            }
                        ],
                    }
                ]
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            toast_script = Path(temp_dir) / "send-toast.ps1"
            toast_script.write_text("Write-Host test\n", encoding="utf-8")
            with patch.object(MODULE, "TOAST_SCRIPT", toast_script), patch.object(
                MODULE.platform, "system", return_value="Windows"
            ):
                next_settings, changed, kept = MODULE.install_or_repair(legacy_settings)

        self.assertEqual(kept, [])
        self.assertIn("PermissionRequest:*", changed)
        self.assertIn("Notification:permission_prompt", changed)
        self.assertIn("Notification:elicitation_dialog", changed)
        self.assertIn("Notification:idle_prompt", changed)
        self.assertIn("Stop:*", changed)
        self.assertIn("StopFailure:*", changed)

        self.assertEqual(next_settings["hooks"]["PermissionRequest"][0]["matcher"], "*")
        notification_matchers = [item["matcher"] for item in next_settings["hooks"]["Notification"]]
        self.assertEqual(notification_matchers, ["permission_prompt", "elicitation_dialog", "idle_prompt"])

        commands = [
            hook["command"]
            for event_name in ("PermissionRequest", "Notification", "Stop", "StopFailure")
            for item in next_settings["hooks"][event_name]
            for hook in item["hooks"]
        ]
        self.assertTrue(all("send-toast.ps1" in command for command in commands))

    def test_install_or_repair_adds_correct_global_hooks_on_macos(self) -> None:
        manager_path = "/Applications/Claude Notify Manager.app/Contents/MacOS/claude-notify-manager"
        with patch.object(MODULE.platform, "system", return_value="Darwin"), patch.object(
            MODULE, "find_manager_binary", return_value=manager_path
        ):
            next_settings, changed, kept = MODULE.install_or_repair({})

        self.assertEqual(kept, [])
        self.assertIn("PermissionRequest:*", changed)
        self.assertIn("Notification:permission_prompt", changed)
        self.assertIn("Notification:elicitation_dialog", changed)
        self.assertIn("Notification:idle_prompt", changed)

        permission_request_command = next_settings["hooks"]["PermissionRequest"][0]["hooks"][0]["command"]
        self.assertIn("claude-notify-manager", permission_request_command)
        self.assertIn("permission_required", permission_request_command)

        notification_commands = [
            hook["command"]
            for item in next_settings["hooks"]["Notification"]
            for hook in item["hooks"]
        ]
        self.assertTrue(any("input_needed" in command for command in notification_commands))


if __name__ == "__main__":
    unittest.main()
