from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd
from pathlib import Path

@dataclass
class PreprocessConfig:
    # Alleen train-set
    augment: bool = False
    augment_factor: int = 0
    augment_methods: List[str] = field(default_factory=list)
    balance_on: bool = False

    # Train, val én test
    onehot_columns: List[str] = field(default_factory=list)
    context_labels: List[str] = field(default_factory=list)
    context_images: bool = False
    context_id: Optional[str] = None      # ← nieuw: kolom om op te groeperen

    # Masks
    mask_column: Optional[str] = None
    apply_mask: bool = False
    zoom_to_mask: bool = False
    zoom_padding: int = 0

    # Vrij veld voor extra dingen
    extra: Dict[str, Any] = field(default_factory=dict)
    elastic_alpha: float = 34.0
    elastic_sigma: float = 4.0
    contrast_min: float = 0.4
    contrast_max: float = 0.9
    jitter_translate_max: int = 10
    # Standaard path
    augmented_image_path: str = "augmented_images"

    def apply(self, df: pd.DataFrame, target_col: str, output_dir: str = "augmented_out") -> pd.DataFrame:
        """
        Roept augmentatie/balancing aan op de data indien gecalled.
        """
        from .transform import augment_and_balance
        return augment_and_balance(
            df_in=df,
            config=self,
            target_col=target_col,
            output_dir=output_dir
        )


# 2 ·  TRAIN-CONFIG
@dataclass
class TrainConfig:
    # Data- en hardware
    input_size: int = 224
    batch_size: int = 32
    epochs: int = 10
    early_stopping_patience: int = 3
    device: str = "cuda"
    mixed_precision: bool = False

    # Optimalisatie
    learning_rate: float = 1e-3
    optimizer: str = "AdamW"
    weight_decay: float = 0.0
    scheduler: str = "None"                # "StepLR" bijv.
    scheduler_params: Dict[str, Any] = field(default_factory=dict)

    # Regularisatie
    dropout: bool = False
    dropout_rate: float = 0.0

    # Checkpoints & metrics
    save_best_model: bool = True
    checkpoint_dir: str = "checkpoints"
    metric: str = "val_loss"               # of "val_auc"
    metric_mode: str = "min"               # of "max"
    confidence_score: bool = False

    # Pre-trained backbones
    pretrained_models: List[str] = field(default_factory=list)

    train_per_label: bool = True
    freeze_backbone:      bool  = False   # alles bevriezen behalve de head
    smart_unfreeze:       bool  = False   # stap 2: geleidelijk blokken loslaten
    train_last_k_blocks:  int   = 1       # hoeveel backbone-blokken al vrij aan het begin
