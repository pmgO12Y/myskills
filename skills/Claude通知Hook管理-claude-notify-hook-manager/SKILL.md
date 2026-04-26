---
name: Claude 通知 Hook 管理
description: 审计、安装、修复或移除 Claude Code 的通知 hooks。默认修改 ~/.claude/settings.json。Windows 和 macOS 都遵循同一套事件判断顺序：先看 PermissionRequest，再看 Notification 下的 permission_prompt、elicitation_dialog、idle_prompt，最后处理 Stop / StopFailure。
---

# Claude 通知 Hook 管理

## 目标

让 Claude Code 在以下场景通知用户：

- 工具权限审批
- 应用编辑确认
- 需要立即输入或确认
- 长时间等待输入
- 当前轮次结束
- 当前轮次异常结束

## 默认作用域

1. 默认修改 `~/.claude/settings.json`。
2. 只有用户明确要求项目级时，才改 `.claude/settings.json` 或 `.claude/settings.local.json`。
3. 不要把全局通知误写到项目级 `settings.local.json`。

## 事件判断顺序

Windows 和 macOS 都遵循同一套顺序：

1. `PermissionRequest:*`
   - 覆盖“是否允许此 bash 命令”这一类工具权限审批。
   - 覆盖“将此编辑应用于 ...”这一类应用编辑确认。
2. `Notification:permission_prompt`
   - 只覆盖真正发出的权限通知事件。
   - 不要把“看到了审批弹窗”直接等同于这里一定会触发。
3. `Notification:elicitation_dialog`
   - 覆盖需要你立即填写输入或确认信息的对话。
4. `Notification:idle_prompt`
   - 覆盖 Claude 等待输入 **60 秒以上** 的场景。
5. `Stop:*`
   - 覆盖当前轮次结束。
6. `StopFailure:*`
   - 覆盖当前轮次异常结束。

## 平台策略

- **Windows**：优先使用 `~/.claude/hooks/send-toast.ps1` + **BurntToast（Windows 原生通知模块）**。
- **macOS**：优先复用 `claude-notify-manager`；没有时回退到 `scripts/send_notification.py` 的原生通知路径。
- **Linux / 其他**：使用 `scripts/send_notification.py`，再由脚本决定是否走系统通知或 bell。

## 经验修正

1. 不要写 `preferredNotifChannel`，当前 Claude Code settings schema 不支持这个字段。
2. 不要只配置 `Notification:permission_prompt`，否则会漏掉审批类弹窗。
3. 审批类弹窗优先依赖 `PermissionRequest:*`。
4. `permission_prompt` 是通知事件，不是所有审批 UI 都会发出它。
5. `idle_prompt` 只有在等待输入超过 **60 秒** 时才会触发。
6. Windows 和 macOS 都按同一套事件判断顺序处理，不再把平台差异误写成事件差异。

## 动作

支持四种动作：

- `status`：检查当前通知覆盖情况
- `install`：安装缺少的通知 hooks
- `repair`：移除本 skill 管理的旧通知命令，再补齐正确配置
- `remove`：仅移除本 skill 管理的 hooks

如果用户没有明确动作，先执行 `status`。

## 执行流程

### 1. 检查当前状态

运行：

```bash
python3 scripts/manage_notify_hooks.py status
```

重点看这些状态：

- `PermissionRequest:*`
- `Notification:permission_prompt`
- `Notification:elicitation_dialog`
- `Notification:idle_prompt`
- `Stop:*`
- `StopFailure:*`

### 2. 安装或修复

运行：

```bash
python3 scripts/manage_notify_hooks.py install
```

或：

```bash
python3 scripts/manage_notify_hooks.py repair
```

安装前必须先读取 `~/.claude/settings.json`。

### 3. 校验结果

安装或修复后必须验证 JSON 合法：

```bash
python3 -m json.tool ~/.claude/settings.json >/dev/null
```

然后再次检查状态：

```bash
python3 scripts/manage_notify_hooks.py status
```

平台验证：

- Windows：

```bash
powershell -ExecutionPolicy Bypass -NoProfile -File "$HOME/.claude/hooks/send-toast.ps1" -Title "Claude Code 测试" -Message "直接通知测试" -Persistent
```

- macOS：

```bash
python3 scripts/send_notification.py task_done
```

### 4. 卸载

仅在用户明确要求移除时运行：

```bash
python3 scripts/manage_notify_hooks.py remove
```

## 约束

- 不要覆盖用户已有的无关 hooks。
- 不要删除不是本 skill 安装的通知命令。
- `remove` 只处理以下来源的条目：
  - 带有 `managed-by claude-notify-hook-manager`
  - 带有 `--managed-by claude-notify-manager` 的旧命令
  - 调用 `send_notification.py`
  - 调用 `send-toast.ps1` 且标题属于本 skill 生成的通知

## 已打包资源

### scripts/

- `scripts/manage_notify_hooks.py`：审计、安装、修复、移除
- `scripts/send_notification.py`：跨平台通知与 bell 回退

## 结果汇报

汇报时只说这几项：

- 当前覆盖了哪些事件
- 新增了哪些事件
- 当前使用的是哪种通知引擎
- 备份文件路径
- Windows / macOS 是否需要重启 Claude Code 才能让新 hook 生效
