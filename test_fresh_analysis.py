"""Two requests for the same source must run every analysis stage again."""
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import automatic_cut as cut

with tempfile.TemporaryDirectory() as temp:
    root=Path(temp)
    (root/'analysis').mkdir()
    model=root/'.model-cache'/'test'
    model.mkdir(parents=True)
    for name in ('model.bin','config.json','tokenizer.json'):
        (model/name).touch()
    source=root/'recording.mp4'
    source.touch()
    calls=[]
    class Model:
        def __init__(self,*args,**kwargs):pass
        def transcribe(self,path,**kwargs):
            calls.append(path)
            word=SimpleNamespace(start=1,end=2,word=' Hello.',probability=1)
            return iter([SimpleNamespace(start=1,end=2,text=' Hello.',words=[word])]),None
    def extract(source,mic,start,end,path):path.touch()
    with patch.object(cut,'ROOT',root), patch.object(cut,'probe',return_value=(5,30,['Voice','Game'])), \
         patch.object(cut,'extract',side_effect=extract) as audio, \
         patch.dict(sys.modules,{'faster_whisper':SimpleNamespace(WhisperModel=Model)}), \
         patch('combat_detection.detect',return_value=([],{})) as combat, \
         patch('speech_edges.refine_edges',side_effect=lambda ranges,*args:(ranges,[])), \
         patch('pause_cleanup.clean_pauses',side_effect=lambda ranges,*args:(ranges,[])):
        first=cut.plan(source,0)
        second=cut.plan(source,0)
    assert first['analysis_run_id']!=second['analysis_run_id']
    assert first['analysis_mode']==second['analysis_mode']=='fresh'
    assert len(calls)==2 and calls[0]!=calls[1]
    assert audio.call_count==4
    assert combat.call_count==2
    assert combat.call_args_list[0].args[2]!=combat.call_args_list[1].args[2]
    assert first['kept']==second['kept'], 'Fresh analysis need not produce random edits'
print('PASS: same recording re-transcribed, audio re-extracted and action analysis isolated each run')
