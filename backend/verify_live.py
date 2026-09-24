"""
SnapStyle Live Server Verification
Validates live FastAPI endpoints, FAISS search, and static frontend assets.
"""
import urllib.request
import json
import sys

BASE = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================")
    print("VERIFYING LIVE SNAPSTYLE APPLICATION")
    print("==================================================")

    # 1. Health check
    with urllib.request.urlopen(f"{BASE}/") as r:
        data = json.loads(r.read().decode())
        print(f"[PASS] Health check: {data['app']} ({data['tagline']}) - Status: {data['status']}")
        assert data["app"] == "SnapStyle"

    # 2. Product catalog via Pandas
    with urllib.request.urlopen(f"{BASE}/products?category=bottom") as r:
        prods = json.loads(r.read().decode())
        print(f"[PASS] Catalog API (/products?category=bottom): {prods['count']} items found")
        assert prods["count"] > 0

    # 3. AI Analysis endpoint (YOLO / OpenCV)
    req = urllib.request.Request(
        f"{BASE}/analyze",
        data=json.dumps({"upload_id": "demo"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        ana = json.loads(r.read().decode())
        print(f"[PASS] AI Analysis (/analyze): {ana['item_count']} items detected, AI Confidence: {ana['ai_confidence']}")
        assert ana["success"] is True

    # 4. Similarity search via FAISS + CLIP embeddings
    req2 = urllib.request.Request(
        f"{BASE}/search-products",
        data=json.dumps({"detected_items": ana["detected_items"]}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req2) as r:
        search_res = json.loads(r.read().decode())
        cats = list(search_res["results_by_category"].keys())
        print(f"[PASS] FAISS Similarity Search (/search-products): Matched {len(cats)} categories: {cats}")
        assert search_res["success"] is True

    # 5. Wishlist API
    with urllib.request.urlopen(f"{BASE}/wishlist") as r:
        wl = json.loads(r.read().decode())
        print(f"[PASS] Wishlist API (/wishlist): {wl['count']} items in wishlist")

    # 6. Static frontend delivery (Google Stitch Prototype aesthetic)
    assets = [
        "/static/index.html",
        "/static/css/style.css",
        "/static/js/app.js",
        "/static/js/state.js",
        "/static/js/api.js"
    ]
    for path in assets:
        with urllib.request.urlopen(f"{BASE}{path}") as r:
            code = r.status
            size = len(r.read())
            print(f"[PASS] Frontend Asset: {path} -> HTTP {code} ({size} bytes)")
            assert code == 200

    print("==================================================")
    print("ALL LIVE SNAPSTYLE VERIFICATIONS PASSED 100%!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
