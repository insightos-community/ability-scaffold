# Ability Scaffold

[English](README.md) | [简体中文](README.zh-CN.md)

🧩 从 OpenAPI / CR YAML 生成 Python Ability 工程，并打包为 AbilityFramework 可安装的包。生成器依赖 PyYAML；生成的能力使用独立的 ability-py SDK。

## 工程结构

- `src/ability_scaffold/`：命令入口、代码生成与打包。
- `examples/`：输入定义与生成示例。
- `pyproject.toml`：包元数据与 CLI 入口。

## 🛠 构建与安装

需要 Python **3.8+** 和 uv；quick-start 使用 **3.13**。

```bash
uv build --wheel
uv venv --python 3.13
uv pip install dist/ability_scaffold-*.whl
.venv/bin/ability-scaffold version
```

Wheel 是开发工具，不是 Ability 包。quick-start 将其安装在 ability-runtime 的构建环境中。

## 生成与打包

在已激活、安装了 ability-scaffold 的环境中：

```bash
ability-scaffold scaffold --openapi MyAbility.openapi.yaml -o ./my-ability
# 实现并测试生成的 Ability 后，再进行打包。
ability-scaffold pack ./my-ability -o my-ability.zip
```

请提供实际 OpenAPI 定义；也可使用 `--cr ability.cr.yaml` 模式。生成工程包含包 / Ability 清单及可执行入口，打包时会检查必要文件并输出 ZIP。

ZIP 可通过 AbilityFramework 安装，或纳入 Robot Bundle。目标能力环境仍需安装 ability-py 与其他运行依赖，安装生成器本身不会提供这些依赖。

## 常见问题

缺少 `package.yaml`、`ability.manifest.yaml`、`bin/ability` 或 `main.py`，通常说明工程不完整或打包目录错误。生成代码只是起点，打包成功不代表机器人行为已验证。

[工程与包参考](README.reference.md) · [示例](examples/)

## 许可证

Copyright 2026 InsightOS。自有代码采用 [Apache-2.0](LICENSE)；第三方组件与资产请查看 [NOTICE](NOTICE) 和[许可范围](LICENSE_SCOPE.md)。

## 三个平台的构建复现

参见 [glibc、musl 与 macOS 构建说明](README.build.md)：包含已锁定的源码版本、实际脚本入口、工具要求、本地与 CI 指令、产物位置和平台验证范围。
