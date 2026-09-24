"""
SnapStyle Object Detection Ensemble Module
Powered by a complementary dual-detector architecture:
1. DeepFashion2 YOLOv8s: Specialized apparel detector trained on DeepFashion2 (13 fine-grained
   clothing classes: shirts, outwear, vests, slings, trousers, shorts, skirts, dresses).
2. COCO YOLOv8n: General vision detector specialized in accessories (handbags, backpacks, ties,
   suitcases, umbrellas) and person silhouette fallback.

Features:
- Dual model caching via singleton loaders (`get_deepfashion2_model()`, `get_yolo_model()`).
- Intelligent detection merging & Non-Maximum Suppression (IoU deduplication) preventing duplicate boxes.
- Precise attribution metadata: `detection_source` ('deepfashion2_yolo' vs 'coco_yolo' vs 'demo_fallback'),
  `model_name` ('yolov8s-seg-deepfashion2' vs 'yolov8n' vs 'prototype_reference'), and authentic confidence.
- Safe prototype fallback if both detectors yield no usable detections or demo is requested.
- Crop thumbnail generation for downstream Transformers CLIP embeddings and FAISS similarity search.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from PIL import Image

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    from huggingface_hub import hf_hub_download
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

# Cached model singleton instances
_yolo_coco_model = None
_deepfashion2_model = None


def get_yolo_model():
    """
    Initializes and caches the standard COCO YOLOv8 model once in memory (singleton pattern).
    Used for accessory detection (handbags, backpacks, ties) and person silhouette fallback.
    """
    global _yolo_coco_model
    if not YOLO_AVAILABLE:
        print("[SnapStyle Detection] Warning: Ultralytics YOLO library is not available.")
        return None

    if _yolo_coco_model is None:
        try:
            base_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(base_dir)
            candidate_paths = [
                os.path.join(project_root, "yolov8n.pt"),
                os.path.join(base_dir, "yolov8n.pt"),
                os.path.abspath("yolov8n.pt"),
                "yolov8n.pt"
            ]
            model_path = next((p for p in candidate_paths if os.path.exists(p)), "yolov8n.pt")
            print(f"[SnapStyle Detection] Initializing COCO YOLO model from: {model_path}")
            _yolo_coco_model = YOLO(model_path)
            print("[SnapStyle Detection] COCO YOLO model successfully loaded and cached in memory.")
        except Exception as e:
            print(f"[SnapStyle Detection] Notice: COCO YOLO model load error: {e}")
            _yolo_coco_model = None

    return _yolo_coco_model


def get_deepfashion2_model():
    """
    Initializes and caches the fashion-specific DeepFashion2 YOLOv8s model once in memory.
    Specialized for fine-grained garment apparel (tops, trousers, skirts, dresses, outwear).
    """
    global _deepfashion2_model
    if not YOLO_AVAILABLE:
        print("[SnapStyle Detection] Warning: Ultralytics YOLO library is not available.")
        return None

    if _deepfashion2_model is None:
        try:
            base_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(base_dir)
            local_model_path = os.path.join(project_root, "data", "models", "deepfashion2_yolov8s-seg.pt")

            if os.path.exists(local_model_path):
                print(f"[SnapStyle Detection] Loading DeepFashion2 model from local cache: {local_model_path}")
                _deepfashion2_model = YOLO(local_model_path)
            elif HF_AVAILABLE:
                print("[SnapStyle Detection] Fetching DeepFashion2 model from Hugging Face Hub (Bingsu/adetailer)...")
                models_dir = os.path.join(project_root, "data", "models")
                os.makedirs(models_dir, exist_ok=True)
                downloaded_path = hf_hub_download(
                    repo_id="Bingsu/adetailer",
                    filename="deepfashion2_yolov8s-seg.pt",
                    local_dir=models_dir
                )
                _deepfashion2_model = YOLO(downloaded_path)
            else:
                print("[SnapStyle Detection] DeepFashion2 weights not found and HF Hub unavailable.")
                return None

            print("[SnapStyle Detection] DeepFashion2 YOLOv8s model successfully loaded and cached in memory.")
        except Exception as e:
            print(f"[SnapStyle Detection] Notice: DeepFashion2 model load error: {e}")
            _deepfashion2_model = None

    return _deepfashion2_model


# DeepFashion2 13 garment categories mapped to SnapStyle taxonomy
DEEPFASHION2_CLASSES: Dict[str, Dict[str, str]] = {
    "short_sleeved_shirt": {
        "category": "top",
        "label": "Short-Sleeved Shirt",
        "attributes": "DeepFashion2 detection: Short-sleeved shirt / top",
        "catalog_filter": "top"
    },
    "long_sleeved_shirt": {
        "category": "top",
        "label": "Long-Sleeved Shirt",
        "attributes": "DeepFashion2 detection: Long-sleeved button-up shirt",
        "catalog_filter": "top"
    },
    "short_sleeved_outwear": {
        "category": "jacket",
        "label": "Short-Sleeved Jacket",
        "attributes": "DeepFashion2 detection: Short-sleeved outwear / light jacket",
        "catalog_filter": "jacket"
    },
    "long_sleeved_outwear": {
        "category": "jacket",
        "label": "Jacket / Trench Coat",
        "attributes": "DeepFashion2 detection: Structured outwear / coat / jacket",
        "catalog_filter": "jacket"
    },
    "vest": {
        "category": "top",
        "label": "Vest",
        "attributes": "DeepFashion2 detection: Vest / sleeveless garment",
        "catalog_filter": "top"
    },
    "sling": {
        "category": "top",
        "label": "Sleeveless Top / Camisole",
        "attributes": "DeepFashion2 detection: Sling / sleeveless top",
        "catalog_filter": "top"
    },
    "shorts": {
        "category": "bottom",
        "label": "Shorts",
        "attributes": "DeepFashion2 detection: Tailored shorts / casual shorts",
        "catalog_filter": "bottom"
    },
    "trousers": {
        "category": "bottom",
        "label": "Trousers / Denim Jeans",
        "attributes": "DeepFashion2 detection: Trousers / straight-leg denim jeans",
        "catalog_filter": "bottom"
    },
    "skirt": {
        "category": "bottom",
        "label": "Skirt",
        "attributes": "DeepFashion2 detection: Skirt / pleated maxi skirt",
        "catalog_filter": "bottom"
    },
    "short_sleeved_dress": {
        "category": "dress",
        "label": "Short-Sleeved Dress",
        "attributes": "DeepFashion2 detection: Short-sleeved dress",
        "catalog_filter": "dress"
    },
    "long_sleeved_dress": {
        "category": "dress",
        "label": "Long-Sleeved Dress",
        "attributes": "DeepFashion2 detection: Long-sleeved dress",
        "catalog_filter": "dress"
    },
    "vest_dress": {
        "category": "dress",
        "label": "Vest Dress",
        "attributes": "DeepFashion2 detection: Vest dress / sleeveless dress",
        "catalog_filter": "dress"
    },
    "sling_dress": {
        "category": "dress",
        "label": "Slip Dress",
        "attributes": "DeepFashion2 detection: Sling / slip dress",
        "catalog_filter": "dress"
    }
}

# 7 Standard SnapStyle Catalog Categories
VALID_CATALOG_CATEGORIES = {"top", "bottom", "jacket", "bag", "shoes", "accessories", "dress"}

def map_detected_item_to_catalog_category(item: Dict[str, Any]) -> str:
    """
    Deterministically maps a detected fashion item to one of the 7 catalog categories:
    ['top', 'bottom', 'jacket', 'bag', 'shoes', 'accessories', 'dress'].
    Ensures strict category filtering before FAISS similarity search.
    """
    raw_class = str(item.get("raw_class", "")).lower().strip()
    label = str(item.get("label", "")).lower().strip()
    category = str(item.get("category", "")).lower().strip()
    catalog_filter = str(item.get("catalog_filter", "")).lower().strip()

    # Direct match if already valid catalog category (other than 'all' or 'person')
    if catalog_filter in VALID_CATALOG_CATEGORIES:
        return catalog_filter

    text = f"{raw_class} {label} {category}"

    # Jacket / Outerwear
    if any(k in text for k in ["jacket", "coat", "trench", "blazer", "outwear", "puffer", "parka", "shacket", "bomber"]):
        return "jacket"

    # Bottoms (jeans, trousers, skirts, shorts)
    if any(k in text for k in ["trouser", "jean", "bottom", "short", "skirt", "pant", "chino", "culotte"]):
        return "bottom"

    # Dresses
    if "dress" in text:
        return "dress"

    # Bags
    if any(k in text for k in ["bag", "tote", "handbag", "backpack", "crossbody", "clutch", "purse", "suitcase"]):
        return "bag"

    # Shoes / Footwear
    if any(k in text for k in ["shoe", "loafer", "sneaker", "boot", "sandal", "flat", "mule", "heel", "slide", "pump", "jutti"]):
        return "shoes"

    # Accessories
    if any(k in text for k in ["sunglass", "earring", "necklace", "belt", "scarf", "watch", "tie", "umbrella", "jewel", "access"]):
        return "accessories"

    # Tops / Shirts / Blouses / Vests
    if any(k in text for k in ["shirt", "top", "blouse", "tee", "t-shirt", "sweater", "cardigan", "camisole", "vest", "polo", "kurta", "sling"]):
        return "top"

    if category in VALID_CATALOG_CATEGORIES:
        return category

    return "top"

# Accessory and wearable classes handled by the COCO detector
COCO_ACCESSORY_CLASSES: Dict[str, Dict[str, str]] = {
    "handbag": {
        "category": "bag",
        "label": "Handbag",
        "attributes": "Real YOLOv8 detection: Handbag / Structured tote",
        "catalog_filter": "bag"
    },
    "backpack": {
        "category": "bag",
        "label": "Backpack",
        "attributes": "Real YOLOv8 detection: Backpack / Daypack",
        "catalog_filter": "bag"
    },
    "suitcase": {
        "category": "bag",
        "label": "Suitcase",
        "attributes": "Real YOLOv8 detection: Suitcase / Travel luggage",
        "catalog_filter": "bag"
    },
    "tie": {
        "category": "accessories",
        "label": "Tie",
        "attributes": "Real YOLOv8 detection: Necktie / Formal wear accessory",
        "catalog_filter": "accessories"
    },
    "umbrella": {
        "category": "accessories",
        "label": "Umbrella",
        "attributes": "Real YOLOv8 detection: Umbrella accessory",
        "catalog_filter": "accessories"
    }
}


def compute_box_iou(boxA: List[float], boxB: List[float]) -> float:
    """
    Computes the Intersection over Union (IoU) between two normalized boxes.
    Box format: [ymin, xmin, ymax, xmax].
    """
    yA = max(boxA[0], boxB[0])
    xA = max(boxA[1], boxB[1])
    yB = min(boxA[2], boxB[2])
    xB = min(boxA[3], boxB[3])

    interWidth = max(0.0, xB - xA)
    interHeight = max(0.0, yB - yA)
    interArea = interWidth * interHeight

    areaA = max(0.0, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    areaB = max(0.0, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    unionArea = areaA + areaB - interArea
    if unionArea <= 0.0:
        return 0.0
    return interArea / unionArea


# Standard reference prototype detections (matching Google Stitch demo screens)
# Explicitly marked as demo_fallback so they are never confused with real YOLO inference.
PROTOTYPE_FALLBACK_ITEMS: List[Dict[str, Any]] = [
    {
        "item_id": "det_top_01",
        "category": "top",
        "label": "White Oversized Shirt",
        "attributes": "Cotton, Button-down, Relaxed fit",
        "confidence": 0.96,
        "bbox": [0.18, 0.28, 0.52, 0.72],
        "hotspot": {"top": 35.0, "left": 48.0},
        "is_fallback": True,
        "detection_source": "demo_fallback",
        "model_name": "prototype_reference",
        "raw_class": "demo_prototype",
        "catalog_filter": "top"
    },
    {
        "item_id": "det_bottom_02",
        "category": "bottom",
        "label": "Light Wash Straight Jeans",
        "attributes": "Denim, Straight leg, High-rise",
        "confidence": 0.94,
        "bbox": [0.48, 0.32, 0.88, 0.68],
        "hotspot": {"top": 66.0, "left": 50.0},
        "is_fallback": True,
        "detection_source": "demo_fallback",
        "model_name": "prototype_reference",
        "raw_class": "demo_prototype",
        "catalog_filter": "bottom"
    },
    {
        "item_id": "det_bag_03",
        "category": "bag",
        "label": "Structured Beige Tote",
        "attributes": "Leather, Minimalist, Top handle",
        "confidence": 0.92,
        "bbox": [0.42, 0.15, 0.72, 0.38],
        "hotspot": {"top": 54.0, "left": 26.0},
        "is_fallback": True,
        "detection_source": "demo_fallback",
        "model_name": "prototype_reference",
        "raw_class": "demo_prototype",
        "catalog_filter": "bag"
    },
    {
        "item_id": "det_shoes_04",
        "category": "shoes",
        "label": "Classic Leather Loafers",
        "attributes": "Calfskin leather, Penny loafer, Brown",
        "confidence": 0.88,
        "bbox": [0.85, 0.38, 0.98, 0.62],
        "hotspot": {"top": 92.0, "left": 48.0},
        "is_fallback": True,
        "detection_source": "demo_fallback",
        "model_name": "prototype_reference",
        "raw_class": "demo_prototype",
        "catalog_filter": "shoes"
    }
]


def detect_fashion_items(
    pil_img: Image.Image,
    upload_id: str,
    crops_dir: str,
    conf_threshold: float = 0.20,
    force_fallback: bool = False
) -> List[Dict[str, Any]]:
    """
    Executes the complementary dual-detector fashion ensemble:
    1. DeepFashion2 YOLOv8s extracts fine-grained garments (tops, outwear, trousers, skirts, dresses).
    2. COCO YOLOv8n extracts accessories (handbags, backpacks, ties) and person silhouette fallback.
    3. Merges detections with intelligent Non-Maximum Suppression (IoU deduplication) preventing overlaps.
    4. Tags each detection with its exact model source and authentic confidence score.
    5. Falls back cleanly to prototype reference items if 0 objects are detected or demo requested.
    6. Crops and stores thumbnails for visual embedding extraction.
    """
    detected_items: List[Dict[str, Any]] = []
    is_demo_request = (upload_id == "demo" or force_fallback)

    if not is_demo_request:
        garment_items: List[Dict[str, Any]] = []
        accessory_items: List[Dict[str, Any]] = []

        # =====================================================================
        # STAGE 1: DeepFashion2 Apparel Detection (Garments Specialist)
        # =====================================================================
        df2_model = get_deepfashion2_model()
        if df2_model is not None:
            try:
                df2_results = df2_model.predict(source=pil_img, conf=conf_threshold, verbose=False)
                if df2_results and len(df2_results) > 0:
                    boxes = df2_results[0].boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        cls_name = df2_model.names.get(cls_id, "").lower()
                        conf = round(float(box.conf[0].item()), 3)

                        if cls_name not in DEEPFASHION2_CLASSES:
                            continue

                        meta = DEEPFASHION2_CLASSES[cls_name]
                        xyxyn = box.xyxyn[0].tolist()  # [xmin, ymin, xmax, ymax]
                        xmin, ymin, xmax, ymax = xyxyn

                        # Clamp normalized coordinates to [0.0, 1.0]
                        xmin = max(0.0, min(1.0, xmin))
                        ymin = max(0.0, min(1.0, ymin))
                        xmax = max(0.0, min(1.0, xmax))
                        ymax = max(0.0, min(1.0, ymax))

                        category = meta["category"]
                        item_id = f"det_{category}_{uuid.uuid4().hex[:6]}"

                        hotspot_top = round(((ymin + ymax) / 2.0) * 100.0, 1)
                        hotspot_left = round(((xmin + xmax) / 2.0) * 100.0, 1)

                        garment_items.append({
                            "item_id": item_id,
                            "category": category,
                            "label": meta["label"],
                            "attributes": f"DeepFashion2: {meta['label']} ({int(conf * 100)}% conf)",
                            "confidence": conf,
                            "bbox": [round(ymin, 4), round(xmin, 4), round(ymax, 4), round(xmax, 4)],
                            "hotspot": {"top": hotspot_top, "left": hotspot_left},
                            "is_fallback": False,
                            "detection_source": "deepfashion2_yolo",
                            "model_name": "yolov8s-seg-deepfashion2",
                            "raw_class": cls_name,
                            "catalog_filter": meta.get("catalog_filter", category)
                        })

                print(f"[SnapStyle Ensemble] DeepFashion2 detected {len(garment_items)} garment(s).")
            except Exception as e:
                print(f"[SnapStyle Ensemble] DeepFashion2 inference error: {e}")

        # =====================================================================
        # STAGE 2: COCO Vision Detection (Accessories & Fallback Specialist)
        # =====================================================================
        coco_model = get_yolo_model()
        coco_person_item = None

        if coco_model is not None:
            try:
                coco_results = coco_model.predict(source=pil_img, conf=conf_threshold, verbose=False)
                if coco_results and len(coco_results) > 0:
                    boxes = coco_results[0].boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        cls_name = coco_model.names.get(cls_id, "").lower()
                        conf = round(float(box.conf[0].item()), 3)

                        xyxyn = box.xyxyn[0].tolist()
                        xmin, ymin, xmax, ymax = xyxyn
                        xmin = max(0.0, min(1.0, xmin))
                        ymin = max(0.0, min(1.0, ymin))
                        xmax = max(0.0, min(1.0, xmax))
                        ymax = max(0.0, min(1.0, ymax))

                        bbox = [round(ymin, 4), round(xmin, 4), round(ymax, 4), round(xmax, 4)]
                        hotspot_top = round(((ymin + ymax) / 2.0) * 100.0, 1)
                        hotspot_left = round(((xmin + xmax) / 2.0) * 100.0, 1)

                        if cls_name in COCO_ACCESSORY_CLASSES:
                            meta = COCO_ACCESSORY_CLASSES[cls_name]
                            category = meta["category"]
                            item_id = f"det_{category}_{uuid.uuid4().hex[:6]}"

                            accessory_items.append({
                                "item_id": item_id,
                                "category": category,
                                "label": meta["label"],
                                "attributes": f"COCO YOLO: {meta['label']} ({int(conf * 100)}% conf)",
                                "confidence": conf,
                                "bbox": bbox,
                                "hotspot": {"top": hotspot_top, "left": hotspot_left},
                                "is_fallback": False,
                                "detection_source": "coco_yolo",
                                "model_name": "yolov8n",
                                "raw_class": cls_name,
                                "catalog_filter": meta.get("catalog_filter", category)
                            })
                        elif cls_name == "person" and coco_person_item is None:
                            # Keep highest-confidence person silhouette as potential fallback
                            coco_person_item = {
                                "item_id": f"det_person_{uuid.uuid4().hex[:6]}",
                                "category": "person",
                                "label": "Person (Full Outfit Look)",
                                "attributes": f"COCO YOLO: Person Silhouette ({int(conf * 100)}% conf)",
                                "confidence": conf,
                                "bbox": bbox,
                                "hotspot": {"top": hotspot_top, "left": hotspot_left},
                                "is_fallback": False,
                                "detection_source": "coco_yolo",
                                "model_name": "yolov8n",
                                "raw_class": "person",
                                "catalog_filter": "all"
                            }

                print(f"[SnapStyle Ensemble] COCO detected {len(accessory_items)} accessory item(s).")
            except Exception as e:
                print(f"[SnapStyle Ensemble] COCO inference error: {e}")

        # =====================================================================
        # STAGE 3: Ensemble Fusion & Non-Maximum Suppression (NMS)
        # =====================================================================
        # 1. Garment Deduplication: Filter overlapping duplicate boxes within same category
        garment_items.sort(key=lambda x: x["confidence"], reverse=True)
        deduped_garments: List[Dict[str, Any]] = []

        for g in garment_items:
            keep = True
            for existing in deduped_garments:
                # Deduplicate if same category with IoU > 0.50
                if g["category"] == existing["category"]:
                    iou = compute_box_iou(g["bbox"], existing["bbox"])
                    if iou > 0.50:
                        keep = False
                        break
                # Special case: outwear vs shirt overlap (if outwear completely overlaps shirt with IoU > 0.70)
                if ("outwear" in g["raw_class"] and "shirt" in existing["raw_class"]) or \
                   ("shirt" in g["raw_class"] and "outwear" in existing["raw_class"]):
                    iou = compute_box_iou(g["bbox"], existing["bbox"])
                    if iou > 0.70:
                        keep = False
                        break
            if keep:
                deduped_garments.append(g)

        # 2. Accessory Deduplication: Filter overlapping duplicate accessories
        accessory_items.sort(key=lambda x: x["confidence"], reverse=True)
        deduped_accessories: List[Dict[str, Any]] = []
        for a in accessory_items:
            keep = True
            for existing in deduped_accessories:
                if a["category"] == existing["category"]:
                    iou = compute_box_iou(a["bbox"], existing["bbox"])
                    if iou > 0.50:
                        keep = False
                        break
            if keep:
                deduped_accessories.append(a)

        # 3. Combine Garments + Accessories
        detected_items.extend(deduped_garments)
        detected_items.extend(deduped_accessories)

        # 4. If 0 garments detected, but person silhouette was detected, include person
        if not deduped_garments and coco_person_item is not None:
            detected_items.append(coco_person_item)
            print("[SnapStyle Ensemble] No specific garments detected: included COCO person silhouette.")

    # =====================================================================
    # STAGE 4: Prototype Fallback Activation
    # =====================================================================
    if not detected_items:
        if is_demo_request:
            print("[SnapStyle Ensemble] Demo mode requested: using verified prototype fallback items.")
        else:
            print("[SnapStyle Ensemble] No fashion objects detected by ensemble: falling back to prototype items.")

        detected_items = [dict(item) for item in PROTOTYPE_FALLBACK_ITEMS]

    # =====================================================================
    # STAGE 5: Save Item Crops for CLIP & FAISS
    # =====================================================================
    os.makedirs(crops_dir, exist_ok=True)
    from backend.image_processing import crop_item_box

    for item in detected_items:
        crop_name = f"crop_{upload_id}_{item['item_id']}.jpg"
        crop_path = os.path.join(crops_dir, crop_name)
        try:
            cropped = crop_item_box(pil_img, item["bbox"])
            cropped.save(crop_path, "JPEG", quality=90)
            item["crop_url"] = f"/uploads/crops/{crop_name}"
            item["crop_path"] = crop_path
        except Exception as e:
            print(f"[SnapStyle Ensemble] Notice cropping item {item['item_id']}: {e}")
            item["crop_url"] = ""

    return detected_items
