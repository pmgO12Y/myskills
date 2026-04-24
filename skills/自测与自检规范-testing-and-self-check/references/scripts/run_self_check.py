#!/usr/bin/env python3
"""
自测与自检规范 — 辅助自检脚本

用法：
    python run_self_check.py [代码目录]

功能：
    1. 检查当前项目的测试框架配置
    2. 运行测试并收集结果
    3. 输出自检清单，供 AI 逐项确认

注意：
    本脚本为辅助工具，自检的核心逻辑在 SKILL.md 中定义。
    AI 应优先遵循 SKILL.md 中的规则和检查清单。
"""

import os
import sys
import subprocess
import json
from pathlib import Path


# ====== 自检清单定义 ======

CHECKLIST = {
    "syntax": [
        "代码能否编译/解释通过？",
        "Linter 是否零报错？",
    ],
    "unit_test": [
        "单元测试是否全部通过？",
        "是否覆盖了 Happy Path？",
        "是否覆盖了边界条件（空值、零值、最大值）？",
        "是否覆盖了异常路径（错误输入、非法状态）？",
        "核心逻辑行覆盖率是否 ≥ 90%？",
    ],
    "boundary": [
        "空数组/空字符串/null 输入是否处理正确？",
        "超大值输入（如 10^6 条数据）是否安全？",
        "特殊字符、emoji、Unicode 输入是否正常？",
        "并发/异步场景是否有竞态条件？",
        "循环是否会无限执行？",
        "内存是否可能泄漏？",
    ],
    "security": [
        "是否存在 SQL 注入风险？",
        "是否存在 XSS 风险？",
        "是否存在命令注入风险？",
        "敏感信息（密钥、密码）是否已脱敏？",
        "日志中是否泄漏了敏感数据？",
    ],
    "integration": [
        "完整调用链路是否通畅？",
        "数据库操作是否正常回滚？",
        "文件 IO 是否正确关闭？",
        "网络请求超时是否优雅降级？",
    ],
    "delivery": [
        "是否有未使用的变量/导入/代码？",
        "错误处理是否完善（不吞异常、给用户友好提示）？",
        "交付物是否符合用户的原始需求？",
    ],
}


# ====== 测试框架检测 ======

def detect_test_framework(project_dir):
    """检测项目使用的测试框架"""
    frameworks = []
    path = Path(project_dir)

    # JavaScript/TypeScript
    if (path / "package.json").exists():
        pkg = json.loads((path / "package.json").read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "jest" in deps:
            frameworks.append(("Jest", "npx jest --coverage"))
        if "vitest" in deps:
            frameworks.append(("Vitest", "npx vitest run --coverage"))
        if "mocha" in deps:
            frameworks.append(("Mocha", "npx mocha"))
        if "playwright" in deps:
            frameworks.append(("Playwright", "npx playwright test"))

    # Python
    if list(path.glob("**/pytest.ini")) or list(path.glob("**/pyproject.toml")):
        frameworks.append(("pytest", "pytest --cov=. --cov-report=term-missing"))
    elif list(path.glob("**/test_*.py")) or list(path.glob("**/*_test.py")):
        frameworks.append(("pytest (detected by file pattern)", "pytest --cov=."))

    # Java
    if (path / "pom.xml").exists():
        frameworks.append(("Maven + JUnit", "mvn test"))
    if (path / "build.gradle").exists():
        frameworks.append(("Gradle + JUnit", "gradle test"))

    # Go
    if list(path.glob("**/*_test.go")):
        frameworks.append(("Go testing", "go test -cover ./..."))

    return frameworks


# ====== 运行测试 ======

def run_tests(project_dir, command):
    """运行测试命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "测试执行超时（>120s）"}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


# ====== 主函数 ======

def main():
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    project_dir = os.path.abspath(project_dir)

    print("=" * 60)
    print("🧪 自测与自检规范 — 辅助自检脚本")
    print("=" * 60)
    print(f"\n📁 项目目录: {project_dir}\n")

    # 1. 检测测试框架
    print("🔍 检测测试框架...")
    frameworks = detect_test_framework(project_dir)
    if frameworks:
        for name, cmd in frameworks:
            print(f"   ✅ 发现: {name}")
            print(f"      运行命令: {cmd}")
    else:
        print("   ⚠️ 未检测到已知测试框架")
    print()

    # 2. 尝试运行测试
    if frameworks:
        name, cmd = frameworks[0]
        print(f"🚀 运行测试 ({name})...")
        result = run_tests(project_dir, cmd)
        if result["returncode"] == 0:
            print("   ✅ 测试通过")
        else:
            print("   ❌ 测试失败")
        if result["stderr"]:
            print(f"\n   错误输出:\n{result['stderr'][:500]}")
        print()

    # 3. 输出自检清单
    print("=" * 60)
    print("📋 自检清单（请逐项确认）")
    print("=" * 60)

    for category, items in CHECKLIST.items():
        category_names = {
            "syntax": "📝 语法检查",
            "unit_test": "🧪 单元测试",
            "boundary": "🔍 边界验证",
            "security": "🔒 安全检查",
            "integration": "🔗 集成验证",
            "delivery": "📦 交付检查",
        }
        print(f"\n{category_names.get(category, category)}")
        print("-" * 40)
        for item in items:
            print(f"  ☐ {item}")

    print("\n" + "=" * 60)
    print("💡 提示: 使用本脚本后，请根据 SKILL.md 中的质量门禁标准判定是否通过。")
    print("=" * 60)


if __name__ == "__main__":
    main()
