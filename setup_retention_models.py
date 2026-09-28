import urllib.request,json,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
root=Path('.model-cache/retention');root.mkdir(exist_ok=True)
sets={'audiomagic/yamnet-onnx':['yamnet.onnx','yamnet_class_map.csv','LICENSE'], 'Xenova/clip-vit-base-patch32':['onnx/vision_model_quantized.onnx','onnx/text_model_quantized.onnx','tokenizer.json','preprocessor_config.json','README.md']}
jobs=[];manifest=[]
for repo,files in sets.items():
 info=json.load(urllib.request.urlopen('https://huggingface.co/api/models/'+repo));sha=info['sha']
 for f in files:jobs.append((repo,sha,f))
def get(job):
 repo,sha,f=job;dest=root/('yamnet' if 'yamnet' in repo else 'clip')/Path(f).name;dest.parent.mkdir(exist_ok=True)
 if not dest.exists():
  tmp=dest.with_suffix(dest.suffix+'.download');urllib.request.urlretrieve(f'https://huggingface.co/{repo}/resolve/{sha}/{f}',tmp);tmp.replace(dest)
 print(dest.name,dest.stat().st_size,flush=True)
 return dict(repo=repo,revision=sha,file=f,local=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
with ThreadPoolExecutor(max_workers=4) as pool:manifest=list(pool.map(get,jobs))
(root/'models.json').write_text(json.dumps(manifest,indent=2))
