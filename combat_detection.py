"""Local audio-event classification with a visual menu/loading veto."""
import csv,json,wave
from pathlib import Path
from app_paths import ROOT,add_dependencies
add_dependencies()
import numpy as np
import av
import onnxruntime as ort
from PIL import Image
from tokenizers import Tokenizer
from review_core import save_json,merge_intervals
MODELS=ROOT/'.model-cache/retention'
PROMPTS=[
 'A screenshot of active first person shooter gameplay, holding a gun and aiming in a combat arena.',
 'A screenshot of third person shooter gameplay, a player fighting outdoors with a weapon and a gameplay HUD.',
 'A screenshot of action video game combat, shooting enemies during a match.',
 'A screenshot of a video game settings menu, configuration window, checkboxes and sliders.',
 'A screenshot of a video game inventory menu with a grid of items and equipment.',
 'A screenshot of a video game lobby menu with a character standing and a play button.',
 'A video game loading screen with text, a progress bar or a black background.',
 'A screenshot of a Windows desktop application or web browser instead of gameplay.'
]

def session(path):
    options=ort.SessionOptions();options.intra_op_num_threads=4;options.inter_op_num_threads=1
    return ort.InferenceSession(str(path),sess_options=options,providers=['CPUExecutionProvider'])

def gunfire_scores(wav,cache,progress,cancel):
    if cache.is_file():return json.loads(cache.read_text())
    with wave.open(str(wav),'rb') as f:
        assert f.getframerate()==16000 and f.getnchannels()==1
        signal=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
    model=session(MODELS/'yamnet/yamnet.onnx');rows=[];hop=7680;count=48
    for start in range(0,len(signal),hop*count):
        if cancel():raise InterruptedError('Analysis stopped')
        chunk=signal[start:start+hop*(count-1)+15600]
        scores=model.run(['output_0'],{'waveform':chunk})[0][:count]
        for i,s in enumerate(scores):
            t=start/16000+i*.48
            if t>=len(signal)/16000:break
            rows.append(dict(start=t,end=min(t+.975,len(signal)/16000),
                gun=float(max(s[421],s[422],s[423])),top=int(s.argmax()),music=float(s[132])))
        progress(f'Checking for shooting: {int(start/16000)//60}:{int(start/16000)%60:02}')
    save_json(cache,rows);return rows

class ScreenCheck:
    def __init__(self):
        tok=Tokenizer.from_file(str(MODELS/'clip/tokenizer.json'))
        tok.enable_truncation(max_length=77);tok.enable_padding(pad_id=49407,pad_token='<|endoftext|>')
        ids=np.asarray([e.ids for e in tok.encode_batch(PROMPTS)],dtype=np.int64)
        text=session(MODELS/'clip/text_model_quantized.onnx').run(None,{'input_ids':ids})[0]
        self.text=text/np.linalg.norm(text,axis=1,keepdims=True)
        self.model=session(MODELS/'clip/vision_model_quantized.onnx')
        config=json.loads((MODELS/'clip/preprocessor_config.json').read_text())
        self.mean=np.asarray(config['image_mean'],dtype=np.float32);self.std=np.asarray(config['image_std'],dtype=np.float32)
    def classify(self,image):
        w,h=image.size;scale=224/min(w,h);im=image.resize((round(w*scale),round(h*scale)),Image.Resampling.BICUBIC)
        x=(im.width-224)//2;y=(im.height-224)//2
        arr=np.asarray(im.crop((x,y,x+224,y+224)).convert('RGB'),dtype=np.float32)/255
        if float(arr.mean())<.035:return dict(gameplay=False,margin=-1,label='dark/loading',scores=[])
        pixels=((arr-self.mean)/self.std).transpose(2,0,1)[None]
        emb=self.model.run(None,{'pixel_values':pixels})[0];emb/=np.linalg.norm(emb,axis=1,keepdims=True)
        scores=(emb@self.text.T)[0];margin=float(max(scores[:3])-max(scores[3:]))
        return dict(gameplay=margin>=0,margin=margin,label=PROMPTS[int(scores.argmax())],scores=scores.tolist())

def detect(source,wav,key,duration,progress,cancel):
    cache=ROOT/'analysis'/f'gunfire-v1-{key}.json'
    scores=gunfire_scores(wav,cache,progress,cancel)
    candidates=[r for r in scores if r['gun']>=.18]
    visual_cache=ROOT/'analysis'/f'screen-check-v1-{key}.json'
    try:visual=json.loads(visual_cache.read_text())
    except (OSError,ValueError):visual={}
    model=None;accepted=[];rejected=[]
    with av.open(str(source)) as c:
        stream=c.streams.video[0]
        for n,r in enumerate(candidates):
            if cancel():raise InterruptedError('Analysis stopped')
            # Sample near the acoustic event, rather than extrapolating from a distant keyframe.
            t=min(duration-.04,r['start']+.48);label=f'{t:.2f}'
            if label not in visual:
                if model is None:model=ScreenCheck()
                c.seek(int(t/stream.time_base),stream=stream)
                frame=next((f for f in c.decode(stream) if f.time is not None and f.time>=t),None)
                visual[label]=model.classify(frame.to_image()) if frame else dict(gameplay=False,label='unreadable frame',margin=-1)
            visual[label]['gameplay']=visual[label]['margin']>=0
            if visual[label]['gameplay']:accepted.append([max(0,r['start']-.20),min(duration,r['end']+.30)])
            else:rejected.append(dict(time=t,gun=r['gun'],screen=visual[label]['label']))
            if n%20==0:
                progress(f'Checking gameplay versus menus: {n+1} / {len(candidates)}')
                save_json(visual_cache,visual)
    save_json(visual_cache,visual)
    return merge_intervals(accepted,0,duration),dict(audio_candidates=len(candidates),visual_rejections=len(rejected),rejected=rejected,
        method='YAMNet gunfire classes >= 0.18, CLIP gameplay score >= menu/loading scores; sampled checks, not guaranteed event recognition')
