"""Extract traceable editorial examples from a Resolve project, not a trained model.

Direct V1 source clips are measured separately from nested compositions and overlays.
Frame mappings are nominal: speed changes and nested timelines require further review.
"""
import collections
import csv
import hashlib
import json
import statistics
import struct
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from review_core import merge_intervals, read_transcript, save_json
from app_paths import ROOT

PROJECT=ROOT/'1st video example Rainbow 6 Siege.drp'
SEQUENCE='SeqContainer/fe39524a-9428-4ddd-a92f-5f87e2e33fbf.xml'
SOURCE=r"T:\Tom Clancy's Rainbow Six Siege\Tom Clancy's Rainbow Six Siege 2026.08.21 - 22.30.24.03.mp4"
FPS=60
START=216000


def frame_value(value):
    if not value:return None
    whole, _, fraction=value.partition('|')
    return int(whole)+(struct.unpack('<d',bytes.fromhex(fraction))[0] if fraction else 0)


def extract_tracks(root, kind):
    result=[]
    for index, wrapper in enumerate(root.find(kind+'TrackVec')):
        rows=[]
        for clip in wrapper.iter('Sm2Ti'+kind+'Clip'):
            start=frame_value(clip.findtext('Start'))
            duration=frame_value(clip.findtext('Duration'))
            source_in=clip.findtext('In')
            rows.append(dict(track=index+1, name=clip.findtext('Name'),
                start_frame=start-START, duration_frames=duration,
                source_in_frame=frame_value(source_in),source_in_raw=source_in,
                source=clip.findtext('MediaFilePath') or None,
                id=clip.attrib.get('DbId')))
        result.append(sorted(rows,key=lambda r:r['start_frame']))
    return result


def continuity_runs(rows):
    runs=[]
    for r in rows:
        if not r['source'] or r['source_in_frame'] is None:
            continue
        if runs and runs[-1]['source']==r['source'] and \
                runs[-1]['start_frame']+runs[-1]['duration_frames']==r['start_frame'] and \
                abs(runs[-1]['source_in_frame']+runs[-1]['duration_frames']-r['source_in_frame'])<1e-5:
            runs[-1]['duration_frames']+=r['duration_frames']
            runs[-1]['entry_ids'].append(r['id'])
        else:
            runs.append(dict(r,entry_ids=[r['id']]))
    return runs


