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
能力工程脚手架工具

从 OpenAPI YAML 或 CR YAML 定义自动生成能力工程代码。
生成的工程基于 ability-py-sdk，开发者只需实现：
  1. ability.py 中的 on_start() — 初始化逻辑
  2. task.py 中各 Task 的 execute() — 业务实现
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

import yaml


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def to_class_name(name: str) -> str:
    """将任意名称转为 PascalCase 类名，保留原有大小写边界"""
    # 如果已经是 PascalCase/camelCase (如 DetectOnce)，按大写字母拆分
    if re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", name):
        # 保留原始 PascalCase
        return name[0].upper() + name[1:]
    # 否则按非字母数字字符拆分
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    return "".join(p.capitalize() for p in parts if p)


TYPE_MAP = {
    "string": "str",
    "str": "str",
    "int": "int",
    "integer": "int",
    "number": "float",
    "float": "float",
    "double": "float",
    "boolean": "bool",
    "bool": "bool",
    "array": "list",
    "object": "dict",
    "uuid": "str",
}


def map_type(t: str) -> str:
    return TYPE_MAP.get(t, t)


def parse_tasks_from_openapi(openapi: dict) -> list:
    """从 OpenAPI YAML 的 x-tasks 提取任务定义"""
    tasks = openapi.get("x-tasks", [])
    if not tasks:
        return []
    result = []
    for task in tasks:
        entry = {
            "taskType": task.get("taskType", 0),
            "summary": task.get("summary", ""),
            "taskName": task.get("taskName", f"Task{task.get('taskType', 0)}"),
            "params": task.get("params", []),
            "returns": task.get("returns", []),
        }
        result.append(entry)
    return result


def parse_tasks_from_cr(cr: dict) -> list:
    """从 CR YAML 的 spec.tasks 提取任务定义"""
    tasks = cr.get("spec", {}).get("tasks", [])
    if not tasks:
        return []
    result = []
    for task in tasks:
        entry = {
            "taskType": task.get("taskType", 0),
            "summary": task.get("summary", ""),
            "taskName": task.get("taskName", f"Task{task.get('taskType', 0)}"),
            "params": task.get("params", []),
            "returns": task.get("returns", []),
        }
        result.append(entry)
    return result


def parse_ability_info_from_openapi(openapi: dict) -> dict:
    """从 OpenAPI YAML 提取能力基本信息"""
    info = openapi.get("info", {})
    x_insightos = openapi.get("x-insightos", {})
    return {
        "abilityName": info.get("title", "MyAbility"),
        "version": info.get("version", "0.1.0"),
        "description": info.get("description", ""),
        "package": x_insightos.get("packageName", "my.ability.org"),
        "kind": x_insightos.get("kind", "AtomAbility"),
    }


def parse_ability_info_from_cr(cr: dict) -> dict:
    """从 CR YAML 提取能力基本信息"""
    spec = cr.get("spec", {})
    return {
        "abilityName": spec.get("abilityName", "MyAbility"),
        "version": spec.get("version", "0.1.0"),
        "description": "",
        "package": spec.get("package", "my.ability.org"),
        "kind": cr.get("kind", "AtomAbility"),
    }


