"""Native launcher argument, path, exit-code and parent-death contracts."""
import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
launcher=Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix='Semantic native ') as directory:
    root=Path(directory)/"中文 path's space";(root/'bin').mkdir(parents=True)
    shutil.copyfile(launcher,root/'bin/ability.exe')
    environment={**os.environ,'SEMANTIC_ABILITY_PYTHON':sys.executable}
    (root/'main.py').write_text('import json, os, sys\nfrom pathlib import Path\nPath(os.environ["ABILITY_ROOT"],"args.json").write_text(json.dumps(sys.argv[1:]))\nsys.exit(7)\n')
    arguments=['robot-id',json.dumps({'path':'C:\\中文 path\\','quote':'a"b','empty':''},ensure_ascii=False)]
    result=subprocess.run([root/'bin/ability.exe',*arguments],env=environment)
    assert result.returncode==7,result.returncode
    assert json.loads((root/'args.json').read_text())==arguments
    # Owner death must not leave the Python child issuing heartbeats.
    (root/'main.py').write_text('import os, time\nfrom pathlib import Path\np=Path(os.environ["ABILITY_ROOT"],"ticks")\nwhile True:\n p.write_text(str(time.monotonic()))\n time.sleep(.05)\n')
    child=subprocess.Popen([root/'bin/ability.exe'],env=environment)
    try:
        deadline=time.monotonic()+10
        while not (root/'ticks').exists():
            assert time.monotonic()<deadline,'Python child not ready';time.sleep(.05)
        child.kill();child.wait(timeout=5);time.sleep(.3)
        last=(root/'ticks').read_text();time.sleep(.3)
        assert (root/'ticks').read_text()==last,'Python child survived launcher death'
    finally:
        if child.poll() is None:child.kill();child.wait()
print('PASS Unicode/space paths, JSON quoting, child exit status and owner-death cleanup')
