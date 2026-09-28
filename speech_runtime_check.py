import hashlib
import json
from pathlib import Path
from app_paths import ROOT

def run():
    from cut_review import AnalyzeWorker, av
    from PySide6.QtCore import QCoreApplication
    app=QCoreApplication([])
    source=Path(json.loads((ROOT/'analysis/simple-preferences.json').read_text())['source'])
    c=av.open(str(source));duration=c.duration/1e6
    names=[s.metadata.get('name','') for s in c.streams.audio];c.close()
    index=next(i for i,n in enumerate(names) if 'mic' in n.lower())
    stat=source.stat()
    key=hashlib.sha1(f'{source.resolve()}:{stat.st_size}:{stat.st_mtime_ns}'.encode()).hexdigest()[:14]
    cache=ROOT/'analysis'/f'transcript-{key}-{index}.json'
    result={'source':str(source),'track':index,'name':names[index]}
    worker=AnalyzeWorker(source,index,duration,cache)
    worker.ready.connect(lambda rows:result.update(success=True,segments=len(rows)))
    worker.failed.connect(lambda error:result.update(success=False,error=error))
    worker.progress.connect(lambda progress:(ROOT/'analysis/speech-check-progress.txt').write_text(progress,encoding='utf-8'))
    worker.run()
    (ROOT/'analysis/speech-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return 0 if result.get('success') else 1
