from review_core import *
from cut_review import DEFAULT_SOURCE
from review_media import audio_sidecars
import subprocess
ref=reference_rows()
kept=[[r['start'],r['end']] for r in ref]
audio=audio_sidecars(DEFAULT_SOURCE,lambda s:print(s,flush=True))
folder=export_review(ROOT/'analysis/resolve-validation',DEFAULT_SOURCE,1477.05,60,[],{},complement(kept,0,1477.05),audio)
p=folder/'create_resolve_draft.lua'
s=p.read_text().replace('Cut Review draft ', 'Cut Review reference sample ')
s+='''
print("VIDEO_TRACKS "..timeline:GetTrackCount("video"))
print("AUDIO_TRACKS "..timeline:GetTrackCount("audio"))
for i=1,timeline:GetTrackCount("audio") do print("AUDIO_ITEMS "..i.." "..#timeline:GetItemListInTrack("audio",i)) end
print("DURATION_FRAMES "..(timeline:GetEndFrame()-timeline:GetStartFrame()))
'''
p.write_text(s)
r=subprocess.run([r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fuscript.exe','-l','lua',str(p)],capture_output=True,text=True,timeout=45)
print(r.stdout);print(r.stderr)
(folder/'validation-output.txt').write_text(r.stdout+'\n'+r.stderr)
assert 'CUT_REVIEW_OK' in r.stdout
