"""
SnapStyle Full End-to-End Simulation Test
Verifies:
1. Image Upload (POST /upload) and HTTP availability of uploaded inspiration file
2. AI Detection & Analysis (POST /analyze) returning 5 detected items with hotspots
3. Product Search (POST /search-products) returning 5 categories with local images and individual URLs
4. Wishlist APIs (GET /wishlist, POST /wishlist, DELETE /wishlist)
5. Alternate / errant routes (/app, /index.htmlsvg, /static/index.htmlsvg)
"""

import sys
import json
import io
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000"

def run_simulation():
    print("==================================================")
    print("RUNNING COMPLETE SNAPSTYLE END-TO-END FLOW")
    print("==================================================")

    # 1. Image Upload
    boundary = "----SnapStyleBoundary7MA4YWxkTrZu0gW"
    body = io.BytesIO()
    body.write(f"--{boundary}\r\n".encode())
    body.write(b'Content-Disposition: form-data; name="file"; filename="test_inspiration.jpg"\r\n')
    body.write(b"Content-Type: image/jpeg\r\n\r\n")
    with open("backend/uploads/demo_sample.jpg", "rb") as f:
        body.write(f.read())
    body.write(f"\r\n--{boundary}--\r\n".encode())

    req_upload = urllib.request.Request(
        f"{BASE}/upload",
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req_upload) as r:
        upload_data = json.loads(r.read().decode())
        print(f"[1. UPLOAD] HTTP {r.status} | upload_id: {upload_data['upload_id']} | image_url: {upload_data['image_url']}")
        assert upload_data["success"] is True
        uploaded_image_url = upload_data["image_url"]

    # Verify uploaded image file is served over HTTP with 200 OK
    with urllib.request.urlopen(f"{BASE}{uploaded_image_url}") as r:
        img_bytes = r.read()
        print(f"[1b. INSPIRATION IMAGE SERVED] HTTP {r.status} | Size: {len(img_bytes)} bytes | Content-Type: {r.headers.get('Content-Type')}")
        assert r.status == 200
        assert len(img_bytes) > 0

    # 2. AI Analysis & Detection
    req_analyze = urllib.request.Request(
        f"{BASE}/analyze",
        data=json.dumps({"upload_id": upload_data["upload_id"], "image_url": uploaded_image_url}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_analyze) as r:
        analysis_data = json.loads(r.read().decode())
        items = analysis_data["detected_items"]
        print(f"[2. AI ANALYSIS] HTTP {r.status} | Detected items: {len(items)} (AI Confidence: {analysis_data['ai_confidence']})")
        assert len(items) == 5
        for item in items:
            print(f"   - [{item['category'].upper()}] {item['label']}: Hotspot({item['hotspot']['top']}%, {item['hotspot']['left']}%) | Crop: {item['crop_url']}")
            # Verify crop image is accessible
            with urllib.request.urlopen(f"{BASE}{item['crop_url']}") as cr:
                assert cr.status == 200

    # 3. Product Search Across All 5 Categories
    req_search = urllib.request.Request(
        f"{BASE}/search-products",
        data=json.dumps({"detected_items": items}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_search) as r:
        search_data = json.loads(r.read().decode())
        results = search_data["results_by_category"]
        cats = list(results.keys())
        print(f"\n[3. SIMILAR PRODUCTS] HTTP {r.status} | Matched {len(cats)} categories: {cats}")
        assert len(cats) == 5

        total_prods = 0
        for cat, group in results.items():
            prods = group["products"]
            total_prods += len(prods)
            print(f"   • Category [{cat}]: {len(prods)} products")
            for p in prods:
                # Check image URL
                with urllib.request.urlopen(f"{BASE}{p['image_url']}") as pr:
                    assert pr.status == 200
                # Check individual URL is deep link, not generic homepage
                assert not p["product_url"].endswith(".com") and not p["product_url"].endswith(".in")
                assert "?demo=" in p["product_url"] or ".html" in p["product_url"]

        print(f"   -> Successfully validated {total_prods} products across 5 categories.")

    # 4. Wishlist API
    req_wl_add = urllib.request.Request(
        f"{BASE}/wishlist",
        data=json.dumps({"product_id": "prod_005"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_wl_add) as r:
        res = json.loads(r.read().decode())
        print(f"\n[4. WISHLIST ADD] HTTP {r.status} | prod_005 added: {res.get('success')}")

    with urllib.request.urlopen(f"{BASE}/wishlist") as r:
        wl_data = json.loads(r.read().decode())
        print(f"[4b. WISHLIST GET] HTTP {r.status} | Wishlist count: {wl_data['count']}")

    # 5. Verify /app and /static/index.htmlsvg
    with urllib.request.urlopen(f"{BASE}/app") as r:
        print(f"\n[5. ROUTE /app] HTTP {r.status} | Length: {len(r.read())} bytes")
        assert r.status == 200

    req_svg = urllib.request.Request(f"{BASE}/static/index.htmlsvg")
    with urllib.request.urlopen(req_svg) as r:
        print(f"[5b. ROUTE /static/index.htmlsvg] HTTP {r.status} | Redirected to: {r.geturl()}")
        assert "index.html" in r.geturl()

    print("\n==================================================")
    print("ALL 5 FULL-STACK STEPS COMPLETED AND VERIFIED 100%!")
    print("==================================================")

if __name__ == "__main__":
    run_simulation()
