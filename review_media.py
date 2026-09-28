"""Preserve independent source audio streams for Resolve's append API."""
import sys
from pathlib import Path
from app_paths import ROOT, add_dependencies
add_dependencies()
import av
import hashlib
import json

def audio_sidecars(source, progress=lambda text:None):
    source=Path(source)
    stat=source.stat()
    key=hashlib.sha1(f'{source.resolve()}:{stat.st_size}:{stat.st_mtime_ns}'.encode()).hexdigest()[:14]
    folder=ROOT/'analysis'/'audio-for-resolve'/key;folder.mkdir(parents=True,exist_ok=True)
    manifest=folder/'complete.json'
    if manifest.exists():
        items=json.loads(manifest.read_text())
        if all(Path(x['path']).exists() for x in items):return items
    c=av.open(str(source));outputs=[];items=[]
    for i,s in enumerate(c.streams.audio):
        if s.start_time is not None and abs(float(s.start_time*s.time_base))>.05:
            c.close();raise ValueError('This recording has offset audio streams. Automatic draft export needs an offset-aware import; review playback still works.')
        # NVIDIA recordings use AAC. Copy packets exactly, without re-encoding.
        if s.codec_context.name!='aac':
            c.close();raise ValueError('Draft export currently supports separate AAC audio tracks. This recording can still be reviewed, but needs a different audio export path.')
        path=folder/f'audio-{i+1}.m4a'
        out=av.open(str(path),mode='w');track=out.add_stream_from_template(s)
        outputs.append((out,track))
        items.append(dict(path=str(path.resolve()),name=s.metadata.get('name',f'Audio {i+1}'),index=s.index))
    mapping={s.index:i for i,s in enumerate(c.streams.audio)}
    last=-1
    try:
        for packet in c.demux(c.streams.audio):
            if packet.dts is None:continue
            idx=mapping[packet.stream.index]
            if packet.pts is not None:
                sec=int(packet.pts*packet.time_base)
                if sec//30>last:last=sec//30;progress(f'Preparing separate audio without re-encoding: {sec//60}:{sec%60:02}')
            out,track=outputs[idx];packet.stream=track;out.mux(packet)
    finally:
        c.close()
        for out,_ in outputs:out.close()
    manifest.write_text(json.dumps(items,indent=2),encoding='utf-8')
    return items