def generate_task_py(tasks: list) -> str:
    """生成 task.py 内容"""
    lines = ["from ability_py import TaskInterface", "", ""]

    for task in tasks:
        class_name = to_class_name(task["taskName"]) + "Task"
        summary = task.get("summary", "")
        task_type = task["taskType"]
        params = task.get("params", [])
        returns = task.get("returns", [])

        lines.append(f"class {class_name}(TaskInterface):")
        # docstring
        doc_lines = [f'    """{summary} (taskType: {task_type})']
        if params:
            doc_lines.append("")
            doc_lines.append("    Args:")
            doc_lines.append("        input_data: {")
            for p in params:
                ptype = map_type(p.get("type", "any"))
                optional = " (optional)" if p.get("optional", False) else ""
                desc = p.get("description", "")
                desc_str = f"  # {desc}" if desc else ""
                doc_lines.append(f'            "{p["name"]}": {ptype}{optional},{desc_str}')
            doc_lines.append("        }")
        if returns:
            doc_lines.append("")
            doc_lines.append("    Returns:")
            doc_lines.append("        {")
            for r in returns:
                rtype = map_type(r.get("type", "any"))
                desc = r.get("description", "")
                desc_str = f"  # {desc}" if desc else ""
                doc_lines.append(f'            "{r["name"]}": {rtype},{desc_str}')
            doc_lines.append("        }")
        doc_lines.append('    """')
        lines.extend(doc_lines)

        # execute method
        lines.append("")
        lines.append("    def execute(self, input_data: dict) -> dict:")

        # 参数解包
        if params:
            for p in params:
                pname = p["name"]
                default = _default_for_type(p.get("type", "string"))
                lines.append(f'        {pname} = input_data.get("{pname}", {default})')
            lines.append("")

        lines.append(f'        # TODO: 实现{summary or task["taskName"]}逻辑')
        lines.append(f'        raise NotImplementedError("{class_name}.execute()")')
        lines.append("")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _default_for_type(t: str) -> str:
    defaults = {
        "string": '""',
        "str": '""',
        "int": "0",
        "integer": "0",
        "number": "0.0",
        "float": "0.0",
        "double": "0.0",
        "boolean": "False",
        "bool": "False",
        "array": "[]",
        "object": "{}",
        "uuid": '""',
    }
    return defaults.get(t, "None")


def generate_main_py(tasks: list) -> str:
    """生成 main.py 内容"""
    lines = ["from service import ImplAbility, task_manager", "import ability_py"]

    # import 语句
    imports = []
    for task in tasks:
        class_name = to_class_name(task["taskName"]) + "Task"
        imports.append(class_name)

    if imports:
        lines.append(f"from task import {', '.join(imports)}")

    lines.append("")
    lines.append("")

    # task 注册
    if tasks:
        lines.append("# 注册 task")
        lines.append("tasks = {")
        for task in tasks:
            class_name = to_class_name(task["taskName"]) + "Task"
            lines.append(f"    {task['taskType']}: {class_name}(),")
        lines.append("}")
        lines.append("")
        lines.append("task_manager.register_tasks(tasks)")
    lines.append("")

    # main
    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    ability = ImplAbility()")
    lines.append("    service = ability_py.AbilityService()")
    lines.append("    service.run(ability)")
    lines.append("")

    return "\n".join(lines)


def generate_ability_py(ability_info: dict) -> str:
    """生成 ability.py 内容"""
    name = ability_info["abilityName"]
    return f'''import ability_py
import threading
from ability_py.task_server import app
from werkzeug.serving import make_server


class ServerThread(threading.Thread):
    def __init__(self, host="0.0.0.0", port=8080):
        super().__init__(daemon=True)
        self.server = make_server(host, port, app)

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


class ImplAbility(ability_py.AbilityInterface):
    """{name} 能力实现"""

    def __init__(self):
        self.ability_port = 0
        self.st = None

    def on_start(self):
        # TODO: 初始化资源（如加载模型、连接设备等）
        pass

    def on_connect(self):
        if self.ability_port:
            return
        self.ability_port = ability_py.get_free_port()
        self.st = ServerThread(host="localhost", port=self.ability_port)
        self.st.start()

    def on_disconnect(self):
        if self.ability_port != 0:
            self.st.shutdown()
            self.ability_port = 0

    def on_terminate(self):
        # TODO: 释放资源
        pass

    def get_ability_port(self) -> int:
        return self.ability_port
'''


def generate_cr_from_openapi(openapi: dict) -> dict:
    """从 OpenAPI 定义生成 CR YAML 结构"""
    info = parse_ability_info_from_openapi(openapi)
    tasks = parse_tasks_from_openapi(openapi)
    config_schema = openapi.get("x-ability-config", {})

    cr = {
        "kind": info["kind"],
        "metadata": {
            "name": info["abilityName"].lower().replace(".", "-"),
        },
        "spec": {
            "package": info["package"],
            "version": info["version"],
            "abilityName": info["abilityName"],
            "position": "localhost",
        },
    }
    if tasks:
        cr["spec"]["tasks"] = tasks
    if config_schema:
        # 从 schema properties 提取默认配置值
        props = config_schema.get("properties", {})
        config = {}
        for k, v in props.items():
            if "example" in v:
                config[k] = v["example"]
            elif "default" in v:
                config[k] = v["default"]
        if config:
            cr["spec"]["config"] = config
    return cr


