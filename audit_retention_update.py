"""Development-only replay: uses saved evidence, never pretends to be fresh ASR."""
import json
from pathlib import Path
from automatic_cut import select_ranges
from action_sequences import action_sequences
from speech_edges import refine_edges
from pause_cleanup import clean_pauses
from cut_integrity import protect_words
from script_review import review_script, readable
from review_core import save_json


def main():
    baseline=json.loads(Path('analysis/last-automatic-cut.json').read_text(encoding='utf-8'))
    cache=next(Path('analysis').glob('*transcript*'+baseline['analysis_run_id']+'*.json'))
    transcript=json.loads(cache.read_text(encoding='utf-8'))
    from transcript_quality import clean
    transcript,warnings=clean(transcript)
    duration,fps=baseline['duration'],baseline['fps']
    kept,speech,duplicates=select_ranges(transcript,baseline['raw_action'],duration)
    events=action_sequences(baseline['raw_action'],speech,duration)
    exclusions=[(d['start'],d['end']) for d in duplicates]
    kept,_=refine_edges(kept,cache.with_suffix('.wav'),events,exclusions)
    kept,_=clean_pauses(kept,cache.with_suffix('.wav'),events)
    kept,edges=protect_words(kept,transcript,exclusions,duration,fps)
    kept,report=review_script(transcript,kept,events,semantic=True,progress=print)
    exclusions.extend((c['source_start'],c['source_end']) for c in report['changes'])
    kept,more=protect_words(kept,transcript,exclusions,duration,fps)
    _,final=review_script(transcript,kept,events,audit_only=True)
    report.update(script=final['script'],flags=final['flags'])
    output=dict(mode='Offline development replay, not a fresh analysis',baseline=baseline['analysis_run_id'],
        before=baseline['kept'],after=kept,script_review=report,edge_changes=edges+more,transcript_warnings=warnings)
    save_json('analysis/context-update-audit.json',output)
    Path('analysis/context-update-script.txt').write_text(readable(report),encoding='utf-8')
    print('BEFORE',len(baseline['kept']),sum(b-a for a,b in baseline['kept']))
    print('AFTER',len(kept),sum(b-a for a,b in kept))
    print('CHANGES',json.dumps(report['changes'],indent=2))
    print('EDGE REPAIRS',len(edges+more))


if __name__=='__main__':main()
