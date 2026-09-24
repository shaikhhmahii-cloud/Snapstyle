# SnapStyle - AI Fashion Discovery Application

> **Tagline**: *"Snap your inspiration. Find your style."*

SnapStyle is an AI-powered visual fashion discovery and outfit recreation application designed with the **Google Stitch "Digital Atelier"** aesthetic. SnapStyle allows users to upload outfit inspiration imagery (from Pinterest, Instagram, street style, or camera), detects individual fashion pieces and accessories using deep learning, generates visual embeddings, and retrieves matching products using vector similarity search to recreate complete looks.

---

## 🌟 Key Features

1. **Google Stitch High-Fidelity UI/UX**:
   - Dark mode editorial luxury palette (`#171119` background, `#e8b3ff` amethyst primary, `#ffb0d0` rose tertiary).
   - High-contrast typography pairing: **Playfair Display** for serif headlines and **Hanken Grotesk** for clean technical labels.
   - Interactive clothing **hotspots** that pulse on inspiration images and map directly to detected piece cards.
   - Signature **focus brackets** and animated **AI laser scanline** visual cues.
   - 10 comprehensive screens: *Splash/Welcome, Home, Find My Look (Upload), AI Analysis, Detected Items, Product Results, Filter Modal, Recreate This Look, Wishlist (Products & Outfits), and User Profile*.

2. **The 7 Required Python Backend Libraries**:
   - **Pillow (PIL)**: Image loading, format conversion (RGBA to RGB), Lanczos aspect-ratio resizing, and bounding-box cropping.
   - **OpenCV (cv2)**: Bilateral noise reduction, contrast sharpening, color conversions, and focus bracket overlays.
   - **Ultralytics YOLO**: Garment and accessory object detection (`top`, `bottom`, `shoes`, `bag`, `accessories`) and hotspot percentage coordinate mapping.
   - **Transformers**: Hugging Face vision model (CLIP) generating 512-dimensional normalized visual feature vectors.
   - **FAISS (faiss-cpu)**: Sub-millisecond exact cosine similarity search (`IndexFlatIP`) over normalized catalog embeddings.
   - **Pandas**: Fashion catalog management, budget tier filtering in Indian Rupees (INR ₹), category filtering, and sorting.
   - **FastAPI**: REST API connecting the AI pipeline to the frontend with CORS, image uploads, and static asset serving.

3. **Curated Look Recreation with Dynamic Price Totaling**:
   - Recreate complete outfits with itemized size selectors and swap controls.
   - Live estimated total price calculation in Indian Rupees (**₹**).
   - Direct retailer integration links and persistent Wishlist / Profile storage.

---

## 🏗️ System Architecture

```
SnapStyle/
│
├── frontend/
│   ├── index.html              # Full-stack UI with all 10 Google Stitch screens
│   ├── css/
│   │   └── style.css           # Focus brackets, scanlines, hotspot rings, transitions
│   ├── js/
│   │   ├── api.js              # FastAPI client communication module
│   │   ├── state.js            # Centralized reactive application store
│   │   └── app.js              # View transitions, modal controls, and user interactions
│   └── assets/                 # Icons and reference imagery
│
├── backend/
│   ├── main.py                 # FastAPI application, CORS, static uploads, routes
│   ├── image_processing.py     # Pillow & OpenCV image preprocessing, cropping, brackets
│   ├── detection.py            # Ultralytics YOLO clothing & accessories detection
│   ├── embeddings.py           # Transformers CLIP 512-dim visual embeddings
│   ├── similarity_search.py    # FAISS vector similarity index manager
│   ├── products.py             # Pandas dataset filtering, wishlist & saved looks
│   ├── test_pipeline.py        # Automated test suite for all 7 libraries
│   ├── requirements.txt        # Python dependency manifest
│   └── uploads/                # Directory for uploaded inspiration photos & crops
│
├── data/
│   └── products.csv            # Fashion catalog (Tops, Bottoms, Shoes, Bags, Accessories)
│
└── README.md                   # Project documentation and guide
```

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.10+** (tested on Python 3.12)
- **Node.js** (optional, for custom static server; Python `http.server` or FastAPI static mounting can also be used)

### 1. Clone & Set Up Python Virtual Environment
```bash
cd Snapstyle
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

---

## 💻 Running the Application

### Option A: Unified FastAPI Full-Stack Server (Recommended)
The FastAPI server serves both the backend REST API and the complete frontend UI:
```bash
venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Now open your web browser at:
**[http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)**

