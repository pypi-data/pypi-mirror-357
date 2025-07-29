# pipeline.py
# ============================================================================
#  End-to-end trainingspipeline:
#  • Laadt en normaliseert afbeeldingen 
#  • Ondersteunt single-channel inputs door duplicatie naar 3-kanalen
#  • Gebruikt torch.amp.GradScaler en torch.amp.autocast volgens nieuwe API
#  • Twee modi:
#      – train_per_label=True: separaat SingleHead-model per target (met herordening per backbone)
#      – train_per_label=False: één MultiHead-model, met aparte early-stopping per head
#  • Print trainings- en validatie-statistieken per epoch (ValLoss)
#  • predict(): voegt per target een kolom "Label_<target>" toe
#  • evaluate(): berekent alleen de gecallde metrics en toont gecallde plots:
#      – confusion_matrix
#      – loss_vs_epoch (train + val loss)
#      – lr_vs_epoch (learning rate)
# ============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union, Optional
import numpy as np

import os
import math
import inspect
import itertools
import shutil
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms.functional import resize, normalize
from torchvision.io import read_image, ImageReadMode
import matplotlib.pyplot as plt

# Torch AMP API moved between versions. Try torch.amp first and fall back to
# torch.cuda.amp for older releases. Wrap autocast so both signatures work.
try:  # PyTorch >=2.0
    from torch.amp import GradScaler, autocast as _autocast

    def autocast(device_type: str | None = None):  # type: ignore[override]
        return _autocast(device_type=device_type)
except Exception:  # pragma: no cover - old API
    from torch.cuda.amp import GradScaler, autocast as _autocast

    def autocast(device_type: str | None = None):  # type: ignore[override]
        return _autocast()
from sklearn.preprocessing import label_binarize        
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    f1_score,
    recall_score,
    precision_score,
    confusion_matrix
)

from .config import PreprocessConfig, TrainConfig  # pragma: no cover

from .transform import augment_and_balance



#  1 · BACKBONE HELPER

# ── helper: laagjes (un)freezen ──────────────────────────────────
def freeze_backbone_layers(
        bb: nn.Module,
        train_last_k_blocks: int = 1,
        keep_bn_trainable: bool = True):
    """
    Zet requires_grad=False voor alle children behalve de laatste k.

    • Voor ResNet-achtigen is een 'block' elk top-level child:
      conv1, bn1, layer1..layer4  → layerX zijn de interessante blokken.
    • Voor MobileNet/EfficientNet werkt dit ook prima (sequential children).
    """
    children = list(bb.children())
    freeze_until = len(children) - train_last_k_blocks
    for idx, child in enumerate(children):
        requires_grad = idx >= freeze_until
        for p in child.parameters():
            p.requires_grad = requires_grad

        # BatchNorm-lagen kun je optioneel *altijd* trainbaar laten
        if keep_bn_trainable and isinstance(child, (nn.BatchNorm2d, nn.BatchNorm1d)):
            for p in child.parameters():
                p.requires_grad = True

    return bb  # (handig voor chaining)

def _infer_nf_runtime(model: nn.Module, input_size: int = 224) -> int:
    """Stuur een dummy door het netwerk om het feature-aantal te bepalen."""
    device = next(model.parameters()).device
    dummy = torch.zeros((1, 3, input_size, input_size), device=device)
    with torch.no_grad():
        out = model(dummy)
    if out.ndim == 4:  # (B,C,H,W) → (B, C*H*W)
        out = out.flatten(1)
    return out.shape[1]


def _strip_head_and_get_nf(model: nn.Module) -> int:
    """
    Verwijder de classificatiekop van bekende torchvision-backbones
    en retourneer de breedte van het feature-vector.
    """
    if hasattr(model, "classifier"):
        head = model.classifier
        if isinstance(head, nn.Sequential):
            nf = next(ly.in_features for ly in head if isinstance(ly, nn.Linear))
        elif isinstance(head, nn.Linear):
            nf = head.in_features
        else:  # pragma: no cover
            raise RuntimeError("Onbekend classifier-type")
        model.classifier = nn.Identity()
        return nf

    if hasattr(model, "fc"):
        nf = model.fc.in_features
        model.fc = nn.Identity()
        return nf

    return _infer_nf_runtime(model)


def backbone(name: str, pretrained: bool = True) -> Tuple[nn.Module, int]:
    """
    Maakt een backbone door naam (bv. 'resnet34', 'mobilenet_v3_large', 'scratch')
    en geeft het (model, num_features) paar terug.
    """
    if name == "scratch":
        cnn = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        return cnn, 64

    from torchvision import models  # lazy import
    if not hasattr(models, name):
        raise ValueError(f"Onbekende backbone-naam: {name!r}")

    ctor = getattr(models, name)
    sig = inspect.signature(ctor)
    kw: Dict[str, Any] = {}
    if pretrained and "weights" in sig.parameters:
        kw["weights"] = "IMAGENET1K_V1"

    m = ctor(**kw)
    nf = _strip_head_and_get_nf(m)
    return m, nf


#  2 · MODEL DEFINITIES

class SingleHead(nn.Module):
    """Backbone + (optioneel) Dropout + Linear classifier (+ contextfeatures)."""

    def __init__(
        self,
        bb: nn.Module,
        nf: int,
        out_dim: int,
        proj_dim: int = 0,
        dropout_rate: float | None = None,
    ) -> None:
        super().__init__()
        layers: List[nn.Module] = []
        if dropout_rate:
            layers.append(nn.Dropout(dropout_rate))
        layers.append(nn.Linear(nf + proj_dim, out_dim))
        self.bb = bb
        self.classifier = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, proj: torch.Tensor | None = None) -> torch.Tensor:
        z = self.bb(x)
        if z.ndim > 2:  # (B,C,H,W) → (B,-1)
            z = torch.flatten(z, 1)
        if proj is not None and proj.numel():
            z = torch.cat([z, proj], dim=1)
        return self.classifier(z)


class MultiHead(nn.Module):
    """
    Eén backbone met meerdere heads (één head per target). 
    Elke head is een Linear (met eventueel Dropout) bovenop gedeelde features.
    """

    def __init__(
        self,
        bb: nn.Module,
        nf: int,
        out_dims: Dict[str, int],
        proj_dim: int = 0,
        dropout_rate: float | None = None,
    ) -> None:
        super().__init__()
        self.bb = bb
        self.heads = nn.ModuleDict()
        for t, od in out_dims.items():
            layers: List[nn.Module] = []
            if dropout_rate:
                layers.append(nn.Dropout(dropout_rate))
            layers.append(nn.Linear(nf + proj_dim, od))
            self.heads[t] = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, proj: torch.Tensor | None = None) -> Dict[str, torch.Tensor]:
        z = self.bb(x)
        if z.ndim > 2:
            z = torch.flatten(z, 1)
        if proj is not None and proj.numel():
            z = torch.cat([z, proj], dim=1)
        out: Dict[str, torch.Tensor] = {}
        for t, head in self.heads.items():
            out[t] = head(z)
        return out


#  3 · DATASET

