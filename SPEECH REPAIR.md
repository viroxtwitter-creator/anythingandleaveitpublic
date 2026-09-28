# Speech and action repair

The local speech model now prefers `.model-cache/speech-small.en` (faster-whisper small.en), with beam size 5. Existing model assets remain as a fallback. Every new user run still performs fresh analysis; no footage is uploaded. The model path is recorded in each plan.

Action candidates are grouped across gaps up to 1.25 seconds. Standalone groups need at least four seconds of detected activity; shorter groups need commentary within one second. Kept groups receive 0.45 seconds of lead and 0.65 seconds of tail. These are conservative acoustic heuristics, not proof of a coherent fight. Quiet important events may still be missed.

On the original Rainbow Six transcript, action-only selection changes from 42 exported clips to nine candidate sequences (before final boundary passes). This measures fragmentation, not audience retention or editorial quality.

The first two minutes were transcribed with the new model. Several garbled phrases became legible; one occurrence of shooting range remains inaccurate. No claim of perfect transcription or semantic understanding is made.

Export now explicitly activates the completed timeline and saves the project before reporting success. The existing DRT backup and clip/audio alignment checks remain.
