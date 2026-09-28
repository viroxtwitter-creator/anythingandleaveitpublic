import ctypes
import runpy
from pathlib import Path
import sys
import traceback

root=Path(sys.executable).resolve().parents[2]
try:
    if '--combat-check' in sys.argv:
        import combat_detection as c
        import numpy as np
        from PIL import Image
        result=c.ScreenCheck().classify(Image.new('RGB',(224,224),(120,150,100)))
        scores=c.session(c.MODELS/'yamnet/yamnet.onnx').run(['output_0'],{'waveform':np.zeros(16000,dtype=np.float32)})[0]
        assert scores.shape[1]==521
        (root/'analysis/combat-runtime-check.json').write_text(__import__('json').dumps({'success':True,'screen':result}))
        sys.exit(0)
    if '--speech-check' in sys.argv:
        from speech_runtime_check import run
        sys.exit(run())
    runpy.run_module('automatic_review',run_name='__main__')
except SystemExit:
    raise
except BaseException:
    details=traceback.format_exc()
    (root/'analysis'/'packaged-error.log').write_text(details,encoding='utf-8')
    if '--launch-check' not in sys.argv:
        ctypes.windll.user32.MessageBoxW(None,'Retention Cut could not start. Error details have been saved.\n\n'+details.splitlines()[-1],'Retention Cut',0x10)
    sys.exit(1)
