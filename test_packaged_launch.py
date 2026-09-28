import subprocess,os,pathlib,json
root=pathlib.Path(r'C:\Users\jordan\Desktop\Edit')
env={k:v for k,v in os.environ.items() if k.upper() in ['SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','COMSPEC','USERNAME','USERDOMAIN','PROGRAMDATA','SYSTEMDRIVE']}
env['PATH']=r'C:\Windows\System32;C:\Windows'
p=subprocess.Popen([str(root/'.app/CutReview/CutReview.exe'),'--launch-check'],env=env,cwd=r'C:\Windows',creationflags=subprocess.DETACHED_PROCESS,close_fds=True)
try:
 print('Exit',p.wait(timeout=30))
except subprocess.TimeoutExpired:
 print('Still running',p.pid)
path=root/'analysis/packaged-check.json'
print(path.read_text() if path.exists() else 'Check did not finish')
