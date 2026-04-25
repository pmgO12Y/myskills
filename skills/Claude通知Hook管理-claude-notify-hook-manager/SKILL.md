---
name: Claude 通知 Hook 管理
description: 审计、安装、修复或移除 Claude Code 的全局通知 hooks。覆盖需要确认、等待输入、输出完成、异常结束。默认修改 ~/.claude/settings.json；优先复用现有 Claude Notify Manager，没有时回退到系统通知与 terminal bell。触发词包括：配置通知、安装通知hook、修复通知提醒、检查通知配置、移除通知hook、通知没生效。
---

# Claude 通知 Hook 管理

## 目标

让 Claude Code 在以下场景通知用户：

- 需要确认权限
- 等待用户输入
- 当前轮次结束
- 当前轮次异常结束

## 默认行为

1. **先审计，后修改**。
2. 默认作用域是 `~/.claude/settings.json`。
3. **保留已有配置**，只补齐缺少的通知事件。
4. 优先复用现有 `claude-notify-manager`。
5. 没有桌面通知能力时，回退到 `terminal bell` 和日志文件 `~/.claude/notify-hook-manager.log`。

## 动作

支持四种动作：

- `status`：检查当前通知覆盖情况
- `install`：安装缺少的通知 hooks
- `repair`：重新补齐和修复缺失项
- `remove`：仅移除本 skill 管理的 hooks

如果用户没有明确动作，先执行 `status`。

## 执行流程

### 1. 检查当前状态

运行：

```bash
python3 scripts/manage_notify_hooks.py status
```

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

### 4. 卸载

仅在用户明确要求移除时运行：

```bash
python3 scripts/manage_notify_hooks.py remove
```

## 约束

- 不要覆盖用户已有的无关 hooks。
- 不要删除不是本 skill 安装的通知命令。
- `remove` 只处理带有 `managed-by claude-notify-hook-manager` 标记，或调用 `send_notification.py` 的条目。
- 如果用户要求改为项目级配置，再改 `.claude/settings.json` 或 `.claude/settings.local.json`。

## 已打包资源

### scripts/

- `scripts/manage_notify_hooks.py`：审计、安装、修复、移除
- `scripts/send_notification.py`：跨平台通知与 bell 回退

## 结果汇报

汇报时只说这几项：

- 当前覆盖了哪些事件
- 新增了哪些事件
- 是否复用了现有通知引擎
- 备份文件路径
- 远程 SSH 场景是否只能回退到 bell
