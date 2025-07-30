"""SyncNet model implementation with Python 3.13 optimizations."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
from torch import Tensor

from syncnet.core.types import ModelState


class SyncNetModel(nn.Module):
    """SyncNet model for audio-visual synchronization.
    
    This model processes audio and visual features separately through
    dedicated encoders and produces embeddings for synchronization scoring.
    
    Args:
        embedding_dim: Dimension of the output embeddings (default: 1024)
    """
    
    def __init__(self, embedding_dim: int = 1024) -> None:
        super().__init__()
        self.embedding_dim = embedding_dim
        
        # Audio encoder: 2D CNN for spectrograms
        self.audio_encoder = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(1, 1), stride=(1, 1)),
            
            nn.Conv2d(64, 192, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(192),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(3, 3), stride=(1, 2)),
            
            nn.Conv2d(192, 384, kernel_size=(3, 3), padding=(1, 1)),
            nn.BatchNorm2d(384),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(384, 256, kernel_size=(3, 3), padding=(1, 1)),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(256, 256, kernel_size=(3, 3), padding=(1, 1)),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(3, 3), stride=(2, 2)),
            
            nn.Conv2d(256, 512, kernel_size=(5, 4), padding=(0, 0)),
            nn.BatchNorm2d(512),
            nn.ReLU(),
        )
        
        # Audio FC layers
        self.audio_fc = nn.Sequential(
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim),
        )
        
        # Visual encoder: 3D CNN for video sequences
        self.visual_encoder = nn.Sequential(
            nn.Conv3d(3, 96, kernel_size=(5, 7, 7), stride=(1, 2, 2), padding=0),
            nn.BatchNorm3d(96),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2)),
            
            nn.Conv3d(96, 256, kernel_size=(1, 5, 5), stride=(1, 2, 2), padding=(0, 1, 1)),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            
            nn.Conv3d(256, 256, kernel_size=(1, 3, 3), padding=(0, 1, 1)),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            
            nn.Conv3d(256, 256, kernel_size=(1, 3, 3), padding=(0, 1, 1)),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            
            nn.Conv3d(256, 256, kernel_size=(1, 3, 3), padding=(0, 1, 1)),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2)),
            
            nn.Conv3d(256, 512, kernel_size=(1, 6, 6), padding=0),
            nn.BatchNorm3d(512),
            nn.ReLU(inplace=True),
        )
        
        # Visual FC layers
        self.visual_fc = nn.Sequential(
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim),
        )
    
    def forward_audio(self, x: Tensor) -> Tensor:
        """Forward pass for audio features.
        
        Args:
            x: Audio spectrogram tensor of shape [batch, 1, height, width]
            
        Returns:
            Audio embeddings of shape [batch, embedding_dim]
        """
        features = self.audio_encoder(x)
        features = features.view(features.size(0), -1)
        return self.audio_fc(features)
    
    def forward_visual(self, x: Tensor) -> Tensor:
        """Forward pass for visual features.
        
        Args:
            x: Video tensor of shape [batch, channels, time, height, width]
            
        Returns:
            Visual embeddings of shape [batch, embedding_dim]
        """
        features = self.visual_encoder(x)
        features = features.view(features.size(0), -1)
        return self.visual_fc(features)
    
    def forward_visual_features(self, x: Tensor) -> Tensor:
        """Extract visual features without FC layers.
        
        Args:
            x: Video tensor of shape [batch, channels, time, height, width]
            
        Returns:
            Visual features of shape [batch, feature_dim]
        """
        features = self.visual_encoder(x)
        return features.view(features.size(0), -1)
    
    def save(self, path: Path | str) -> None:
        """Save model state to file.
        
        Args:
            path: Path to save the model state
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), path)
        print(f"Model saved to {path}")
    
    @classmethod
    def load(cls, path: Path | str, embedding_dim: int = 1024) -> SyncNetModel:
        """Load model from saved state.
        
        Args:
            path: Path to the saved model state
            embedding_dim: Embedding dimension (must match saved model)
            
        Returns:
            Loaded SyncNetModel instance
        """
        model = cls(embedding_dim=embedding_dim)
        state_dict = torch.load(path, map_location='cpu')
        model.load_state_dict(state_dict)
        return model


def save_model(model: nn.Module, path: Path | str) -> None:
    """Save a PyTorch model to file.
    
    Args:
        model: Model to save
        path: Path to save the model
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "wb") as f:
        torch.save(model, f)
    print(f"{path} saved.")


def load_model(path: Path | str) -> nn.Module:
    """Load a PyTorch model from file.
    
    Args:
        path: Path to the saved model
        
    Returns:
        Loaded PyTorch model
    """
    return torch.load(path, map_location='cpu')