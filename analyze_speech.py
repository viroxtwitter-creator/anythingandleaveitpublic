import os
import sys
from pathlib import Path

from app_paths import ROOT, add_dependencies
add_dependencies()
os.environ['HF_HOME'] = str(ROOT / '.model-cache')
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
import av
import numpy as np
import json
import wave

OUT = ROOT / 'analysis'
SOURCE = Path("T:/Tom Clancy's Rainbow Six Siege/Tom Clancy's Rainbow Six Siege 2026.08.21 - 22.30.24.03.mp4")

def extract(path, index, start, end, dest):
    if dest.exists():
        return
    c = av.open(str(path))
    stream = c.streams.audio[index]
    print('Audio stream', index, stream.metadata, flush=True)
    c.seek(int(start * 1e6))
    resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
    data = np.zeros(round((end-start)*16000), dtype=np.int16)
    for frame in c.decode(stream):
        if frame.time is not None and frame.time > end + 0.2:
            break
        for f in resampler.resample(frame):
            pos = round((float(f.pts * f.time_base)-start)*16000)
            values = f.to_ndarray().reshape(-1)
            lo, hi = max(0, pos), min(len(data), pos + len(values))
            if hi > lo:
                data[lo:hi] = values[lo-pos:hi-pos]
    c.close()
    with wave.open(str(dest), 'wb') as w:
        w.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        w.writeframes(data.tobytes())

if __name__ == '__main__':
    for i in range(2):
        extract(SOURCE, i, 230, 335, OUT / f'reference-audio-{i}.wav')
    from faster_whisper import WhisperModel
    model = WhisperModel('base.en', device='cpu', compute_type='int8', cpu_threads=4,
                         download_root=str(ROOT / '.model-cache'))
    for i in range(2):
        dest = OUT / f'reference-transcript-{i}.json'
        if dest.exists():
            continue
        segs, info = model.transcribe(str(OUT / f'reference-audio-{i}.wav'),
            language='en', vad_filter=True, word_timestamps=True, beam_size=3,
            condition_on_previous_text=False)
        rows = []
        for s in segs:
            row = {'start': s.start+230, 'end': s.end+230, 'text': s.text,
                   'words': [{'start': w.start+230, 'end': w.end+230,
                              'text': w.word, 'probability': w.probability} for w in s.words]}
            rows.append(row)
            print(i, round(row['start'],2), row['text'], flush=True)
        dest.write_text(json.dumps(rows, indent=2), encoding='utf-8')
    print('DONE', flush=True)
