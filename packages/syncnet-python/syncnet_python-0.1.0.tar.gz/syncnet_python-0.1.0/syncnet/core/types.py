"""Type definitions for SyncNet components."""

from pathlib import Path
from typing import TypeAlias, TypedDict, NotRequired
import numpy as np
import torch

# Basic type aliases
BBox: TypeAlias = tuple[float, float, float, float]
Frame: TypeAlias = np.ndarray
AudioData: TypeAlias = np.ndarray
MFCCFeatures: TypeAlias = np.ndarray

# Detection types
class Detection(TypedDict):
    """Face detection result."""
    frame_idx: int
    bbox: BBox
    confidence: float
    landmarks: NotRequired[np.ndarray]

# Track types
class Track(TypedDict):
    """Face track information."""
    frame: np.ndarray
    bbox: np.ndarray
    start_frame: int
    end_frame: int

# Result types
class SyncResult(TypedDict):
    """Synchronization result."""
    offset: int
    confidence: float
    dists: list[float]
    track_id: NotRequired[int]

class PipelineResult(TypedDict):
    """Complete pipeline result."""
    video_path: str | Path
    sync_results: list[SyncResult]
    num_tracks: int
    processing_time: float
    error: NotRequired[str]

# Model types
ModelState: TypeAlias = dict[str, torch.Tensor]
EmbeddingBatch: TypeAlias = torch.Tensor  # Shape: [batch_size, embedding_dim]