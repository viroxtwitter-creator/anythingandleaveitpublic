import tempfile,wave
from pathlib import Path
from app_paths import add_dependencies
add_dependencies()
import numpy as np
from speech_edges import refine_edges

with tempfile.TemporaryDirectory() as temp:
    wav=Path(temp)/'voice.wav'
    audio=np.zeros(48000,dtype=np.int16)
    audio[16000:32000]=(np.sin(np.arange(16000)*.2)*5000).astype(np.int16)
    with wave.open(str(wav),'wb') as f:
        f.setparams((1,2,16000,0,'NONE','not compressed'));f.writeframes(audio.tobytes())
    ranges,changes=refine_edges([[.6,1.9]],wav)
    assert .90<ranges[0][0]<1 and 2.05<ranges[0][1]<2.2
    assert changes
    ranges,_=refine_edges([[.6,2.5]],wav,events=[(.5,.9),(2.2,2.6)])
    assert ranges==[[.6,2.5]],'Selected gameplay trimmed'
    ranges,_=refine_edges([[1.1,1.9]],wav,exclusions=[(.5,1.1),(1.9,2.4)])
    assert ranges==[[1.1,1.9]],'Removed take restored'
print('PASS: empty lead trimmed, clipped tail extended, gameplay and removed-take barriers preserved')
