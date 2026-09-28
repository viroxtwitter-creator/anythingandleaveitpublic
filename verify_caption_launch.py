import os,subprocess,json,time
from pathlib import Path
root=Path.cwd();report=root/'analysis/automatic-launch-check.json';started=time.time()
p=subprocess.run([str(root/'.app-captions/CutReview/CutReview.exe'),'--launch-check'],timeout=30)
assert p.returncode==0 and report.stat().st_mtime>=started-1
print(report.read_text())
