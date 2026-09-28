"""Actual local instruction-model editorial regression; no cloud calls."""
from local_editor import Editor

CASES=[
    ('community',"And there's a huge player base using it.",
     "And we have a huge community using it right now because it's one of the most trusted cheats on the entire market.",'B'),
    ('abandoned introduction',"Alright guys, we're in game,",
     "Alright guys, we're in the shooting range, I'm gonna inject it with Inferno.",'both'),
    ('unique detail', 'This setting makes aiming much easier for beginners.',
     'This setting makes the graphics much brighter for beginners.','both'),
    ('contradiction', 'I think this weapon is really good for beginners.',
     'I think this weapon is really bad for beginners.','both'),
    ('numbers', 'This weapon has twelve bullets remaining in the magazine.',
     'This weapon has thirteen bullets remaining in the magazine.','both'),
    ('fuller earlier', 'The setting makes aiming easier and also reduces recoil.',
     'This setting makes aiming easier.','A'),
]

if __name__=='__main__':
    with Editor() as editor:
        for name,a,b,expected in CASES:
            result=editor.verify(a,b)
            print(name,result,flush=True)
            assert result['keep']==expected,(name,result)
    assert editor.process.poll() is not None,'Model process leaked after review'
    print('PASS: local model choices, information-loss verification and engine cleanup',flush=True)
