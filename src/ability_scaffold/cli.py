#!/usr/bin/env python3
# Copyright 2026 InsightOS
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ability-scaffold CLI — 统一入口

子命令:
  scaffold  从 OpenAPI/CR YAML 生成能力工程代码
  pack      将能力工程目录打包为 zip 能力包
"""
import sys


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("usage: ability-scaffold <command> [args...]")
        print()
        print("commands:")
        print("  scaffold   从 OpenAPI/CR YAML 生成能力工程代码")
        print("  pack       将能力工程目录打包为 zip 能力包")
        print("  version    显示版本")
        print()
        print("示例:")
        print("  ability-scaffold scaffold --openapi MyAbility.openapi.yaml -o ./my-ability")
        print("  ability-scaffold pack ./my-ability -o my-ability-1.0.0.zip")
        sys.exit(0)

    cmd = sys.argv[1]
    # 把子命令从 argv 里剥掉, 让下游 argparse 能正常解析
    sys.argv = [f"ability-scaffold {cmd}"] + sys.argv[2:]

    if cmd == "scaffold":
        from ability_scaffold.scaffold import main as scaffold_main
        sys.exit(scaffold_main() or 0)
    elif cmd == "pack":
        from ability_scaffold.pack import main as pack_main
        sys.exit(pack_main() or 0)
    elif cmd == "version":
        from ability_scaffold import __version__
        print(f"ability-scaffold {__version__}")
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print("run 'ability-scaffold --help' for usage", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
