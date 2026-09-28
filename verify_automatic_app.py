import os,json,time,subprocess,sys
from pathlib import Path
root=Path.cwd();exe=root/(sys.argv[1] if len(sys.argv)>1 else '.app-auto')/'CutReview/CutReview.exe'
env={k:v for k,v in os.environ.items() if k.upper() in ['SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','COMSPEC','USERNAME','USERDOMAIN','PROGRAMDATA','SYSTEMDRIVE']};env['PATH']=r'C:\Windows\System32;C:\Windows'
for flag,file in [('--launch-check','automatic-launch-check.json'),('--auto-check','automatic-ui-check.json')]:
 started=time.time();p=subprocess.Popen([str(exe),flag],cwd=r'C:\Windows',env=env,creationflags=subprocess.DETACHED_PROCESS)
 code=p.wait(timeout=900);report=root/'analysis'/file
 assert report.is_file() and report.stat().st_mtime>=started-1,'No fresh report'
 x=json.loads(report.read_text());assert code==0 and x.get('visible',x.get('success',False)),x
 print(flag,'PASS',json.dumps({k:v for k,v in x.items() if k!='result'}),flush=True)
 if flag=='--auto-check':
  r=x['result'];print('Actual packaged button created',r['clips'],'clips,',r['edited_duration'],'seconds',flush=True)
  assert r['verified'] and Path(r['folder'],'Automatic cut.drt').is_file()
print('Packaged launch and actual button-to-Resolve test passed.',flush=True)
