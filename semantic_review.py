"""Local sentence embeddings for nearby alternative takes, not factual entailment."""
import re,json
from functools import lru_cache
from app_paths import ROOT,add_dependencies
add_dependencies()
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

@lru_cache(maxsize=1)
def runtime():
    folder=ROOT/'.model-cache/semantic-minilm'
    options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
    session=ort.InferenceSession(str(folder/'onnx/model_quantized.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
    tok=Tokenizer.from_file(str(folder/'tokenizer.json'));tok.enable_truncation(max_length=256);tok.enable_padding(pad_id=0,pad_token='[PAD]')
    return session,tok

def encode(texts):
    session,tok=runtime();result=[]
    for start in range(0,len(texts),16):
        batch=tok.encode_batch(texts[start:start+16])
        ids=np.asarray([x.ids for x in batch],dtype=np.int64)
        mask=np.asarray([x.attention_mask for x in batch],dtype=np.int64)
        feed={'input_ids':ids,'attention_mask':mask,'token_type_ids':np.zeros_like(ids)}
        output=session.run(None,{x.name:feed[x.name] for x in session.get_inputs()})[0]
        pooled=(output*mask[:,:,None]).sum(1)/np.maximum(mask.sum(1)[:,None],1)
        result.extend(pooled/np.maximum(np.linalg.norm(pooled,axis=1,keepdims=True),1e-9))
    return np.asarray(result)

def terms(text):return re.findall(r"[a-z0-9]+(?:'[a-z]+)?",text.lower())

def facts(text):
    tokens=terms(text)
    numbers={'one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','first','second','third'}
    negation={'not','never','no','without',"don't","can't","won't","isn't","doesn't"}
    return {x for x in tokens if any(c.isdigit() for c in x) or x in numbers|negation}

def opposite(a,b):
    first,second=set(terms(a)),set(terms(b))
    groups=[({'good','great','amazing','better'},{'bad','awful','terrible','worse'}),({'love'},{'hate'}),({'enable'},{'disable'}),({'increase'},{'decrease'})]
    return any((first&x and second&y) or (first&y and second&x) for x,y in groups)

def quality(row):
    words=row['words'];text=row['text'].rstrip()
    complete=not text.endswith(('-', '—','…','...')) and terms(text)[-1] not in {'and','but','to','the','a','because','if'}
    confidence=sum(w.get('probability',1) for w in words)/len(words)
    return (complete,round(confidence,1),min(len(words),40))

def review(rows,ranges,events):
    eligible=[(i,r) for i,r in enumerate(rows) if 6<=len(r['words'])<=60]
    if len(eligible)<2:return ranges,[],dict(model='all-MiniLM-L6-v2 quantized',comparisons=[])
    embeddings=encode([r['text'] for _,r in eligible]);removed=set();changes=[];comparisons=[]
    preferences=json.loads((ROOT/'semantic-preferences.json').read_text(encoding='utf-8'))
    for ai,(i,a) in enumerate(eligible):
        if i in removed:continue
        for bi in range(ai+1,min(ai+4,len(eligible))):
            j,b=eligible[bi]
            if j in removed:continue
            gap=b['source_start']-a['source_end']
            if gap>25:break
            score=float(embeddings[ai]@embeddings[bi])
            approved=any(terms(a['text'])==terms(x['earlier']) and terms(b['text'])==terms(x['keep']) for x in preferences['approved_alternative_takes'])
            if score<.86 and not approved:continue
            reason=None
            if facts(a['text'])!=facts(b['text']):reason='Different protected facts or polarity'
            elif opposite(a['text'],b['text']):reason='Opposing statements'
            elif any(a['source_start']<y and b['source_end']>x for x,y in events):reason='Gameplay between or within takes'
            elif any(t in terms(b['text'])[:4] for t in ('also','another','additionally','however')):reason='Explicit additional point'
            # Retakes must be comparable in scope; do not drop an explanation for
            # a short summary or a sentence that adds an entire extra clause.
            elif min(len(a['words']),len(b['words']))/max(len(a['words']),len(b['words']))<.65:reason='Different scope'
            comparisons.append(dict(first=a['text'],second=b['text'],similarity=score,blocked=reason))
            if reason:continue
            loser,winner=(a,b) if approved or quality(b)>=quality(a) else (b,a)
            idx=i if loser is a else j
            removed.add(idx)
            changes.append(dict(source_start=loser['source_start'],source_end=loser['source_end'],text=loser['text'],kept_text=winner['text'],similarity=score,reason='User-confirmed alternative introduction' if approved else 'Nearby semantically similar alternative take; one talking point retained'))
            if idx==i:break
    return [r for i,r in enumerate(ranges) if i not in removed],changes,dict(model='all-MiniLM-L6-v2 quantized',threshold=.86,comparisons=comparisons)