def generate_manifest_from_openapi(openapi: dict) -> dict:
    """从 OpenAPI 定义生成 ability.manifest.yaml 结构"""
    info = parse_ability_info_from_openapi(openapi)
    tasks = parse_tasks_from_openapi(openapi)
    config_schema = openapi.get("x-ability-config", {})
    debug_option = openapi.get("x-debug-option", {})
    depends = openapi.get("x-depends", {})

    manifest = {
        "abilityName": info["abilityName"],
        "kind": info["kind"],
    }
    if tasks:
        manifest["tasks"] = tasks
    if config_schema:
        manifest["schema"] = {"config": {"openAPIV3Schema": config_schema}}
    if debug_option:
        manifest.setdefault("schema", {})["debugOption"] = {
            "openAPIV3Schema": debug_option
        }
    if depends:
        manifest["depends"] = depends

    return manifest


def scaffold(
    tasks: list,
    ability_info: dict,
    output_dir: str,
    cr_data: dict = None,
    manifest_data: dict = None,
):
    """生成完整的能力工程目录"""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1. 复制 service/ 模板目录
    template_dir = Path(__file__).parent / "templates" / "service"
    service_dir = out / "service"
    if service_dir.exists():
        shutil.rmtree(service_dir)
    shutil.copytree(template_dir, service_dir)

    # 2. 生成 ability.py (覆盖模板中的)
    ability_content = generate_ability_py(ability_info)
    (service_dir / "ability.py").write_text(ability_content, encoding="utf-8")

    # 3. 生成 task.py
    task_content = generate_task_py(tasks)
    (out / "task.py").write_text(task_content, encoding="utf-8")

    # 4. 生成 main.py
    main_content = generate_main_py(tasks)
    (out / "main.py").write_text(main_content, encoding="utf-8")

    # 5. 写入 CR 和 manifest (如果有)
    if cr_data:
        with open(out / "ability.cr.yaml", "w", encoding="utf-8") as f:
            yaml.dump(cr_data, f, default_flow_style=False, allow_unicode=True)

    if manifest_data:
        with open(out / "ability.manifest.yaml", "w", encoding="utf-8") as f:
            yaml.dump(manifest_data, f, default_flow_style=False, allow_unicode=True)

    return out


def main():
    parser = argparse.ArgumentParser(
        description="能力工程脚手架工具 - 从 OpenAPI/CR 定义生成能力工程代码"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--openapi", type=str, help="OpenAPI YAML 文件路径 (一步到位: 生成 CR + 工程)"
    )
    group.add_argument("--cr", type=str, help="CR YAML 文件路径 (从已有 CR 生成工程)")
    parser.add_argument(
        "--output", "-o", type=str, default="./output", help="输出目录 (默认: ./output)"
    )

    args = parser.parse_args()

    if args.openapi:
        print(f"读取 OpenAPI 定义: {args.openapi}")
        openapi = load_yaml(args.openapi)
        ability_info = parse_ability_info_from_openapi(openapi)
        tasks = parse_tasks_from_openapi(openapi)
        cr_data = generate_cr_from_openapi(openapi)
        manifest_data = generate_manifest_from_openapi(openapi)
    else:
        print(f"读取 CR 定义: {args.cr}")
        cr_data = load_yaml(args.cr)
        ability_info = parse_ability_info_from_cr(cr_data)
        tasks = parse_tasks_from_cr(cr_data)
        manifest_data = None

    print(f"能力名称: {ability_info['abilityName']}")
    print(f"任务数量: {len(tasks)}")
    for t in tasks:
        print(f"  - taskType {t['taskType']}: {t['taskName']} ({t['summary']})")

    out = scaffold(
        tasks=tasks,
        ability_info=ability_info,
        output_dir=args.output,
        cr_data=cr_data,
        manifest_data=manifest_data,
    )
    print(f"\n工程已生成至: {out.resolve()}")
    print("\n接下来:")
    print("  1. 编辑 service/ability.py 中的 on_start() 实现初始化逻辑")
    print("  2. 编辑 task.py 中各 Task 的 execute() 实现业务逻辑")
    print("  3. 运行: python main.py <uuid> '{\"port\": 8080}'")


if __name__ == "__main__":
    main()
