"""Final source-coordinate and word-edge invariants, after all editorial passes."""
import math


def protect_words(ranges, transcript, exclusions, duration, fps):
    words = [w for s in transcript for w in s['words'] if 0 < w['end'] - w['start'] < 3]
    rejected=lambda w:any(x-1e-6 <= (w['start'] + w['end']) / 2 <= y+1e-6 for x, y in exclusions)
    allowed = [w for w in words if not rejected(w)]
    changes, result = [], []
    for a, b in ranges:
        # A waveform edge can pass the midpoint of a quiet word. Any meaningful
        # surviving audio overlap warrants protecting that word, unless the word
        # belongs to an explicit editorial deletion (filtered above).
        selected = [w for w in allowed if min(b,w['end'])-max(a,w['start'])>.015]
        left, right = a, b
        hard_left,hard_right=0,duration
        if selected:
            left = min(left, selected[0]['start'] - .075)
            right = max(right, selected[-1]['end'] + .12)
        # Do not leave the audible tail/head of a deliberately removed word.
        for w in words:
            if rejected(w):
                if w['start'] < left < w['end']:
                    left=max(left,w['end']);hard_left=max(hard_left,w['end'])
                if w['start'] < right < w['end']:
                    right=min(right,w['start']);hard_right=min(hard_right,w['start'])
        for x, y in exclusions:
            if y <= a + .001:
                left = max(left, y)
            if x >= b - .001:
                right = min(right, x)
        left = max(0, math.floor(left * fps + 1e-6) / fps)
        right = min(duration, math.ceil(right * fps - 1e-6) / fps)
        left=max(left,math.ceil(hard_left*fps-1e-6)/fps)
        right=min(right,math.floor(hard_right*fps+1e-6)/fps)
        # Frame quantization must not cross an explicit deletion barrier.
        for x, y in exclusions:
            if y <= a + .001:
                left = max(left, math.ceil(y * fps - 1e-6) / fps)
            if x >= b - .001:
                right = min(right, math.floor(x * fps + 1e-6) / fps)
        if right <= left:
            continue
        if abs(left-a) > .001 or abs(right-b) > .001:
            changes.append(dict(before=[a,b], after=[left,right], reason='Protect retained word edges and quantize to source frames'))
        if result and left <= result[-1][1]:
            result[-1][1] = max(result[-1][1], right)
        else:
            result.append([left, right])
    validate(result, duration, fps)
    return result, changes


def validate(ranges, duration, fps):
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError('Invalid source frame rate')
    previous = 0
    for a, b in ranges:
        if not all(math.isfinite(v) for v in (a,b)) or not 0 <= a < b <= duration + .001 or a < previous - .001:
            raise ValueError('Invalid or overlapping cut boundaries; export stopped')
        if round(b * fps) <= round(a * fps):
            raise ValueError('Empty frame range; export stopped')
        previous = b
