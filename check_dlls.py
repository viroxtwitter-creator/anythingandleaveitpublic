import sys,pathlib,hashlib
root=pathlib.Path.cwd()
for source,target in [('PySide6/QtCore.pyd','PySide6/QtCore.pyd'),('PySide6/Qt6Core.dll','Qt6Core.dll'),('PySide6/pyside6.abi3.dll','pyside6.abi3.dll'),('shiboken6/shiboken6.abi3.dll','shiboken6.abi3.dll')]:
 a=root/'.analysis-deps'/source;b=root/'.app/CutReview/_internal'/target
 print(source,hashlib.sha256(a.read_bytes()).hexdigest()==hashlib.sha256(b.read_bytes()).hexdigest())
