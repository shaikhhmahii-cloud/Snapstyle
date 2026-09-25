"""
SnapStyle FastAPI Backend Application
Main entry point for SnapStyle AI fashion discovery.
Connects Pillow, OpenCV, Ultralytics YOLO, Transformers, FAISS, and Pandas.
"""

import os
import uuid
import shutil
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.image_processing import (
    validate_and_open_image,
    resize_image_for_ai,
    preprocess_for_detection,
    draw_focus_brackets
)
from backend.detection import detect_fashion_items, map_detected_item_to_catalog_category
from backend.embeddings import generate_image_embedding
from backend.similarity_search import fashion_index
from backend.products import (
    get_all_products,
    get_product_by_id,
    filter_products,
    get_wishlist_products,
    add_to_wishlist,
    remove_from_wishlist,
    get_saved_looks,
    save_new_look
)

BASE_DIR = os.path.dirname(__file__)
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
CROPS_DIR = os.path.join(UPLOADS_DIR, "crops")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CROPS_DIR, exist_ok=True)

app = FastAPI(
    title="SnapStyle API",
    description="Full-stack AI Fashion Discovery Backend powered by YOLO, CLIP, FAISS, Pillow, OpenCV, Pandas, and FastAPI.",
    version="1.0.0"
)

# Enable CORS for local dev and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads directory for serving inspiration photos and crops
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

@app.get("/static/index.htmlsvg")
@app.get("/index.htmlsvg")
def redirect_errant_htmlsvg():
    """Gracefully redirects errant /index.htmlsvg paths to /static/index.html."""
    return RedirectResponse(url="/static/index.html", status_code=307)

