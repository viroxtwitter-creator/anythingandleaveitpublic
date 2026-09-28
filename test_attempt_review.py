from script_review import review_script

def run(lines,events=()):
    t=[];k=[]
    for i,line in enumerate(lines):
        start=1+i*10
        words=[dict(text=' '+x,start=start+j*.2,end=start+j*.2+.15) for j,x in enumerate(line.split())]
        t.append(dict(words=words));k.append((start-.07,words[-1]['end']+.12))
    result,report=review_script(t,k,events)
    again,report2=review_script(t,result,events)
    assert again==result and not report2['changes'],'Review must settle in one run'
    return result,report
k,r=run(["It is great for ranked games as it's su-", "as it's super simple and all you need."])
assert r['changes'] and r['script'][0]['text']=='It is great for ranked games'
k,r=run(["It is great for ranked games as it's su -", "as it's super simple and all you need."])
assert r['changes'] and r['script'][0]['text']=='It is great for ranked games'
k,r=run(['This works extremely-', "It is extremely good for ranked games."])
assert len(k)==1
for lines in [ ['I like this weapon-', 'The map is really dark.'],
               ['We have 12 bullets left.', 'We have 13 bullets left.'],
               ['This is not working-', 'This is working perfectly now.'],
               ['Go go go!', 'Go go go!'] ]:
    assert not run(lines)[1]['changes'],lines
assert not run(['This works extremely-', 'It is extremely good for ranked games.'],[(0,5)])[1]['changes']
print('PASS: word-level cutoff repair, abandoned clauses, meaning protection, action protection, idempotence')
