# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
#  0 · Imports
# ---------------------------------------------------------------------------
import random
from pathlib import Path
from typing import Optional

import pandas as pd
import torch
from torchvision import io
import torchvision.transforms.functional as TF
from torchvision.utils import save_image

from .config import PreprocessConfig   # dataclass with transform hyper-params
# ---------------------------------------------------------------------------
#  1 · Low-level transforms
# ---------------------------------------------------------------------------
def elastic_transform(
    image: torch.Tensor,
    alpha: float = 34.0,
    sigma: float = 4.0
) -> torch.Tensor:
    """
    Classic elastic-deformation used in many medical-image papers.
    """
    from scipy.ndimage import gaussian_filter, map_coordinates
    import numpy as np

    image_np = image.numpy()
    shape = image_np.shape[1:]                       # (H, W)

    dx = gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma) * alpha
    dy = gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma) * alpha

    x, y   = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    idx    = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))

    out = np.empty_like(image_np)
    for c in range(image_np.shape[0]):
        out[c] = map_coordinates(image_np[c], idx, order=1, mode="reflect").reshape(shape)

    return torch.tensor(out)


# ---------------------------------------------------------------------------
#  2 · Augmentation switchboard (now incl. “jitter”)
# ---------------------------------------------------------------------------
def _apply_augment(
    t: torch.Tensor,
    method: str,
    rng: random.Random,
    cfg: PreprocessConfig
) -> torch.Tensor:
    """
    Apply ONE augmentation and ALWAYS return a tensor.
    Legal methods: contrast · elastic · contrast_elastic · jitter
    """
    out = t.clone()                                 # safe copy

    # ------------------------- CONTRAST ------------------------- #
    if method == "contrast":
        factor = rng.uniform(cfg.contrast_min, cfg.contrast_max)
        out = TF.adjust_contrast(out, factor)

    # -------------------------- ELASTIC ------------------------- #
    elif method == "elastic":
        out = elastic_transform(
            out,
            alpha = cfg.elastic_alpha,
            sigma = cfg.elastic_sigma,
        )

    # --------------- CONTRAST + ELASTIC (combo) ---------------- #
    elif method == "contrast_elastic":
        factor = rng.uniform(cfg.contrast_min, cfg.contrast_max)
        out = TF.adjust_contrast(out, factor)
        out = elastic_transform(
            out,
            alpha = cfg.elastic_alpha,
            sigma = cfg.elastic_sigma,
        )

    # --------------------------- JITTER ------------------------- #
    elif method == "jitter":
        import torch.nn.functional as F

        # ─── Random shift between 3 and 12 pixels ───
        shift_px  = rng.randint(3, 12)
        axis      = rng.choice(["x", "y"])        # choose horizontal or vertical shift
        direction = rng.choice([-1, 1])           # left/up or right/down

        dx, dy = (direction * shift_px, 0) if axis == "x" else (0, direction * shift_px)

        # ─── Shifted copy ───
        ghost = torch.roll(out, shifts=(dy, dx), dims=(1, 2))

        # ─── Apply soft blur to ghost ───
        kernel = torch.ones((3, 1, 3, 3), device=ghost.device) / 9.0
        blurred = F.conv2d(ghost.unsqueeze(0), kernel, padding=1, groups=3).squeeze(0)

        # ─── Combine via per-pixel min (black wins) ───
        out = torch.minimum(out, blurred)
    elif method == "motion_patch":
        import torch.nn.functional as F

        # 1) Build the usual subtle motion_patch layer
        num_patches = rng.randint(2, 2)      # fixed
        max_offset  = rng.randint(55, 55)    # fixed
        alpha       = 0.25

        ghost = out.clone()
        motion_layer = torch.zeros_like(out)

        for _ in range(num_patches):
            dx = rng.randint(-max_offset, max_offset)
            dy = rng.randint(-max_offset, max_offset)
            shifted = torch.roll(ghost, shifts=(dy, dx), dims=(1, 2))
            motion_only = torch.clamp(shifted - out, min=0.0)
            motion_layer += motion_only

        patched = torch.clamp(out + alpha * motion_layer, 0.0, 1.0)

        # 2) Now add a very small jitter on top of the patched image
        jitter_px  = rng.randint(10, 10)          # tiny 1–2 pixel shake
        axis       = rng.choice(["x", "y"])
        direction  = rng.choice([-1, 1])
        dxj, dyj   = (direction * jitter_px, 0) if axis == "x" else (0, direction * jitter_px)

        jittered = torch.roll(patched, shifts=(dyj, dxj), dims=(1, 2))

        # 3) Blend 90% patched + 10% jitter for a barely-there shake
        out = torch.clamp(0.9 * patched + 0.1 * jittered, 0.0, 1.0)

    return out



# ---------------------------------------------------------------------------
#  3 · Main helper  –  balancing + augmentation
# ---------------------------------------------------------------------------
def augment_and_balance(
    df_in: pd.DataFrame,
    config: PreprocessConfig,
    target_col: str,
    output_dir: str,
    seed: int = 42,
    img_column: str = "img_path"
) -> pd.DataFrame:
    """
    Perform class balancing and/or augmentation as dictated by **config**.
    Returns a *new* dataframe whose rows point to both original and augmented
    PNG files stored under *output_dir*.
    """
    if not config.augment and not config.balance_on:
        return df_in.copy()

    rng        = random.Random(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # 3a · Balancing – naive oversampling to equalise class counts
    # -----------------------------------------------------------------------
    df_bal = df_in.copy()
    if config.balance_on:
        counts     = df_in[target_col].value_counts().to_dict()
        max_count  = max(counts.values())
        for cls, cur in counts.items():
            need = max_count - cur
            pool = df_in[df_in[target_col] == cls]
            extra = pool.sample(n=need, replace=True, random_state=seed)
            df_bal = pd.concat([df_bal, extra], ignore_index=True)
        print(f"{target_col} balanced → {dict(df_bal[target_col].value_counts())}")

    # -----------------------------------------------------------------------
    # 3b · Augmentation loop
    # -----------------------------------------------------------------------
    new_rows = []
    for i, row in df_bal.iterrows():
        pid, sid = int(row["Patient_ID"]), int(row["Series_ID"])
        base     = f"R{pid:04d}_S{sid}_{i}"
        img_path = row[img_column]
        rgb      = io.read_image(img_path, io.ImageReadMode.RGB).float() / 255.

        # Save original image
        orig_fname = output_dir / f"{base}_orig.png"
        save_image(rgb, orig_fname)

        r = row.to_dict()
        r[img_column] = str(orig_fname)
        new_rows.append(r)

        # Synthetic variants
        if config.augment:
            for j in range(config.augment_factor):
                method = rng.choice(config.augment_methods)
                aug_t  = _apply_augment(rgb, method, rng, config)

                fname = output_dir / f"{base}_{method}_{j}.png"
                save_image(aug_t, fname)

                r_aug = row.to_dict()
                r_aug[img_column] = str(fname)
                new_rows.append(r_aug)

    return pd.DataFrame(new_rows)
