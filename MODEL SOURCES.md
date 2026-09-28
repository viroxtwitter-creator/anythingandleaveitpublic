# Local model sources

Speech uses the existing local faster-whisper model. Added local models:

- YAMNet ONNX conversion: https://huggingface.co/audiomagic/yamnet-onnx (Apache 2.0). Upstream: https://github.com/tensorflow/models/blob/master/research/audioset/yamnet/README.md . Class map: https://github.com/tensorflow/models/blob/master/research/audioset/yamnet/yamnet_class_map.csv . The app uses Gunshot, Machine gun and Fusillade scores; raw loudness is not an event selector.
- Quantized CLIP ViT-B/32: https://huggingface.co/Xenova/clip-vit-base-patch32 . Model preprocessing: https://huggingface.co/Xenova/clip-vit-base-patch32/blob/main/preprocessor_config.json . Used for sampled gameplay vs menu/loading comparisons, not kill recognition.

Pinned revisions and downloaded SHA-256 checksums are stored in .model-cache/retention/models.json. Model licences/cards are stored with the model assets. These are general pretrained models, not trained on the user's three editing references. Scores are heuristic selection criteria, not calibrated probabilities of an in-game event.
