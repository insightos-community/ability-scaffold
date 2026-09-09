# Ability project and package reference

[English overview](README.md) | [中文概览](README.zh-CN.md)

This curated reference replaces contradictory installation instructions in the earlier README.

## Generator inputs

`scaffold --openapi FILE -o DIR` generates a project from an OpenAPI YAML definition. Alternatively use `scaffold --cr FILE -o DIR`. Supply a new output directory and inspect generated files before integrating them into an existing project.

See [examples](examples/) for input definitions and a generated project. Implement business logic before deployment; generated interfaces do not provide robot behavior.

## Package contract

The packer validates the following required files:

| File | Role |
|---|---|
| `package.yaml` | Package name, version, architecture, and metadata |
| `ability.manifest.yaml` | Ability interface and execution metadata |
| `bin/ability` | Executable entry point |
| `main.py` | Python application entry point |

```bash
ability-scaffold pack ./my-ability -o my-ability.zip
```

Install the ZIP through AbilityFramework's package interface or include it in a versioned Robot Bundle. Do not embed credentials, local environments, or host-specific paths.

## Dependency boundary

The generator depends on PyYAML. Generated Python abilities depend on ability-py and their declared application dependencies; these must be available in the target runtime environment. Packaging is not equivalent to resolving, vendoring, or testing every runtime dependency.

For the exact validation rules, see [pack.py](src/ability_scaffold/pack.py); for generation behavior, see [scaffold.py](src/ability_scaffold/scaffold.py).
