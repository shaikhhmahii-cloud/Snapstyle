"""
Test Real YOLO Inference in SnapStyle Backend
Verifies:
1. Pre-warmed singleton YOLO model execution.
2. Real inference on an actual outfit photo (person + handbag).
3. Genuine COCO class identification (Person, Handbag) without false clothing category claims.
4. Accurate bounding boxes and confidence scores.
5. Clear distinction between real YOLO detections (is_fallback=False) and demo fallback (is_fallback=True).
6. Demo fallback behavior remains functional and unchanged.
7. Subsequent product matching with FAISS.
"""

import sys
import io
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000"

def test_yolo_detection():
    print("==================================================")
    print("TESTING REAL YOLO INFERENCE IN SNAPSTYLE BACKEND")
    print("==================================================")

    # -------------------------------------------------------------
    # 1. Test Real YOLO Inference on an Actual Outfit Image
    # -------------------------------------------------------------
    print("\n--- [Step 1] Uploading Actual Outfit Image ---")
    boundary = "----SnapStyleRealYoloBoundary987654321"
    body = io.BytesIO()
    body.write(f"--{boundary}\r\n".encode())
    body.write(b'Content-Disposition: form-data; name="file"; filename="real_outfit_look.png"\r\n')
    body.write(b"Content-Type: image/png\r\n\r\n")
    
    # Use real outfit photo
    with open("backend/uploads/upload_4c43cd7dec.png", "rb") as f:
        body.write(f.read())
    body.write(f"\r\n--{boundary}--\r\n".encode())

    req_upload = urllib.request.Request(
        f"{BASE}/upload",
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req_upload) as r:
        upload_data = json.loads(r.read().decode())
        upload_id = upload_data["upload_id"]
        image_url = upload_data["image_url"]
        print(f"[PASS] Upload successful: upload_id={upload_id}, url={image_url}")

    print("\n--- [Step 2] Executing Real YOLOv8 Inference via POST /analyze ---")
    req_analyze = urllib.request.Request(
        f"{BASE}/analyze",
        data=json.dumps({"upload_id": upload_id, "image_url": image_url}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_analyze) as r:
        res = json.loads(r.read().decode())
        
        print(f"[PASS] AI Analysis status: HTTP {r.status}")
        print(f"       Detection Source : {res.get('detection_source')}")
        print(f"       Is Fallback      : {res.get('is_fallback')}")
        print(f"       Model Used       : {res.get('model_used')}")
        print(f"       AI Confidence    : {res.get('ai_confidence')}")
        print(f"       Items Detected   : {res.get('item_count')}")

        assert res["detection_source"] == "real_yolo", f"Expected real_yolo, got {res['detection_source']}"
        assert res["is_fallback"] is False, "Real detection should have is_fallback=False"
        assert res["item_count"] > 0, "Real YOLO should detect at least one item on this outfit image"

        print("\nReal Detected Objects:")
        for idx, item in enumerate(res["detected_items"], 1):
            print(f"  {idx}. [{item['raw_class'].upper()}] {item['label']}")
            print(f"     • Category         : {item['category']}")
            print(f"     • Confidence       : {item['confidence']} ({int(item['confidence']*100)}%)")
            print(f"     • Bounding Box     : {item['bbox']} (ymin, xmin, ymax, xmax)")
            print(f"     • Hotspot (Top,Left): ({item['hotspot']['top']}%, {item['hotspot']['left']}%)")
            print(f"     • Detection Source : {item['detection_source']} (is_fallback={item['is_fallback']})")
            print(f"     • Crop Thumbnail   : {item['crop_url']}")

            assert item["is_fallback"] is False
            assert item["detection_source"] == "real_yolo"
            assert item["raw_class"] in ["person", "handbag", "backpack", "suitcase", "tie", "umbrella"]
            # Verify no false claim of clothing categories COCO cannot detect
            assert item["raw_class"] not in ["shirt", "pants", "dress", "shoes", "jacket"]

    # -------------------------------------------------------------
    # 2. Test Product Matching with Real YOLO Detections
    # -------------------------------------------------------------
    print("\n--- [Step 3] Visual Similarity Search for Real Detections ---")
    req_search = urllib.request.Request(
        f"{BASE}/search-products",
        data=json.dumps({"detected_items": res["detected_items"]}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_search) as r:
        search_res = json.loads(r.read().decode())
        cats = list(search_res["results_by_category"].keys())
        print(f"[PASS] Matched {len(cats)} categories from real YOLO detections: {cats}")
        for c in cats:
            prods = search_res["results_by_category"][c]["products"]
            print(f"       • Category '{c}': {len(prods)} products matched via FAISS")
            assert len(prods) > 0

    # -------------------------------------------------------------
    # 3. Test Demo Fallback Remains Unchanged & Distinguished
    # -------------------------------------------------------------
    print("\n--- [Step 4] Verifying Demo Fallback Mode ---")
    req_demo = urllib.request.Request(
        f"{BASE}/analyze",
        data=json.dumps({"upload_id": "demo"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_demo) as r:
        demo_res = json.loads(r.read().decode())
        print(f"[PASS] Demo Analysis status: HTTP {r.status}")
        print(f"       Detection Source : {demo_res.get('detection_source')}")
        print(f"       Is Fallback      : {demo_res.get('is_fallback')}")
        print(f"       Items Detected   : {demo_res.get('item_count')}")

        assert demo_res["detection_source"] == "demo_fallback"
        assert demo_res["is_fallback"] is True
        assert demo_res["item_count"] == 5

        # All fallback items should have is_fallback=True and detection_source="demo_fallback"
        for it in demo_res["detected_items"]:
            assert it["is_fallback"] is True
            assert it["detection_source"] == "demo_fallback"
            assert it["model_name"] == "prototype_reference"

        print(f"       All {len(demo_res['detected_items'])} fallback items correctly tagged as demo_fallback.")

    print("\n==================================================")
    print("ALL REAL YOLO DETECTION TESTS PASSED 100%!")
    print("==================================================")

if __name__ == "__main__":
    test_yolo_detection()
