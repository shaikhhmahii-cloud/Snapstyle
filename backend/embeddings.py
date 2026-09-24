"""
SnapStyle Visual Embeddings Module
Powered by Hugging Face Transformers CLIP (Vision Transformer).
- Loads a suitable CLIP model once in memory (cached singleton pattern).
- Generates 512-dimensional L2-normalized visual feature embeddings for outfit images and catalog items.
- Supports both deep learning CLIP vision features and fallback deterministic visual features.
- Enables exact cosine similarity vector search with FAISS IndexFlatIP.
"""

import os
import hashlib
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, Optional

try:
    import torch
    import transformers
    from transformers import CLIPProcessor, CLIPModel, CLIPVisionModelWithProjection
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Cached CLIP singleton model and processor instances
_clip_model = None
_clip_processor = None
_clip_model_name = "wkcn/TinyCLIP-ViT-8M-16-Text-3M-YFCC15M"
EMBEDDING_DIM = 512

def get_clip_model():
    """
    Initializes and caches the Transformers CLIP model and processor once in memory.
    Subsequent calls return the cached singleton instances instantly.
    """
    global _clip_model, _clip_processor, _clip_model_name
    if not TRANSFORMERS_AVAILABLE:
        print("[SnapStyle Embeddings] Notice: Transformers/PyTorch is not available.")
        return None, None

    if os.environ.get("SNAPSTYLE_FORCE_FAST_EMBED", "0") == "1":
        return None, None

    if _clip_model is None:
        # Candidate model repositories (local cache first, then fallback)
        candidate_models = [
            "wkcn/TinyCLIP-ViT-8M-16-Text-3M-YFCC15M",
            "openai/clip-vit-base-patch32"
        ]

        for model_id in candidate_models:
            try:
                print(f"[SnapStyle Embeddings] Loading CLIP model from: {model_id}...")
                # First attempt loading from local cache
                try:
                    processor = CLIPProcessor.from_pretrained(model_id, local_files_only=True)
                    model = CLIPModel.from_pretrained(model_id, local_files_only=True)
                except Exception:
                    # If not yet in cache, load normally
                    processor = CLIPProcessor.from_pretrained(model_id)
                    model = CLIPModel.from_pretrained(model_id)

                model.eval()
                _clip_model = model
                _clip_processor = processor
                _clip_model_name = model_id
                print(f"[SnapStyle Embeddings] Successfully loaded real CLIP model: {model_id} (Dim: {EMBEDDING_DIM})")
                break
            except Exception as e:
                print(f"[SnapStyle Embeddings] Could not load {model_id}: {e}")
                continue

    return _clip_model, _clip_processor

def is_real_clip_loaded() -> bool:
    """Returns True if a real Transformers CLIP model is loaded and ready."""
    model, processor = get_clip_model()
    return model is not None and processor is not None

def get_clip_model_info() -> Dict[str, Any]:
    """Returns detailed metadata about the active visual embedding model."""
    model, _ = get_clip_model()
    is_real = model is not None
    return {
        "model_name": _clip_model_name if is_real else "deterministic_visual_projection",
        "model_type": "Transformers CLIP (ViT-8M/16)" if is_real else "deterministic_fallback",
        "embedding_dimension": EMBEDDING_DIM,
        "is_real_clip": is_real,
        "source": "real_clip" if is_real else "fallback",
        "device": "cpu"
    }

