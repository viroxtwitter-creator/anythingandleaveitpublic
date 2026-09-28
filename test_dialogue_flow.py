from dialogue_cut import clean_dialogue
from dialogue_flow import speech_ranges

def sentence(text,start=1):
 return {'words':[dict(text=' '+t,start=start+i*.2,end=start+i*.2+.15) for i,t in enumerate(text.split())]}
for text in ('I I I think this works.', 'I think I think this works.', 'um I can see it.'):
 ranges,cuts,rows=clean_dialogue([sentence(text)],20)
 assert rows,text
 final=sentence(text)['words'][-1]
 assert any(a<=final['start'] and b>=final['end'] for a,b in ranges)
assert not clean_dialogue([sentence('That is very very good!')],20)[2]
assert not clean_dialogue([sentence('Go go go!')],20)[2]
assert clean_dialogue([sentence('Th- this works.')],20)[2]
assert not clean_dialogue([sentence('I will turn on every option now.',1),sentence('I will turn on...',4)],20)[2]
assert not clean_dialogue([sentence('I think the graphics look amazing.',1),sentence('I think the controls feel awkward.',4)],20)[2]
assert not clean_dialogue([sentence('We have 12 bullets left now.',1),sentence('We have 13 bullets left now.',3)],20)[2]
assert not clean_dialogue([sentence('Shake it shake it shake it shake it!')],20)[2]
assert clean_dialogue([sentence('I was gonna'),sentence('Look at this enemy.',5)],20)[2]
assert not clean_dialogue([sentence('I was gonna'),sentence('try the other route.',1.8)],20)[2]
w=sentence('The next thing works.')['words'];w[2]['start']+=.15;w[2]['end']+=.15;w[3]['start']+=.15;w[3]['end']+=.15
assert len(speech_ranges(w,20))==1,'Normal thinking pause was chopped'
print('PASS: stutter chains, fillers, abandoned starts, emphasis and natural pauses')

from automatic_cut import select_ranges
t=[sentence('The reload animation looks really smooth.',1),sentence('The reload animation looks really smooth.',5)]
k,_,_=select_ranges(t,[],20)
assert all(b-a>.2 for a,b in k),'Removed take left a padding-only flash clip'
assert all(a>4 for a,b in k),'Earlier take or its tail survived'

# Real ASR alignment: dropping "get" manufactured a false "to to" stutter.
aligned={'words':[dict(text=' '+text,start=a,end=b) for text,a,b in
 [('trying',1,1.2),('to',1.2,1.4),('get',1.4,1.4),('to',1.4,1.6),('his',1.6,1.8),('teammate.',1.8,2)]]}
assert not clean_dialogue([aligned],5)[2]
from script_review import review_script
assert 'to get to' in review_script([aligned],[(.9,2.2)])[1]['script'][0]['text']
touching={'words':[dict(text=' '+text,start=a,end=b) for text,a,b in
 [('I',1,1.2),('I',1.2,1.4),('think',1.4,1.6),('so.',1.6,1.8)]]}
ranges,cuts,rows=clean_dialogue([touching],5)
assert rows[0]['end']==1.2,'Stutter tail was retained'
assert not any(a<1.2 and b>1 for a,b in ranges)
assert any(a<=1.2 and b>=1.4 for a,b in ranges),'Retained onset clipped'
