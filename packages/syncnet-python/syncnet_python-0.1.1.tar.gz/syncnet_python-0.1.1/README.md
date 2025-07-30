# SyncNet Python

Audio-visual synchronization detection using deep learning.

This is an updated version of the original [SyncNet implementation](https://github.com/joonson/syncnet_python) by Joon Son Chung, compatible with modern Python versions (3.9+).

## Overview

SyncNet Python is a PyTorch implementation of the SyncNet model, which detects audio-visual synchronization in videos. It can identify lip-sync errors by analyzing the correspondence between mouth movements and spoken audio.

## Features

- 🎥 **Audio-Visual Sync Detection**: Accurately detect synchronization between audio and video
- 🔍 **Face Detection**: Automatic face detection and tracking using S3FD
- 🚀 **Batch Processing**: Process multiple videos efficiently
- 🐍 **Python API**: Easy-to-use Python interface
- 📊 **Confidence Scores**: Get confidence metrics for sync quality

## Installation

```bash
pip install syncnet-python
```

### Additional Requirements

1. **FFmpeg**: Required for video processing
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   ```

2. **Model Weights**: Download pre-trained weights
   - Download `sfd_face.pth` and `syncnet_v2.model`
   - Place them in a `weights/` directory

## Quick Start

```python
from syncnet_python import SyncNetPipeline

# Initialize pipeline
pipeline = SyncNetPipeline(
    s3fd_weights="weights/sfd_face.pth",
    syncnet_weights="weights/syncnet_v2.model",
    device="cuda"  # or "cpu"
)

# Process video
results = pipeline.inference(
    video_path="video.mp4",
    audio_path=None  # Extract from video
)

# Get results
offset, confidence = results['offset'], results['confidence']
print(f"AV Offset: {offset} frames")
print(f"Confidence: {confidence:.3f}")
```

## Command Line Usage

```bash
# Process single video
syncnet-python video.mp4

# Process multiple videos
syncnet-python video1.mp4 video2.mp4 --output results.json

# Use CPU instead of GPU
syncnet-python video.mp4 --device cpu
```

## Requirements

- Python 3.9+
- PyTorch 2.0+
- CUDA (optional but recommended)
- FFmpeg

## Credits

This package is based on the original [SyncNet implementation](https://github.com/joonson/syncnet_python) by Joon Son Chung.

## Citation

If you use this code in your research, please cite the original paper:

```bibtex
@inproceedings{chung2016out,
  title={Out of time: automated lip sync in the wild},
  author={Chung, Joon Son and Zisserman, Andrew},
  booktitle={Asian Conference on Computer Vision},
  year={2016}
}
```

## License

MIT License - see LICENSE file for details.

## Links

- GitHub: https://github.com/yourusername/syncnet-python
- Documentation: https://syncnet-python.readthedocs.io
- Issues: https://github.com/yourusername/syncnet-python/issues