"""Reject collapsed, low-confidence ASR text without deleting valid zero-time words."""


def clean(transcript):
    result,warnings=[],[]
    for segment in transcript:
        words=segment['words']
        collapsed=[w for w in words if w['end']-w['start']<=.001]
        anchors=[w for w in words if w['end']-w['start']>.001]
        impossible=(len(collapsed)>=4 and len(collapsed)/max(1,len(words))>=.75 and
            segment['end']-segment['start']<.8 and
            (not anchors or max(w.get('probability',1) for w in anchors)<.1))
        if impossible:
            warnings.append(dict(source_start=segment['start'],source_end=segment['end'],
                text=segment.get('text',''),reason='Unreliable ASR: several words collapsed to one timestamp with no confident speech anchor'))
        else:result.append(segment)
    return result,warnings
