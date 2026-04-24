#!/usr/bin/env python3
"""
对话记录自动保存脚本

用法：
    python save_conversation.py <输出文件路径>
    python save_conversation.py --append <已有文件路径>

从标准输入读取对话内容，保存为 Markdown 文件。
--append 模式：在已有文件末尾追加内容，并自动插入续接分隔标题。
"""

import sys
import os
from datetime import datetime


def main():
    append_mode = False
    file_args = []

    for arg in sys.argv[1:]:
        if arg == '--append':
            append_mode = True
        else:
            file_args.append(arg)

    if not file_args:
        print("用法: python save_conversation.py [--append] <输出文件路径>", file=sys.stderr)
        sys.exit(1)

    output_path = file_args[0]

    # 确保目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 从标准输入读取内容
    content = sys.stdin.read()

    if append_mode:
        # 追加模式：插入续接分隔标题
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        separator = f"\n\n## 续接 — {now}\n\n"
        full_content = separator + content
        mode = 'a'
    else:
        # 新建模式：直接写入
        full_content = content
        mode = 'w'

    # 写入文件
    with open(output_path, mode, encoding='utf-8') as f:
        f.write(full_content)

    # 静默执行，不输出成功信息


if __name__ == '__main__':
    main()
