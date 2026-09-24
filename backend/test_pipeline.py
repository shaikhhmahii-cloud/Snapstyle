"""
SnapStyle Pipeline Test Suite
Validates all 7 required Python libraries:
1. Pillow (PIL)
2. OpenCV (cv2)
3. Ultralytics YOLO
4. Transformers (CLIP)
5. FAISS (faiss-cpu)
6. Pandas
7. FastAPI
"""

import os
import sys
import numpy as np
from PIL import Image

# Add SnapStyle root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def test_pillow_and_opencv():
    print("\n--- [1 & 2] Testing Pillow & OpenCV ---")
    from backend.image_processing import (
        validate_and_open_image,
        resize_image_for_ai,
        preprocess_for_detection,
        crop_item_box,
        draw_focus_brackets
    )
    import cv2

    # 1. Create a synthetic test image with Pillow
    img = Image.new("RGB", (1200, 1600), color=(240, 230, 220))
    resized = resize_image_for_ai(img, max_dim=800)
    assert max(resized.size) == 800, f"Pillow resize failed, got {resized.size}"
    print(f"[PASS] Pillow image created & resized: {resized.size}")

    # 2. Preprocess with OpenCV
    cv2_enhanced, pil_enhanced = preprocess_for_detection(resized)
    assert cv2_enhanced.shape[0] == 800 or cv2_enhanced.shape[1] == 800
    print(f"[PASS] OpenCV preprocessing applied: shape={cv2_enhanced.shape}")

    # 3. Crop bounding box
    bbox = [0.2, 0.2, 0.6, 0.6]
    cropped = crop_item_box(pil_enhanced, bbox)
    assert cropped.size[0] > 0 and cropped.size[1] > 0
    print(f"[PASS] Bounding box cropped: size={cropped.size}")

    # 4. Draw Stitch focus brackets
    bracketed = draw_focus_brackets(cv2_enhanced, bbox)
    assert bracketed.shape == cv2_enhanced.shape
    print(f"[PASS] Google Stitch focus brackets drawn with OpenCV")

def test_detection():
    print("\n--- [3] Testing Ultralytics YOLO Detection ---")
    from backend.detection import detect_fashion_items

    img = Image.new("RGB", (600, 800), color=(235, 230, 225))
    crops_dir = os.path.join(BASE_DIR, "backend", "uploads", "test_crops")
    
    items = detect_fashion_items(img, "test_upload", crops_dir)
    assert len(items) > 0, "No items detected"
    for it in items:
        assert "item_id" in it
        assert "category" in it
        assert "bbox" in it
        assert "hotspot" in it
        assert "top" in it["hotspot"] and "left" in it["hotspot"]
    print(f"[PASS] YOLO fashion items detected: {len(items)} items")
    for it in items[:3]:
        print(f"   • [{it['category'].upper()}] {it['label']} (Hotspot: {it['hotspot']['top']}%, {it['hotspot']['left']}%)")

def test_embeddings():
    print("\n--- [4] Testing Transformers (CLIP) Visual Embeddings ---")
    from backend.embeddings import generate_image_embedding, EMBEDDING_DIM

    img = Image.new("RGB", (128, 128), color=(250, 245, 240))
    vec = generate_image_embedding(img, "top_shirt")
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (EMBEDDING_DIM,), f"Expected shape ({EMBEDDING_DIM},), got {vec.shape}"
    norm = np.linalg.norm(vec)
    assert np.isclose(norm, 1.0, atol=1e-3), f"Vector not normalized: norm={norm}"
    print(f"[PASS] 512-dim normalized embedding generated: norm={norm:.4f}")

def test_faiss():
    print("\n--- [5] Testing FAISS Similarity Search ---")
    from backend.similarity_search import FashionSimilarityIndex
    import faiss

    index = FashionSimilarityIndex(dimension=512)
    # Add synthetic products
    v1 = np.random.randn(512).astype(np.float32)
    v1 /= np.linalg.norm(v1)
    v2 = np.random.randn(512).astype(np.float32)
    v2 /= np.linalg.norm(v2)
    
    index.add_product("prod_test_1", "top", v1)
    index.add_product("prod_test_2", "bottom", v2)

    # Search with v1 plus slight perturbation
    q = v1 + np.random.randn(512).astype(np.float32) * 0.05
    q /= np.linalg.norm(q)

    matches = index.search(q, category_filter="top", top_k=2)
    assert len(matches) > 0
    assert matches[0]["product_id"] == "prod_test_1"
    print(f"[PASS] FAISS similarity search retrieved nearest neighbor: {matches[0]['product_id']} ({matches[0]['match_pct']})")

def test_pandas_products():
    print("\n--- [6] Testing Pandas Product Catalog & Filtering ---")
    from backend.products import (
        get_all_products,
        filter_products,
        add_to_wishlist,
        get_wishlist_products,
        remove_from_wishlist
    )

    products = get_all_products()
    assert len(products) > 0, "No products loaded from products.csv"
    print(f"[PASS] Pandas loaded {len(products)} products from CSV")

    # Filter by category
    tops = filter_products(category="top")
    assert len(tops) > 0
    assert all(p["category"] == "top" for p in tops)
    print(f"[PASS] Pandas filtered category 'top': {len(tops)} products found")

    # Filter by budget
    budget_items = filter_products(budget_tier="under_1000")
    assert all(p["price"] <= 1000 for p in budget_items)
    print(f"[PASS] Pandas budget filter 'Under ₹1,000': {len(budget_items)} products found")

    # Wishlist testing
    test_pid = products[0]["product_id"]
    add_to_wishlist(test_pid)
    wishlist = get_wishlist_products()
    assert any(p["product_id"] == test_pid for p in wishlist)
    remove_from_wishlist(test_pid)
    print("[PASS] Wishlist add/remove verified")

def test_fastapi_endpoints():
    print("\n--- [7] Testing FastAPI Application Endpoints ---")
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    
    # 1. Health check
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["app"] == "SnapStyle"
    print(f"[PASS] GET / -> {data['status']}, app={data['app']}")

    # 2. GET /products
    res = client.get("/products?category=top")
    assert res.status_code == 200
    prods = res.json()["products"]
    print(f"[PASS] GET /products?category=top -> {len(prods)} products")

    # 3. POST /analyze (with demo)
    res = client.post("/analyze", json={"upload_id": "demo"})
    assert res.status_code == 200
    ana = res.json()
    assert ana["success"] is True
    print(f"[PASS] POST /analyze -> {ana['item_count']} detected items, confidence={ana['ai_confidence']}")

    # 4. POST /search-products
    res = client.post("/search-products", json={"detected_items": ana["detected_items"]})
    assert res.status_code == 200
    search_data = res.json()
    assert search_data["success"] is True
    cats = list(search_data["results_by_category"].keys())
    print(f"[PASS] POST /search-products -> Matched categories: {cats}")

    # 5. Wishlist API
    res = client.get("/wishlist")
    assert res.status_code == 200
    print(f"[PASS] GET /wishlist -> {res.json()['count']} items")

if __name__ == "__main__":
    print("==================================================")
    print("RUNNING SNAPSTYLE FULL-STACK AI PIPELINE TESTS")
    print("==================================================")
    test_pillow_and_opencv()
    test_detection()
    test_embeddings()
    test_faiss()
    test_pandas_products()
    test_fastapi_endpoints()
    print("\n==================================================")
    print("ALL 7 REQUIRED LIBRARIES VERIFIED & WORKING 100%!")
    print("==================================================")