class _Dataset(Dataset):
    def __init__(
        self,
        df: pd.DataFrame,
        target_cols: List[str],
        context_cols: Sequence[str],
        input_size: int,
        normalize_means: Tuple[float, float, float] = (0.485, 0.456, 0.406),
        normalize_stds: Tuple[float, float, float] = (0.229, 0.224, 0.225),
        context_images: bool = False,
        context_id: Optional[str] = None,
        include_context_labels: bool = False,
    ) -> None:
        self.df = df.reset_index(drop=True)
        self.img_paths = df["img_path"].tolist()
        self.target_cols = target_cols
        self.context = (
            df[context_cols].astype("float32").values if context_cols else None
        )
        self.input_size = input_size
        self.normalize_means = normalize_means
        self.normalize_stds = normalize_stds

        self.context_images = context_images
        self.context_id = context_id
        self.include_context_labels = include_context_labels
        if self.context_images:
            if not self.context_id or self.context_id not in self.df.columns:
                raise ValueError(f"context_id '{self.context_id}' niet gevonden in DataFrame")
            self.groups = self.df.groupby(self.context_id).groups

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        # --- hoofdplaatje laden en normaliseren ---
        img = read_image(self.img_paths[idx], ImageReadMode.RGB).float() / 255.0
        if img.shape[0] == 1:
            img = img.repeat(3, 1, 1)
        img = resize(img, [self.input_size, self.input_size])
        img = normalize(img, mean=self.normalize_means, std=self.normalize_stds)

        # --- label en context‐features voor hoofdplaatje ---
        y_dict = {t: self.df.loc[idx, t] for t in self.target_cols}
        proj = torch.from_numpy(self.context[idx]) if self.context is not None else torch.empty(0)

        # --- context‐plaatjes opzoeken ---
        if not self.context_images:
            return img, proj, y_dict

        pid = self.df.loc[idx, self.context_id]
        sibling_idxs = [i for i in self.groups[pid] if i != idx]

        ctx_imgs: List[torch.Tensor] = []
        ctx_lbls: List[Dict[str, Any]] = []
        for i in sibling_idxs:
            im = read_image(self.img_paths[i], ImageReadMode.RGB).float() / 255.0
            if im.shape[0] == 1:
                im = im.repeat(3, 1, 1)
            im = resize(im, [self.input_size, self.input_size])
            im = normalize(im, mean=self.normalize_means, std=self.normalize_stds)
            ctx_imgs.append(im)
            if self.include_context_labels:
                ctx_lbls.append({t: self.df.loc[i, t] for t in self.target_cols})

        # altijd 5‐tuple: bij include_context_labels=False is ctx_lbls gewoon leeg
        return img, proj, y_dict, ctx_imgs, ctx_lbls


#  4 · PIPELINE

# bovenaan in pipeline.py, naast je andere imports:
import os
import shutil