### Option B: Running Frontend Separately
If you want to run the frontend independently:
```bash
# In another terminal:
cd frontend
python -m http.server 3000
```
Open **[http://localhost:3000](http://localhost:3000)** (the frontend automatically points to `http://localhost:8000`).

---

## 🧪 Testing the AI Pipeline

SnapStyle includes an automated test suite verifying all 7 Python libraries:
```bash
venv\Scripts\python.exe backend/test_pipeline.py
```
This script tests:
1. Pillow format verification, Lanczos resizing, bounding-box cropping
2. OpenCV bilateral filtering, unsharp masking, and focus bracket rendering
3. Ultralytics YOLO clothing item detection & hotspot percentage computation
4. Transformers CLIP visual feature embedding generation (512-dim unit vector)
5. FAISS IndexFlatIP vector indexing & cosine nearest neighbor retrieval
6. Pandas product filtering by category, brand, and INR budget tiers
7. FastAPI REST endpoints (`/`, `/products`, `/analyze`, `/search-products`, `/wishlist`)

---

## 🧠 How the AI Pipeline Works

```
USER UPLOADS AN INSPIRATION PHOTO
               ↓
1. IMAGE VALIDATION & PREPROCESSING (Pillow + OpenCV)
   - Exif transpose & RGB conversion via Pillow
   - Resized to Lanczos resolution
   - Bilateral edge filtering & sharpening via OpenCV
               ↓
2. FASHION OBJECT DETECTION (Ultralytics YOLO)
   - Identifies tops, bottoms, bags, shoes, accessories
   - Computes normalized bounding boxes [ymin, xmin, ymax, xmax]
   - Calculates relative percentage coordinates (top%, left%) for interactive UI hotspots
   - Crops detected fashion components
               ↓
3. VISUAL EMBEDDINGS (Transformers CLIP)
   - Detected component crops are passed to CLIP vision model
   - 512-dimensional visual feature vectors are generated
   - Normalized to unit length (L2 norm = 1.0)
               ↓
4. SIMILARITY SEARCH (FAISS)
   - IndexFlatIP performs exact cosine similarity search over product catalog
   - Retrieves Top-K candidates with percentage match scores (e.g. 94% Match)
               ↓
5. PRODUCT CATALOG MANAGEMENT (Pandas)
   - Loads and filters catalog by category, price range in INR, and brand
               ↓
6. API EXPOSURE (FastAPI)
   - Connects frontend to AI engine with asynchronous endpoints
```

---

## 📦 Product Dataset (`data/products.csv`)

The dataset is stored in `data/products.csv` with fields:
- `product_id`: Unique identifier (e.g. `prod_001`)
- `product_name`: Title of the garment (e.g. `Crisp White Blouse`)
- `category`: `top`, `bottom`, `shoes`, `bag`, `accessories`, `jacket`, `dress`
- `brand`: Retailer brand (Zara, H&M, Levi's, Mango, Nike, Aurate, Charles & Keith)
- `price`: Integer price in Indian Rupees (INR ₹)
- `image_url`: High-resolution product image
- `product_url`: Direct shopping URL
- `description`: Fabric, styling, and tailoring description
- `rating`: Customer review score (e.g. 4.8)

### How to Replace Demo Data with Real Product APIs
To integrate a live retailer API (such as Google Shopping API, Shopify, or Myntra Affiliate API):
1. In `backend/products.py`, modify `get_products_df()` or implement a `fetch_live_products(query)` function.
2. In `backend/main.py`, replace or augment `search_similar_products()` to call your live shopping API with the detected item labels and category hints.
3. The rest of the frontend and AI detection pipeline remains identical because the API contract (`product_id`, `product_name`, `image_url`, `product_url`, `formatted_price`) is decoupled.

---

## 🎨 Translation of Google Stitch Prototype into SnapStyle

The Google Stitch prototype served as the primary design benchmark. We translated every design token and user journey:
- **Editorial Typography**: Combined Google Fonts *Playfair Display* for large editorial headlines with *Hanken Grotesk* for technical body text and tracked uppercase labels.
- **Color Identity**: Built using Tailwind with `#171119` (ink-dark background), `#e8b3ff` (amethyst primary), `#ffb0d0` (magenta-berry tertiary), and `#241d26` (surface container).
- **Interactive Hotspots**: Recreated the Stitch prototype's pulsating dots on the inspiration image (`snapstyle_detected_items`), highlighting the corresponding garment card on hover and click.
- **Focus Brackets**: Thin amethyst corner brackets on images to reinforce the AI atelier scanning aesthetic.
- **Complete Look Recreation**: Preserved the exact itemized breakdown and live total price calculation (`₹4,094`) from the `snapstyle_recreate_this_look` prototype screen.
