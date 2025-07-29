from tree2json import Tree2Json

from tree2proj import ProjBuilder

tree_str = """
.
├── data
│   └── sample.txt       ← 示例数据文件
"""

parser = Tree2Json()
parser.from_string(tree_str)

builder = ProjBuilder(parser.to_dict())
builder.create_fs("output_project")
