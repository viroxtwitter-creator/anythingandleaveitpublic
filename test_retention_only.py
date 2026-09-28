import tempfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import automatic_cut as cut

with tempfile.TemporaryDirectory() as temp:
    root=Path(temp);(root/'analysis').mkdir()
    scripts=[]
    def export(folder,*args,**kwargs):
        folder.mkdir(parents=True)
        script=folder/'create_resolve_draft.lua'
        script.write_text('-- base cut only\n',encoding='utf-8');scripts.append(script)
    def run(*args,**kwargs):
        script=scripts[0].read_text(encoding='utf-8')
        for forbidden in ('CreateSubtitlesFromAudio','AddFusionComp','AddMarker','AUTO_SFX','Snap'):
            assert forbidden not in script
        return SimpleNamespace(stdout='CUT_REVIEW_OK RETENTION - test\nAUTO_VERIFIED 1 60 2',stderr='')
    result=dict(source='example.mp4',duration=10,fps=60,kept=[[1,2]],sfx_enabled=True,captions_enabled=True,motion_enabled=True)
    with patch.object(cut,'ROOT',root),patch.object(cut,'export_review',export),patch.object(cut.subprocess,'run',run),patch('review_media.audio_sidecars',return_value=[]):
        out=cut.send(result)
    assert not any(k.startswith(('sfx_','caption','motion_')) for k in out)
    assert out['verified']
print('PASS: export path contains only retention cuts and original audio')
