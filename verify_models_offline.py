import json,os,subprocess,time
from pathlib import Path
root=Path.cwd();report=root/'analysis/combat-runtime-check.json'
env={k:v for k,v in os.environ.items() if k.upper() in ['SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','COMSPEC','USERNAME','USERDOMAIN','PROGRAMDATA','SYSTEMDRIVE']};env['PATH']=r'C:\Windows\System32;C:\Windows'
started=time.time()
p=subprocess.run([str(root/'.app-retention-v2/CutReview/CutReview.exe'),'--combat-check'],cwd=r'C:\Windows',env=env,timeout=40)
assert p.returncode==0 and report.stat().st_mtime>=started-1
assert json.loads(report.read_text())['success']
print('PASS: current packaged models run without launching the UI or contacting Resolve.')