@app.get("/app")
def serve_app():
    """Serves the SnapStyle frontend directly on /app."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return RedirectResponse(url="/static/index.html")

@app.get("/")
def serve_root():
    """Redirects root URL to the SnapStyle mobile app UI."""
    return RedirectResponse(url="/app")

@app.get("/manifest.json")
def serve_manifest():
    """Serves PWA manifest.json at root for mobile installability."""
    manifest_path = os.path.join(FRONTEND_DIR, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/manifest+json")
    raise HTTPException(status_code=404, detail="Manifest not found")

@app.get("/service-worker.js")
def serve_sw():
    """Serves PWA service-worker.js at root for PWA caching and offline support."""
    sw_path = os.path.join(FRONTEND_DIR, "service-worker.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Service worker not found")

@app.get("/download/apk")
@app.get("/SnapStyle.apk")
def download_apk():
    """Serves the compiled SnapStyle Android APK for direct mobile installation."""
    apk_path = os.path.join(os.path.dirname(BASE_DIR), "SnapStyle.apk")
    if os.path.exists(apk_path):
        return FileResponse(
            apk_path,
            media_type="application/vnd.android.package-archive",
            filename="SnapStyle.apk"
        )
    return RedirectResponse(
        url="https://github.com/shaikhhmahii-cloud/Snapstyle/releases/download/v1.0.0/SnapStyle.apk"
    )

# Mount frontend directory for easy full-stack unified serving
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

DEMO_PRODUCT_URLS = {
    "prod_001": "https://www.zara.com/in/en/crisp-white-blouse-p08432001.html",
    "prod_002": "https://www.myntra.com/shirts/hm/hm-men-white-cotton-poplin-relaxed-fit-casual-shirt/21456789/buy",
    "prod_003": "https://www.myntra.com/tops/snapstyle/women-white-structured-sweetheart-crop-top/19842003/buy",
    "prod_004": "https://www.zara.com/in/en/oversized-poplin-shirt-p08432004.html",
    "prod_005": "https://www.massimodutti.com/in/white-oversized-shirt-l05123005",
    "prod_006": "https://www.myntra.com/jeans/mango/mango-women-light-wash-high-rise-straight-fit-jeans/18923006/buy",
    "prod_007": "https://www.myntra.com/jeans/levis/levis-vintage-clothing-women-classic-straight-fit-jeans/17584007/buy",
    "prod_008": "https://www.myntra.com/jeans/levis/levis-women-501-original-straight-fit-jeans/17584102/buy",
    "prod_009": "https://www.myntra.com/jeans/hm/hm-women-wide-high-waisted-denim-jeans/21456009/buy",
    "prod_010": "https://www.myntra.com/handbags/charles--keith/charles--keith-structured-beige-tote-bag/23456010/buy",
    "prod_011": "https://www.zara.com/in/en/minimalist-leather-handbag-p06232011.html",
    "prod_012": "https://www.myntra.com/jewellery/aurate/aurate-women-14k-gold-vermeil-pendant-necklace--hoops-set/18456012/buy",
    "prod_013": "https://www.massimodutti.com/in/classic-leather-loafers-l0123013",
    "prod_014": "https://www.myntra.com/casual-shoes/nike/nike-court-royale-2-minimalist-white-leather-sneakers/19456014/buy",
    "prod_015": "https://www.myntra.com/jackets/mango/mango-women-structured-double-breasted-trench-coat/18923456/buy",
    "prod_016": "https://www.myntra.com/sunglasses/ray-ban/ray-ban-unisex-tortoise-square-sunglasses/15678901/buy",
    "prod_017": "https://www.zara.com/in/en/linen-tailored-trousers-p07332017.html",
    "prod_018": "https://www.myntra.com/handbags/charles--keith/charles--keith-leather-crossbody-mini-bag/23456018/buy",
    "prod_019": "https://www.myntra.com/jewellery/hm/hm-women-chunky-brushed-gold-plated-chain-necklace/21456019/buy",
    "prod_020": "https://www.zara.com/in/en/suede-pointed-ballet-flats-p02132020.html",
    "prod_021": "https://www.myntra.com/tops/mango/mango-women-ribbed-knit-sleeveless-high-neck-top/18923021/buy",
    "prod_022": "https://www.zara.com/in/en/pleated-slip-maxi-skirt-p04232022.html",
    "prod_023": "https://www.myntra.com/heels/charles--keith/charles--keith-women-strappy-minimal-heeled-sandals/23456023/buy",
    "prod_024": "https://www.myntra.com/handbags/hm/hm-women-artisanal-woven-straw-market-tote-bag/21456024/buy",
    "prod_025": "https://www.zara.com/in/en/striped-relaxed-poplin-shirt-p08432025.html",
    "prod_026": "https://www.massimodutti.com/in/linen-mandarin-collar-shirt-l05123026",
    "prod_027": "https://www.myntra.com/tops/mango/mango-women-black-ribbed-mock-neck-top/21456027/buy",
    "prod_028": "https://www.myntra.com/tshirts/hm/hm-men-classic-crew-neck-organic-cotton-tshirt/21456028/buy",
    "prod_029": "https://www.myntra.com/shirts/marks--spencer/m-and-s-women-silk-satin-tie-neck-formal-blouse/21456029/buy",
    "prod_030": "https://www.myntra.com/shirts/levis/levis-men-classic-chambray-denim-button-down-shirt/21456030/buy",
    "prod_031": "https://www.zara.com/in/en/knitted-cable-polo-sweater-p08432031.html",
    "prod_032": "https://www.myntra.com/tops/only/only-women-square-neck-structured-corset-camisole/21456032/buy",
    "prod_033": "https://www.massimodutti.com/in/merino-wool-turtleneck-sweater-l05123033",
    "prod_034": "https://www.myntra.com/tops/hm/hm-women-boxy-cropped-linen-blend-short-sleeve-blouse/21456034/buy",
    "prod_035": "https://www.myntra.com/tshirts/roadster/roadster-unisex-vintage-wash-oversized-graphic-tee/21456035/buy",
    "prod_036": "https://www.myntra.com/sweaters/mango/mango-women-pointelle-knit-scallop-trim-cardigan/21456036/buy",
    "prod_037": "https://www.myntra.com/shirts/marks--spencer/m-and-s-men-pure-cotton-tailored-oxford-shirt/21456037/buy",
    "prod_038": "https://www.myntra.com/tops/vero-moda/vero-moda-women-lace-trim-satin-v-neck-camisole/21456038/buy",
    "prod_039": "https://www.zara.com/in/en/cotton-crochet-halter-top-p08432039.html",
    "prod_040": "https://www.myntra.com/tops/fabindia/fabindia-women-handblock-printed-khadi-cotton-short-kurta/21456040/buy",
    "prod_041": "https://www.zara.com/in/en/high-rise-wide-leg-trousers-p08432041.html",
    "prod_042": "https://www.myntra.com/jeans/levis/levis-women-mile-high-super-skinny-fit-jeans/21456042/buy",
    "prod_043": "https://www.massimodutti.com/in/tailored-linen-bermuda-shorts-l05123043",
    "prod_044": "https://www.myntra.com/skirts/mango/mango-women-a-line-denim-maxi-skirt-with-slit/21456044/buy",
    "prod_045": "https://www.myntra.com/trousers/marks--spencer/m-and-s-men-regular-fit-stretch-chino-trousers/21456045/buy",
    "prod_046": "https://www.myntra.com/skirts/hm/hm-women-pleated-a-line-tennis-mini-skirt/21456046/buy",
    "prod_047": "https://www.myntra.com/trousers/roadster/roadster-unisex-high-waist-cotton-cargo-jogger-pants/21456047/buy",
    "prod_048": "https://www.zara.com/in/en/cropped-cigarette-trousers-p08432048.html",
    "prod_049": "https://www.myntra.com/jeans/levis/levis-women-ribcage-bootcut-vintage-flared-jeans/21456049/buy",
    "prod_050": "https://www.myntra.com/skirts/mango/mango-women-bias-cut-flowy-satin-midi-skirt/21456050/buy",
    "prod_051": "https://www.myntra.com/trousers/fabindia/fabindia-unisex-pure-linen-drawstring-wide-leg-pants/21456051/buy",
    "prod_052": "https://www.myntra.com/shorts/only/only-women-high-rise-distressed-denim-cut-off-shorts/21456052/buy",
    "prod_053": "https://www.myntra.com/trousers/vero-moda/vero-moda-women-paperbag-waist-belted-chinos/21456053/buy",
    "prod_054": "https://www.massimodutti.com/in/houndstooth-wool-blend-culottes-l05123054",
    "prod_055": "https://www.myntra.com/trousers/hm/hm-men-straight-leg-ribbed-cotton-corduroy-pants/21456055/buy",
    "prod_056": "https://www.myntra.com/skirts/fabindia/fabindia-women-tiered-cotton-boho-flared-maxi-skirt/21456056/buy",
    "prod_057": "https://www.zara.com/in/en/oversized-wool-blend-blazer-p08432057.html",
    "prod_058": "https://www.massimodutti.com/in/leather-biker-motorcycle-jacket-l05123058",
    "prod_059": "https://www.myntra.com/jackets/levis/levis-unisex-original-vintage-trucker-denim-jacket/21456059/buy",
    "prod_060": "https://www.myntra.com/jackets/mango/mango-women-cropped-quilted-puffer-jacket/21456060/buy",
    "prod_061": "https://www.myntra.com/blazers/marks--spencer/m-and-s-men-pure-linen-tailored-summer-blazer/21456061/buy",
    "prod_062": "https://www.zara.com/in/en/textured-boucle-tweed-jacket-p08432062.html",
    "prod_063": "https://www.massimodutti.com/in/belted-longline-wool-wrap-coat-l05123063",
    "prod_064": "https://www.myntra.com/jackets/puma/puma-unisex-classic-satin-varsity-bomber-jacket/21456064/buy",
    "prod_065": "https://www.myntra.com/jackets/hm/hm-men-cotton-canvas-oversized-utility-shacket/21456065/buy",
    "prod_066": "https://www.myntra.com/jackets/only/only-women-faux-shearling-lined-aviator-jacket/21456066/buy",
    "prod_067": "https://www.myntra.com/jackets/vero-moda/vero-moda-women-suede-finish-western-fringe-jacket/21456067/buy",
    "prod_068": "https://www.myntra.com/jackets/marks--spencer/m-and-s-women-stormwear-water-resistant-hooded-parka/21456068/buy",
    "prod_069": "https://www.myntra.com/jackets/roadster/roadster-women-acid-wash-denim-shacket/21456069/buy",
    "prod_070": "https://www.zara.com/in/en/canvas-leather-shopper-tote-p08432070.html",
    "prod_071": "https://www.myntra.com/handbags/charles--keith/charles--keith-crescent-moon-leather-baguette-bag/21456071/buy",
    "prod_072": "https://www.massimodutti.com/in/saddle-leather-crossbody-flap-bag-l05123072",
    "prod_073": "https://www.myntra.com/handbags/hm/hm-women-puffer-quilted-nylon-shoulder-cloud-bag/21456073/buy",
    "prod_074": "https://www.myntra.com/handbags/aldo/aldo-women-structured-box-top-handle-handbag/21456074/buy",
    "prod_075": "https://www.myntra.com/handbags/mango/mango-women-woven-leather-drawstring-bucket-bag/21456075/buy",
    "prod_076": "https://www.myntra.com/backpacks/fossil/fossil-unisex-classic-leather-city-commuter-backpack/21456076/buy",
    "prod_077": "https://www.zara.com/in/en/raffia-envelope-clutch-p08432077.html",
    "prod_078": "https://www.myntra.com/handbags/nike/nike-sportswear-utility-multi-pocket-crossbody-bag/21456078/buy",
    "prod_079": "https://www.myntra.com/handbags/fabindia/fabindia-women-hand-embroidered-jute-market-tote/21456079/buy",
    "prod_080": "https://www.myntra.com/handbags/charles--keith/charles--keith-metallic-pleated-evening-clutch/21456080/buy",
    "prod_081": "https://www.myntra.com/handbags/hm/hm-unisex-convertible-nylon-belt-fanny-pack-bag/21456081/buy",
    "prod_082": "https://www.massimodutti.com/in/slouchy-leather-hobo-shoulder-bag-l05123082",
    "prod_083": "https://www.myntra.com/handbags/mango/mango-women-miniature-leather-coin-pouch-crossbody/21456083/buy",
    "prod_084": "https://www.zara.com/in/en/chunky-lug-sole-leather-loafers-p08432084.html",
    "prod_085": "https://www.myntra.com/casual-shoes/nike/nike-air-force-1-07-classic-all-white-leather-sneakers/21456085/buy",
    "prod_086": "https://www.myntra.com/heels/charles--keith/charles--keith-women-ankle-strap-block-heel-sandals/21456086/buy",
    "prod_087": "https://www.massimodutti.com/in/leather-chelsea-ankle-boots-l05123087",
    "prod_088": "https://www.myntra.com/flats/mango/mango-women-suede-ballet-flats-with-dainty-bow/21456088/buy",
    "prod_089": "https://www.myntra.com/casual-shoes/puma/puma-unisex-retro-suede-classic-court-sneakers/21456089/buy",
    "prod_090": "https://www.myntra.com/heels/aldo/aldo-women-pointed-toe-leather-slip-on-mule-heels/21456090/buy",
    "prod_091": "https://www.myntra.com/heels/hm/hm-women-traditional-braided-jute-espadrille-wedges/21456091/buy",
    "prod_092": "https://www.zara.com/in/en/lace-up-combat-ankle-boots-p08432092.html",
    "prod_093": "https://www.massimodutti.com/in/minimalist-leather-flat-slides-l05123093",
    "prod_094": "https://www.myntra.com/heels/charles--keith/charles--keith-embellished-metallic-stiletto-pumps/21456094/buy",
    "prod_095": "https://www.myntra.com/flats/fabindia/fabindia-women-handcrafted-embroidered-leather-juttis/21456095/buy",
    "prod_096": "https://www.myntra.com/casual-shoes/roadster/roadster-men-canvas-low-top-casual-skater-shoes/21456096/buy",
    "prod_097": "https://www.myntra.com/sunglasses/mango/mango-women-retro-cat-eye-acetate-sunglasses/21456097/buy",
    "prod_098": "https://www.myntra.com/sunglasses/ray-ban/ray-ban-unisex-round-metal-frame-green-lens-sunglasses/21456098/buy",
    "prod_099": "https://www.myntra.com/jewellery/aurate/aurate-women-14k-gold-vermeil-chunky-tubular-hoop-earrings/21456099/buy",
    "prod_100": "https://www.massimodutti.com/in/reversible-italian-leather-belt-l05123100",
    "prod_101": "https://www.zara.com/in/en/printed-mulberry-silk-square-scarf-p08432101.html",
    "prod_102": "https://www.myntra.com/watches/fossil/fossil-unisex-minimalist-slim-case-mesh-bracelet-watch/21456102/buy",
    "prod_103": "https://www.zara.com/in/en/satin-bias-cut-slip-midi-dress-p08432103.html",
    "prod_104": "https://www.massimodutti.com/in/belted-linen-button-down-shirt-dress-l05123104",
    "prod_105": "https://www.myntra.com/dresses/mango/mango-women-ribbed-knit-sleeveless-bodycon-maxi-dress/21456105/buy",
}

def ensure_catalog_indexed():
    """Builds the FAISS similarity index for product catalog using real CLIP embeddings."""
    if fashion_index.index is None or fashion_index.index.ntotal == 0:
        products = get_all_products()
        from backend.embeddings import generate_image_embedding
        from PIL import Image

        def catalog_embedder(product: Dict[str, Any]):
            pid = product.get("product_id", "")
            img_path = os.path.join(FRONTEND_DIR, "assets", "products", f"{pid}.jpg")
            if os.path.exists(img_path):
                try:
                    p_img = Image.open(img_path)
                    return generate_image_embedding(p_img, category_hint=product.get("category", ""))
                except Exception:
                    pass
            dummy = Image.new("RGB", (64, 64), color=(245, 240, 235))
            return generate_image_embedding(dummy, category_hint=f"{product.get('category', '')}_{product.get('product_name', '')}")

        fashion_index.build_catalog_index(products, catalog_embedder)

@app.on_event("startup")
def startup_event():
    """Builds the FAISS similarity index and pre-warms YOLO and CLIP models on startup."""
    print("[SnapStyle] Starting up AI Fashion Discovery Backend...")
    # Pre-warm DeepFashion2 and COCO YOLO models once
    from backend.detection import get_deepfashion2_model, get_yolo_model
    get_deepfashion2_model()
    get_yolo_model()
    # Pre-warm CLIP model singleton once
    from backend.embeddings import get_clip_model
    get_clip_model()
    # Index catalog with real CLIP visual embeddings
    ensure_catalog_indexed()
    print("[SnapStyle] FAISS catalog index, DeepFashion2 YOLO, COCO YOLO, and CLIP models initialized successfully.")

@app.get("/")
def root(request: Request):
    """Health check endpoint confirming SnapStyle backend status and components. Serves HTML to browsers."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

    from backend.embeddings import get_clip_model_info
    clip_info = get_clip_model_info()
    faiss_status = fashion_index.get_index_status()

    return {
        "app": "SnapStyle",
        "tagline": "Snap your inspiration. Find your style.",
        "status": "running",
        "version": "1.0.0",
        "ai_pipeline": {
            "image_processing": "Pillow + OpenCV",
            "detection": "Ultralytics YOLO (v8)",
            "embeddings": f"Transformers CLIP ({clip_info['model_name']})",
            "embedding_dimension": clip_info["embedding_dimension"],
            "clip_real": clip_info["is_real_clip"],
            "similarity_search": "FAISS IndexFlatIP",
            "indexed_products_count": faiss_status["indexed_products_count"],
            "faiss_real": faiss_status["is_real_faiss"],
            "catalog": "Pandas"
        }
    }