def compute_deterministic_visual_embedding(pil_img: Image.Image, category_hint: str = "") -> np.ndarray:
    """
    Fallback deterministic 512-dimensional visual feature vector based on:
    - Dominant color distribution (RGB & HSV)
    - 8x8 spatial luminance moments
    - Edge gradients and color histogram
    - Stable perceptual seed projection
    Returns an L2-normalized float32 vector of shape (512,).
    """
    img = pil_img.convert("RGB").resize((64, 64))
    arr = np.array(img, dtype=np.float32) / 255.0

    mean = np.mean(arr, axis=(0, 1))
    std = np.std(arr, axis=(0, 1))

    gray = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]
    blocks = gray.reshape(8, 8, 8, 8).mean(axis=(1, 3)).flatten()

    diff_x = np.abs(np.diff(gray, axis=1)).mean(axis=1)
    diff_y = np.abs(np.diff(gray, axis=0)).mean(axis=0)

    r_bins = np.digitize(arr[:, :, 0], np.linspace(0, 1, 5)) - 1
    g_bins = np.digitize(arr[:, :, 1], np.linspace(0, 1, 5)) - 1
    b_bins = np.digitize(arr[:, :, 2], np.linspace(0, 1, 5)) - 1
    hist, _ = np.histogramdd((r_bins.flatten(), g_bins.flatten(), b_bins.flatten()), bins=(4, 4, 4))
    hist = hist.flatten() / (hist.sum() + 1e-6)

    thumb = pil_img.resize((16, 16)).tobytes()
    seed_int = int(hashlib.md5(thumb + category_hint.encode()).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed_int)
    random_projection = rng.randn(512)

    vec = np.zeros(512, dtype=np.float32)
    vec[:3] = mean
    vec[3:6] = std
    vec[10:74] = blocks
    vec[80:144] = hist
    vec[150:214] = np.resize(diff_x, 64)
    vec[220:284] = np.resize(diff_y, 64)
    vec += random_projection * 0.2

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    return vec.astype(np.float32)

def generate_image_embedding(pil_img: Image.Image, category_hint: str = "") -> np.ndarray:
    """
    Generates an L2-normalized 512-dimensional visual embedding vector.
    Uses the real Transformers CLIP model if available; otherwise falls back gracefully.
    """
    emb, _ = generate_image_embedding_with_meta(pil_img, category_hint)
    return emb

def generate_image_embedding_with_meta(
    pil_img: Image.Image,
    category_hint: str = ""
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Generates an L2-normalized 512-dimensional visual embedding vector and metadata.
    Returns: (embedding_numpy_array, metadata_dict)
    """
    model, processor = get_clip_model()
    rgb_img = pil_img.convert("RGB")

    if model is not None and processor is not None:
        try:
            inputs = processor(images=rgb_img, return_tensors="pt")
            with torch.no_grad():
                # Extract image features from CLIP model
                outputs = model.get_image_features(pixel_values=inputs["pixel_values"])
                
                # Extract tensor whether returned as container or raw tensor
                if hasattr(outputs, "pooler_output") and outputs.pooler_output is not None:
                    raw_tensor = outputs.pooler_output
                elif hasattr(outputs, "image_embeds") and outputs.image_embeds is not None:
                    raw_tensor = outputs.image_embeds
                elif isinstance(outputs, torch.Tensor):
                    raw_tensor = outputs
                else:
                    raw_tensor = outputs[0]

                features = raw_tensor.cpu().numpy().flatten().astype(np.float32)
                
                # Verify L2 normalization to unit sphere (norm == 1.0)
                norm = float(np.linalg.norm(features))
                if norm > 0:
                    features = features / norm

                meta = {
                    "source": "real_clip",
                    "model_name": _clip_model_name,
                    "embedding_dimension": int(len(features)),
                    "is_real_clip": True,
                    "l2_norm": round(float(np.linalg.norm(features)), 4)
                }
                return features, meta
        except Exception as e:
            print(f"[SnapStyle Embeddings] Real CLIP inference error, using fallback: {e}")

    # Fallback if CLIP is unavailable
    fallback_vec = compute_deterministic_visual_embedding(rgb_img, category_hint)
    meta = {
        "source": "fallback",
        "model_name": "deterministic_visual_projection",
        "embedding_dimension": int(len(fallback_vec)),
        "is_real_clip": False,
        "l2_norm": round(float(np.linalg.norm(fallback_vec)), 4)
    }
    return fallback_vec, meta
