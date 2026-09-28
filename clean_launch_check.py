import subprocess,os,pathlib,json
root=pathlib.Path(r'C:\Users\jordan\Desktop\Edit')
runtime=pathlib.Path(r'C:\Users\jordan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python')
env={k:v for k,v in os.environ.items() if k.upper() in ['SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','COMSPEC','USERNAME','USERDOMAIN','PROGRAMDATA','SYSTEMDRIVE']}
env['PATH']=r'C:\Windows\System32;C:\Windows'
for name in ['python.exe','pythonw.exe']:
 p=subprocess.run([str(runtime/name),str(root/'diagnose_launch.py')],env=env,cwd=r'C:\Windows',capture_output=True,timeout=30)
 print(name,p.returncode,p.stderr.decode(errors='replace')[-500:])
 print((root/'analysis'/('diagnostic-'+pathlib.Path(name).stem+'.json')).read_text())
