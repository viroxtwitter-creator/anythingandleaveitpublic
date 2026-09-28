"""Export an AI-authored edit plan. Selection is performed by Codex, not this script.

This prototype deliberately keeps editorial decisions separate from the reliable
Resolve import path. It does not pretend a reusable autonomous selector exists yet.
"""
import argparse
import json
import subprocess
from pathlib import Path

from app_paths import ROOT, add_dependencies
add_dependencies()
import av
from review_core import export_review, read_transcript, save_json
from review_media import audio_sidecars


def prepare(plan_path, folder):
    plan = json.loads(Path(plan_path).read_text(encoding='utf-8'))
    source = Path(plan['source'])
    with av.open(str(source)) as container:
        duration = container.duration / av.time_base
        fps = float(container.streams.video[0].base_rate)
        stream_names = [s.metadata.get('name', f'Audio {i+1}')
                        for i, s in enumerate(container.streams.audio)]
    if abs(duration-plan['source_duration']) > .1:
        raise ValueError('The recording duration no longer matches the edit plan.')
    ranges = [[r['start'], r['end']] for r in plan['clips']]
    # Validate before preparing any large assets or making changes in Resolve.
    if not ranges or not all(0 <= a < b <= duration for a, b in ranges):
        raise ValueError('The plan contains an invalid source range.')
    transcript = read_transcript(ROOT / plan['transcript'])
    if transcript is None:
        raise ValueError('The transcript used to check dialogue is missing.')
    words = [w for segment in transcript for w in segment['words']]
    violations = []
    for i, (a,b) in enumerate(ranges):
        for boundary in (a,b):
            for w in words:
                if w.get('probability', 0) >= .5 and w['start']+.035 < boundary < w['end']-.035:
                    violations.append(dict(clip=i+1, boundary=boundary, word=w))
    if violations:
        raise ValueError('A cut splits a transcribed word: '+json.dumps(violations))
    audio = audio_sidecars(source, lambda s: print(s, flush=True))
    note = ('AI-selected rough-cut experiment using microphone word timing and sampled gameplay frames. '
            'A short reaction is repeated as a cold open. Review story continuity and audible joins. '
            'Original video and separate, packet-copied audio; no added sound effects or finished mix.')
    export_review(folder, source, duration, fps, [], {}, audio=audio,
                  keep_ranges=ranges, timeline_prefix=plan['timeline_prefix'], draft_note=note)
    folder = Path(folder)
    script_path = folder/'create_resolve_draft.lua'
    script = script_path.read_text(encoding='utf-8')
    position = 0
    for i, clip in enumerate(plan['clips']):
        frames = round(clip['end']*fps)-round(clip['start']*fps)
        title = clip['label']
        explanation = f"Source {clip['start']:.2f}-{clip['end']:.2f}s. {clip['reason']}"
        if position > 0:
            script += f'\ntimeline:AddMarker({position}, "Blue", {json.dumps(title)}, {json.dumps(explanation)}, 1)\n'
        position += frames
    script += '\nprint("AUTO_DRAFT_FRAMES "..(timeline:GetEndFrame()-timeline:GetStartFrame()))\n'
    script += 'print("AUTO_DRAFT_VIDEO_CLIPS "..#timeline:GetItemListInTrack("video",1))\n'
    script += 'for i=1,#audioClips do print("AUTO_DRAFT_AUDIO "..i.." "..#timeline:GetItemListInTrack("audio",i)) end\n'
    script += 'timeline:SetCurrentTimecode(timeline:GetStartTimecode())\n'
    script_path.write_text(script, encoding='utf-8')
    save_json(folder/'edit-plan.json', plan)
    report = dict(source=str(source), source_duration=duration,
                  draft_duration=position/fps, fps=fps, clips=len(ranges),
                  audio_tracks=stream_names, transcript_word_splits=violations,
                  selection_method='Codex interpretation of cached transcript and sampled frames; not a standalone automatic selector',
                  listening_review_completed=False)
    save_json(folder/'checks.json', report)
    print(json.dumps(report, indent=2), flush=True)
    return script_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('plan', type=Path)
    parser.add_argument('--import-resolve', action='store_true')
    args = parser.parse_args()
    folder = ROOT/'exports'/'Arc Raiders auto rough cut'
    script = prepare(args.plan, folder)
    if args.import_resolve:
        result = subprocess.run([r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fuscript.exe',
                                 '-l','lua',str(script)], capture_output=True, text=True,
                                timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
        output = result.stdout+'\n'+result.stderr
        (folder/'resolve-output.txt').write_text(output, encoding='utf-8')
        print(output)
        if result.returncode != 0 or 'CUT_REVIEW_OK ' not in output or 'AUTO_DRAFT_AUDIO 2 ' not in output:
            raise RuntimeError('Resolve import did not pass all checks. Inspect resolve-output.txt before retrying.')


if __name__ == '__main__':
    main()
