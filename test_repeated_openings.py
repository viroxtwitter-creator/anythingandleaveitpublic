from script_review import review_script

def check(a,b,expected):
    def phrase(text,start):return dict(words=[dict(text=' '+t,start=start+i*.15,end=start+i*.15+.12) for i,t in enumerate(text.split())])
    t=[phrase(a,1),phrase(b,6)]
    ranges=[(.9,t[0]['words'][-1]['end']+.1),(5.9,t[1]['words'][-1]['end']+.1)]
    k,r=review_script(t,ranges)
    assert len(r['changes'])==expected,(a,b,r)
    return k,r
check("Alright guys we're in-game and of course", "Alright guys we're in-game and we're starting off with legit.",1)
_,r=check('This is an insanely clean and simple cheat that most of the user base uses.', 'This is an insanely clean and simple cheat,',1)
assert r['changes'][0]['text'].endswith('cheat,')
check('I think this weapon is great.', 'I think this weapon is awful.',0)
check('We have twelve bullets left.', 'We have thirteen bullets left.',0)
check('Go go go!', 'Go go go!',0)
print('PASS: abandoned opening, later failed repeat, different meanings and emphasis')
