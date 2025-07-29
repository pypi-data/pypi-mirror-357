import argparse
import json
import os
import sys
from tree2proj import ProjBuilder
def main():
    try:
        import pyperclip
    except ImportError:
        print("❗ 需要安装 pyperclip 模块： pip install pyperclip")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Build project structure from JSON or tree text.")
    parser.add_argument("json_file", nargs="?", help="Path to tree.json (or leave blank to use clipboard)")
    parser.add_argument("--output", "-o", help="Output directory", default=None)
    args = parser.parse_args()

    if args.json_file:
        # 从 JSON 文件读取
        if not os.path.isfile(args.json_file):
            print(f"❌ 文件不存在: {args.json_file}")
            sys.exit(1)
        with open(args.json_file, "r", encoding="utf-8") as f:
            tree = json.load(f)
        builder = ProjBuilder(tree)
        builder.create_fs(base_path=args.output)
    else:
        # 从剪贴板读取字符串
        print("📋 正在从剪贴板读取目录树...")
        tree_str = pyperclip.paste()
        if not tree_str.strip():
            print("❌ 剪贴板为空，请先复制目录树结构文本。")
            sys.exit(1)
        ProjBuilder.build_from_tree_str(tree_str, base_path=args.output)
        print("✅ 项目结构已生成！")