@app.get("/app")
def serve_app():
    """Serves the SnapStyle frontend application."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend index.html not found.")

@app.get("/static/index.htmlsvg")
@app.get("/index.htmlsvg")
def redirect_index_htmlsvg():
    """Redirects errant index.htmlsvg path cleanly to /static/index.html."""
    return RedirectResponse(url="/static/index.html")

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Handles outfit inspiration image upload.
    Validates with Pillow, resizes, and stores in uploads/.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image (JPEG, PNG, WEBP).")

    upload_id = uuid.uuid4().hex[:10]
    ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
    filename = f"upload_{upload_id}{ext}"
    filepath = os.path.join(UPLOADS_DIR, filename)

    try:
        contents = await file.read()
        pil_img = validate_and_open_image(contents)
        pil_img = resize_image_for_ai(pil_img, max_dim=1200)
        pil_img.save(filepath, "JPEG", quality=92)
        
        width, height = pil_img.size
        
        return {
            "success": True,
            "upload_id": upload_id,
            "filename": filename,
            "image_url": f"/uploads/{filename}",
            "dimensions": {"width": width, "height": height}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload processing failed: {str(e)}")

class AnalyzeRequest(BaseModel):
    upload_id: Optional[str] = None
    image_url: Optional[str] = None
    image_path: Optional[str] = None

@app.post("/analyze")
def analyze_image(req: AnalyzeRequest):
    """
    Analyzes the uploaded outfit inspiration image.
    Uses OpenCV to preprocess and Ultralytics YOLO to detect clothing and accessories.
    Returns detected categories with bounding boxes and interactive hotspot percentages.
    """
    image_path = None
    if req.image_path and os.path.exists(req.image_path):
        image_path = req.image_path
    elif req.upload_id:
        if req.upload_id in ["demo", "demo_sample", "demo_atelier_look"]:
            candidate = os.path.join(UPLOADS_DIR, "demo_sample.jpg")
            if os.path.exists(candidate):
                image_path = candidate
        else:
            for fname in os.listdir(UPLOADS_DIR):
                if fname.startswith(f"upload_{req.upload_id}"):
                    image_path = os.path.join(UPLOADS_DIR, fname)
                    break
                
    if not image_path and req.image_url:
        # Check if local upload path or test images path
        if req.image_url.startswith("/uploads/"):
            local_rel = req.image_url.replace("/uploads/", "")
            potential_path = os.path.join(UPLOADS_DIR, local_rel)
            if os.path.exists(potential_path):
                image_path = potential_path
        elif req.image_url.startswith("/tests/"):
            test_rel = req.image_url.replace("/tests/test_images/", "").replace("/tests/", "")
            for t_dir in [
                os.path.join(os.path.dirname(BASE_DIR), "tests", "test_images"),
                os.path.join(BASE_DIR, "tests", "test_images"),
                os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "tests", "test_images")
            ]:
                candidate = os.path.join(t_dir, test_rel)
                if os.path.exists(candidate):
                    image_path = candidate
                    break
        elif os.path.exists(req.image_url):
            image_path = req.image_url

    # Fallback to prototype sample image if no specific file found
    if not image_path or not os.path.exists(image_path):
        # Create a sample placeholder if needed
        image_path = os.path.join(UPLOADS_DIR, "demo_sample.jpg")
        if not os.path.exists(image_path):
            from PIL import Image
            sample = Image.new("RGB", (600, 800), color=(240, 235, 230))
            sample.save(image_path)

    try:
        pil_img = validate_and_open_image(image_path)
        # Preprocess with OpenCV
        cv2_enhanced, pil_enhanced = preprocess_for_detection(pil_img)
        
        # Ensemble YOLO detection
        upload_id = req.upload_id or (os.path.splitext(os.path.basename(image_path))[0] if image_path else "demo")
        detected_items = detect_fashion_items(pil_enhanced, upload_id, CROPS_DIR)
        
        is_fallback = all(it.get("is_fallback", False) for it in detected_items)
        if is_fallback:
            detection_source = "demo_fallback"
            model_used = "prototype_reference"
        else:
            sources = set(it.get("detection_source") for it in detected_items)
            if "deepfashion2_yolo" in sources and "coco_yolo" in sources:
                detection_source = "ensemble_deepfashion2_coco"
                model_used = "yolov8s-seg-deepfashion2 + yolov8n"
            elif "deepfashion2_yolo" in sources:
                detection_source = "deepfashion2_yolo"
                model_used = "yolov8s-seg-deepfashion2"
            else:
                detection_source = "coco_yolo"
                model_used = "yolov8n"

        avg_conf = sum(it.get("confidence", 0.9) for it in detected_items) / max(len(detected_items), 1)
        ai_confidence = f"{int(round(avg_conf * 100))}%"
        
        return {
            "success": True,
            "upload_id": upload_id,
            "item_count": len(detected_items),
            "ai_confidence": ai_confidence,
            "detection_source": detection_source,
            "is_fallback": is_fallback,
            "model_used": model_used,
            "detected_items": detected_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

class SearchProductsRequest(BaseModel):
    detected_items: Optional[List[Dict[str, Any]]] = None
    category: Optional[str] = None
    budget_tier: Optional[str] = None
    brand: Optional[str] = None
    sort_by: Optional[str] = "match"

@app.post("/search-products")
def search_similar_products(req: SearchProductsRequest):
    """
    Performs visual similarity search with FAISS.
    Generates Transformers CLIP embeddings for detected fashion items and returns
    curated matching products grouped by category with match score percentages.
    """
    items_to_search = req.detected_items or []
    
    # If no detected items passed, search across key categories
    if not items_to_search:
        items_to_search = [
            {"item_id": "det_top_01", "category": "top", "label": "White Oversized Shirt"},
            {"item_id": "det_bottom_02", "category": "bottom", "label": "Light Wash Straight Jeans"},
            {"item_id": "det_bag_03", "category": "bag", "label": "Structured Beige Tote"},
            {"item_id": "det_shoes_04", "category": "shoes", "label": "Classic Leather Loafers"}
        ]

    ensure_catalog_indexed()
    category_results = {}
    results_by_item = []
    wishlist_ids = {p["product_id"] for p in get_wishlist_products()}
    from PIL import Image

    for idx, item in enumerate(items_to_search):
        # 1. Map each detected item to an appropriate catalog category BEFORE FAISS ranking
        mapped_cat = map_detected_item_to_catalog_category(item)
        item_label = item.get("label") or mapped_cat.title()
        item_id = item.get("item_id") or f"det_{mapped_cat}_{idx+1}"
        
        # 2. Use cropped detected-item image for CLIP embedding
        crop_path = item.get("crop_path")
        if not crop_path or not os.path.exists(crop_path):
            crop_url = item.get("crop_url", "")
            if crop_url.startswith("/uploads/crops/"):
                c_fname = crop_url.replace("/uploads/crops/", "")
                candidate = os.path.join(CROPS_DIR, c_fname)
                if os.path.exists(candidate):
                    crop_path = candidate
            elif crop_url.startswith("/uploads/"):
                c_fname = crop_url.replace("/uploads/", "")
                candidate = os.path.join(UPLOADS_DIR, c_fname)
                if os.path.exists(candidate):
                    crop_path = candidate
            elif crop_url.startswith("/static/"):
                rel_path = crop_url.replace("/static/", "")
                candidate = os.path.join(FRONTEND_DIR, rel_path)
                if os.path.exists(candidate):
                    crop_path = candidate

        query_img = None
        if crop_path and os.path.exists(crop_path):
            try:
                query_img = Image.open(crop_path)
            except Exception:
                query_img = None

        if query_img is None:
            query_img = Image.new("RGB", (64, 64), color=(245, 240, 235))

        q_vec = generate_image_embedding(query_img, category_hint=f"{mapped_cat}_{item_label}")
        
        # 3. FAISS category-filtered search: strictly rank within mapped catalog category
        # Return top 4 visually similar products (within requested 3-5 range)
        raw_matches = fashion_index.search(q_vec, category_filter=mapped_cat, top_k=4)
        
        matched_products = []
        for m in raw_matches:
            prod_info = get_product_by_id(m["product_id"])
            if prod_info:
                p_copy = dict(prod_info)
                p_copy["similarity_score"] = m.get("similarity_score")
                p_copy["match_pct"] = m["match_pct"]
                p_copy["match_number"] = m["match_number"]
                p_copy["search_source"] = m.get("search_source", "real_faiss")
                p_copy["formatted_price"] = f"₹{p_copy['price']:,}"
                p_copy["is_wishlisted"] = p_copy["product_id"] in wishlist_ids
                p_copy["image_url"] = f"/static/assets/products/{p_copy['product_id']}.jpg"
                p_copy["product_url"] = prod_info.get("product_url") or DEMO_PRODUCT_URLS.get(p_copy["product_id"], "#")
                matched_products.append(p_copy)
                
        if matched_products:
            item_entry = {
                "item_id": item_id,
                "detected_item": item_label,
                "category_label": item_label,
                "category": mapped_cat,
                "confidence": item.get("confidence", 0.9),
                "crop_url": item.get("crop_url", ""),
                "products": matched_products
            }
            # Key by unique item_id so multiple items in the same category never overwrite each other
            category_results[item_id] = item_entry
            results_by_item.append(item_entry)

    status = fashion_index.get_index_status()
    return {
        "success": True,
        "results_by_item": results_by_item,
        "results_by_category": category_results,
        "search_metadata": {
            "indexed_products_count": status["indexed_products_count"],
            "is_real_faiss": status["is_real_faiss"],
            "search_source": status["search_source"],
            "dimension": status["dimension"],
            "similarity_metric": status["similarity_metric"]
        }
    }

@app.get("/products")
def list_products(
    category: Optional[str] = Query(None),
    budget: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    sort: Optional[str] = Query("match"),
    q: Optional[str] = Query(None)
):
    """Returns catalog products with optional filtering and sorting via Pandas."""
    products = filter_products(
        category=category,
        budget_tier=budget,
        brand=brand,
        sort_by=sort,
        search_query=q
    )
    for p in products:
        p["image_url"] = f"/static/assets/products/{p['product_id']}.jpg"
        p["product_url"] = DEMO_PRODUCT_URLS.get(p["product_id"], p.get("product_url", "#"))
    return {
        "count": len(products),
        "products": products
    }

@app.get("/products/{product_id}")
def get_product(product_id: str):
    """Returns single product details by ID."""
    prod = get_product_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    prod["formatted_price"] = f"₹{prod['price']:,}"
    prod["image_url"] = f"/static/assets/products/{prod['product_id']}.jpg"
    prod["product_url"] = DEMO_PRODUCT_URLS.get(prod["product_id"], prod.get("product_url", "#"))
    return prod

class WishlistAction(BaseModel):
    product_id: str

@app.post("/wishlist")
def add_wishlist_item(action: WishlistAction):
    """Adds a product to user's wishlist."""
    add_to_wishlist(action.product_id)
    return {"success": True, "message": "Product added to wishlist", "product_id": action.product_id}

