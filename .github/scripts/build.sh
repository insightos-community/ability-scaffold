#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
mkdir -p .output/payload
uv build
uv venv .output/test --python 3.13
uv pip install --python .output/test/bin/python dist/*.whl
.output/test/bin/ability-scaffold version
.output/test/bin/ability-scaffold scaffold --openapi examples/EndpointControl.openapi.yaml -o .output/example
.output/test/bin/ability-scaffold pack .output/example -o .output/example.zip
python3 -c "import zipfile; z=zipfile.ZipFile('.output/example.zip'); assert z.testzip() is None; assert 'main.py' in z.namelist()"
