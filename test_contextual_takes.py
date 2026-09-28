"""Real-model regression tests: no API and no mocked editorial scores."""
from contextual_takes import review
from cut_integrity import protect_words, validate


def fixture(texts, starts=None):
    transcript, ranges = [], []
    starts = starts or [1+i*12 for i in range(len(texts))]
    for text, start in zip(texts, starts):
        words = [dict(text=' '+t, start=start+i*.2, end=start+i*.2+.16, probability=.95)
                 for i,t in enumerate(text.split())]
        transcript.append(dict(words=words))
        ranges.append([start-.075, words[-1]['end']+.12])
    return transcript, ranges


def check(name, texts, removed, starts=None, events=()):
    transcript, ranges = fixture(texts, starts)
    result, report = review(transcript, ranges, events)
    assert len(report['changes']) == removed, (name,report)
    # Every replacement must still be selected; a retake chain cannot erase all.
    for change in report['changes']:
        assert any(a <= change['kept_source_start'] < b for a,b in result), (name, report)
    again, second = review(transcript,result,events)
    assert again == result and not second['changes'], (name,'non-idempotent',second)
    print('PASS:',name,flush=True)
    return transcript, ranges, result, report


check('paraphrased aim setting', ['This setting makes aiming much easier for beginners.',
    'This setting makes it much easier for beginners to aim.'],1)
check('uncertain community paraphrase is not forced', ["And there's a huge player base using it.",
    "And we have a huge community using it right now because it's one of the most trusted cheats on the entire market."],0)
check('changed quantity', ['This weapon has twelve bullets remaining in the magazine.',
    'This weapon has thirteen bullets remaining in the magazine.'],0)
check('changed polarity', ['This option does not work with this game.',
    'This option does work with this game.'],0)
check('contradictory opinion', ['I think this weapon is really good for beginners.',
    'I think this weapon is really bad for beginners.'],0)
check('different feature same subject', ['This setting makes aiming much easier for beginners.',
    'This setting makes the graphics much brighter for beginners.'],0)
check('additional information', ['This weapon is accurate at long distances.',
    'This weapon also reloads quickly during combat.'],0)
check('callback after scene', ['This setting makes aiming much easier for beginners.',
    'This setting makes it much easier for beginners to aim.'],0,starts=[1,100])
check('action protected', ['This setting makes aiming much easier for beginners.',
    'This setting makes it much easier for beginners to aim.'],0,events=[(0,30)])
check('three alternative takes', ['This setting makes aiming much easier for beginners.',
    'This setting makes it much easier for beginners to aim.',
    'Aiming is much easier for beginners with this setting.'],2)
# The repeated sentence shares a clip with a distinct useful sentence.
t,r=fixture(['This setting makes aiming much easier for beginners. The reload takes three seconds.',
             'This setting makes it much easier for beginners to aim.'])
k,report=review(t,r)
assert len(report['changes'])==1,report
reload_word=next(w for w in t[0]['words'] if 'reload' in w['text'])
assert any(a <= reload_word['start'] < b for a,b in k),'Unique explanation deleted'
print('PASS: delete sentence inside clip, preserve unique following information',flush=True)
# Quiet consonants at either end are restored; explicitly deleted attempts stay out.
t,r=fixture(['Keep every quiet word intact.'])
words=t[0]['words']
k,c=protect_words([[1.04,words[-1]['end']-.03]],t,[],20,60)
assert k[0][0] <= 1 and k[0][1] >= words[-1]['end']
protected,_=protect_words([[1.2,2]],t,[(0,1.2)],20,60)
assert protected[0][0]>=1.2
try:validate([[2,3],[1,2]],10,60)
except ValueError:pass
else:raise AssertionError('Overlapping or reversed export accepted')
print('PASS: word handles, deletion barriers, invalid export rejection',flush=True)
