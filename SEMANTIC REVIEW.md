# Local talking-point review

Uses all-MiniLM-L6-v2 sentence embeddings through the Xenova quantized ONNX export. Assets live in `.model-cache/semantic-minilm`; no transcript or footage is uploaded. Embeddings are recomputed each run. Model resources may remain loaded within one app session.

Sources: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 and https://huggingface.co/Xenova/all-MiniLM-L6-v2

Reviews 6–60-word selections within 25 seconds and at most three nearby candidates. Cosine similarity must reach 0.86 unless the precise pair is a user-confirmed alternative in `semantic-preferences.json`. Protects differing numbers/negation, known opposites, explicit additive openings, large scope differences and selected gameplay. Prefers completed speech, then transcription confidence and completeness of coverage. Every change records both texts and the model score.

The two introductions the user identified score approximately 0.65. They contain different claims, and their removal is explicitly a user preference—not proof that the model considers them equivalent. The preference retains the clean/simple introduction.

Sentence similarity is not entailment or a guarantee of redundant information. Safeguards are incomplete; novel facts can still be missed. No claim of general human-level semantic editing is made. Tests include a real model paraphrase, the approved example, changed numbers, opposing evaluations, negation, distant callbacks and gameplay protection.
