import json
from pathlib import Path
import automatic_cut as cut
from automatic_captions import lua_for_captions
from review_core import save_json
bridge=lua_for_captions(1)
start=bridge.index('local charPattern');end=bridge.index('\nguard()\nlocal enabled',start)
test=bridge[start:end]+'''\nassert(clean([[Hello, \"world\"!]])=='Hello world')
assert(clean([[don't... stop—now?!]])=='dont stopnow')
assert(clean('abcdefghijklmnop')=='abcdefghijklmno\\np')
assert(clean('one two three four five')=='one two three\\nfour five')
assert(clean('“hello” （world）')=='hello world')
print('CAPTION_TEXT_TESTS_PASS')
'''
Path('analysis/caption-text-tests.lua').write_text(test,encoding='utf-8')
original=cut.export_review
def guarded_export(*args,**kwargs):
 original(*args,**kwargs)
 p=Path(args[0])/'create_resolve_draft.lua';s=p.read_text(encoding='utf-8');s=s.replace('assert(project, "Open a project first.")','assert(project and project:GetName()=="test2", "Caption testing restricted to test2")');p.write_text(s,encoding='utf-8')
cut.export_review=guarded_export
result=dict(source=r'T:\Fortnite\Fortnite 2026.09.05 - 20.55.01.01.mp4',duration=1254.96,fps=60,kept=[[55,68]],microphone=1)
r=cut.send(result,print,add_sfx=True)
assert r['captions_enabled'] and r['captions_verified'] and r['caption_count']>0,r
save_json('analysis/caption-integration-result.json',r)
print('PASS: default caption pipeline,',r['caption_count'],'captions,',r['edited_duration'],'seconds; backup',r['folder'])
