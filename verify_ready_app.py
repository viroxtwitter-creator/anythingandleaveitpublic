import os,sys,json,time,subprocess,zipfile
from pathlib import Path
root=Path.cwd(); exe=root/'.app-ready/CutReview/CutReview.exe'
assert zipfile.is_zipfile(exe.parent/'_internal/base_library.zip'), 'Damaged runtime archive'
env={k:v for k,v in os.environ.items() if k.upper() in ['SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','COMSPEC','USERNAME','USERDOMAIN','PROGRAMDATA','SYSTEMDRIVE']};env['PATH']=r'C:\Windows\System32;C:\Windows'
for flag,report in [('--launch-check','packaged-check.json'),('--speech-check','speech-check.json')]:
 t=time.time();p=subprocess.Popen([str(exe),flag],cwd=r'C:\Windows',env=env,creationflags=subprocess.DETACHED_PROCESS)
 print('Testing',flag,flush=True);code=p.wait(timeout=300)
 f=root/'analysis'/report
 print('Exit',code,flush=True)
 assert f.exists() and f.stat().st_mtime>=t-1,'No fresh check result'
 data=json.loads(f.read_text());print(json.dumps(data,indent=2),flush=True)
 assert code==0, data
 assert data.get('visible') or data.get('success'),data
print('BOTH TESTS PASSED',flush=True)
