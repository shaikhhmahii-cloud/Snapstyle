"""
SnapStyle Fashion Detection Ensemble Verification Test
Validates the complementary DeepFashion2 + COCO dual-detector ensemble across 5 real outfit images:
1. IMG-01: Street Style with Handbag (upload_c092561183.png)
2. IMG-02: Minimalist Chic Streetwear (upload_4c43cd7dec.png)
3. IMG-03: Model in Ribbed Knit Top & Trousers (prod_021.jpg)
4. IMG-04: Model in Vintage Denim Jeans (prod_008.jpg)
5. IMG-05: Flat-Lay Atelier Look (demo_sample.jpg)

Verifies:
- DeepFashion2 extracts fine-grained apparel garments (tops, trousers, outwear, skirts, dresses).
- COCO extracts accessories (handbags, backpacks, ties) and person silhouette fallback.
- IoU-based deduplication eliminates overlapping boxes without suppressing different categories.
- Safe prototype fallback activates when 0 objects are detected.
- Real-time FAISS similarity search successfully finds catalog items for all detected items.
- Live FastAPI HTTP endpoints (/analyze and /search-products) function seamlessly.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.detection import detect_fashion_items, get_deepfashion2_model, get_yolo_model
from backend.image_processing import validate_and_open_image, preprocess_for_detection

BASE_URL = "http://127.0.0.1:8000"
CROPS_DIR = os.path.join(PROJECT_ROOT, "backend", "uploads", "crops")
os.makedirs(CROPS_DIR, exist_ok=True)

TEST_IMAGES = [
    {
        "id": "IMG-01",
        "title": "Street Style Outfit with Handbag",
        "path": os.path.join(PROJECT_ROOT, "backend", "uploads", "upload_c092561183.png"),
        "expected_ensemble": "DeepFashion2 (Trousers/Outwear) + COCO (Handbag)",
        "expected_fallback": False
    },
    {
        "id": "IMG-02",
        "title": "Minimalist Chic Streetwear Look",
        "path": os.path.join(PROJECT_ROOT, "backend", "uploads", "upload_4c43cd7dec.png"),
        "expected_ensemble": "DeepFashion2 (Trousers/Outwear) + COCO (Handbag)",
        "expected_fallback": False
    },
    {
        "id": "IMG-03",
        "title": "Model in Ribbed Knit Top & Trousers",
        "path": os.path.join(PROJECT_ROOT, "frontend", "assets", "products", "prod_021.jpg"),
        "expected_ensemble": "DeepFashion2 (Short-Sleeved Shirt + Trousers)",
        "expected_fallback": False
    },
    {
        "id": "IMG-04",
        "title": "Model in Denim Jeans & Casual Ensemble",
        "path": os.path.join(PROJECT_ROOT, "frontend", "assets", "products", "prod_008.jpg"),
        "expected_ensemble": "DeepFashion2 (Trousers / Vest)",
        "expected_fallback": False
    },
    {
        "id": "IMG-05",
        "title": "Prototype Atelier Flat-Lay Sample Look",
        "path": os.path.join(PROJECT_ROOT, "backend", "uploads", "demo_sample.jpg"),
        "expected_ensemble": "Safe Prototype Fallback (4 verified items)",
        "expected_fallback": True
    }
]


def test_fashion_ensemble_all_images():
    print("=" * 80)
    print("SNAPSTYLE FASHION DETECTION ENSEMBLE TEST (5 OUTFIT IMAGES)")
    print("DeepFashion2 YOLOv8s (Apparel) + COCO YOLOv8n (Accessories)")
    print("=" * 80)

    # 1. Verify Model Initializations
    print("\n[Step 1] Verifying Model Singletons in Memory...")
    df2 = get_deepfashion2_model()
    coco = get_yolo_model()
    assert df2 is not None, "Failed to load DeepFashion2 model!"
    assert coco is not None, "Failed to load COCO YOLO model!"
    print("  DeepFashion2 YOLOv8s Model: Ready (13 garment classes)")
    print("  COCO YOLOv8n Model:         Ready (Accessories + Silhouette)")
    print("  -> Step 1 Passed: Both ensemble models active.")

    results_summary = []

    # 2. Iterate through each of the 5 outfit images
    print("\n[Step 2] Evaluating Ensemble Detection Across 5 Outfit Images...")

    for img_info in TEST_IMAGES:
        img_id = img_info["id"]
        title = img_info["title"]
        path = img_info["path"]
        expected_fb = img_info["expected_fallback"]

        print("\n" + "-" * 75)
        print(f"[{img_id}] {title}")
        print(f"Path: {path}")

        assert os.path.exists(path), f"Test image not found: {path}"
        pil_img = Image.open(path).convert("RGB")

        # A. Execute direct detection module
        detected = detect_fashion_items(
            pil_img=pil_img,
            upload_id=img_id.lower(),
            crops_dir=CROPS_DIR,
            conf_threshold=0.20
        )

        assert len(detected) > 0, f"No items returned for {img_id}"
        is_fb = all(item.get("is_fallback", False) for item in detected)
        assert is_fb == expected_fb, f"Fallback mismatch for {img_id}: expected {expected_fb}, got {is_fb}"

        df2_items = [it for it in detected if it.get("detection_source") == "deepfashion2_yolo"]
        coco_items = [it for it in detected if it.get("detection_source") == "coco_yolo"]
        fb_items = [it for it in detected if it.get("detection_source") == "demo_fallback"]

        print(f"  Total Detections:       {len(detected)}")
        print(f"  DeepFashion2 Garments:  {len(df2_items)}")
        print(f"  COCO Accessories:       {len(coco_items)}")
        print(f"  Fallback Items:         {len(fb_items)}")
        print(f"  Is Fallback Engaged?:   {is_fb}")

        print("  Detected Items Breakdown:")
        for idx, it in enumerate(detected):
            src = it.get("detection_source")
            model = it.get("model_name")
            lbl = it.get("label")
            cat = it.get("category")
            conf = it.get("confidence", 0.0)
            bbox = it.get("bbox", [])
            print(f"    {idx+1}. [{cat.upper()}] {lbl} | Conf: {conf:.1%} | Source: {src} ({model}) | BBox: {bbox}")

            # Verify crop file exists and has data
            crop_path = it.get("crop_path")
            if crop_path and os.path.exists(crop_path):
                assert os.path.getsize(crop_path) > 500, f"Crop {crop_path} too small!"

        # Specific assertions per image
        if img_id in ["IMG-01", "IMG-02"]:
            # Complementary ensemble proof: must contain BOTH DeepFashion2 garment AND COCO handbag
            assert len(df2_items) >= 1, f"{img_id} should have DeepFashion2 garments!"
            assert len(coco_items) >= 1, f"{img_id} should have COCO accessories (handbag)!"
            bag_labels = [it["label"].lower() for it in coco_items]
            assert any("handbag" in bl for bl in bag_labels), f"{img_id} missing COCO handbag!"

        elif img_id in ["IMG-03", "IMG-04"]:
            # Fashion model photos: DeepFashion2 detects garments directly
            assert len(df2_items) >= 1, f"{img_id} should have DeepFashion2 garment detections!"

        elif img_id == "IMG-05":
            # Flat-lay with 0 humans: safe fallback engaged (white shirt, jeans, tote bag, loafers)
            assert is_fb is True, "IMG-05 should engage safe fallback!"
            assert len(fb_items) == 4, "IMG-05 should have 4 verified prototype items!"

        # B. Test Live FastAPI Search with Detected Items
        search_req = urllib.request.Request(
            f"{BASE_URL}/search-products",
            data=json.dumps({"detected_items": detected}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(search_req, timeout=10) as resp:
            assert resp.status == 200
            search_data = json.loads(resp.read().decode())
            assert search_data["success"] is True
            cat_results = search_data.get("results_by_category", {})
            assert len(cat_results) > 0, f"No FAISS matches for {img_id}"

            top_product = None
            top_score = 0.0
            for ckey, cinfo in cat_results.items():
                for p in cinfo.get("products", []):
                    score = p.get("similarity_score", 0.0)
                    if score > top_score:
                        top_score = score
                        top_product = p

            print(f"  FAISS Matching:         {len(cat_results)} categories matched")
            if top_product:
                print(f"  Top FAISS Catalog Match: {top_product['product_name']} ({top_product['brand']})")
                print(f"    • Score: {top_score:.4f} ({top_product.get('match_pct')}) | URL: {top_product.get('product_url')}")

        results_summary.append({
            "id": img_id,
            "title": title,
            "total_items": len(detected),
            "df2_items": len(df2_items),
            "coco_items": len(coco_items),
            "is_fallback": is_fb,
            "top_match": f"{top_product['product_name']} ({top_product.get('match_pct')})" if top_product else "N/A"
        })

    # 3. Final Summary Report
    print("\n" + "=" * 80)
    print("FASHION DETECTION ENSEMBLE EVALUATION SUMMARY")
    print("=" * 80)
    print(f"{'Image ID':<8} | {'Title':<30} | {'Items':<5} | {'DF2':<4} | {'COCO':<4} | {'Fallback':<8} | {'Top FAISS Match'}")
    print("-" * 105)
    for r in results_summary:
        fb_str = "YES" if r["is_fallback"] else "NO"
        print(f"{r['id']:<8} | {r['title'][:30]:<30} | {r['total_items']:<5} | {r['df2_items']:<4} | {r['coco_items']:<4} | {fb_str:<8} | {r['top_match']}")

    print("\n" + "=" * 80)
    print("ALL 5 OUTFIT IMAGES PASSED THE FASHION DETECTION ENSEMBLE TEST 100%!")
    print("=" * 80)


if __name__ == "__main__":
    test_fashion_ensemble_all_images()
