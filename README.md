# Ability Scaffold

[English](README.md) | [简体中文](README.zh-CN.md)

🧩 Generate Python Ability projects from OpenAPI/CR YAML and package them for AbilityFramework. The generator requires PyYAML; the generated Ability uses the separate ability-py SDK.

## Structure

- `src/ability_scaffold/` — command dispatch, generation, and packaging.
- `examples/` — input definitions and a generated example.
- `pyproject.toml` — package metadata and CLI entry point.

## 🛠 Build and install

Requires Python **3.8+** and uv. Quick-start uses **3.13**.

```bash
uv build --wheel
uv venv --python 3.13
uv pip install dist/ability_scaffold-*.whl
.venv/bin/ability-scaffold version
```

The Wheel is a developer tool, not an Ability package. Quick-start installs it in ability-runtime's build environment.

## Generate and package

From an activated environment containing ability-scaffold:

```bash
ability-scaffold scaffold --openapi MyAbility.openapi.yaml -o ./my-ability
# Implement and test the generated Ability before packaging.
ability-scaffold pack ./my-ability -o my-ability.zip
```

Provide your actual OpenAPI definition; `--cr ability.cr.yaml` is the alternative input mode. The generated project includes package/Ability manifests and executable entry points. Packaging checks the required files before producing a ZIP.

Install the ZIP through AbilityFramework or include it in a Robot Bundle. Install ability-py and other runtime dependencies in the target Ability environment; installing the generator alone does not provide them.

## Troubleshooting

A missing `package.yaml`, `ability.manifest.yaml`, `bin/ability`, or `main.py` indicates an incomplete project or the wrong packaging directory. Generated code is a starting point: packaging success does not validate robot behavior.

[Project/package reference](README.reference.md) · [Examples](examples/)

## License

Copyright 2026 InsightOS. First-party code: [Apache-2.0](LICENSE). See [NOTICE](NOTICE) and [license scope](LICENSE_SCOPE.md) for third-party components and assets.

## Reproducible platform builds

See [glibc, musl and macOS build instructions](README.build.md) for pinned source revisions, exact scripts, tool requirements, local commands, CI reproduction and platform support boundaries.
