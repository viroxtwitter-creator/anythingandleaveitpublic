import subprocess,os,pathlib
root=pathlib.Path(r'C:\Users\jordan\Desktop\Edit')
pythonw=r'C:\Users\jordan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe'
p=subprocess.Popen([pythonw,str(root/'diagnose_launch.py')],cwd=r'C:\Windows',creationflags=subprocess.DETACHED_PROCESS,close_fds=True)
p.wait(timeout=20)
print((root/'analysis/diagnostic-pythonw.json').read_text())