@app.get("/wishlist")
def get_wishlist():
    """Retrieves all saved wishlist products."""
    items = get_wishlist_products()
    return {
        "count": len(items),
        "products": items
    }

@app.delete("/wishlist/{product_id}")
def remove_wishlist_item(product_id: str):
    """Removes a product from user's wishlist."""
    remove_from_wishlist(product_id)
    return {"success": True, "message": "Product removed from wishlist", "product_id": product_id}

class SaveLookRequest(BaseModel):
    title: Optional[str] = "My Curated Look"
    inspiration_image: str
    items: List[Dict[str, Any]]
    total_price: int

@app.post("/saved-looks")
def save_look_endpoint(req: SaveLookRequest):
    """Saves a recreated outfit look."""
    look = {
        "look_id": f"look_{uuid.uuid4().hex[:8]}",
        "title": req.title,
        "inspiration_image": req.inspiration_image,
        "items": req.items,
        "total_price": req.total_price,
        "total_price_formatted": f"₹{req.total_price:,}",
        "created_at": "Just now"
    }
    saved = save_new_look(look)
    return {"success": True, "look": saved}

@app.get("/saved-looks")
def get_saved_looks_endpoint():
    """Returns all saved complete looks."""
    looks = get_saved_looks()
    return {
        "count": len(looks),
        "looks": looks
    }
