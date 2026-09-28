from pathlib import Path
from review_core import export_review
from review_media import audio_sidecars
from automatic_captions import lua_for_captions
source=r'T:\Fortnite\Fortnite 2026.09.05 - 20.55.01.01.mp4'
f=Path('exports/Caption integration test')
export_review(f,source,1254.96,60,[],{},audio=audio_sidecars(source),keep_ranges=[[55,68]],timeline_prefix='CAPTION TEST - ')
p=f/'create_resolve_draft.lua';s=p.read_text(encoding='utf-8');s=s.replace('assert(project, "Open a project first.")','assert(project and project:GetName()=="test2", "Caption testing is restricted to test2")')
s+=lua_for_captions(1)
p.write_text(s,encoding='utf-8')
print(p.resolve())
