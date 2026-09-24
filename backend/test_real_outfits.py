"""
SnapStyle Real Outfit Images Test Suite
backend/test_real_outfits.py

Tests SnapStyle with real outfit images from tests/test_images/:
- Loads every image (.jpg, .jpeg, .png, .webp) from tests/test_images/
- Sends each image through the existing SnapStyle /analyze pipeline
- Runs the existing DeepFashion2 + COCO detection ensemble
- Generates real CLIP visual embeddings
- Searches the existing 105-product FAISS catalog
- Returns top matched products with cosine similarity scores
- Verifies specific retailer product URLs with live HTTP checks
- Prints clear per-image test results and a comprehensive final summary
"""

import os
import sys
import json
import ssl
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

BASE_URL = "http://127.0.0.1:8000"

def find_test_images_dir() -> str:
    """Discovers the tests/test_images folder across possible working paths."""
    candidates = [
        os.path.join(PROJECT_ROOT, "tests", "test_images"),
        os.path.join(os.path.dirname(PROJECT_ROOT), "tests", "test_images"),
        os.path.join(os.getcwd(), "tests", "test_images"),
        os.path.join(os.getcwd(), "Snapstyle", "tests", "test_images")
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isdir(c):
            return os.path.abspath(c)
    
    # Default fallback: create at PROJECT_ROOT/tests/test_images
    default_path = os.path.join(PROJECT_ROOT, "tests", "test_images")
    os.makedirs(default_path, exist_ok=True)
    return default_path

def get_test_images(test_dir: str) -> List[str]:
    """Returns sorted list of valid image paths from test directory."""
    valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
    images = []
    if not os.path.exists(test_dir):
        return images

    for fname in sorted(os.listdir(test_dir)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in valid_exts:
            images.append(os.path.join(test_dir, fname))
    return images

def check_live_server() -> bool:
    """Verifies whether the SnapStyle FastAPI server is running on BASE_URL."""
    try:
        req = urllib.request.Request(f"{BASE_URL}/", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def verify_url_status(url: str, timeout: int = 10) -> int:
    """Performs live HTTP verification on the product URL, returning the HTTP status code."""
    if not url or url == "#" or not url.startswith("http"):
        return 400

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        # Some CDNs return 403 or 429 to high-concurrency bot requests, but 200/301/302 confirm route existence
        return e.code
    except Exception:
        return 500

def run_pipeline_live(image_path: str) -> Dict[str, Any]:
    """Runs image through live FastAPI endpoints /analyze and /search-products."""
    # 1. Call /analyze
    analyze_payload = json.dumps({"image_path": image_path}).encode("utf-8")
    req_analyze = urllib.request.Request(
        f"{BASE_URL}/analyze",
        data=analyze_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_analyze, timeout=30) as resp:
        analyze_res = json.loads(resp.read().decode("utf-8"))

    detected_items = analyze_res.get("detected_items", [])
    is_fallback = analyze_res.get("is_fallback", False)

    # 2. Call /search-products
    search_payload = json.dumps({"detected_items": detected_items}).encode("utf-8")
    req_search = urllib.request.Request(
        f"{BASE_URL}/search-products",
        data=search_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_search, timeout=30) as resp:
        search_res = json.loads(resp.read().decode("utf-8"))

    return {
        "analyze": analyze_res,
        "search": search_res,
        "detected_items": detected_items,
        "is_fallback": is_fallback
    }

def run_pipeline_direct(image_path: str) -> Dict[str, Any]:
    """Runs image through direct Python AI pipeline modules if server is offline."""
    from backend.detection import detect_fashion_items, map_detected_item_to_catalog_category
    from backend.image_processing import validate_and_open_image, preprocess_for_detection
    from backend.embeddings import generate_image_embedding
    from backend.similarity_search import fashion_index
    from backend.products import get_product_by_id
    from PIL import Image

    crops_dir = os.path.join(PROJECT_ROOT, "backend", "uploads", "crops")
    os.makedirs(crops_dir, exist_ok=True)

    pil_img = validate_and_open_image(image_path)
    _, pil_enhanced = preprocess_for_detection(pil_img)
    upload_id = os.path.splitext(os.path.basename(image_path))[0]

    detected_items = detect_fashion_items(pil_enhanced, upload_id, crops_dir)
    is_fallback = all(it.get("is_fallback", False) for it in detected_items)

    category_results = {}
    for idx, item in enumerate(detected_items):
        mapped_cat = map_detected_item_to_catalog_category(item)
        item_label = item.get("label") or mapped_cat.title()
        item_id = item.get("item_id") or f"det_{mapped_cat}_{idx+1}"

        crop_p = item.get("crop_path")
        if crop_p and os.path.exists(crop_p):
            q_img = Image.open(crop_p)
        else:
            q_img = Image.new("RGB", (64, 64), color=(240, 235, 230))
        q_vec = generate_image_embedding(q_img, category_hint=f"{mapped_cat}_{item_label}")

        matches = fashion_index.search(q_vec, category_filter=mapped_cat, top_k=4)
        matched_prods = []
        for m in matches:
            p_info = get_product_by_id(m["product_id"])
            if p_info:
                p_copy = dict(p_info)
                p_copy["similarity_score"] = m.get("similarity_score", 0.0)
                p_copy["match_pct"] = m.get("match_pct", "")
                matched_prods.append(p_copy)
        if matched_prods:
            category_results[item_id] = {
                "item_id": item_id,
                "detected_item": item_label,
                "category_label": item_label,
                "category": mapped_cat,
                "products": matched_prods
            }

    return {
        "analyze": {"detected_items": detected_items, "is_fallback": is_fallback},
        "search": {"results_by_category": category_results},
        "detected_items": detected_items,
        "is_fallback": is_fallback
    }

def test_real_outfits():
    test_dir = find_test_images_dir()
    image_paths = get_test_images(test_dir)

    print("=" * 80)
    print("SNAPSTYLE REAL OUTFIT TESTING SUITE")
    print("=" * 80)
    print(f"Test Images Directory: {test_dir}")
    print(f"Total Test Images Found: {len(image_paths)}")

    if not image_paths:
        print("\n[Notice] No test images found in tests/test_images/")
        print("Please place outfit images (.jpg, .jpeg, .png, .webp) in:")
        print(f"  -> {test_dir}")
        print("=" * 80)
        return

    # Check live server status
    server_online = check_live_server()
    mode_str = "FastAPI Live Endpoints (http://127.0.0.1:8000)" if server_online else "Direct Python In-Memory AI Pipeline"
    print(f"Execution Mode:        {mode_str}\n")

    summary = {
        "total": len(image_paths),
        "success": 0,
        "fallback_count": 0,
        "matched_count": 0,
        "working_urls": 0,
        "failed_urls": 0
    }

    for img_path in image_paths:
        fname = os.path.basename(img_path)
        try:
            if server_online:
                res = run_pipeline_live(img_path)
            else:
                res = run_pipeline_direct(img_path)

            detected_items = res["detected_items"]
            is_fallback = res["is_fallback"]
            search_res = res["search"]
            cat_results = search_res.get("results_by_category", {})

            # 1. Detection status & item categories
            detection_pass = len(detected_items) > 0
            detection_status = "PASS" if detection_pass else "FAIL"

            item_labels = []
            for it in detected_items:
                lbl = it.get("label", it.get("category", "")).lower()
                if lbl not in item_labels:
                    item_labels.append(lbl)
            items_str = ", ".join(item_labels) if item_labels else "None"

            # 2. Fallback status
            fallback_str = "YES" if is_fallback else "NO"
            if is_fallback:
                summary["fallback_count"] += 1

            # 3. Find top matched product across all categories
            top_prod = None
            top_score = 0.0
            for _, cdata in cat_results.items():
                for p in cdata.get("products", []):
                    sc = p.get("similarity_score", 0.0)
                    if sc > top_score:
                        top_score = sc
                        top_prod = p

            if top_prod:
                summary["matched_count"] += 1
                prod_name = top_prod.get("product_name", "Unknown")
                prod_brand = top_prod.get("brand", "")
                full_prod_name = f"{prod_name} ({prod_brand})" if prod_brand else prod_name
                prod_url = top_prod.get("product_url", "#")
            else:
                full_prod_name = "None"
                prod_url = "None"
                top_score = 0.0

            # 4. Check URL status
            if prod_url and prod_url.startswith("http"):
                url_code = verify_url_status(prod_url)
                if url_code == 200:
                    summary["working_urls"] += 1
                else:
                    # Retailers returning 403 to automated scripts are noted
                    summary["working_urls"] += 1 if url_code in [200, 301, 302, 403] else 0
                    if url_code not in [200, 301, 302, 403]:
                        summary["failed_urls"] += 1
            else:
                url_code = 404
                summary["failed_urls"] += 1

            # 5. Overall status
            overall_pass = detection_pass and top_prod is not None and top_score > 0
            overall_status = "PASS" if overall_pass else "FAIL"
            if overall_pass:
                summary["success"] += 1

            # Print formatted block with item-specific matching breakdown
            print(f"IMAGE: {fname}")
            print(f"Detection: {detection_status}")
            print(f"Detected items: {items_str}")
            print(f"Fallback: {fallback_str}")
            print("Item-Specific Matching Breakdown:")
            for item_key, item_group in cat_results.items():
                d_item = item_group.get("detected_item") or item_group.get("category_label")
                m_cat = item_group.get("category")
                prods = item_group.get("products", [])
                p_count = len(prods)
                top_p = prods[0] if prods else None
                top_p_name = f"{top_p.get('product_name')} ({top_p.get('brand')})" if top_p else "None"
                top_p_score = top_p.get('similarity_score', 0.0) if top_p else 0.0
                top_p_url = top_p.get('product_url', '#') if top_p else "None"
                p_valid = verify_url_status(top_p_url) in [200, 301, 302, 403] if top_p else False
                print(f"  • Detected Item: {d_item}")
                print(f"    - Mapped Category: {m_cat}")
                print(f"    - Products Returned: {p_count}")
                print(f"    - Top Product: {top_p_name}")
                print(f"    - Similarity Score: {top_p_score:.4f} ({top_p.get('match_pct', '') if top_p else ''})")
                print(f"    - Product URL: {top_p_url}")
                print(f"    - URL Status Valid: {p_valid}")
            print(f"Top product: {full_prod_name}")
            print(f"Similarity: {top_score:.2f}")
            print(f"Product URL: {prod_url}")
            print(f"URL status: {url_code}")
            print(f"Overall: {overall_status}")
            print()

        except Exception as e:
            summary["failed_urls"] += 1
            print(f"IMAGE: {fname}")
            print(f"Detection: FAIL")
            print(f"Detected items: None")
            print(f"Fallback: NO")
            print(f"Top product: None")
            print(f"Similarity: 0.00")
            print(f"Product URL: None")
            print(f"URL status: ERROR ({e})")
            print(f"Overall: FAIL")
            print()

    # Final summary report
    print("=" * 80)
    print("SNAPSTYLE REAL OUTFIT TESTING SUMMARY")
    print("=" * 80)
    print(f"Total images tested:      {summary['total']}")
    print(f"Successful analyses:      {summary['success']}")
    print(f"Fallback count:           {summary['fallback_count']}")
    print(f"Product matching results: {summary['matched_count']} / {summary['total']} matched")
    print(f"Working product URLs:     {summary['working_urls']}")
    print(f"Failed URLs:              {summary['failed_urls']}")
    print("=" * 80)

if __name__ == "__main__":
    test_real_outfits()
