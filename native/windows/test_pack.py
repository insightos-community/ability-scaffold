"""Pack an installed-wheel project and execute its extracted native entry."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

launcher = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix='Semantic pack ') as temporary:
    root = Path(temporary)/"中文 project's directory"
    root.mkdir()
    (root/'package.yaml').write_text('name: test.native\nversion: 1.0.0\narch: x86_64\ndescription: 中文能力\n', encoding='utf-8')
    (root/'ability.manifest.yaml').write_text('abilityName: NativeTest\nkind: AtomAbility\n', encoding='utf-8')
    (root/'main.py').write_text('import json,sys\nfrom pathlib import Path\nPath(__file__).with_name("args.json").write_text(json.dumps(sys.argv[1:]))\n', encoding='utf-8')
    (root/'nested').mkdir()
    (root/'nested/说明.txt').write_text('保留 UTF-8 内容', encoding='utf-8')
    archive = Path(temporary)/'ability.zip'
    env = {**os.environ, 'SEMANTIC_WINDOWS_ABILITY_LAUNCHER': str(launcher)}
    result = subprocess.run([sys.executable, '-m', 'ability_scaffold.cli', 'pack', str(root), '-o', str(archive)], env=env)
    assert result.returncode == 0, result.returncode
    target = Path(temporary)/'extracted 中文'
    with zipfile.ZipFile(archive) as package:
        assert all('\\' not in name for name in package.namelist())
        assert package.read('bin/ability.exe') == launcher.read_bytes()
        assert package.read('nested/说明.txt').decode('utf-8') == '保留 UTF-8 内容'
        package.extractall(target)
    arguments = ['robot-1', json.dumps({'text':'中文', 'quoted':'a"b'}, ensure_ascii=False)]
    result = subprocess.run([target/'bin/ability.exe', *arguments], env={**env, 'SEMANTIC_ABILITY_PYTHON': sys.executable})
    assert result.returncode == 0
    assert json.loads((target/'args.json').read_text()) == arguments
print('PASS installed pack CLI, ZIP paths, UTF-8 metadata and extracted native entry')
