"""
SnapStyle End-to-End Real AI Integration Test
Validates the complete 6-stage AI pipeline:
Stage 1: Pillow / OpenCV Image Validation & Preprocessing
Stage 2: Real Ultralytics YOLOv8 Inference on an Uploaded Outfit Image
Stage 3: Hugging Face Transformers CLIP Visual Embedding Extraction (512-dim, L2-normalized)
Stage 4: Real FAISS IndexFlatIP Cosine Similarity Search against 24 Product Images
Stage 5: Pandas Catalog Data Enrichment (INR pricing, retailers, product details)
Stage 6: Live FastAPI HTTP API Endpoints (/analyze, /search-products)
"""

import os
import sys
import json
import numpy as np
from PIL import Image
import urllib.request
import urllib.error

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.image_processing import (
    validate_and_open_image,
    preprocess_for_detection,
    crop_item_box
)
from backend.detection import (
    get_yolo_model,
    detect_fashion_items
)
from backend.embeddings import (
    get_clip_model,
    get_clip_model_info,
    generate_image_embedding_with_meta
)
from backend.similarity_search import (
    fashion_index,
    FashionSimilarityIndex,
    FAISS_AVAILABLE
)
from backend.products import (
    get_product_by_id,
    get_all_products
)

def run_end_to_end_ai_test():
    print("=" * 80)
    print("SNAPSTYLE END-TO-END REAL AI INTEGRATION TEST")
    print("=" * 80)

    # Candidate real outfit image
    test_image_filename = "upload_c092561183.png"
    test_image_path = os.path.join(PROJECT_ROOT, "backend", "uploads", test_image_filename)
    if not os.path.exists(test_image_path):
        test_image_filename = "upload_4c43cd7dec.png"
        test_image_path = os.path.join(PROJECT_ROOT, "backend", "uploads", test_image_filename)

    assert os.path.exists(test_image_path), f"Test outfit image not found at {test_image_path}"
    print(f"\n[Test Outfit Image] Selected: {test_image_filename} ({os.path.getsize(test_image_path):,} bytes)")

    # --------------------------------------------------------------------------
    # STAGE 1: Pillow / OpenCV Preprocessing
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STAGE 1: Pillow / OpenCV Image Validation & Preprocessing")
    print("-" * 70)
    
    # 1.1 Pillow Validation
    raw_img = validate_and_open_image(test_image_path)
    print(f"  Pillow Image Loaded:        Format={raw_img.format or 'PNG'}, Mode={raw_img.mode}, Size={raw_img.size}")
    assert raw_img.mode == "RGB", f"Expected RGB mode, got {raw_img.mode}"
    assert raw_img.width > 100 and raw_img.height > 100, "Image dimensions too small"

    # 1.2 OpenCV Preprocessing & Enhancement
    cv2_bgr, pil_enhanced = preprocess_for_detection(raw_img)
    print(f"  OpenCV BGR Frame:           Shape={cv2_bgr.shape}, Dtype={cv2_bgr.dtype}")
    print(f"  Enhanced PIL Image:         Size={pil_enhanced.size}")
    assert cv2_bgr.shape[2] == 3, "Expected 3-channel BGR array"
    print("  -> STAGE 1 PASSED: Pillow validation and OpenCV enhancement successful.")

    # --------------------------------------------------------------------------
    # STAGE 2: Real Ultralytics YOLOv8 Detection
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STAGE 2: Real Ultralytics YOLOv8 Inference")
    print("-" * 70)
    
    yolo_model = get_yolo_model()
    assert yolo_model is not None, "YOLO model failed to load!"
    print(f"  YOLO Model Loaded:          {type(yolo_model).__name__} (yolov8n.pt)")

    crops_dir = os.path.join(PROJECT_ROOT, "backend", "uploads", "crops")
    upload_id = test_image_filename.replace("upload_", "").split(".")[0]
    
    detected_items = detect_fashion_items(
        pil_img=pil_enhanced,
        upload_id=upload_id,
        crops_dir=crops_dir,
        conf_threshold=0.20,
        force_fallback=False
    )

    print(f"  Total Items Detected:       {len(detected_items)}")
    assert len(detected_items) > 0, "No items returned by detection!"

    real_yolo_count = 0
    fallback_count = 0

    for idx, item in enumerate(detected_items, 1):
        is_fb = item.get("is_fallback", False)
        source = item.get("detection_source", "unknown")
        if is_fb:
            fallback_count += 1
        else:
            real_yolo_count += 1

        print(f"  Item {idx}: [{item['category'].upper()}] {item['label']}")
        print(f"    • Confidence:             {item.get('confidence'):.3f} ({int(item.get('confidence', 0)*100)}%)")
        print(f"    • Bounding Box (ymin,xmin,ymax,xmax): {item.get('bbox')}")
        print(f"    • Hotspot Position:       Top={item['hotspot']['top']}%, Left={item['hotspot']['left']}%")
        print(f"    • Detection Source:       {source} (is_fallback={is_fb})")
        print(f"    • Crop File:              {item.get('crop_path')}")
        if item.get("crop_path"):
            assert os.path.exists(item["crop_path"]), f"Crop file not created: {item['crop_path']}"

    print(f"  Summary: {real_yolo_count} Real YOLO detection(s), {fallback_count} Fallback item(s)")
    assert real_yolo_count > 0, "Expected real YOLO detections for this outfit image!"
    print("  -> STAGE 2 PASSED: Real YOLO inference successfully extracted authentic fashion objects.")

    # --------------------------------------------------------------------------
    # STAGE 3: Transformers CLIP Visual Embeddings
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STAGE 3: Transformers CLIP Visual Embedding Generation")
    print("-" * 70)

    clip_model, clip_processor = get_clip_model()
    assert clip_model is not None, "CLIP model failed to load!"
    clip_info = get_clip_model_info()
    print(f"  Active CLIP Model:          {clip_info['model_name']}")
    print(f"  Embedding Dimension:        {clip_info['embedding_dimension']}")
    print(f"  Is Real CLIP:               {clip_info['is_real_clip']}")
    print(f"  Source:                     {clip_info['source']}")
    assert clip_info["is_real_clip"] is True, "Expected is_real_clip to be True"

    item_embeddings = []
    for item in detected_items:
        crop_path = item.get("crop_path")
        if crop_path and os.path.exists(crop_path):
            crop_img = Image.open(crop_path)
        else:
            crop_img = Image.new("RGB", (64, 64), color=(240, 235, 230))
            
        emb, meta = generate_image_embedding_with_meta(crop_img, category_hint=item.get("category", ""))
        
        # Verify embedding properties
        assert isinstance(emb, np.ndarray), "Embedding must be numpy array"
        assert emb.shape == (512,), f"Expected shape (512,), got {emb.shape}"
        assert emb.dtype == np.float32, f"Expected float32, got {emb.dtype}"
        norm = float(np.linalg.norm(emb))
        assert abs(norm - 1.0) < 1e-4, f"Vector not L2 normalized: norm={norm}"
        assert meta["source"] == "real_clip", f"Expected real_clip, got {meta['source']}"
        assert meta["is_real_clip"] is True, "Expected is_real_clip=True"

        item_embeddings.append({
            "item": item,
            "embedding": emb,
            "metadata": meta
        })
        print(f"  Generated CLIP Embedding for '{item['label']}':")
        print(f"    • Shape: (512,) | Dtype: float32 | L2 Norm: {norm:.6f} | Source: {meta['source']}")

    print("  -> STAGE 3 PASSED: All detected item crops converted to normalized 512-dim CLIP vectors.")

    # --------------------------------------------------------------------------
    # STAGE 4: Real FAISS Cosine Similarity Search
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STAGE 4: Real FAISS Similarity Search (IndexFlatIP)")
    print("-" * 70)

    # Ensure catalog is loaded in FAISS
    fashion_index.load_from_disk()
    status = fashion_index.get_index_status()
    print(f"  FAISS Index Status:         {status['index_type']}")
    print(f"  Total Indexed Products:     {status['indexed_products_count']}")
    print(f"  Is Real FAISS:              {status['is_real_faiss']}")
    print(f"  Search Source:              {status['search_source']}")
    print(f"  Similarity Metric:          {status['similarity_metric']}")

    assert status["is_real_faiss"] is True, "Expected real FAISS index"
    assert status["indexed_products_count"] == 24, f"Expected 24 indexed products, got {status['indexed_products_count']}"

    faiss_search_results = {}
    for entry in item_embeddings:
        item = entry["item"]
        emb = entry["embedding"]
        cat = item["category"]
        catalog_filter = item.get("catalog_filter", cat)

        matches = fashion_index.search(emb, category_filter=catalog_filter, top_k=6)
        faiss_search_results[item["item_id"]] = {
            "item": item,
            "matches": matches
        }

        print(f"\n  FAISS Results for Detected [{cat.upper()}] '{item['label']}':")
        print(f"    • Catalog Filter Applied: {catalog_filter}")
        print(f"    • Number of Matches:     {len(matches)}")
        assert len(matches) > 0, f"Expected matches for category {cat}"

        for rank, m in enumerate(matches, 1):
            assert m["search_source"] == "real_faiss", f"Expected real_faiss, got {m['search_source']}"
            assert m["is_real_similarity"] is True, "Expected is_real_similarity to be True"
            score = m["similarity_score"]
            assert 0.0 <= score <= 1.0, f"Score out of range: {score}"
            print(f"      {rank}. Product: {m['product_id']} | Match: {m['match_pct']} | Cosine Sim: {score:.4f} | Source: {m['search_source']}")

    print("\n  -> STAGE 4 PASSED: FAISS exact cosine similarity search executed with authentic scores.")

    # --------------------------------------------------------------------------
    # STAGE 5: Pandas Catalog Data Enrichment
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STAGE 5: Pandas Catalog Data Enrichment")
    print("-" * 70)

    for item_id, res in faiss_search_results.items():
        item = res["item"]
        matches = res["matches"]
        print(f"\n  Enriched Catalog Products for [{item['category'].upper()}] '{item['label']}':")
        for m in matches[:3]: # Show top 3
            prod = get_product_by_id(m["product_id"])
            assert prod is not None, f"Product {m['product_id']} not found in catalog!"
            assert "price" in prod and "brand" in prod, "Incomplete product record!"
            price_formatted = f"₹{prod['price']:,}"
            print(f"    • {prod['product_name']} by {prod['brand']}")
            print(f"      Price: {price_formatted} | Category: {prod['category']} | Match: {m['match_pct']} (Score: {m['similarity_score']:.4f})")
            print(f"      Deep Link: {prod.get('product_url', '#')}")

    print("\n  -> STAGE 5 PASSED: Pandas catalog data enrichment verified.")

    # --------------------------------------------------------------------------
    # STAGE 6: Live FastAPI HTTP End-to-End API Verification
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STAGE 6: Live FastAPI HTTP End-to-End API Execution")
    print("-" * 70)

    # 6.1 Check Live Server Root Health Check
    root_req = urllib.request.Request("http://127.0.0.1:8000/", headers={"Accept": "application/json"})
    with urllib.request.urlopen(root_req, timeout=5) as resp:
        assert resp.status == 200, f"Expected 200 from GET /, got {resp.status}"
        root_data = json.loads(resp.read().decode())
        print(f"  GET / Response Status:      HTTP {resp.status}")
        print(f"  AI Pipeline Reported:       YOLO={root_data['ai_pipeline']['detection']}, CLIP={root_data['ai_pipeline']['embeddings']}")
        print(f"  FAISS Indexed Products:     {root_data['ai_pipeline']['indexed_products_count']}")
        print(f"  FAISS Real:                 {root_data['ai_pipeline']['faiss_real']}")
        assert root_data["ai_pipeline"]["indexed_products_count"] == 24
        assert root_data["ai_pipeline"]["faiss_real"] is True

    # 6.2 Test Live POST /analyze with Upload ID
    analyze_payload = json.dumps({"upload_id": upload_id}).encode("utf-8")
    analyze_req = urllib.request.Request(
        "http://127.0.0.1:8000/analyze",
        data=analyze_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(analyze_req, timeout=10) as resp:
        assert resp.status == 200, f"Expected 200 from POST /analyze, got {resp.status}"
        analyze_data = json.loads(resp.read().decode())
        print(f"\n  POST /analyze Response:")
        print(f"    • Success:                {analyze_data['success']}")
        print(f"    • Detection Source:       {analyze_data['detection_source']}")
        print(f"    • Is Fallback:            {analyze_data['is_fallback']}")
        print(f"    • Model Used:             {analyze_data['model_used']}")
        print(f"    • Items Detected:         {len(analyze_data['detected_items'])}")
        assert analyze_data["detection_source"] == "real_yolo"
        assert analyze_data["is_fallback"] is False

    # 6.3 Test Live POST /search-products with Real Detected Items
    search_payload = json.dumps({"detected_items": analyze_data["detected_items"]}).encode("utf-8")
    search_req = urllib.request.Request(
        "http://127.0.0.1:8000/search-products",
        data=search_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(search_req, timeout=10) as resp:
        assert resp.status == 200, f"Expected 200 from POST /search-products, got {resp.status}"
        search_data = json.loads(resp.read().decode())
        print(f"\n  POST /search-products Response:")
        print(f"    • Success:                {search_data['success']}")
        meta = search_data.get("search_metadata", {})
        print(f"    • Search Source:          {meta.get('search_source')}")
        print(f"    • Is Real FAISS:          {meta.get('is_real_faiss')}")
        print(f"    • Indexed Products:       {meta.get('indexed_products_count')}")
        print(f"    • Metric:                 {meta.get('similarity_metric')}")
        
        assert meta.get("search_source") == "real_faiss"
        assert meta.get("is_real_faiss") is True
        assert meta.get("indexed_products_count") == 24

        cat_results = search_data.get("results_by_category", {})
        print(f"    • Categories Matched:     {list(cat_results.keys())}")
        for cat, cinfo in cat_results.items():
            prods = cinfo.get("products", [])
            print(f"      - Category [{cat}]: {len(prods)} products matched")
            if prods:
                top = prods[0]
                print(f"        Top Match: {top['product_name']} ({top['brand']}) | Score: {top['similarity_score']} ({top['match_pct']}) | Source: {top['search_source']}")
                assert top["search_source"] == "real_faiss"
                assert top["similarity_score"] is not None

    print("\n  -> STAGE 6 PASSED: Live FastAPI HTTP API successfully returned complete real AI pipeline results.")

    print("\n" + "=" * 80)
    print("ALL 6 PIPELINE STAGES VERIFIED AND PASSED 100%!")
    print("================================================================================")

if __name__ == "__main__":
    run_end_to_end_ai_test()
