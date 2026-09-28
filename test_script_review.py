from script_review import review_script
def seg(text,start):
 return {'words':[{'text':' '+t,'start':start+i*.2,'end':start+i*.2+.15} for i,t in enumerate(text.split())]}
a=seg('The sniper reload feels slow.',1);b=seg('The sniper reload feels slow.',4)
kept=[[.925,2.19],[3.925,5.19]]
r,report=review_script([a,b],kept)
assert len(r)==1 and len(report['changes'])==1
assert r==review_script([a,b],r)[0],'Review must be idempotent'
r,report=review_script([a,b],kept,[[1,2]])
assert r==kept,'Gameplay must not be deleted from text alone'
r,report=review_script([a,seg('The sniper reload feels fast.',4)],kept)
assert r==kept,'Different meaning must survive'
r,report=review_script([seg('I want to',1)],[[.925,1.8]])
assert len(report['flags'])==1 and r==[[.925,1.8]]
r,report=review_script([seg('Look here',1)],[[1.08,1.4]])
assert report['flags'],'Partial word must be reported'
print('PASS: assembled-script repeats, gameplay protection, meaning changes and suspicious joins')
t=[seg('I want to',1),seg('try another route.',1.8)]
r,report=review_script(t,[[.925,1.65],[1.725,2.6]])
assert not any('unfinished' in reason for f in report['flags'] for reason in f['reasons']),'Continuous sentence flagged as abandoned'
