# Dialogue flow update

## Cutting-only revision

The shipped app now excludes captions, SFX, memes and motion modules. The interface and export API expose only retention cutting. Earlier effect scripts and exports are historical files, not active features.

The expanded reference audit covers 119 speech-bearing selections: 23 Rainbow Six, 69 Fortnite, 27 MW4. Evaluating start/end handles independently yields 16 eligible leads (median 0.075 seconds) and 89 eligible tails (median 0.24 seconds). 97 starts and 20 ends overlap ASR word intervals. These discrepancies prevent treating the nominal picture edges as precise acoustic edit boundaries. This supersedes the smaller paired-edge sample below.

The repeat detector now protects complete takes from later clearly unfinished attempts, requires more than a shared grammatical opener, and protects changed facts across separate phrases. Ten cached transcripts (3,925 words) passed interval and retained-onset invariants; dedicated regression tests cover stutters, chants, emphasis, changed facts and failed later takes. Those checks do not establish audiovisual quality.

The installed cutting-only build passed the actual app-to-Resolve workflow in twst4: 149 selections, 395.03 seconds, 11 cleanup decisions, no subtitles or Fusion comps. The longer result is not a claim of stronger retention: these changes favour preserving meaning and natural handles over removal counts. Listening and narrative evaluation remain necessary.

## Word-context correction

Zero-duration ASR words now remain in dialogue matching and the assembled script without inventing timestamps. A real "to get to" alignment had a zero-duration "get"; dropping it caused a false stutter removal. Regression coverage now protects that sentence. Contiguous stutter cuts reach the discarded word's end rather than leaving a fragment for the retained take's lead handle. Overlapping stutter alignments are preserved when a safe boundary cannot be established.

The `.app-word-context` packaged build passed an actual Resolve import: 57 selections, 140.4 seconds, four cleanup decisions and two script warnings. All four regression scripts and interval checks across 11 cached transcripts (4,473 words) passed. This does not certify perceptual or semantic quality; the script review remains rule-based.

## Earlier experiment (superseded measurements)

Measured all three supplied reference selection maps against available cached source-word timestamps. Eleven selections had at least three words and both handles between zero and 0.6 seconds: one Rainbow Six, five Fortnite, five MW4. Median picture-cut lead was 0.073 seconds; median tail was 0.323 seconds. These are nominal picture/source measurements, not verified acoustic edges or J/L-cut timings.

The new default leaves 0.075 seconds before a phrase, 0.12 seconds after an unfinished clause and 0.30 after a punctuated sentence. Within-phrase gaps up to 0.48 seconds remain connected. Nearby action detections bridge up to 0.35 seconds. There is no runtime or removal quota.

Added a word-level pass for repeated function words, short repeated starts, hesitation fillers and isolated grammatical starts abandoned before a long pause. Retake exclusion edges stop before the retained speech onset. Overlapping detector evidence is deduplicated. Expressive repetitions and chants have regression coverage.

The cached Fortnite comparison retains 15 retake decisions. Duration increases from 382.63 to 391.61 seconds because the new handles preserve breathing room. This is a decision audit, not proof of finished editorial quality. ASR can miss stutters, place words incorrectly or invent punctuation; arbitrary incomplete thoughts and semantic paraphrases still need audiovisual review.
