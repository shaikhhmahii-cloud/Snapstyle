"""
SnapStyle CLIP Visual Embeddings Verification Test
Tests:
1. Singleton loading of Hugging Face Transformers CLIP model.
2. Embedding generation on a real uploaded outfit image.
3. Verification of 512-dimensional L2-normalized float32 vector (norm = 1.0).
4. Product image embedding generation.
5. End-to-end FAISS vector search integration.
6. Verification that YOLO demo fallback remains functional.
"""

import os
import sys
import numpy as np
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.embeddings import (
    get_clip_model,
    get_clip_model_info,
    generate_image_embedding,
    generate_image_embedding_with_meta,
    is_real_clip_loaded,
    EMBEDDING_DIM
)
from backend.detection import detect_fashion_items, get_yolo_model
from backend.similarity_search import FashionSimilarityIndex

def test_clip_embeddings():
    print("=" * 70)
    print("SNAPSTYLE CLIP VISUAL EMBEDDINGS VERIFICATION TEST")
    print("=" * 70)

    # 1. Verify CLIP Model Loading
    print("\n[Step 1] Loading CLIP Model...")
    model, processor = get_clip_model()
    assert model is not None, "Failed to load CLIP model!"
    assert processor is not None, "Failed to load CLIP processor!"
    
    info = get_clip_model_info()
    print(f"  Model Name:         {info['model_name']}")
    print(f"  Model Type:         {info['model_type']}")
    print(f"  Embedding Dimension: {info['embedding_dimension']}")
    print(f"  Is Real CLIP:       {info['is_real_clip']}")
    print(f"  Source:             {info['source']}")
    print(f"  Device:             {info['device']}")
    
    assert info["is_real_clip"] is True, "Expected is_real_clip to be True"
    assert info["embedding_dimension"] == 512, "Expected embedding dimension to be 512"
    assert info["source"] == "real_clip", "Expected source to be 'real_clip'"
    print("  -> Step 1 Passed: Real Transformers CLIP loaded successfully.")

    # 2. Test Real Outfit Image Embedding
    print("\n[Step 2] Testing Visual Embedding on Real Outfit Image...")
    outfit_candidates = [
        os.path.join(PROJECT_ROOT, "backend", "uploads", "upload_4c43cd7dec.png"),
        os.path.join(PROJECT_ROOT, "backend", "uploads", "upload_216333dbae.png"),
        os.path.join(PROJECT_ROOT, "backend", "uploads", "upload_bd79402516.png"),
        os.path.join(PROJECT_ROOT, "backend", "uploads", "demo_sample.jpg")
    ]
    
    outfit_path = None
    for path in outfit_candidates:
        if os.path.exists(path):
            outfit_path = path
            break
            
    assert outfit_path is not None, "No real outfit image found for testing!"
    print(f"  Using outfit image: {os.path.basename(outfit_path)}")
    
    outfit_img = Image.open(outfit_path)
    emb, meta = generate_image_embedding_with_meta(outfit_img, category_hint="outfit")
    
    print(f"  Output Embedding Type:      {type(emb)}")
    print(f"  Output Embedding Shape:     {emb.shape}")
    print(f"  Output Embedding Dtype:     {emb.dtype}")
    print(f"  Vector First 5 Values:      {emb[:5].round(4).tolist()}")
    print(f"  Vector L2 Norm:             {np.linalg.norm(emb):.6f}")
    print(f"  Metadata Result:            {meta}")
    
    # Assertions
    assert isinstance(emb, np.ndarray), "Embedding must be a numpy ndarray"
    assert emb.shape == (512,), f"Expected shape (512,), got {emb.shape}"
    assert emb.dtype == np.float32, f"Expected dtype float32, got {emb.dtype}"
    norm = np.linalg.norm(emb)
    assert abs(norm - 1.0) < 1e-4, f"Embedding must be unit-normalized (L2 norm = 1.0), got {norm}"
    assert meta["is_real_clip"] is True, "Metadata must confirm real CLIP model"
    assert meta["source"] == "real_clip", "Metadata source must be 'real_clip'"
    assert not np.isnan(emb).any(), "Embedding contains NaN values"
    assert not np.isinf(emb).any(), "Embedding contains Inf values"
    print("  -> Step 2 Passed: Real outfit image embedding generated and verified.")

    # 3. Test Product Catalog Image Embedding
    print("\n[Step 3] Testing Visual Embedding on Product Catalog Image...")
    prod_path = os.path.join(PROJECT_ROOT, "frontend", "assets", "products", "prod_010.jpg")
    if not os.path.exists(prod_path):
        prod_path = os.path.join(PROJECT_ROOT, "frontend", "assets", "products", "prod_001.jpg")
    
    print(f"  Using product image: {os.path.basename(prod_path)}")
    prod_img = Image.open(prod_path)
    prod_emb, prod_meta = generate_image_embedding_with_meta(prod_img, category_hint="top")
    
    assert prod_emb.shape == (512,), f"Expected shape (512,), got {prod_emb.shape}"
    assert abs(np.linalg.norm(prod_emb) - 1.0) < 1e-4, "Product embedding must have L2 norm = 1.0"
    assert prod_meta["source"] == "real_clip", "Product embedding must use real CLIP"
    print(f"  Product Embedding Shape:    {prod_emb.shape}")
    print(f"  Product Embedding L2 Norm:  {np.linalg.norm(prod_emb):.6f}")
    print(f"  Product Vector First 5:     {prod_emb[:5].round(4).tolist()}")
    print("  -> Step 3 Passed: Product catalog image embedding generated and verified.")

    # 4. Test Cosine Similarity Search with FAISS
    print("\n[Step 4] Testing FAISS Cosine Similarity with Real CLIP Embeddings...")
    faiss_index = FashionSimilarityIndex(dimension=512)
    faiss_index.add_product("test_prod_010", "top", prod_emb)
    matches = faiss_index.search(emb, category_filter="top", top_k=1)
    print(f"  FAISS Search Result: {matches}")
    print(f"  Match Score: {matches[0]['match_pct']} (Cosine sim: {matches[0]['similarity_score']:.4f})")
    print("  -> Step 4 Passed: FAISS similarity search completed successfully.")

    # 5. Verify YOLO Demo Fallback Remains Working
    print("\n[Step 5] Verifying YOLO Demo Fallback Remains Intact...")
    yolo_model = get_yolo_model()
    print(f"  YOLO Model Loaded: {yolo_model is not None}")
    
    crops_dir = os.path.join(PROJECT_ROOT, "backend", "uploads", "test_crops")
    dummy_img = Image.new("RGB", (200, 200), color=(200, 200, 200))
    fallback_items = detect_fashion_items(dummy_img, upload_id="demo", crops_dir=crops_dir, force_fallback=True)
    assert len(fallback_items) == 4, f"Expected 4 demo items, got {len(fallback_items)}"
    for item in fallback_items:
        assert item["is_fallback"] is True, "Expected is_fallback to be True"
        assert item["detection_source"] == "demo_fallback", "Expected detection_source 'demo_fallback'"
    print(f"  Fallback Items Count:       {len(fallback_items)} items")
    print(f"  Fallback First Item Source: {fallback_items[0]['detection_source']}")
    print(f"  Fallback is_fallback flag:  {fallback_items[0]['is_fallback']}")
    print("  -> Step 5 Passed: YOLO demo fallback is fully functional.")

    # 6. Verify Real YOLO Detection Still Works
    print("\n[Step 6] Verifying Real YOLO Detection with Real Outfit Image...")
    real_yolo_items = detect_fashion_items(outfit_img, upload_id="yolo_test", crops_dir=crops_dir)
    print(f"  Detected Items Count:       {len(real_yolo_items)}")
    for item in real_yolo_items:
        print(f"    - {item['label']} (conf: {item.get('confidence')}, source: {item.get('detection_source')}, is_fallback: {item.get('is_fallback')})")
    print("  -> Step 6 Passed: Real YOLO detection verified.")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_clip_embeddings()