def main():
    out=ROOT/'analysis'/'editing-style';out.mkdir(exist_ok=True)
    with zipfile.ZipFile(PROJECT) as z:
        root=ET.fromstring(re.sub(r'(<\/?\w+)::',r'\1__',z.read(SEQUENCE).decode()))
    video=extract_tracks(root,'Video');audio=extract_tracks(root,'Audio')
    runs=continuity_runs(video[0]);main_runs=[r for r in runs if r['source']==SOURCE]
    transcript=read_transcript(ROOT/'analysis'/'full-transcript.json')
    if transcript is None:raise ValueError('Missing valid reference transcript')
    words=[w for segment in transcript for w in segment['words'] if w['end']>w['start']]
    examples=[]
    for r in main_runs:
        a=r['source_in_frame']/FPS;b=a+r['duration_frames']/FPS
        selected=[w for w in words if w['end']>a and w['start']<b]
        voiced=merge_intervals([(w['start'],w['end']) for w in selected],a,b)
        examples.append(dict(timeline_start=r['start_frame']/FPS,source_start=a,source_end=b,
            duration=b-a,source_words=''.join(w['text'] for w in selected).strip(),
            source_speech_seconds=sum(y-x for x,y in voiced),
            no_transcribed_source_words=not selected,entry_ids=r['entry_ids']))
    video_boundaries={r['start_frame'] for r in main_runs}
    bridges=[]
    for r in continuity_runs(audio[1]):
        if r['source']!=SOURCE:continue
        crossed=sorted(t for t in video_boundaries if r['start_frame']<t<r['start_frame']+r['duration_frames'])
        if crossed:
            bridges.append(dict(audio_timeline_start=r['start_frame']/FPS,
                audio_timeline_end=(r['start_frame']+r['duration_frames'])/FPS,
                picture_boundaries=[t/FPS for t in crossed],entry_ids=r['entry_ids']))
    durations=[r['duration_frames']/FPS for r in main_runs]
    quiet=[r for r in examples if r['no_transcribed_source_words']]
    gaps=[]
    for left,right in zip(examples,examples[1:]):
        a=left['source_end'];b=right['source_start']
        if b>a:
            gaps.append(dict(source_start=a,source_end=b,duration=b-a,
                between_timeline_selections=[left['timeline_start'],right['timeline_start']],
                source_words=''.join(w['text'] for w in words if w['end']>a and w['start']<b).strip(),
                label='omitted between these direct V1 selections; may appear in other tracks or nested clips'))
    video_edges={r['start_frame'] for r in video[0] if r['source']==SOURCE}
    video_edges.update(r['start_frame']+r['duration_frames'] for r in video[0] if r['source']==SOURCE)
    independent_audio_edges=sum(t not in video_edges for r in audio[1] if r['source']==SOURCE
        for t in (r['start_frame'],r['start_frame']+r['duration_frames']))
    sfx=collections.Counter(r['name'] for track in audio[2:5] for r in track)
    profile=dict(schema_version=1, status='reference evidence, not trained automatic selection',
        reference=dict(project=str(PROJECT),sha256=hashlib.sha256(PROJECT.read_bytes()).hexdigest(),
            sequence=SEQUENCE,source=SOURCE,fps=FPS,timeline_start_frame=START),
        user_preferences=dict(target_duration_seconds=None,length_policy='Keep worthwhile material; duration follows content.',
            workflow='Full recording to an editable Resolve cut',reference_style=True),
        measurements=dict(base_track_entries=len(video[0]),direct_source_entries=sum(bool(r['source']) for r in video[0]),
            direct_source_continuity_runs=len(runs),
            main_recording_entries=sum(r['source']==SOURCE for r in video[0]),
            main_recording_continuity_runs=len(main_runs),
            main_run_duration_min=min(durations),main_run_duration_median=statistics.median(durations),
            main_run_duration_max=max(durations),main_run_duration_total=sum(durations),
            runs_with_no_transcribed_source_words=len(quiet),
            seconds_in_runs_with_no_transcribed_source_words=sum(r['duration'] for r in quiet),
            audio_track_2_runs_crossing_picture_boundaries=len(bridges),
            audio_track_2_edges_not_matching_direct_source_video_edges=independent_audio_edges,
            common_effect_assets=sfx.most_common(8)),
        policies=[
            'No target runtime or required percentage of footage removed.',
            'Learn which moments are selected, not merely how often timeline entries split.',
            'Preserve important gameplay even when the source microphone is quiet.',
            'Use complete setup/action/payoff beats; remove travel and waits inside them where context survives.',
            'Treat the observed shot durations as examples, not a global cut-every-N-seconds rule.',
            'Allow dialogue to bridge picture cuts when continuity requires it; always preserve source sync.',
            'Use the same source moment again for a teaser only when editorially useful.',
            'Keep audio tracks independent and keep the original media available for revisions.'
        ],
        limitations=[
            'One finished example cannot establish a reliable personal style model or viewer retention performance.',
            'Statistics cover direct V1 clips; nested compound clips, upper-track coverage and speed changes are not flattened.',
            'Contiguous source frames are grouped for content-selection analysis; their treatment changes may still matter visually.',
            'Source-word absence does not mean the final edit contains no dialogue; voice can come from another source or time.',
            'Audio track 2 is measured structurally; audible mix and J/L-cut intent require listening review.',
            'Sound-effect filenames and placements are evidence, not a finished sound-design automation rule.'
        ])
    save_json(out/'reference-profile.json',profile)
    save_json(out/'source-selection-examples.json',examples)
    save_json(out/'between-selection-gaps.json',gaps)
    save_json(out/'audio-picture-bridges.json',bridges)
    save_json(out/'tracks.json',dict(video=video,audio=audio))
    with (out/'source-selection-examples.csv').open('w',newline='',encoding='utf-8-sig') as f:
        cols=[k for k in examples[0] if k!='entry_ids'];w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader();w.writerows({k:r[k] for k in cols} for r in examples)
    save_json(ROOT/'analysis'/'editing-preferences.json',profile['user_preferences'])
    print(json.dumps(profile['measurements'],indent=2))


if __name__=='__main__':main()