class Pipeline:
    """
    Eén klasse die alles doet:
      • fit()      : trainen (per target per backbone) of MultiHead met aparte early-stopping per head
      • predict()  : voorspellingen toevoegen als kolommen "Label_<target>"
      • evaluate() : berekent metrics, toont plots, slaat alles weg
      • save()/load()
    """
    def __init__(
        self,
        preprocess_config: PreprocessConfig,
        train_config:      TrainConfig,
        targets:           List[str],
        tests:       bool  = False,
        tests_dir:   str   = "testen",
    ) -> None:

        # ── algemene bookkeeping ────────────────────────────────────
        self.pre_cfg   = preprocess_config
        self.train_cfg = train_config
        self.targets   = targets

        # device / mixed-precision
        self.device = torch.device(train_config.device)
        self.mixed  = bool(train_config.mixed_precision and self.device.type == "cuda")

        # ── NEW: nested histories  history[label][model_key] -> list[float]
        self.train_loss_history: Dict[str, Dict[str, List[float]]] = {t: {} for t in targets}
        self.val_loss_history:   Dict[str, Dict[str, List[float]]] = {t: {} for t in targets}

        # overige runtime-state
        self.lr_history : Union[List[float], Dict[str, List[float]]] = []
        self.out_dims   : Dict[str, int]                               = {}
        self.models     : Dict[str, nn.Module]                         = {}
        self.all_states : Dict[str, Dict[str, Dict[str, torch.Tensor]]] = {}

        # best-tracking
        self.best_epochs   : Dict[str, int] = {t: None for t in targets}
        self.best_backbone : Dict[str, str] = {}

        # ── output / test-folders ───────────────────────────────────
        self.tests     = tests
        self.tests_dir = tests_dir
        if self.tests:
            os.makedirs(self.tests_dir, exist_ok=True)

    # ------------------------------------------------------------------
    #  P R E D I C T _ A L L
    # ------------------------------------------------------------------
    def predict_all(self, test_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """
        Geeft een dict  {model_name: predict_df}
        met per model één DataFrame met kolommen  Label_<target>.
        """
        out: dict[str, pd.DataFrame] = {}

        # ---- (1) predictions met de 'best'-modellen die al in self.models zitten
        out["best"] = self.predict(test_df)

        # ---- (2) eventuele extra back-bones (self.all_states) ----------
        for bb_name, states in self.all_states.items():
            df = test_df.copy()
            for t in self.targets:
                col = f"Label_{t}"
                df[col] = pd.NA
                if t not in states:          # kan bij multiclass zijn overgeslagen
                    continue

                # --- NIEUWE SingleHead mét juiste dropout -----------------
                bb, nf = backbone(bb_name, pretrained=False)
                tmp_net = SingleHead(
                    bb,
                    nf,
                    self.out_dims[t],
                    dropout_rate=(
                        self.train_cfg.dropout_rate
                        if getattr(self.train_cfg, "dropout", False) else None
                    ),
                ).to(self.device)                                               # ← toegevoegd
                tmp_net.load_state_dict(states[t])
                tmp_net.eval()

                # -----------------------------------------------------------
                ds = _Dataset(
                    df,
                    [t],
                    getattr(self.pre_cfg, "context_labels", []),
                    self.train_cfg.input_size,
                )
                ld = DataLoader(
                    ds,
                    batch_size=self.train_cfg.batch_size,
                    shuffle=False,
                    num_workers=0,
                )

                preds: list[int] = []
                for x, proj, _ in ld:
                    x = x.to(self.device)
                    proj = proj.to(self.device) if proj.numel() else None
                    with torch.no_grad():
                        logits = tmp_net(x, proj).cpu()
                    if self.out_dims[t] == 1:
                        preds.extend(
                            (torch.sigmoid(logits.squeeze(1)) >= 0.5).long().numpy()
                        )
                    else:
                        preds.extend(torch.argmax(torch.softmax(logits, 1), 1).numpy())
                df[col] = preds
            out[bb_name] = df

        return out


    def fit(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame | None = None,
    ) -> None:
        """
        Train the pipeline.

        • Writes a checkpoint every time a head (or full multi-model) achieves a
          new best validation loss, so long-running jobs are never lost.
        • Checkpoint directory = TrainConfig.checkpoint_dir (default: “checkpoints”).
        """
        from pathlib import Path

        # ────────────────────────────────────────────────────────────
        # 0 · helper: where to save and a tiny utility
        # ────────────────────────────────────────────────────────────
        ckpt_root = Path(getattr(self.train_cfg, "checkpoint_dir", "checkpoints"))
        ckpt_root.mkdir(parents=True, exist_ok=True)

        def _save_ckpt(state: Dict[str, torch.Tensor], subdir: str, epoch: int):
            """Save *state* under  <ckpt_root>/<subdir>/best_epoch_<epoch>.pt."""
            dst = ckpt_root / subdir
            dst.mkdir(parents=True, exist_ok=True)
            torch.save(state, dst / f"best_epoch_{epoch}.pt")

        # ────────────────────────────────────────────────────────────
        # 1 · sanity-checks + augmentation / balancing (unchanged)
        # ────────────────────────────────────────────────────────────
        if self.train_cfg.smart_unfreeze and not self.train_cfg.freeze_backbone:
            raise ValueError("smart_unfreeze=True requires freeze_backbone=True.")
        if getattr(self.pre_cfg, "balance_on", False) and not getattr(self.pre_cfg, "augment", False):
            raise ValueError("Balancing requires 'augment=True'.")

        # optional on-the-fly augmentation + class balancing
        if getattr(self.pre_cfg, "augment", False) or getattr(self.pre_cfg, "balance_on", False):
            aug_root = Path(getattr(self.pre_cfg, "augmented_image_path", "augmented_images"))
            aug_root.mkdir(exist_ok=True)
            for t in self.targets:
                out_dir = aug_root / t
                out_dir.mkdir(exist_ok=True)
                try:
                    train_df = augment_and_balance(
                        df_in=train_df,
                        config=self.pre_cfg,
                        target_col=t,
                        output_dir=str(out_dir),
                        seed=42,
                        img_column="img_path",
                    )
                    print(f"> augmentation / balancing for '{t}' → {out_dir}")
                except Exception as e:
                    print(f"> augment_and_balance failed for {t}: {e}.  Skipping.")

        # ────────────────────────────────────────────────────────────
        # 2 · misc. setup
        # ────────────────────────────────────────────────────────────
        context_cols = list(itertools.chain(
            getattr(self.pre_cfg, "onehot_columns", []),
            getattr(self.pre_cfg, "context_labels", []),
        ))
        scaler          = torch.amp.GradScaler(enabled=self.mixed)
        autocast_device = "cuda" if self.mixed else "cpu"

        # determine binary vs. multiclass per target
        for t in self.targets:
            classes = sorted(int(x) for x in train_df[t].dropna().unique())
            self.out_dims[t] = 1 if len(classes) <= 2 else len(classes)


        # >>>>>> CASE A – train_per_label == False  (multi-head)  >>>>>>>>>>>>>>>>
        if not getattr(self.train_cfg, "train_per_label", False):

            # ------------------------------------------------------------------
            # 0 · backbone + model
            # ------------------------------------------------------------------
            bb_name               = self.train_cfg.pretrained_models[0]
            bb, nf                = backbone(bb_name, pretrained=True)
            if self.train_cfg.freeze_backbone:
                bb = freeze_backbone_layers(bb,
                                            train_last_k_blocks=self.train_cfg.train_last_k_blocks)

            multi_model = MultiHead(
                bb        = bb,
                nf        = nf,
                out_dims  = self.out_dims,
                proj_dim  = len(context_cols),
                dropout_rate = (
                    self.train_cfg.dropout_rate
                    if getattr(self.train_cfg, "dropout", False) else None
                ),
            ).to(self.device)
            if self.mixed:
                multi_model = multi_model.to(memory_format=torch.channels_last)

            optimizer = torch.optim.AdamW(multi_model.parameters(),
                                        lr=self.train_cfg.learning_rate,
                                        weight_decay=1e-4)

            loss_fns  = {
                t: (nn.BCEWithLogitsLoss() if self.out_dims[t] == 1 else nn.CrossEntropyLoss())
                for t in self.out_dims
            }

            # ------------------------------------------------------------------
            # 1 · data loaders
            # ------------------------------------------------------------------
            tr_ld = DataLoader(
                _Dataset(train_df, self.targets, context_cols,
                        input_size=self.train_cfg.input_size,
                        context_images=self.pre_cfg.context_images,
                        context_id=self.pre_cfg.context_id,
                        include_context_labels=True),
                batch_size=self.train_cfg.batch_size, shuffle=True, num_workers=0)

            va_ld = None
            if val_df is not None and len(val_df):
                va_ld = DataLoader(
                    _Dataset(val_df, self.targets, context_cols,
                            input_size=self.train_cfg.input_size,
                            context_images=self.pre_cfg.context_images,
                            context_id=self.pre_cfg.context_id,
                            include_context_labels=False),
                    batch_size=self.train_cfg.batch_size, shuffle=False, num_workers=0)

            # ------------------------------------------------------------------
            # 2 · history containers  (NEW – nested by model key)
            # ------------------------------------------------------------------
            model_key = "multi"
            for t in self.targets:
                self.train_loss_history.setdefault(t, {})[model_key] = []
                self.val_loss_history  .setdefault(t, {})[model_key] = []

            # ------------------------------------------------------------------
            # 3 · early-stopping bookkeeping
            # ------------------------------------------------------------------
            best_loss   = {t: float("inf") for t in self.targets}
            best_states = {}                # state_dict snapshots (per head)
            bad_cnt     = {t: 0            for t in self.targets}
            active      = {t: True         for t in self.targets}
            patience    = getattr(self.train_cfg, "early_stopping_patience", 0)

            scaler             = torch.amp.GradScaler(enabled=self.mixed)
            autocast_device    = "cuda" if self.mixed else "cpu"

            # ------------------------------------------------------------------
            # 4 · epoch loop
            # ------------------------------------------------------------------
            for ep in range(1, self.train_cfg.epochs + 1):

                # ---------- TRAIN ----------
                multi_model.train()
                total_train   = {t: 0.0 for t in self.targets}
                total_samples = 0

                for x, proj, y_dict, ctx_imgs, ctx_lbls in tr_ld:
                    optimizer.zero_grad(set_to_none=True)
                    x    = x.to(self.device)
                    proj = proj.to(self.device) if proj.numel() else None

                    # build y-tensors -------------------------------------------------
                    y_tensors = {}
                    for t in self.targets:
                        dtype = torch.float32 if self.out_dims[t] == 1 else torch.long
                        y_tensors[t] = torch.tensor([y_dict[t]] * x.size(0),
                                                    dtype=dtype, device=self.device)

                    # context images (optional) --------------------------------------
                    if self.pre_cfg.context_images and ctx_imgs:
                        flat_imgs, flat_proj, flat_ys = [], [], {t: [] for t in self.targets}
                        for i in range(len(ctx_imgs)):
                            for ci, lbl in zip(ctx_imgs[i], ctx_lbls[i]):
                                flat_imgs.append(ci)
                                if proj is not None: flat_proj.append(proj[i])
                                for t in self.targets: flat_ys[t].append(lbl[t])
                        x_ctx         = torch.stack(flat_imgs).to(self.device)
                        proj_ctx      = (torch.stack(flat_proj).to(self.device)
                                        if proj is not None and flat_proj else None)
                        x             = torch.cat([x, x_ctx])
                        proj          = (torch.cat([proj, proj_ctx]) if proj_ctx is not None else proj)
                        for t in self.targets:
                            dt     = torch.float32 if self.out_dims[t] == 1 else torch.long
                            y_ctx  = torch.tensor(flat_ys[t], dtype=dt, device=self.device)
                            y_tensors[t] = torch.cat([y_tensors[t], y_ctx])

                    # forward / backward ---------------------------------------------
                    with torch.amp.autocast(device_type=autocast_device):
                        logits = multi_model(x, proj)
                        batch_losses = []
                        for t in self.targets:
                            if not active[t]:
                                continue
                            mask = ~torch.isnan(y_tensors[t])
                            if not mask.any():
                                continue
                            preds_t = logits[t].squeeze(1) if self.out_dims[t] == 1 else logits[t]
                            loss_t  = loss_fns[t](preds_t[mask], y_tensors[t][mask])
                            batch_losses.append(loss_t)
                            total_train[t] += loss_t.item() * mask.sum().item()
                        if not batch_losses:   # no active tasks in this batch
                            continue
                        scaler.scale(torch.stack(batch_losses).mean()).backward()
                    scaler.step(optimizer)
                    scaler.update()
                    total_samples += x.size(0)

                # mean train loss per head ------------------------------------------
                for t in self.targets:
                    mean_tr = total_train[t] / total_samples if total_samples else float("nan")
                    self.train_loss_history[t][model_key].append(mean_tr)

                # ---------- VALIDATION ----------
                avg_val = {t: float("nan") for t in self.targets}
                if va_ld is not None:
                    multi_model.eval()
                    v_sum = {t: 0.0 for t in self.targets}
                    v_cnt = {t: 0   for t in self.targets}
                    with torch.no_grad(), torch.amp.autocast(device_type=autocast_device):
                        for x_v, proj_v, yv_dict, _, _ in va_ld:
                            x_v    = x_v.to(self.device)
                            proj_v = proj_v.to(self.device) if proj_v.numel() else None
                            logits_v = multi_model(x_v, proj_v)
                            for t in self.targets:
                                if not active[t]:
                                    continue
                                dtype = torch.float32 if self.out_dims[t] == 1 else torch.long
                                yv    = torch.tensor(yv_dict[t], dtype=dtype, device=self.device)
                                mask  = ~torch.isnan(yv)
                                if not mask.any():
                                    continue
                                preds_v = logits_v[t].squeeze(1) if self.out_dims[t]==1 else logits_v[t]
                                lv      = loss_fns[t](preds_v[mask], yv[mask])
                                v_sum[t] += lv.item() * mask.sum().item()
                                v_cnt[t] += mask.sum().item()
                    for t in self.targets:
                        if v_cnt[t]:
                            avg_val[t] = v_sum[t] / v_cnt[t]
                            self.val_loss_history[t][model_key].append(avg_val[t])

                # ---------- logging ----------
                stat_line = "  ".join(
                    f"{t}: tr={self.train_loss_history[t][model_key][-1]:.4f} "
                    f"val={avg_val[t]:.4f}" for t in self.targets
                )
                print(f"[Multi] epoch {ep}/{self.train_cfg.epochs}  {stat_line}")

                # ---------- early-stop & checkpoint ----------
                all_stopped = True
                for t in self.targets:
                    if not active[t]:
                        continue
                    if avg_val[t] < best_loss[t]:
                        best_loss[t]   = avg_val[t]
                        bad_cnt[t]     = 0
                        best_states[t] = {k: v.clone().cpu()
                                        for k, v in multi_model.state_dict().items()}
                        self.best_epochs[t] = ep
                        _save_ckpt(best_states[t], "multi", ep)     # checkpoint 🔥
                    else:
                        bad_cnt[t] += 1
                        if bad_cnt[t] >= patience:
                            active[t] = False
                    all_stopped &= (not active[t])

                if all_stopped:
                    print(f"All heads early-stopped on epoch {ep}.")
                    break

            # ------------------------------------------------------------------
            # 5 · restore best parameters & register model
            # ------------------------------------------------------------------
            final_state = multi_model.state_dict()
            for t, st in best_states.items():           # replace only improved heads
                for k, v in st.items():
                    final_state[k] = v.to(self.device)
            multi_model.load_state_dict(final_state)
            multi_model.eval()

            self.models["_multi"]  = multi_model
            self.best_backbone     = {t: bb_name for t in self.targets}
        # <<<<<< CASE A – end >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


        # >>>>>> CASE B – train_per_label == True  (single-head per label) >>>>>>>
        else:  # self.train_cfg.train_per_label == True
            global_best_loss   = {t: float("inf") for t in self.targets}
            global_best_state  = {t: {}             for t in self.targets}
            global_best_model  = {t: ""             for t in self.targets}

            for bb_name in self.train_cfg.pretrained_models:
                try:
                    bb_raw, nf_raw = backbone(bb_name, pretrained=True)
                    if self.train_cfg.freeze_backbone:
                        bb_raw = freeze_backbone_layers(
                            bb_raw, train_last_k_blocks=self.train_cfg.train_last_k_blocks)
                except Exception as e:
                    print(f"[WARN] backbone {bb_name} cannot be loaded: {e}")
                    continue

                for tgt in self.targets:
                    tr_sub = train_df.dropna(subset=[tgt]).copy()
                    if tr_sub.empty:
                        print(f"[INFO] no training samples for target {tgt}; skipping.")
                        continue

                    # histories  -----------------------------------------------------------------
                    self.train_loss_history.setdefault(tgt, {})[bb_name] = []
                    self.val_loss_history  .setdefault(tgt, {})[bb_name] = []

                    # loaders  -------------------------------------------------------------------
                    tr_ld = DataLoader(
                        _Dataset(tr_sub, [tgt], context_cols,
                                input_size=self.train_cfg.input_size),
                        batch_size=self.train_cfg.batch_size, shuffle=True, num_workers=0)

                    va_ld = None
                    if val_df is not None:
                        va_sub = val_df.dropna(subset=[tgt]).copy()
                        if not va_sub.empty:
                            va_ld = DataLoader(
                                _Dataset(va_sub, [tgt], context_cols,
                                        input_size=self.train_cfg.input_size),
                                batch_size=self.train_cfg.batch_size, shuffle=False, num_workers=0)

                    # model + loss ---------------------------------------------------------------
                    out_dim  = self.out_dims[tgt]
                    loss_fn  = nn.BCEWithLogitsLoss() if out_dim == 1 else nn.CrossEntropyLoss()

                    model = SingleHead(
                        bb_raw, nf_raw, out_dim,
                        proj_dim=len(context_cols),
                        dropout_rate=(
                            self.train_cfg.dropout_rate
                            if getattr(self.train_cfg, "dropout", False) else None)
                    ).to(self.device)
                    if self.mixed:
                        model = model.to(memory_format=torch.channels_last)

                    optimizer = torch.optim.AdamW(multi_model.parameters(),
                            lr=self.train_cfg.learning_rate,
                            weight_decay=1e-4)
                    scaler      = torch.amp.GradScaler(enabled=self.mixed)
                    auto_device = "cuda" if self.mixed else "cpu"

                    best_loss_bb  = float("inf")
                    best_state_bb = {}
                    bad           = 0
                    patience      = getattr(self.train_cfg, "early_stopping_patience", 0)

                    # ---------------------- epoch loop ----------------------
                    for ep in range(1, self.train_cfg.epochs + 1):

                        # —— TRAIN ——
                        model.train()
                        tr_sum = tr_cnt = 0.0
                        for x, proj, y_dict in tr_ld:
                            optimizer.zero_grad(set_to_none=True)
                            x = x.to(self.device)
                            y = torch.tensor(
                                y_dict[tgt],
                                dtype=(torch.float32 if out_dim == 1 else torch.long),
                                device=self.device,
                            )
                            proj = proj.to(self.device) if proj.numel() else None

                            with torch.amp.autocast(device_type=auto_device):
                                logits = model(x, proj)
                                loss = (loss_fn(logits.squeeze(1), y)
                                        if out_dim == 1 else loss_fn(logits, y))
                            scaler.scale(loss).backward()
                            scaler.step(optimizer)
                            scaler.update()
                            tr_sum += loss.item() * x.size(0)
                            tr_cnt += x.size(0)

                        tr_loss_mean = tr_sum / tr_cnt
                        self.train_loss_history[tgt][bb_name].append(tr_loss_mean)

                        # —— VALIDATION ——
                        val_loss_mean = float("nan")
                        if va_ld is not None:
                            model.eval()
                            v_sum = v_cnt = 0.0
                            with torch.no_grad(), torch.amp.autocast(device_type=auto_device):
                                for x_v, proj_v, yv_dict in va_ld:
                                    x_v = x_v.to(self.device)
                                    yv = torch.tensor(
                                        yv_dict[tgt],
                                        dtype=(torch.float32 if out_dim == 1 else torch.long),
                                        device=self.device,
                                    )
                                    proj_v = proj_v.to(self.device) if proj_v.numel() else None
                                    logits_v = model(x_v, proj_v)
                                    lv = (loss_fn(logits_v.squeeze(1), yv)
                                        if out_dim == 1 else loss_fn(logits_v, yv))
                                    v_sum += lv.item() * x_v.size(0)
                                    v_cnt += x_v.size(0)
                            val_loss_mean = v_sum / v_cnt
                            self.val_loss_history[tgt][bb_name].append(val_loss_mean)

                        # —— logging ——
                        print(f"[{tgt}|{bb_name}] epoch {ep}/{self.train_cfg.epochs}  "
                            f"train loss={tr_loss_mean:.4f}  val loss={val_loss_mean:.4f}")

                        # —— early-stopping & checkpoint ——
                        if val_loss_mean < best_loss_bb:
                            best_loss_bb  = val_loss_mean
                            best_state_bb = {k: v.clone() for k, v in model.state_dict().items()}
                            bad = 0
                            self.best_epochs[tgt] = ep
                            _save_ckpt(best_state_bb, f"{tgt}/{bb_name}", ep)  # checkpoint
                        else:
                            bad += 1
                            if bad >= patience:
                                print(f"[{tgt}|{bb_name}] early-stop on epoch {ep}")
                                break

                    # gather per-backbone states -------------------------------------------------
                    if bb_name not in self.all_states:
                        self.all_states[bb_name] = {}
                    self.all_states[bb_name][tgt] = best_state_bb

                    if best_loss_bb < global_best_loss[tgt]:
                        global_best_loss[tgt]  = best_loss_bb
                        global_best_state[tgt] = best_state_bb
                        global_best_model[tgt] = bb_name

                    del model, optimizer
                    torch.cuda.empty_cache()

            # ------------- rebuild best-of-all models -------------
            for tgt in self.targets:
                bb_final, nf_final = backbone(global_best_model[tgt], pretrained=False)
                net = SingleHead(
                    bb_final, nf_final, self.out_dims[tgt],
                    proj_dim=len(context_cols),
                    dropout_rate=(
                        self.train_cfg.dropout_rate
                        if getattr(self.train_cfg, "dropout", False) else None)
                ).to(self.device)
                net.load_state_dict(global_best_state[tgt])
                net.eval()
                self.models[tgt] = net
            self.best_backbone = global_best_model
        # <<<<<< CASE B – end >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


    @staticmethod
    def _collate_fn(batch):
        """
        Custom collate: als elk item 3 elementen heeft, stapel die.
        Als elk item 5 elementen heeft (met context), pak lijsten netjes in.
        """
        # batch[0] kan zijn: (img, proj, y_dict) of (img, proj, y_dict, ctx_imgs, ctx_lbls)
        if len(batch[0]) == 3:
            imgs, projs, y_dicts = zip(*batch)
            imgs = torch.stack(imgs, dim=0)
            # projs is een tuple van Tensor(voorbeeld, features) of lege tensor
            projs = torch.stack(projs, dim=0) if projs[0].numel() else torch.empty(0)
            return imgs, projs, list(y_dicts)
        else:
            imgs, projs, y_dicts, ctx_imgs_list, ctx_lbls_list = zip(*batch)
            imgs = torch.stack(imgs, dim=0)
            projs = torch.stack(projs, dim=0) if projs[0].numel() else torch.empty(0)
            # ctx_imgs_list is tuple van lijsten van Tensor, we willen lijst van lijsten
            return imgs, projs, list(y_dicts), list(ctx_imgs_list), list(ctx_lbls_list)



    def predict(
        self,
        test_df: pd.DataFrame,
        return_confidence: bool = False,
    ) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]:
        """
        Predict labels (and optionally confidences) on test_df.
        If return_confidence=True, also adds 'Conf_<target>' columns.
        Returns either a single DataFrame or a dict of DataFrames
        (one per backbone, if self.all_states is non-empty).
        """
        if test_df is None or test_df.empty:
            raise ValueError("test_df mag niet leeg zijn.")

        def _collect(df_in: pd.DataFrame, net, target: str):
            ds = _Dataset(
                df_in, [target],
                getattr(self.pre_cfg, "context_labels", []),
                input_size=self.train_cfg.input_size,
                context_images=self.pre_cfg.context_images,
                context_id=self.pre_cfg.context_id,
                include_context_labels=False,
            )
            ld = DataLoader(
                ds,
                batch_size=self.train_cfg.batch_size,
                shuffle=False,
                num_workers=0,
                collate_fn=self._collate_fn,
            )

            labels, confs = [], []
            for batch in ld:
                if self.pre_cfg.context_images:
                    x, proj, _, _, _ = batch
                else:
                    x, proj, _ = batch

                x = x.to(self.device)
                proj = proj.to(self.device) if proj.numel() else None
                with torch.no_grad():
                    logits = net(x, proj).cpu()

                if self.out_dims[target] == 1:
                    probs = torch.sigmoid(logits.squeeze(1)).numpy()
                    labs = (probs >= 0.5).astype(int)
                else:
                    soft = torch.softmax(logits, dim=1).numpy()
                    labs = soft.argmax(axis=1)
                    probs = soft.max(axis=1)

                labels.extend(labs.tolist())
                confs.extend(probs.tolist())

            return labels, confs

        def _make_df(df_in: pd.DataFrame, states: bool):
            df_out = df_in.copy()
            for t in self.targets:
                df_out[f"Label_{t}"] = pd.NA
                if return_confidence:
                    df_out[f"Conf_{t}"] = pd.NA

                # choose correct net (single-head vs multi-head)
                if self.train_cfg.train_per_label:
                    base_net = self.models[t]
                else:
                    multi = self.models["_multi"]
                    base_net = lambda x,p,label=t,m=multi: m(x,p)[label]

                labs, confs = _collect(df_out, base_net, t)
                df_out[f"Label_{t}"] = labs
                if return_confidence:
                    df_out[f"Conf_{t}"] = confs

            return df_out

        # (1) always do the “best” model
        best_df = _make_df(test_df, states=False)

        # (2) if no extra backbones, return single DataFrame
        if not self.all_states:
            return best_df

        # (3) otherwise build a dict including each backbone
        out: dict[str, pd.DataFrame] = {"best": best_df}
        for bb_name, label_states in self.all_states.items():
            # reconstruct a temp SingleHead for each target
            df_bb = test_df.copy()
            for t, st in label_states.items():
                bb_mod, nf = backbone(bb_name, pretrained=False)
                tmp = SingleHead(
                    bb_mod, nf, self.out_dims[t],
                    dropout_rate=(
                        self.train_cfg.dropout_rate
                        if getattr(self.train_cfg, "dropout", False) else None
                    ),
                ).to(self.device)
                tmp.load_state_dict(st)
                tmp.eval()

                labs, confs = _collect(df_bb, tmp, t)
                df_bb[f"Label_{t}"] = labs
                if return_confidence:
                    df_bb[f"Conf_{t}"] = confs

            out[bb_name] = df_bb

        return out

    # ────────────────────────────────────────────────────────────────
    #  E V A L U A T E
    # ────────────────────────────────────────────────────────────────
    @torch.no_grad()
    def evaluate(
        self,
        *,
        predict_df: pd.DataFrame | dict[str, pd.DataFrame] | None = None,
        predict_dfs: dict[str, pd.DataFrame] | None = None,
        plots: list[str] | None = None,
        metrics: list[str] | None = None,
    ) -> pd.DataFrame:
        import os, numpy as np, pandas as pd, torch        # ← added torch
        from sklearn.metrics import (
            roc_auc_score, accuracy_score, recall_score,
            precision_score, f1_score, confusion_matrix, roc_curve
        )
        from sklearn.preprocessing import label_binarize
        from torch.utils.data import DataLoader
        import seaborn as sns

        # ─── Prepare predictions dict ───────────────────────────────
        if predict_dfs is None and isinstance(predict_df, dict):
            predict_dfs = predict_df; predict_df = None
        if predict_dfs is None:
            if predict_df is None:
                raise ValueError("Provide either predict_df or predict_dfs.")
            predict_dfs = {"best": predict_df}
        if self.tests:
            # project–level folder
            os.makedirs(os.path.join(self.tests_dir, "plots"), exist_ok=True)
            # per-target folders
            for t in self.targets:
                os.makedirs(os.path.join(self.tests_dir, f"model_{t}", "plots"), exist_ok=True)

        # ─── Dump “wide” per-image predictions for all models ───────
        os.makedirs(self.tests_dir, exist_ok=True)

        base_df = next(iter(predict_dfs.values()))

        # keep the FULL original test-set (all columns that are *not* already preds)
        orig_cols = [c for c in base_df.columns
                    if not (c.startswith("Label_") or c.startswith("Conf_"))]
        dump = base_df[orig_cols].copy()              # ← changed line

        # add predictions & (optionally) confidences for every model
        for name, dfp in predict_dfs.items():
            for t in self.targets:
                dump[f"{name}_pred_{t}"] = dfp[f"Label_{t}"]
                if f"Conf_{t}" in dfp.columns:
                    dump[f"{name}_conf_{t}"] = dfp[f"Conf_{t}"]

        # final CSV (same filename / location)
        dump.to_csv(
            os.path.join(self.tests_dir, "test_with_preds_all_labels.csv"),
            index=False
        )


        # ─── Compute metrics table …  (unchanged code here) ──────────
        model_names  = list(predict_dfs.keys())
        multi_mode   = not getattr(self.train_cfg, "train_per_label", True)
        multi_model  = self.models.get("_multi", None)
        context_cols = getattr(self.pre_cfg, "context_labels", [])
        n_labels     = len(self.targets)
        if metrics is None:
            metrics = ["AUC", "accuracy", "recall", "precision", "sens", "spec", "f1"]

        rows: list[dict] = []
        for mname, df in predict_dfs.items():
            for t in self.targets:
                rec = {"model": mname, "target": t}
                yt, yp = t, f"Label_{t}"
                sub = df.dropna(subset=[yt, yp]) if {yt, yp} <= set(df.columns) else pd.DataFrame()

                if sub.empty:
                    rec.update({m: np.nan for m in metrics})
                else:
                    y_true = sub[yt].astype(int).to_numpy()
                    y_pred = sub[yp].astype(int).to_numpy()

                    # — MULTICLASS helper (unchanged) —
                    if self.out_dims[t] > 2:
                        ds_mc = _Dataset(sub, [t], context_cols, self.train_cfg.input_size)
                        ld_mc = DataLoader(ds_mc, batch_size=self.train_cfg.batch_size, shuffle=False)
                        if not self.train_cfg.train_per_label:
                            def _inf(x, p, label=t, net=multi_model): return net(x, p)[label]
                            net_inf = _inf
                        else:
                            net_inf = self.models[t]

                        probs_list = []
                        for x_mc, proj_mc, _ in ld_mc:
                            x_mc    = x_mc.to(self.device)
                            proj_mc = proj_mc.to(self.device) if proj_mc.numel() else None
                            logits  = net_inf(x_mc, proj_mc)
                            probs_list.append(torch.softmax(logits, dim=1).cpu().numpy())
                        all_probs = np.concatenate(probs_list, axis=0)
                        y_one     = label_binarize(y_true, classes=list(range(self.out_dims[t])))
                        macro_auc = roc_auc_score(y_one, all_probs, multi_class="ovr", average="macro")
                        cm = confusion_matrix(y_true, y_pred, labels=list(range(self.out_dims[t])))
                        tp = np.diag(cm)
                        fp = cm.sum(axis=0) - tp
                        tn = cm.sum() - (tp + fp + (cm.sum(axis=1) - tp))
                        spec_vals  = [tn_i/(tn_i+fp_i) for tn_i, fp_i in zip(tn, fp) if (tn_i+fp_i)]
                        macro_spec = np.nanmean(spec_vals) if spec_vals else np.nan

                    # — fill metrics —
                    for m in metrics:
                        if m == "AUC":
                            rec[m] = (roc_auc_score(y_true, y_pred.astype(float))
                                    if self.out_dims[t] <= 2 else macro_auc)
                        elif m == "accuracy":
                            rec[m] = accuracy_score(y_true, y_pred)
                        elif m in ("recall", "sens"):
                            rec[m] = recall_score(
                                y_true, y_pred,
                                average="binary" if self.out_dims[t] == 1 else "macro",
                                zero_division=0
                            )
                        elif m == "precision":
                            rec[m] = precision_score(
                                y_true, y_pred,
                                average="binary" if self.out_dims[t] == 1 else "macro",
                                zero_division=0
                            )
                        elif m == "spec":
                            if self.out_dims[t] == 1:
                                tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
                                rec[m] = tn / (tn + fp) if (tn + fp) else np.nan
                            else:
                                rec[m] = macro_spec
                        elif m == "f1":
                            rec[m] = f1_score(
                                y_true, y_pred,
                                average="binary" if self.out_dims[t] == 1 else "macro",
                                zero_division=0
                            )
                rows.append(rec)

        results_df = pd.DataFrame(rows)
        results_df[metrics] = results_df[metrics].round(2)

        # ─── Save per-label outputs ──────────────────────────────────
        if self.tests:
            best_df = predict_dfs["best"]
            for t in self.targets:
                base = os.path.join(self.tests_dir, f"model_{t}")
                os.makedirs(base, exist_ok=True)

                # 1) metrics CSV
                grp = results_df[(results_df.target == t) & (results_df.model != "macro")].copy()
                grp.loc[grp.model == "best", "model"] += " (best)"
                grp.to_csv(os.path.join(base, f"metrics_{t}.csv"), index=False)

                # 2) save original test rows
                orig_cols = [c for c in best_df.columns if not c.startswith("Label_")]
                best_df[orig_cols].to_csv(os.path.join(base, "original_test_set.csv"), index=False)

                # 3) save label-specific model  ← NEW
                if self.train_cfg.train_per_label and t in self.models:
                    torch.save(self.models[t].state_dict(),
                            os.path.join(base, f"model_{t}.pt"))

                # 4) error examples (unchanged)
                err_dir = os.path.join(base, "error_predictions")
                os.makedirs(err_dir, exist_ok=True)
                for _, row in best_df.iterrows():
                    if row[t] != row[f"Label_{t}"]:
                        src  = row["img_path"]
                        name = os.path.splitext(os.path.basename(src))[0]
                        dst  = f"{name}_actual_{row[t]}_pred_{row[f'Label_{t}']}.png"
                        shutil.copy(src, os.path.join(err_dir, dst))
           # bewaar volledige pipeline voor later gebruik
            # opslaan in de tests_dir zelf zodat alle gewichten
            # afzonderlijk beschikbaar zijn
            self.save(self.tests_dir)
        # ─── Optional plots ─────────────────────────────────────────
        if not plots:
            return results_df
        # ───────────────────────────────────────────────────────────
        # 2 · CONFUSION-MATRIX (identiek aan origineel)
        # ───────────────────────────────────────────────────────────
        if "confusion_matrix" in plots:
            for t in self.targets:
                df_cm = predict_dfs[model_names[0]].dropna(subset=[t, f"Label_{t}"])
                if df_cm.empty:
                    continue
                y_true = df_cm[t].astype(int).to_numpy()
                y_pred = df_cm[f"Label_{t}"].astype(int).to_numpy()
                labels = [0, 1] if self.out_dims[t] == 1 else sorted(set(np.concatenate([y_true, y_pred])))

                # absolute matrix
                cm  = confusion_matrix(y_true, y_pred, labels=labels)
                fig, ax = plt.subplots(figsize=(4, 4))
                sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                            cbar=False, ax=ax, xticklabels=labels, yticklabels=labels)
                ax.set_xlabel("Predicted"); ax.set_ylabel("True")
                ax.set_title(f"Confusion matrix – {t}")
                plt.tight_layout()
                if self.tests:
                    fig.savefig(os.path.join(self.tests_dir,
                         f"model_{t}", "plots",
                         f"cm_{t}.png"), dpi=300)
                plt.show(); plt.close(fig)

                # rij-genormaliseerd
                rowsum = cm.sum(axis=1, keepdims=True); rowsum[rowsum == 0] = 1
                cm_pct = (cm / rowsum) * 100
                annot  = np.array([[f"{cm_pct[i, j]:.0f}%{' (n='+str(cm[i, j])+')' if cm[i, j] else ''}"
                                    for j in range(cm.shape[1])] for i in range(cm.shape[0])])
                fig, ax = plt.subplots(figsize=(4, 4))
                sns.heatmap(cm_pct, annot=annot, fmt="",
                            cmap="Blues", vmin=0, vmax=100,
                            cbar=False, ax=ax,
                            xticklabels=labels, yticklabels=labels)
                ax.set_xlabel("Predicted"); ax.set_ylabel("True")
                ax.set_title(f"Confusion matrix – {t} (rows = 100 %)")
                plt.tight_layout()
                if self.tests:
                    fig.savefig(os.path.join(self.tests_dir,
                         f"model_{t}", "plots",
                         f"cm_perc_{t}.png"), dpi=300)
                plt.show(); plt.close(fig)

        # ───────────────────────────────────────────────────────────
        # 3 · ROC- / AUC-PLOTS
        # ───────────────────────────────────────────────────────────
        if "auc_plot" in plots:
            for t in self.targets:
                # data en ground-truth + voorspellingen
                df_sub = predict_dfs["best"].dropna(subset=[t, f"Label_{t}"])
                if df_sub.empty:
                    continue

                # figuur aanmaken
                fig, ax = plt.subplots(figsize=(5, 5))
                y_true = df_sub[t].astype(int).to_numpy()

                # scores ophalen
                # binaire of multiclass?
                if self.out_dims[t] <= 2:
                    # Binaire case
                    # wrapper voor MultiHead indien nodig
                    if multi_mode:
                        def _infer(x, proj, label=t, net=multi_model):
                            return net(x, proj)[label]
                        net = _infer
                    else:
                        net = self.models[t]

                    # probabilities verzamelen
                    probs: list[float] = []
                    ds = _Dataset(df_sub, [t], context_cols, self.train_cfg.input_size)
                    ld = DataLoader(ds, batch_size=self.train_cfg.batch_size, shuffle=False, num_workers=0)
                    for x, proj, _ in ld:
                        x = x.to(self.device)
                        proj = proj.to(self.device) if proj.numel() else None
                        with torch.no_grad():
                            logits = net(x, proj).cpu()
                        probs.extend(torch.sigmoid(logits.squeeze(1)).numpy())

                    fpr, tpr, _ = roc_curve(y_true, np.array(probs))
                    auc_val = roc_auc_score(y_true, np.array(probs))
                    ax.plot(1 - fpr, tpr, label=f"{t} (AUC {auc_val:.2f})")

                else:
                    # Multiclass: one-vs-rest voor elke unieke klasse
                    classes = sorted(df_sub[t].unique())
                    # logits → softmax-probs
                    logits_list = []
                    if multi_mode:
                        def _infer(x, proj, net=multi_model): return net(x, proj)[t]
                        net = _infer
                    else:
                        net = self.models[t]

                    ds = _Dataset(df_sub, [t], context_cols, self.train_cfg.input_size)
                    ld = DataLoader(ds, batch_size=self.train_cfg.batch_size, shuffle=False, num_workers=0)
                    for x, proj, _ in ld:
                        x = x.to(self.device)
                        proj = proj.to(self.device) if proj.numel() else None
                        with torch.no_grad():
                            logits_list.append(net(x, proj).cpu().numpy())
                    probs = torch.softmax(torch.tensor(np.concatenate(logits_list, 0)), dim=1).numpy()

                    # per klasse de ROC
                    for idx, cls in enumerate(classes):
                        y_bin = (y_true == cls).astype(int)
                        fpr, tpr, _ = roc_curve(y_bin, probs[:, idx])
                        auc_val = roc_auc_score(y_bin, probs[:, idx])
                        ax.plot(1 - fpr, tpr, label=f"{t}={cls} (AUC {auc_val:.2f})")

                # chance‐lijn en opmaak
                ax.plot([1, 0], [0, 1], ":", lw=1, label="Random Guess")
                ax.set_xlim(1, 0); ax.set_ylim(0, 1)
                ax.set_xlabel("1 - specificity"); ax.set_ylabel("sensitivity")
                ax.set_title(f"ROC – {t}")
                ax.legend(fontsize="small", loc="lower right")
                ax.set_aspect("equal", "box")
                plt.tight_layout()
                if self.tests:
                    fig.savefig(os.path.join(self.tests_dir,
                         f"model_{t}", "plots",
                         f"roc_{t}.png"), dpi=300)
                plt.show()
                plt.close(fig)


        # ===========================================================
        # 4 · LOSS-PLOTS  (per-label, per-backbone)
        # ===========================================================
        if "loss_vs_epoch" in plots:

            # (a) ONE combined figure – colour = label, linestyle = backbone
            fig, ax = plt.subplots(figsize=(7, 4))
            for t, backs in self.train_loss_history.items():
                for bk, tr_hist in backs.items():
                    ax.plot(range(1, len(tr_hist)+1),
                            tr_hist,
                            label=f"{t} – {bk} train")
                    vl_hist = self.val_loss_history[t].get(bk, [])
                    if vl_hist:
                        ax.plot(range(1, len(vl_hist)+1),
                                vl_hist,
                                linestyle="--",
                                label=f"{t} – {bk} val")
            ax.set_xlabel("epoch"); ax.set_ylabel("loss")
            ax.set_title("Loss vs epoch  (all labels & backbones)")
            ax.legend(fontsize="x-small", ncol=2, loc="upper right")
            fig.tight_layout()
            if self.tests:
                fig.savefig(os.path.join(self.tests_dir, "plots", "loss_all_labels.png"),
                            dpi=300)
            plt.show(); plt.close(fig)

            # (b) PER-label grid – every backbone a separate curve
            cols = min(3, len(self.targets))
            rows = math.ceil(len(self.targets) / cols)
            fig, axs = plt.subplots(rows, cols,
                                    figsize=(4*cols, 3.5*rows),
                                    squeeze=False)
            for idx, t in enumerate(self.targets):
                r, c = divmod(idx, cols)
                ax   = axs[r][c]
                for bk, tr_hist in self.train_loss_history[t].items():
                    ax.plot(range(1, len(tr_hist)+1),
                            tr_hist,
                            label=f"{bk} train")
                    vl_hist = self.val_loss_history[t].get(bk, [])
                    if vl_hist:
                        ax.plot(range(1, len(vl_hist)+1),
                                vl_hist,
                                linestyle="--",
                                label=f"{bk} val")
                ax.set_title(t); ax.set_xlabel("epoch"); ax.set_ylabel("loss")
                ax.legend(fontsize="x-small", loc="upper right")
            # blank panels off
            for blank in range(len(self.targets), rows*cols):
                r, c = divmod(blank, cols)
                axs[r][c].axis("off")
            fig.tight_layout()
            if self.tests:
                fig.savefig(os.path.join(self.tests_dir, "plots", "loss_per_label.png"),
                            dpi=300)
            plt.show(); plt.close(fig)


        # ===========================================================
        # 5 · LR-schema
        # ===========================================================
        if "lr_vs_epoch" in plots and getattr(self, "lr_history", None):
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(range(1, len(self.lr_history) + 1), self.lr_history)
            ax.set_xlabel("epoch"); ax.set_ylabel("learning rate")
            ax.set_title("LR schedule")
            fig.tight_layout()
            if self.tests:
                for t in self.targets:
                    fig.savefig(os.path.join(
                        self.tests_dir, f"model_{t}", "plots",
                        "lr.png"), dpi=300)
            plt.show(); plt.close(fig)

        # ===========================================================
        # 6 · CORRELATIE HEAT-MAP (true labels)
        # ===========================================================
        if "correlation" in plots:
            merged = pd.concat(predict_dfs.values())[self.targets].astype(float)
            corr   = merged.corr()

            base   = 1.2 * n_labels
            fig_sz = max(4, base)
            fig, ax = plt.subplots(figsize=(fig_sz, fig_sz))
            sns.heatmap(corr, annot=True, cmap="coolwarm",
                        vmin=-1, vmax=1, ax=ax, fmt=".2f",
                        linewidths=.5, square=True)
            ax.set_title("Correlation of true labels")
            fig.tight_layout()
            if self.tests:
                fig.savefig(os.path.join(self.tests_dir, "plots", "corr.png"), dpi=300)
            plt.show(); plt.close(fig)

        # ===========================================================
        # 7 · CLASS IMBALANCE GRID
        # ===========================================================
        if "class_imbalance" in plots:
            merged = pd.concat(predict_dfs.values())
            max_cols = 3
            cols     = min(max_cols, n_labels)
            rows     = math.ceil(n_labels / cols)

            fig, axs = plt.subplots(rows, cols,
                                    figsize=(4 * cols, 4 * rows),
                                    squeeze=False)
            for idx, t in enumerate(self.targets):
                r, c = divmod(idx, cols)
                ax   = axs[r][c]
                counts = merged[t].value_counts().sort_index()
                ax.bar(counts.index.astype(str), counts.values)
                ax.set_title(f"{t} (n={int(counts.sum())})", fontsize=9)
                ax.set_xlabel("class"); ax.set_ylabel("count")

            # lege subplots verbergen
            for blank in range(n_labels, rows * cols):
                r, c = divmod(blank, cols)
                axs[r][c].axis("off")

            fig.tight_layout()
            if self.tests:
                fig.savefig(os.path.join(self.tests_dir, "plots", "imbalance_grid.png"), dpi=300)
            plt.show(); plt.close(fig)

        # ────────────────────────────────────────────────────────────
        return results_df






    #  SAVE / LOAD
    def save(self, file_path: str | Path) -> None:
        """Bewaar complete model- en configuratiestaat.

        Als ``file_path`` een directory is, worden de gewichten per label
        afzonderlijk opgeslagen naast een ``pipeline_full.pt`` met de
        configuratie.  Wordt een pad naar een enkel bestand opgegeven, dan
        wordt alles daarin gebundeld.
        """

        import dataclasses

        path = Path(file_path)
        is_dir = path.suffix == "" or path.is_dir()
        if is_dir:
            path.mkdir(parents=True, exist_ok=True)
            meta_path = path / "pipeline_full.pt"
        else:
            meta_path = path

        state: Dict[str, Any] = {
            "out_dims": self.out_dims,
            "targets": self.targets,
            "train_cfg": dataclasses.asdict(self.train_cfg),
            "pre_cfg": dataclasses.asdict(self.pre_cfg),
            "best_backbone": self.best_backbone,
            "all_states": self.all_states,
        }

        if "_multi" in self.models:
            state["multi_state"] = self.models["_multi"].state_dict()
        else:
            state["models"] = {t: m.state_dict() for t, m in self.models.items()}

        torch.save(state, meta_path)

        if is_dir:
            if "_multi" in self.models:
                torch.save(self.models["_multi"].state_dict(), path / "model_multi.pt")
            else:
                for t, m in self.models.items():
                    torch.save(m.state_dict(), path / f"model_{t}.pt")

    def load(self, file_path: str | Path) -> None:
        """Laad een model dat eerder met :py:meth:`save` is opgeslagen.

        Zowel het gebundelde formaat (één bestand) als de directoryvariant
        worden ondersteund.
        """

        path = Path(file_path)
        if path.is_dir() or path.suffix == "":
            ckpt_path = path / "pipeline_full.pt"
            ckpt = torch.load(ckpt_path, map_location=self.device)
            if "multi_state" not in ckpt and (path / "model_multi.pt").exists():
                ckpt["multi_state"] = torch.load(path / "model_multi.pt", map_location=self.device)
            if "models" not in ckpt:
                model_dict: Dict[str, Any] = {}
                for t in ckpt.get("targets", []):
                    f = path / f"model_{t}.pt"
                    if f.exists():
                        model_dict[t] = torch.load(f, map_location=self.device)
                if model_dict:
                    ckpt["models"] = model_dict
        else:
            ckpt = torch.load(path, map_location=self.device)
        self.out_dims = ckpt["out_dims"]
        self.targets = ckpt.get("targets", self.targets)

        # Restore configs but keep current device setting
        if "train_cfg" in ckpt:
            cfg = TrainConfig(**ckpt["train_cfg"])
            cfg.device = self.train_cfg.device  # keep runtime device
            self.train_cfg = cfg
            self.device = torch.device(cfg.device)
        if "pre_cfg" in ckpt:
            self.pre_cfg = PreprocessConfig(**ckpt["pre_cfg"])

        self.best_backbone = ckpt.get("best_backbone", {})
        self.all_states = ckpt.get("all_states", {})

        self.models = {}
        if "multi_state" in ckpt:
            bb_dummy, nf_dummy = backbone(self.train_cfg.pretrained_models[0], pretrained=False)
            multi_model = MultiHead(
                bb=bb_dummy,
                nf=nf_dummy,
                out_dims=self.out_dims,
                proj_dim=0,
                dropout_rate=(self.train_cfg.dropout_rate
                              if getattr(self.train_cfg, "dropout", False) else None),
            )
            multi_model.load_state_dict(ckpt["multi_state"])
            multi_model.to(self.device).eval()
            self.models["_multi"] = multi_model
        elif "models" in ckpt:
            for t, sd in ckpt["models"].items():
                out_dim = self.out_dims[t]
                bb_name = ckpt.get("best_backbone", {}).get(t, self.train_cfg.pretrained_models[0])
                bb_dummy, nf_dummy = backbone(bb_name, pretrained=False)
                model = SingleHead(
                    bb_dummy,
                    nf_dummy,
                    out_dim,
                    proj_dim=0,
                    dropout_rate=(self.train_cfg.dropout_rate
                                  if getattr(self.train_cfg, "dropout", False) else None),
                )
                model.load_state_dict(sd)
                model.to(self.device).eval()
                self.models[t] = model