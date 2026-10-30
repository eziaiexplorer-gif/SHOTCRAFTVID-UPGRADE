#!/usr/bin/env python3
"""Read-only dependency/path diagnostic. No network, installation or credential output."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--strict',action='store_true');a=p.parse_args()
    here=Path(__file__).resolve().parent
    config=here/'shotcraft-paths.json'
    sd=Path(os.environ.get('SHOTCRAFT_SKILLS_DIR') or (json.loads(config.read_text())['skills_dir'] if config.exists() else here))
    tools={x:shutil.which(x) for x in ['ffmpeg','ffprobe','node','npm','claude','codex','opencode']}
    modules={x:importlib.util.find_spec(x) is not None for x in ['numpy','PIL','scipy','edge_tts','cv2']}
    required=['numpy','PIL','scipy']
    ready=sys.version_info>=(3,11) and all(modules[x] for x in required) and all(tools[x] for x in ['ffmpeg','ffprobe']) and (sd/'reels-templates/scripts/smart_render.py').is_file()
    report={'core_renderer_ready':bool(ready),'python':sys.version.split()[0],'python_executable':sys.executable,'skills_dir':str(sd),'executables':tools,'modules':modules,'notes':['Node/Remotion dependencies and browser are separate from the Pillow engine','Offline neural speech requires an installed engine/model; bundled voice references alone do not synthesize speech','No provider/API credentials were accessed or tested']}
    print(json.dumps(report,indent=2))
    return 0 if ready or not a.strict else 1
if __name__=='__main__':raise SystemExit(main())
