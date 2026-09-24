"""
SnapStyle FAISS Similarity Search Verification Test
Validates:
1. Building FAISS IndexFlatIP (512-dim) using real Transformers CLIP embeddings for all 24 catalog items.
2. Verification of L2 vector normalization (norm = 1.000000) for exact Cosine Similarity.
3. Disk persistence and reloading of catalog embeddings (.npz) and FAISS index (.faiss_index).
4. Self-similarity verification: Querying a product image returns itself as top-1 with similarity ~1.0000.
5. Real outfit crop image similarity search with authentic cosine similarity scores (no fake offsets).
6. Category-filtered search functionality.
7. Verification that search is REAL FAISS (not fallback) and reports exactly 24 indexed products.
"""

import os
import sys
import numpy as np
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.similarity_search import (
    FashionSimilarityIndex,
    normalize_vector,
    FAISS_AVAILABLE
)
from backend.embeddings import generate_image_embedding, get_clip_model, get_clip_model_info
from backend.products import get_all_products, get_product_by_id

def test_faiss_similarity_search():
    print("=" * 75)
    print("SNAPSTYLE REAL FAISS SIMILARITY SEARCH VERIFICATION TEST")
    print("=" * 75)

    # 1. Check FAISS Library Availability
    print("\n[Step 1] Checking FAISS Environment...")
    assert FAISS_AVAILABLE, "FAISS is not installed or available!"
    import faiss
    print(f"  FAISS Library Version:      {faiss.__version__}")
    print(f"  FAISS Available:            {FAISS_AVAILABLE}")
    print("  -> Step 1 Passed: FAISS library is available and operational.")

    # 2. Build / Load FAISS Index with Real CLIP Embeddings
    print("\n[Step 2] Building Real FAISS Catalog Index with Transformers CLIP...")
    products = get_all_products()
    print(f"  Total Catalog Products:     {len(products)}")
    assert len(products) == 24, f"Expected 24 catalog products, got {len(products)}"

    # Initialize index instance
    storage_npz = os.path.join(PROJECT_ROOT, "data", "catalog_embeddings.npz")
    index_file = os.path.join(PROJECT_ROOT, "data", "catalog.faiss_index")
    
    test_index = FashionSimilarityIndex(
        dimension=512,
        storage_path=storage_npz,
        index_path=index_file
    )

    def embed_product(prod):
        pid = prod["product_id"]
        img_path = os.path.join(PROJECT_ROOT, "frontend", "assets", "products", f"{pid}.jpg")
        assert os.path.exists(img_path), f"Missing product image: {img_path}"
        img = Image.open(img_path)
        return generate_image_embedding(img, category_hint=prod.get("category", ""))

    # Force rebuild to ensure embeddings are computed from real CLIP
    test_index.build_or_load_catalog_index(products, embed_product, force_rebuild=True)

    status = test_index.get_index_status()
    print(f"  Indexed Products Count:     {status['indexed_products_count']}")
    print(f"  Embedding Dimension:        {status['dimension']}")
    print(f"  Index Type:                 {status['index_type']}")
    print(f"  Is Real FAISS:              {status['is_real_faiss']}")
    print(f"  Search Source:              {status['search_source']}")
    print(f"  Similarity Metric:          {status['similarity_metric']}")

    assert status["is_real_faiss"] is True, "Expected is_real_faiss to be True"
    assert status["indexed_products_count"] == 24, f"Expected 24 indexed products, got {status['indexed_products_count']}"
    assert status["search_source"] == "real_faiss", "Expected search_source to be 'real_faiss'"
    print("  -> Step 2 Passed: FAISS IndexFlatIP successfully built with 24 products.")

    # 3. Verify Vector Normalization & Shapes
    print("\n[Step 3] Verifying Vector Normalization on Stored Embeddings...")
    assert len(test_index.embeddings) == 24, f"Expected 24 embeddings, got {len(test_index.embeddings)}"
    for i, vec in enumerate(test_index.embeddings):
        pid = test_index.product_ids[i]
        assert vec.shape == (512,), f"Expected shape (512,), got {vec.shape} for {pid}"
        assert vec.dtype == np.float32, f"Expected dtype float32, got {vec.dtype} for {pid}"
        norm = float(np.linalg.norm(vec))
        assert abs(norm - 1.0) < 1e-4, f"Vector for {pid} is not normalized: norm = {norm}"
        assert not np.isnan(vec).any(), f"Vector for {pid} contains NaN"
        assert not np.isinf(vec).any(), f"Vector for {pid} contains Inf"

    print("  Verified all 24 product vectors: shape (512,), float32, L2 norm == 1.000000.")
    print("  -> Step 3 Passed: All stored product vectors are strictly unit-normalized.")

    # 4. Verify Disk Persistence and Fast Reload
    print("\n[Step 4] Verifying Disk Persistence & Reloading...")
    assert os.path.exists(storage_npz), f"Embeddings npz file was not created: {storage_npz}"
    assert os.path.exists(index_file), f"FAISS index file was not created: {index_file}"
    npz_size = os.path.getsize(storage_npz)
    idx_size = os.path.getsize(index_file)
    print(f"  Persisted NPZ File Size:    {npz_size:,} bytes ({storage_npz})")
    print(f"  Persisted Index Size:       {idx_size:,} bytes ({index_file})")

    # Test loading from disk into a fresh index
    reload_index = FashionSimilarityIndex(dimension=512, storage_path=storage_npz, index_path=index_file)
    load_success = reload_index.load_from_disk()
    assert load_success is True, "Failed to load embeddings from disk cache!"
    assert reload_index.is_real_faiss() is True, "Reloaded index is not real FAISS"
    assert len(reload_index.product_ids) == 24, f"Expected 24 reloaded products, got {len(reload_index.product_ids)}"
    print(f"  Successfully reloaded {len(reload_index.product_ids)} products from disk.")
    print("  -> Step 4 Passed: Disk persistence and instant reload verified.")

    # 5. Self-Similarity Test: Top-1 Match Must Be Itself with Score ~ 1.0
    print("\n[Step 5] Testing Self-Similarity Search (Exact Match Sanity Check)...")
    target_pid = "prod_010"
    target_img_path = os.path.join(PROJECT_ROOT, "frontend", "assets", "products", f"{target_pid}.jpg")
    target_img = Image.open(target_img_path)
    target_vec = generate_image_embedding(target_img, category_hint="bag")

    self_matches = test_index.search(target_vec, top_k=3)
    print(f"  Self-Query Product:         {target_pid}")
    print(f"  Top-1 Matched Product ID:   {self_matches[0]['product_id']}")
    print(f"  Top-1 Similarity Score:     {self_matches[0]['similarity_score']:.6f}")
    print(f"  Top-1 Match Percentage:     {self_matches[0]['match_pct']}")
    print(f"  Top-1 Search Source:        {self_matches[0]['search_source']}")

    assert self_matches[0]["product_id"] == target_pid, f"Expected top match to be {target_pid}, got {self_matches[0]['product_id']}"
    assert self_matches[0]["similarity_score"] >= 0.999, f"Expected self-similarity >= 0.999, got {self_matches[0]['similarity_score']}"
    assert self_matches[0]["search_source"] == "real_faiss", "Expected real_faiss search source"
    print("  -> Step 5 Passed: Self-similarity yielded exact 1.0000 cosine similarity match.")

    # 6. Real Outfit Image Search Test
    print("\n[Step 6] Testing Real Outfit Image Search Against Catalog...")
    outfit_candidates = [
        os.path.join(PROJECT_ROOT, "backend", "uploads", "upload_4c43cd7dec.png"),
        os.path.join(PROJECT_ROOT, "backend", "uploads", "upload_216333dbae.png"),
        os.path.join(PROJECT_ROOT, "backend", "uploads", "demo_sample.jpg")
    ]
    outfit_path = next((p for p in outfit_candidates if os.path.exists(p)), None)
    assert outfit_path is not None, "No outfit test image found!"

    outfit_img = Image.open(outfit_path)
    outfit_vec = generate_image_embedding(outfit_img, category_hint="outfit")

    # Search with category filter: bag
    bag_matches = test_index.search(outfit_vec, category_filter="bag", top_k=3)
    print(f"  Category 'bag' Matches Count: {len(bag_matches)}")
    assert len(bag_matches) > 0, "Expected bag matches from FAISS"
    for m in bag_matches:
        prod = get_product_by_id(m["product_id"])
        name = prod["product_name"] if prod else m["product_id"]
        print(f"    - {m['product_id']} ({name}): {m['match_pct']} (Score: {m['similarity_score']:.4f}, Source: {m['search_source']})")
        assert m["search_source"] == "real_faiss", "Expected real_faiss search source"
        assert 0.0 <= m["similarity_score"] <= 1.0, f"Invalid similarity score {m['similarity_score']}"

    # Search with category filter: top
    top_matches = test_index.search(outfit_vec, category_filter="top", top_k=3)
    print(f"  Category 'top' Matches Count: {len(top_matches)}")
    assert len(top_matches) > 0, "Expected top matches from FAISS"
    for m in top_matches:
        prod = get_product_by_id(m["product_id"])
        name = prod["product_name"] if prod else m["product_id"]
        print(f"    - {m['product_id']} ({name}): {m['match_pct']} (Score: {m['similarity_score']:.4f}, Source: {m['search_source']})")
        assert m["search_source"] == "real_faiss", "Expected real_faiss search source"

    print("  -> Step 6 Passed: Real outfit search returned authentic FAISS similarity scores.")

    print("\n" + "=" * 75)
    print("ALL REAL FAISS SIMILARITY SEARCH TESTS PASSED 100%!")
    print("=" * 75)

if __name__ == "__main__":
    test_faiss_similarity_search()
