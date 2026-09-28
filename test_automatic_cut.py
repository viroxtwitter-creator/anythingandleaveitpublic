from automatic_cut import select_ranges
from dialogue_cut import clean_dialogue

def sentence(text,start):
 return {'words':[dict(text=' '+t,start=start+i*.2,end=start+i*.2+.15) for i,t in enumerate(text.split())]}
t=[sentence('This is a complete repeated sentence.',10),sentence('This is a complete repeated sentence.',15)]
k,s,d=select_ranges(t,[[9,18]],30)
assert len(d)==1 and d[0]['kept_start']==15
assert not any(a<11.15 and b>10 for a,b in k),'Combat restored a retake'
assert any(a<=15 and b>=16.15 for a,b in k)
k,_,_=select_ranges([sentence('Hello there.',10)],[],100)
assert len(k)==1 and abs(k[0][0]-9.925)<.001 and abs(k[0][1]-10.59)<.001
assert select_ranges([],[],100)[0]==[], 'Silent menus cannot be selected without approved combat'
for first,second in [('We have 12 bullets left now.','We have 13 bullets left now.'),('This setting is working perfectly now.','This setting is not working perfectly now.')]:
 assert not clean_dialogue([sentence(first,10),sentence(second,15)],30)[2]
assert not clean_dialogue([sentence('Oh my god!',10),sentence('Oh my god!',15)],30)[2]
short=clean_dialogue([sentence('This is insane.',10),sentence('This is insane.',12)],30)[2]
assert len(short)==1 and short[0]['kept_start']==12
partial=clean_dialogue([sentence('I am gonna try to snipe.',10),sentence('I am gonna try to snipe this guy.',12)],30)[2]
assert len(partial)==1 and partial[0]['kept_start']==12
reworded=clean_dialogue([sentence('Because of combat mode if I press B it goes away.',10),sentence('It comes with combat mode so if I press B it goes away.',13)],30)[2]
assert len(reworded)==1 and reworded[0]['kept_start']==13
stem=clean_dialogue([sentence('I think I will send the inputs.',10),sentence('I think I will turn the smoothing down.',12)],30)[2]
assert not stem,'Different ideas sharing a grammatical opening must survive'
mid=clean_dialogue([sentence('I am not gonna lie I dont think it is an issue with crush I dont think that is an issue with crush.',10)],30)[2]
assert len(mid)==1 and mid[0]['earlier'].lower().startswith('i dont think')
number_restart=clean_dialogue([sentence('We have 15 alright we have 14 kills right now.',10)],30)[2]
assert len(number_restart)==1 and '15' in number_restart[0]['earlier']
far=clean_dialogue([sentence('This exact longer explanation should only appear one time.',10),sentence('This exact longer explanation should only appear one time.',100)],130)[2]
assert len(far)==1 and far[0]['kept_start']==100 and 'later in recording' in far[0]['reason']
assert not clean_dialogue([sentence('This exact longer explanation should only appear one time.',10),sentence('This exact longer explanation should only appear one time.',220)],250)[2]
print('PASS: tight padding, partial/reworded/internal restarts, short repeats, distant callback and changed-fact safeguards.')
