from semantic_review import review

def check(a,b,expected,gap=2,events=()):
    rows=[];ranges=[]
    for text,start in [(a,1),(b,7+gap)]:
        words=[dict(text=' '+t,start=start+i*.2,end=start+i*.2+.15) for i,t in enumerate(text.split())]
        end=words[-1]['end']+.1
        rows.append(dict(text=text,words=words,source_start=start-.05,source_end=end));ranges.append((start-.05,end))
    k,c,r=review(rows,ranges,events)
    assert len(c)==expected,(a,b,c,r)
    return c
check('This setting makes aiming much easier for beginners.', 'This setting makes it much easier for beginners to aim.',1)
check('This weapon has twelve bullets remaining in the magazine.', 'This weapon has thirteen bullets remaining in the magazine.',0)
check('I think this weapon is really good for beginners.', 'I think this weapon is really bad for beginners.',0)
check('This option does not work with this game.', 'This option does work with this game.',0)
check('This setting makes aiming much easier for beginners.', 'This setting makes it much easier for beginners to aim.',0,gap=90)
check('This setting makes aiming much easier for beginners.', 'This setting makes it much easier for beginners to aim.',0,events=[(0,20)])
check('This is an extremely well-known cheat and it performs insanely good in-game.', 'This is an insanely clean and simple cheat that most of the user base uses.',1)
print('PASS: real local model paraphrase, user-approved alternatives, numbers, polarity, callbacks and gameplay')
