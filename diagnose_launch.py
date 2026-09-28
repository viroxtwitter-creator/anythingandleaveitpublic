import sys,os,json,traceback,importlib.util,importlib.machinery
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.analysis-deps'))
report={'executable':sys.executable,'version':sys.version,'path':sys.path,'cwd':os.getcwd(),
        'suffixes':importlib.machinery.EXTENSION_SUFFIXES,'stderr':str(sys.stderr)}
try:
    import PySide6
    report['pyside_file']=PySide6.__file__
    report['pyside_path']=list(PySide6.__path__)
    report['qtcore_exists']=(Path(PySide6.__file__).parent/'QtCore.pyd').exists()
    report['qtcore_spec']=str(importlib.util.find_spec('PySide6.QtCore'))
    from PySide6.QtCore import qVersion
    report['qt_version']=qVersion()
except BaseException:report['error']=traceback.format_exc()
(ROOT/'analysis'/('diagnostic-'+Path(sys.executable).stem+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
