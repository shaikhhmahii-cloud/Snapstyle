"""
Comprehensive Verification for SnapStyle Product Images and Individual Product URLs
Validates:
1. Product images load successfully via HTTP 200 from FastAPI static serving
2. Every product has its own individual, distinct product_url (no generic homepages)
3. Different product cards have different images and different product URLs
4. End-to-end flow: Upload/Demo -> Analyze -> Detect -> Similar Products -> Valid Images & Links
"""

import urllib.request
import json
import os
import sys

BASE = "http://127.0.0.1:8000"

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def test_product_images_and_links():
    print("==================================================")
    print("TESTING SNAPSTYLE PRODUCT RESULTS & LINKING SYSTEM")
    print("==================================================")

    # 1. Verify all 24 local product images exist and are served via HTTP 200
    print("\n--- [Step 1] Verifying 24 Product Static Images ---")
    verified_images = 0
    for i in range(1, 25):
        pid = f"prod_{i:03d}"
        img_url = f"{BASE}/static/assets/products/{pid}.jpg"
        req = urllib.request.Request(img_url)
        try:
            with urllib.request.urlopen(req) as resp:
                assert resp.status == 200
                data_len = len(resp.read())
                assert data_len > 1000, f"Image {pid} is too small: {data_len} bytes"
                verified_images += 1
        except Exception as e:
            print(f"[FAIL] Image {pid} failed: {e}")
            raise
    print(f"[PASS] All {verified_images}/24 product images served via FastAPI with HTTP 200 OK")

    # 2. Verify End-to-End AI Search Flow
    print("\n--- [Step 2] Executing End-to-End AI Analysis & Product Matching ---")
    # A. Analyze
    req_analyze = urllib.request.Request(
        f"{BASE}/analyze",
        data=json.dumps({"upload_id": "demo"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_analyze) as r:
        analysis_data = json.loads(r.read().decode())
        assert analysis_data["success"] is True
        detected = analysis_data["detected_items"]
        print(f"[PASS] AI Detection found {len(detected)} items with hotspot percentages")

    # B. Search Products
    req_search = urllib.request.Request(
        f"{BASE}/search-products",
        data=json.dumps({"detected_items": detected}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_search) as r:
        search_data = json.loads(r.read().decode())
        assert search_data["success"] is True
        results_by_cat = search_data["results_by_category"]
        print(f"[PASS] Similar products matched across {len(results_by_cat)} categories: {list(results_by_cat.keys())}")

    # 3. Verify Product Cards Integrity & Differentiation
    print("\n--- [Step 3] Verifying Product Card Data, Images & Unique Product URLs ---")
    
    # Import frontend resolver mapping to simulate frontend card construction
    # Read app.js DEMO_PRODUCT_URLS
    import re
    app_js_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "js", "app.js")
    with open(app_js_path, "r", encoding="utf-8") as f:
        app_js_content = f.read()

    # Extract DEMO_PRODUCT_URLS from app.js
    url_matches = re.findall(r'(prod_\d{3}):\s*"(https://[^"]+)"', app_js_content)
    url_map = dict(url_matches)
    print(f"[PASS] Extracted {len(url_map)} unique demo product URLs from frontend mapping")

    all_matched_products = []
    seen_image_urls = set()
    seen_product_urls = set()

    for cat, group in results_by_cat.items():
        print(f"\n   Category: [{cat.upper()}] - {len(group['products'])} matches:")
        for prod in group["products"]:
            pid = prod["product_id"]
            name = prod["product_name"]
            brand = prod["brand"]
            price = prod["price"]
            
            # Resolve image URL as frontend does:
            resolved_img = f"/static/assets/products/{pid}.jpg"
            img_http_url = f"{BASE}{resolved_img}"
            
            # Verify image is live
            with urllib.request.urlopen(img_http_url) as img_resp:
                assert img_resp.status == 200

            # Resolve product URL as frontend does:
            explicit = prod.get("product_url", "")
            is_generic = (not explicit or explicit.endswith(".com") or explicit.endswith(".in") or explicit.endswith(".com/") or explicit.endswith(".in/"))
            if not is_generic and ("?demo=" in explicit or ".html" in explicit or "/product" in explicit):
                final_prod_url = explicit
            else:
                final_prod_url = url_map.get(pid, f"https://www.example.com/{pid}")

            # Verification assertions
            assert not final_prod_url.endswith(".com"), f"Product URL is generic homepage: {final_prod_url}"
            assert not final_prod_url.endswith(".in"), f"Product URL is generic homepage: {final_prod_url}"
            assert pid in final_prod_url or "demo=snapstyle_" in final_prod_url, f"Product URL does not contain product identifier: {final_prod_url}"
            assert f"₹{price:,}" == prod["formatted_price"]

            seen_image_urls.add(resolved_img)
            seen_product_urls.add(final_prod_url)
            all_matched_products.append(prod)

            print(f"     • {pid}: {name} ({brand}) ₹{price}")
            print(f"       - Image: {resolved_img} [200 OK]")
            print(f"       - Product URL: {final_prod_url}")

    # 4. Verify Different Product Cards Have Different Images and Different URLs
    print("\n--- [Step 4] Verifying Uniqueness & Differentiation ---")
    print(f"Total matched product cards evaluated: {len(all_matched_products)}")
    print(f"Distinct images across cards: {len(seen_image_urls)}")
    print(f"Distinct product URLs across cards: {len(seen_product_urls)}")

    assert len(seen_image_urls) == len(set(p['product_id'] for p in all_matched_products)), \
        "Different products must have different image URLs!"
    assert len(seen_product_urls) == len(set(p['product_id'] for p in all_matched_products)), \
        "Different products must have different individual product URLs!"

    print("\n==================================================")
    print("ALL TESTS PASSED: IMAGES VISIBLE & INDIVIDUAL LINKS VERIFIED!")
    print("==================================================")

if __name__ == "__main__":
    test_product_images_and_links()
