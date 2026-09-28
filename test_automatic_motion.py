import json
from automatic_motion import choose_motion,lua_for_motion

r=json.load(open('analysis/last-automatic-cut.json'))
p=choose_motion(r)
assert p
assert all(x['duration_frames']>=60 for x in p)
assert all(b['anchor_frame']-a['anchor_frame']>=10*r['fps'] for a,b in zip(p,p[1:]))
assert any(x['phrase'] in ('oh my god','this is insane','thats insane','pretty insane','what is this') for x in p)
lua=lua_for_motion(p)
assert 'comp:BezierSpline()' in lua and 'curve:SetKeyFrames' in lua
assert 'AddTool("Transform"' in lua and 'transform.Size=curve' in lua
assert 'resolvefx.Transform' not in lua and 'transform.zoom' not in lua
assert '1.186' in lua and '1.367' in lua
assert 'AUTO_MOTION_VERIFIED '+str(len(p)) not in lua # count is printed by Lua at runtime
print('PASS:',len(p),'spaced transcript-confirmed Fusion zooms using the reference curve')
