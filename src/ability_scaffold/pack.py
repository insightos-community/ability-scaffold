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
能力包打包工具

将能力工程目录打包为 zip 格式的能力包，可通过框架 API 或 WebUI 一键导入。

包结构:
  package.yaml              # 包清单 (name, version, arch)
  ability.manifest.yaml     # 能力清单
  bin/ability               # 启动脚本
  main.py, task.py, ...     # 能力代码
  service/                  # SDK 模板
  requirements.txt          # Python 依赖 (可选)

用法:
  python pack.py <project-dir> [-o output.zip]

示例:
  python pack.py examples/endpoint-control-demo-impl -o endpoint-control-1.0.0.zip
"""

import argparse
import os
import shutil
import platform
import sys
import zipfile
from pathlib import Path

import yaml

EXCLUDE_PATTERNS = {
    ".venv",
    "__pycache__",
    ".git",
    ".pyc",
    "ability.cr.yaml",  # CR 不属于包，应放在 crs/ 目录
}


def should_exclude(path: Path, base: Path) -> bool:
    rel = path.relative_to(base)
    for part in rel.parts:
        if part in EXCLUDE_PATTERNS or part.endswith(".pyc"):
            return True
    return False


def validate_project(project_dir: Path) -> dict:
    """验证工程目录包含必要文件，返回包信息"""
    package_yaml = project_dir / "package.yaml"
    manifest_yaml = project_dir / "ability.manifest.yaml"
    bin_ability = project_dir / "bin" / "ability"
    main_py = project_dir / "main.py"

    errors = []
    if not package_yaml.exists():
        errors.append("缺少 package.yaml")
    if not manifest_yaml.exists():
        errors.append("缺少 ability.manifest.yaml")
    if not main_py.exists():
        errors.append("缺少 main.py")

    if errors:
        return {"valid": False, "errors": errors}

    with open(package_yaml, "r", encoding="utf-8") as f:
        pkg = yaml.safe_load(f)

    name = pkg.get("name", "unknown")
    version = pkg.get("version", "0.0.0")
    arch = pkg.get("arch", platform.machine())

    if os.name == "nt":
        native_entry = project_dir / "bin" / "ability.exe"
        if not native_entry.exists():
            source = Path(os.environ.get("SEMANTIC_WINDOWS_ABILITY_LAUNCHER", ""))
            if not source.is_file():
                return {"valid": False, "errors": ["Set SEMANTIC_WINDOWS_ABILITY_LAUNCHER to the verified native ability.exe"]}
            native_entry.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, native_entry)
    else:
        # 如果没有 bin/ability，自动生成
        if not bin_ability.exists():
            os.makedirs(project_dir / "bin", exist_ok=True)
            with open(bin_ability, "w") as f:
                f.write('#!/bin/bash\n')
                f.write('SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"\n')
                f.write('exec python3 "$SCRIPT_DIR/main.py" "$@"\n')
            os.chmod(bin_ability, 0o755)
            print(f"  自动生成 bin/ability (使用系统 python3)")

    return {
        "valid": True,
        "name": name,
        "version": version,
        "arch": arch,
    }


def create_requirements(project_dir: Path):
    """如果没有 requirements.txt，自动生成基础版本"""
    req_file = project_dir / "requirements.txt"
    if not req_file.exists():
        with open(req_file, "w") as f:
            f.write("flask\nrequests\nability-py\n")
        print(f"  自动生成 requirements.txt")


def pack(project_dir: Path, output_path: Path) -> Path:
    """打包工程目录为 zip"""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_dir):
            root_path = Path(root)
            # 排除不需要的目录
            dirs[:] = [
                d for d in dirs
                if not should_exclude(root_path / d, project_dir)
            ]
            for f in files:
                file_path = root_path / f
                if should_exclude(file_path, project_dir):
                    continue
                # ZIP names always use POSIX separators, including on Windows.
                # getinfo() must use the same normalized name as write().
                arcname = file_path.relative_to(project_dir).as_posix()
                zf.write(file_path, arcname)
                # 保持可执行权限信息
                if os.access(file_path, os.X_OK):
                    info = zf.getinfo(arcname)
                    info.external_attr = 0o755 << 16

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="能力包打包工具 - 将能力工程打包为可导入的 zip 包"
    )
    parser.add_argument(
        "project_dir",
        type=Path,
        help="能力工程目录",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="输出 zip 文件路径（默认: <name>-<version>-<arch>.zip）",
    )
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    if not project_dir.is_dir():
        print(f"错误: {project_dir} 不是目录")
        return 1

    print(f"打包工程: {project_dir}")

    # 验证
    info = validate_project(project_dir)
    if not info["valid"]:
        for e in info["errors"]:
            print(f"  错误: {e}")
        return 1

    print(f"  包名: {info['name']}")
    print(f"  版本: {info['version']}")
    print(f"  架构: {info['arch']}")

    # 自动生成 requirements.txt
    create_requirements(project_dir)

    # 输出路径
    if args.output:
        output_path = args.output.resolve()
    else:
        output_path = Path.cwd() / f"{info['name']}-{info['version']}-{info['arch']}.zip"

    pack(project_dir, output_path)

    size_kb = output_path.stat().st_size / 1024
    print(f"\n包已生成: {output_path} ({size_kb:.1f} KB)")
    print(f"\n导入方式:")
    print(f"  # 通过 API")
    print(f'  curl -X POST http://localhost:8080/api/package -F "file=@{output_path.name}"')
    print(f"  # 或通过 WebUI 的包管理页面上传")

    return 0


if __name__ == "__main__":
    exit(main())
