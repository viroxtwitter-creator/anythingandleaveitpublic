# clipemo.com — contextual retention update

This is an in-place update of the existing retention-only app. No captions,
motion graphics, music or sound effects have been reintroduced.

## What changes

- Sentence spans are reconstructed from word timestamps, independently of clip
  boundaries. One repeated sentence can be removed without deleting another
  useful sentence in the same clip.
- The local editorial reviewer proposes a take choice, then separately audits
  information lost by the proposed deletion. Disagreement keeps both. It cannot
  invent text or times.
- Directional entailment checks distinguish a fuller take from a short summary.
  Explicit number/polarity changes, questions, additional points, uncertain ASR
  and protected action remain guarded.
- A surviving replacement is required for each deletion. Conflicting retake
  chains cannot remove both the rejected take and its replacement.
- Retained words receive a final boundary check before and after script review.
  Deleted takes are hard barriers. Exports reject reversed/overlapping ranges.
- Quiet leading words clipped past their midpoint are protected too. Partial
  remnants of rejected words are trimmed rather than restored at a join.
- Repeated stranded connectors are removed at the word level. Collapsed ASR
  passages with multiple zero-duration words and no confident speech anchor are
  rejected; ordinary individual zero-duration words remain valid.
- Each run still extracts and transcribes afresh. Run ID, pipeline version,
  frame-range signature and comparison against the previous export are recorded.
  An identical recomputed result is reported honestly, not presented as a changed cut.

## Local models and privacy

Speech remains faster-whisper small.en. Candidate retrieval uses MiniLM. The
meaning check uses full-precision DeBERTa; the compressed variant was rejected
after unstable candidate scores during testing. Qwen3-4B Q4_K_M supplies the
editorial judgments. Its llama.cpp process is bound to authenticated loopback,
has no browser UI, and is terminated when the review ends. Recordings and
transcripts are not uploaded. No paid inference API is used.

Models live in `.model-cache`, shared by the application builds. The new
editorial engine requires its local model/runtime files; a missing engine stops
the run rather than silently pretending that semantic review happened.

Sources: [Qwen3-4B GGUF](https://huggingface.co/Qwen/Qwen3-4B-GGUF),
[DeBERTa ONNX](https://huggingface.co/Xenova/nli-deberta-v3-small),
[llama.cpp server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server).
The Windows Vulkan runtime is pinned to b10809 and its download SHA-256 was
checked against the official release metadata.
Qwen weights are pinned by downloaded revision
`bc640142c66e1fdd12af0bd68f40445458f3869b`; the local file's SHA-256 is
`7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`.

## Audit trail and limits

Each export includes `automatic-plan.json`, `script-review.json` and
`selected-script.txt`. They distinguish rule repairs, model judgments and the
previous user-approved introduction preference. The reports record rejected
candidates as well as removals.
An `entailment` value is the separate NLI model's score, not a percentage chance
that an edit is correct. Editorial approvals and the saved user preference are
labelled separately; they must not be described as high-confidence NLI results.

This is still an automatic rough cut, not guaranteed human editorial judgment.
Transcription errors can hide stutters or alter meaning; action safeguards can
retain a repeat. Tests verify known examples and counterexamples, not every
possible recording. Listen to the resulting joins before publishing.
In the Rainbow Six test recording, the repeated config explanations near source
6:11 and 6:36 remain an ambiguous case: the transcript differs (including
"unbalanced" versus "un-banned") and the action safeguard blocks automatic
semantic removal. Zero word-overlap warnings do not mean zero editorial issues.

`audit_retention_update.py` is a development replay of saved evidence, explicitly
labelled as such. It is not used by the application and does not replace the
fresh-analysis path. `verify_automatic_app.py` tests the actual packaged button
through a fresh recording analysis and Resolve export.

## Verified release — 9 September 2026

Installed build: `.app-retention-v2/CutReview/CutReview.exe`.
The two normal shortcuts and `START CUT REVIEW.cmd` point to this build.
The previous `.app-semantic` working build remains available for rollback.

The actual packaged app freshly processed the 20:45 Rainbow Six recording and
exported 38 clips / 184.25 seconds. Resolve independently reported that the new
18-36-52 timeline was active, with 11,055 frames at 60 fps. Run ID:
`8b8a1d65bf1446f2a89940c316bacd7a`.

Confirmed removals include the short community/player-base retake, the abandoned
in-game opening, and the dangling repeated `But`, alongside the existing repaired
introductions and cut-off sentence tail. The full transcript and judgment records
are in `exports/Retention cut 20260909-183652-83400`.

Regression checks covered paraphrases, changed quantities/polarity, distinct
details, fuller earlier takes, retake chains, word/clip boundaries, protected
gameplay, fresh analysis, export validation, and UI states. An additional 1,000
randomized fractional-frame deletion-barrier cases passed. These are technical
and example-based checks, not a claim that the edit has been fully listened to
or is editorially perfect.

## Hidden-ASR-retake repair — 9 September 2026

The repeat reported at old timeline timecode `01:00:04:32` was upstream of the
edit rules. Source `36.67–43.37` contained an abandoned introduction followed by
its complete replacement. Whole-window recognition emitted only one sentence,
with the word `that` stretched across 2.98 seconds. Short acoustic windows
recovered both takes, including the abandoned `that is-` ending.

`speech_recheck.py` now checks unusually long word timestamps for an internal
acoustic pause, retranscribes both sides locally, and accepts replacements only
when the separate windows recover a substantial repeated phrase with sufficient
confidence and coverage of the original words. Normal pauses without additional
repeated wording leave the original transcript unchanged. This is a general
audio-evidence check, not an exact-phrase deletion rule.

Raw transcripts remain unchanged for audit. Each run writes `word-rechecks-*`
and includes `transcript_rechecks` in its export plan. `test_speech_recheck.py`
tests recovery and ordinary-pause counterexamples; `verify_flagged_retakes.py`
checks the final selected source ranges for this specific reported regression.
The check targets one known ASR failure mode; it does not guarantee that every
possible recognition omission or editorial repeat will be found.

Verified and installed `.app-hidden-retakes-20260909/CutReview/CutReview.exe`.
Fresh packaged run `980081bb10ce4f4094cd55fa57835773` created the `19-07-16`
Resolve timeline (38 clips, 181.033 seconds). The targeted regression passed:
the old source `36.583–43.617` clip is now `39.800–43.617`. Resolve independently
confirmed the same 2,388-frame source offset and 229-frame duration on video and
both audio tracks. The new timeline is positioned at `01:00:04:32` for audition.
Both application shortcuts and `START CUT REVIEW.cmd` point to this tested build;
the prior `.app-retention-v2` build is preserved.
