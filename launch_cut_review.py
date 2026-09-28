"""Visible error handling for launches from Windows Explorer."""
import ctypes
import os
from pathlib import Path
import runpy
import sys
import traceback

ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0,str(ROOT))
try:
    runpy.run_path(str(ROOT/'automatic_review.py'),run_name='__main__')
except SystemExit as e:
    if e.code not in (None,0):
        ctypes.windll.user32.MessageBoxW(None,'Cut Review could not start. Please tell Codex what happened.','Cut Review',0x10)
        raise
except BaseException:
    details=traceback.format_exc()
    folder=ROOT/'analysis';folder.mkdir(exist_ok=True)
    (folder/'launch-error.log').write_text(details,encoding='utf-8')
    ctypes.windll.user32.MessageBoxW(None,
        'Cut Review could not open. The error has been saved so Codex can fix it.\n\n'+details.splitlines()[-1],
        'Cut Review — could not start',0x10)
    sys.exit(1)
