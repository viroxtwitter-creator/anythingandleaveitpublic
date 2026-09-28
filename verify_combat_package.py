import json,os,subprocess,time
from pathlib import Path
root=Path.cwd();exe=root/'.app-tight-retention/CutReview/CutReview.exe'
env={k:v for k,v in os.environ.items() if k.upper() in ['SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','COMSPEC','USERNAME','USERDOMAIN','PROGRAMDATA','SYSTEMDRIVE']};env['PATH']=r'C:\Windows\System32;C:\Windows'
p=subprocess.Popen([str(exe),'--combat-check'],cwd=r'C:\Windows',env=env);print('exit',p.wait(timeout=40));print((root/'analysis/combat-runtime-check.json').read_text()[:150])
