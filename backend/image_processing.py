"""
SnapStyle Image Processing Module
Handles image validation, resizing, preprocessing with OpenCV and Pillow,
and focus bracket overlay according to Google Stitch design specs.
"""

import io
import os
import cv2
import numpy as np
from PIL import Image, ImageOps

SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP", "MPO"}

def validate_and_open_image(file_bytes_or_path) -> Image.Image:
    """
    Validates and opens an image from bytes or file path using Pillow.
    Ensures correct orientation (EXIF) and converts RGBA/Palette to RGB.
    """
    try:
        if isinstance(file_bytes_or_path, (str, os.PathLike)):
            img = Image.open(file_bytes_or_path)
        else:
            img = Image.open(io.BytesIO(file_bytes_or_path))
        
        # Check format
        fmt = (img.format or "JPEG").upper()
        if fmt not in SUPPORTED_FORMATS and fmt != "MPO":
            # Allow common formats anyway if Pillow can decode
            pass
        
        # Handle EXIF orientation
        img = ImageOps.exif_transpose(img)
        
        # Convert to standard RGB
        if img.mode != "RGB":
            img = img.convert("RGB")
            
        return img
    except Exception as e:
        raise ValueError(f"Invalid or corrupted image format: {str(e)}")

def resize_image_for_ai(pil_img: Image.Image, max_dim: int = 1024) -> Image.Image:
    """
    Resizes image maintaining aspect ratio using Pillow with high-quality Lanczos resampling.
    """
    width, height = pil_img.size
    if max(width, height) <= max_dim:
        return pil_img
    
    scale = max_dim / max(width, height)
    new_w = int(width * scale)
    new_h = int(height * scale)
    
    return pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Converts PIL RGB Image to OpenCV BGR ndarray."""
    rgb_arr = np.array(pil_img)
    return cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """Converts OpenCV BGR ndarray to PIL RGB Image."""
    rgb_arr = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_arr)

def preprocess_for_detection(pil_img: Image.Image) -> tuple[np.ndarray, Image.Image]:
    """
    Preprocesses image using OpenCV for optimal feature detection:
    - Subtle bilateral filter / noise reduction
    - Contrast and sharpness enhancement
    Returns (cv2_preprocessed_bgr, pil_enhanced_rgb).
    """
    cv2_img = pil_to_cv2(pil_img)
    
    # Mild bilateral filtering to preserve edges while smoothing texture noise
    smoothed = cv2.bilateralFilter(cv2_img, d=5, sigmaColor=50, sigmaSpace=50)
    
    # Mild unsharp masking for crisper clothing boundaries
    gaussian = cv2.GaussianBlur(smoothed, (0, 0), 2.0)
    enhanced = cv2.addWeighted(smoothed, 1.15, gaussian, -0.15, 0)
    
    pil_enhanced = cv2_to_pil(enhanced)
    return enhanced, pil_enhanced

def crop_item_box(pil_img: Image.Image, bbox: list[float], padding_pct: float = 0.05) -> Image.Image:
    """
    Crops a detected fashion component given normalized bbox [ymin, xmin, ymax, xmax].
    Applies small padding and clamps to image dimensions.
    """
    width, height = pil_img.size
    ymin, xmin, ymax, xmax = bbox
    
    pad_h = (ymax - ymin) * padding_pct
    pad_w = (xmax - xmin) * padding_pct
    
    y1 = max(0, int((ymin - pad_h) * height))
    x1 = max(0, int((xmin - pad_w) * width))
    y2 = min(height, int((ymax + pad_h) * height))
    x2 = min(width, int((xmax + pad_w) * width))
    
    # Guard against invalid box
    if x2 <= x1 or y2 <= y1:
        return pil_img
        
    return pil_img.crop((x1, y1, x2, y2))

def draw_focus_brackets(cv2_img: np.ndarray, bbox: list[float], color=(255, 176, 232), thickness=2, arm_len=18) -> np.ndarray:
    """
    Draws editorial focus brackets (signature Google Stitch style) at bbox corners.
    Color default: BGR for Amethyst/Lavender #e8b3ff (RGB: 232, 179, 255 -> BGR: 255, 179, 232)
    """
    h, w = cv2_img.shape[:2]
    ymin, xmin, ymax, xmax = bbox
    x1, y1 = int(xmin * w), int(ymin * h)
    x2, y2 = int(xmax * w), int(ymax * h)
    
    img = cv2_img.copy()
    
    # Top-Left
    cv2.line(img, (x1, y1), (x1 + arm_len, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + arm_len), color, thickness)
    
    # Top-Right
    cv2.line(img, (x2, y1), (x2 - arm_len, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + arm_len), color, thickness)
    
    # Bottom-Left
    cv2.line(img, (x1, y2), (x1 + arm_len, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - arm_len), color, thickness)
    
    # Bottom-Right
    cv2.line(img, (x2, y2), (x2 - arm_len, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - arm_len), color, thickness)
    
    return img
