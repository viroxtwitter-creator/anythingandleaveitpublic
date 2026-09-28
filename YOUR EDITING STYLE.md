Updated: all three supplied projects are now included in [REFERENCE COMPARISON.md](REFERENCE%20COMPARISON.md). The detailed single-project findings below remain scoped to the first reference.

# Editing reference: Jordan

The recording determines the length. There is no runtime target and no quota for how much footage to remove.

The reference is "1st video example Rainbow 6 Siege.drp", paired with its original media and the finished "arctic unlock frost.mov" export. This profile records observed examples and editorial guidance; it is not a trained autonomous model.

## What the first project establishes

The direct base-track selections from the main Rainbow Six recording contain 37 continuous source selections after joining splits that do not skip any source frames. Their median length is 2.27 seconds, with a range of 1.05 to 8.20 seconds. They account for 100.65 seconds of the finished timeline. These figures exclude nested compositions and upper-track coverage, so they are not whole-video statistics.

This is substantially tighter picture selection than the first Arc Raiders draft. The practical lesson is to find the useful instant inside an action, while leaving enough context to understand it. It is not an instruction to cut mechanically every two seconds.

18 of those 37 selections have no transcribed words in the corresponding source microphone passage, accounting for 46.95 seconds of kept picture. Speech recognition can miss speech, and the finished timeline can use audio from elsewhere. Nevertheless, the selection evidence clearly rules out using microphone silence as the sole reason to discard gameplay.

The opening uses source moments out of order, and its first source moment appears again later. A short opening preview is consistent with this reference, when the footage supports it.

The project contains short contiguous source-frame splits that belong to visual treatment rather than new footage selection. These must be represented separately, or learning from timeline cut counts will produce excessive chopping.

Source audio has some edges that differ from direct base-picture edges. No continuous track-2 source-audio run was found spanning the measured main-recording picture boundaries. This analysis therefore does not establish a preference for J/L cuts; independent audio editing needs closer audiovisual inspection.

## Rules for the next automatic-edit prototype

- Let the useful material determine the final length.
- Select the strongest setup, demonstration, outcome and reaction moments.
- Compress waiting and travel within a sequence without losing cause and effect.
- Keep worthwhile gameplay when the mic is quiet.
- Use shorter picture selections where the action is already clear; allow explanations and payoffs more time when needed.
- Treat the reference's pace as context-dependent examples, not a fixed shot-length formula.
- Keep editable source handles and separate audio tracks.
- Evaluate selection and flow before attempting exact sound-effect placement.

## Adding references

Two or three more finished projects would help distinguish recurring preferences from choices specific to this one video. Put their DRP files in the Edit folder. A finished export for each is helpful for evaluating nested effects and sound timing. The original media can remain where it is: inspect paths stored in each DRP, then check whether those files are available. A DRP does not contain the original recording itself.

Prefer representative finished work, including a video with substantial quiet gameplay and one with more continuous commentary. References from Arc Raiders would help separate game-specific selection decisions from general pacing preferences.

## Evidence files

analysis/editing-style/reference-profile.json: measurements, scope and rules.
analysis/editing-style/source-selection-examples.csv: kept source ranges with word timing context.
analysis/editing-style/between-selection-gaps.json: intervening omitted source passages, labelled with their limited scope.
analysis/editing-style/tracks.json: extracted main-timeline track entries.
analysis/editing-preferences.json: no fixed target duration.

Validation: the extracted eight-selection section at timeline 00:57.38-01:19.05 matches the earlier live-Resolve check exactly, totalling 1,300 frames at 60 fps. This validates that reference section's mapping, not every nested or retimed item in the project.
