import { api } from "./api.js?v=5.0";
import { state, DEMO_IMAGE_URL } from "./state.js?v=5.0";

// Comprehensive catalog map of individual demo product URLs (each product has its own unique destination)
export const DEMO_PRODUCT_URLS = {
  prod_001: "https://www.zara.com/in/en/crisp-white-blouse-p08432001.html",
  prod_002: "https://www.myntra.com/shirts/hm/hm-men-white-cotton-poplin-relaxed-fit-casual-shirt/21456789/buy",
  prod_003: "https://www.myntra.com/tops/snapstyle/women-white-structured-sweetheart-crop-top/19842003/buy",
  prod_004: "https://www.zara.com/in/en/oversized-poplin-shirt-p08432004.html",
  prod_005: "https://www.massimodutti.com/in/white-oversized-shirt-l05123005",
  prod_006: "https://www.myntra.com/jeans/mango/mango-women-light-wash-high-rise-straight-fit-jeans/18923006/buy",
  prod_007: "https://www.myntra.com/jeans/levis/levis-vintage-clothing-women-classic-straight-fit-jeans/17584007/buy",
  prod_008: "https://www.myntra.com/jeans/levis/levis-women-501-original-straight-fit-jeans/17584102/buy",
  prod_009: "https://www.myntra.com/jeans/hm/hm-women-wide-high-waisted-denim-jeans/21456009/buy",
  prod_010: "https://www.myntra.com/handbags/charles--keith/charles--keith-structured-beige-tote-bag/23456010/buy",
  prod_011: "https://www.zara.com/in/en/minimalist-leather-handbag-p06232011.html",
  prod_012: "https://www.myntra.com/jewellery/aurate/aurate-women-14k-gold-vermeil-pendant-necklace--hoops-set/18456012/buy",
  prod_013: "https://www.massimodutti.com/in/classic-leather-loafers-l0123013",
  prod_014: "https://www.myntra.com/casual-shoes/nike/nike-court-royale-2-minimalist-white-leather-sneakers/19456014/buy",
  prod_015: "https://www.myntra.com/jackets/mango/mango-women-structured-double-breasted-trench-coat/18923456/buy",
  prod_016: "https://www.myntra.com/sunglasses/ray-ban/ray-ban-unisex-tortoise-square-sunglasses/15678901/buy",
  prod_017: "https://www.zara.com/in/en/linen-tailored-trousers-p07332017.html",
  prod_018: "https://www.myntra.com/handbags/charles--keith/charles--keith-leather-crossbody-mini-bag/23456018/buy",
  prod_019: "https://www.myntra.com/jewellery/hm/hm-women-chunky-brushed-gold-plated-chain-necklace/21456019/buy",
  prod_020: "https://www.zara.com/in/en/suede-pointed-ballet-flats-p02132020.html",
  prod_021: "https://www.myntra.com/tops/mango/mango-women-ribbed-knit-sleeveless-high-neck-top/18923021/buy",
  prod_022: "https://www.zara.com/in/en/pleated-slip-maxi-skirt-p04232022.html",
  prod_023: "https://www.myntra.com/heels/charles--keith/charles--keith-women-strappy-minimal-heeled-sandals/23456023/buy",
  prod_024: "https://www.myntra.com/handbags/hm/hm-women-artisanal-woven-straw-market-tote-bag/21456024/buy",
  prod_025: "https://www.zara.com/in/en/striped-relaxed-poplin-shirt-p08432025.html",
  prod_026: "https://www.massimodutti.com/in/linen-mandarin-collar-shirt-l05123026",
  prod_027: "https://www.myntra.com/tops/mango/mango-women-black-ribbed-mock-neck-top/21456027/buy",
  prod_028: "https://www.myntra.com/tshirts/hm/hm-men-classic-crew-neck-organic-cotton-tshirt/21456028/buy",
  prod_029: "https://www.myntra.com/shirts/marks--spencer/m-and-s-women-silk-satin-tie-neck-formal-blouse/21456029/buy",
  prod_030: "https://www.myntra.com/shirts/levis/levis-men-classic-chambray-denim-button-down-shirt/21456030/buy",
  prod_031: "https://www.zara.com/in/en/knitted-cable-polo-sweater-p08432031.html",
  prod_032: "https://www.myntra.com/tops/only/only-women-square-neck-structured-corset-camisole/21456032/buy",
  prod_033: "https://www.massimodutti.com/in/merino-wool-turtleneck-sweater-l05123033",
  prod_034: "https://www.myntra.com/tops/hm/hm-women-boxy-cropped-linen-blend-short-sleeve-blouse/21456034/buy",
  prod_035: "https://www.myntra.com/tshirts/roadster/roadster-unisex-vintage-wash-oversized-graphic-tee/21456035/buy",
  prod_036: "https://www.myntra.com/sweaters/mango/mango-women-pointelle-knit-scallop-trim-cardigan/21456036/buy",
  prod_037: "https://www.myntra.com/shirts/marks--spencer/m-and-s-men-pure-cotton-tailored-oxford-shirt/21456037/buy",
  prod_038: "https://www.myntra.com/tops/vero-moda/vero-moda-women-lace-trim-satin-v-neck-camisole/21456038/buy",
  prod_039: "https://www.zara.com/in/en/cotton-crochet-halter-top-p08432039.html",
  prod_040: "https://www.myntra.com/tops/fabindia/fabindia-women-handblock-printed-khadi-cotton-short-kurta/21456040/buy",
  prod_041: "https://www.zara.com/in/en/high-rise-wide-leg-trousers-p08432041.html",
  prod_042: "https://www.myntra.com/jeans/levis/levis-women-mile-high-super-skinny-fit-jeans/21456042/buy",
  prod_043: "https://www.massimodutti.com/in/tailored-linen-bermuda-shorts-l05123043",
  prod_044: "https://www.myntra.com/skirts/mango/mango-women-a-line-denim-maxi-skirt-with-slit/21456044/buy",
  prod_045: "https://www.myntra.com/trousers/marks--spencer/m-and-s-men-regular-fit-stretch-chino-trousers/21456045/buy",
  prod_046: "https://www.myntra.com/skirts/hm/hm-women-pleated-a-line-tennis-mini-skirt/21456046/buy",
  prod_047: "https://www.myntra.com/trousers/roadster/roadster-unisex-high-waist-cotton-cargo-jogger-pants/21456047/buy",
  prod_048: "https://www.zara.com/in/en/cropped-cigarette-trousers-p08432048.html",
  prod_049: "https://www.myntra.com/jeans/levis/levis-women-ribcage-bootcut-vintage-flared-jeans/21456049/buy",
  prod_050: "https://www.myntra.com/skirts/mango/mango-women-bias-cut-flowy-satin-midi-skirt/21456050/buy",
  prod_051: "https://www.myntra.com/trousers/fabindia/fabindia-unisex-pure-linen-drawstring-wide-leg-pants/21456051/buy",
  prod_052: "https://www.myntra.com/shorts/only/only-women-high-rise-distressed-denim-cut-off-shorts/21456052/buy",
  prod_053: "https://www.myntra.com/trousers/vero-moda/vero-moda-women-paperbag-waist-belted-chinos/21456053/buy",
  prod_054: "https://www.massimodutti.com/in/houndstooth-wool-blend-culottes-l05123054",
  prod_055: "https://www.myntra.com/trousers/hm/hm-men-straight-leg-ribbed-cotton-corduroy-pants/21456055/buy",
  prod_056: "https://www.myntra.com/skirts/fabindia/fabindia-women-tiered-cotton-boho-flared-maxi-skirt/21456056/buy",
  prod_057: "https://www.zara.com/in/en/oversized-wool-blend-blazer-p08432057.html",
  prod_058: "https://www.massimodutti.com/in/leather-biker-motorcycle-jacket-l05123058",
  prod_059: "https://www.myntra.com/jackets/levis/levis-unisex-original-vintage-trucker-denim-jacket/21456059/buy",
  prod_060: "https://www.myntra.com/jackets/mango/mango-women-cropped-quilted-puffer-jacket/21456060/buy",
  prod_061: "https://www.myntra.com/blazers/marks--spencer/m-and-s-men-pure-linen-tailored-summer-blazer/21456061/buy",
  prod_062: "https://www.zara.com/in/en/textured-boucle-tweed-jacket-p08432062.html",
  prod_063: "https://www.massimodutti.com/in/belted-longline-wool-wrap-coat-l05123063",
  prod_064: "https://www.myntra.com/jackets/puma/puma-unisex-classic-satin-varsity-bomber-jacket/21456064/buy",
  prod_065: "https://www.myntra.com/jackets/hm/hm-men-cotton-canvas-oversized-utility-shacket/21456065/buy",
  prod_066: "https://www.myntra.com/jackets/only/only-women-faux-shearling-lined-aviator-jacket/21456066/buy",
  prod_067: "https://www.myntra.com/jackets/vero-moda/vero-moda-women-suede-finish-western-fringe-jacket/21456067/buy",
  prod_068: "https://www.myntra.com/jackets/marks--spencer/m-and-s-women-stormwear-water-resistant-hooded-parka/21456068/buy",
  prod_069: "https://www.myntra.com/jackets/roadster/roadster-women-acid-wash-denim-shacket/21456069/buy",
  prod_070: "https://www.zara.com/in/en/canvas-leather-shopper-tote-p08432070.html",
  prod_071: "https://www.myntra.com/handbags/charles--keith/charles--keith-crescent-moon-leather-baguette-bag/21456071/buy",
  prod_072: "https://www.massimodutti.com/in/saddle-leather-crossbody-flap-bag-l05123072",
  prod_073: "https://www.myntra.com/handbags/hm/hm-women-puffer-quilted-nylon-shoulder-cloud-bag/21456073/buy",
  prod_074: "https://www.myntra.com/handbags/aldo/aldo-women-structured-box-top-handle-handbag/21456074/buy",
  prod_075: "https://www.myntra.com/handbags/mango/mango-women-woven-leather-drawstring-bucket-bag/21456075/buy",
  prod_076: "https://www.myntra.com/backpacks/fossil/fossil-unisex-classic-leather-city-commuter-backpack/21456076/buy",
  prod_077: "https://www.zara.com/in/en/raffia-envelope-clutch-p08432077.html",
  prod_078: "https://www.myntra.com/handbags/nike/nike-sportswear-utility-multi-pocket-crossbody-bag/21456078/buy",
  prod_079: "https://www.myntra.com/handbags/fabindia/fabindia-women-hand-embroidered-jute-market-tote/21456079/buy",
  prod_080: "https://www.myntra.com/handbags/charles--keith/charles--keith-metallic-pleated-evening-clutch/21456080/buy",
  prod_081: "https://www.myntra.com/handbags/hm/hm-unisex-convertible-nylon-belt-fanny-pack-bag/21456081/buy",
  prod_082: "https://www.massimodutti.com/in/slouchy-leather-hobo-shoulder-bag-l05123082",
  prod_083: "https://www.myntra.com/handbags/mango/mango-women-miniature-leather-coin-pouch-crossbody/21456083/buy",
  prod_084: "https://www.zara.com/in/en/chunky-lug-sole-leather-loafers-p08432084.html",
  prod_085: "https://www.myntra.com/casual-shoes/nike/nike-air-force-1-07-classic-all-white-leather-sneakers/21456085/buy",
  prod_086: "https://www.myntra.com/heels/charles--keith/charles--keith-women-ankle-strap-block-heel-sandals/21456086/buy",
  prod_087: "https://www.massimodutti.com/in/leather-chelsea-ankle-boots-l05123087",
  prod_088: "https://www.myntra.com/flats/mango/mango-women-suede-ballet-flats-with-dainty-bow/21456088/buy",
  prod_089: "https://www.myntra.com/casual-shoes/puma/puma-unisex-retro-suede-classic-court-sneakers/21456089/buy",
  prod_090: "https://www.myntra.com/heels/aldo/aldo-women-pointed-toe-leather-slip-on-mule-heels/21456090/buy",
  prod_091: "https://www.myntra.com/heels/hm/hm-women-traditional-braided-jute-espadrille-wedges/21456091/buy",
  prod_092: "https://www.zara.com/in/en/lace-up-combat-ankle-boots-p08432092.html",
  prod_093: "https://www.massimodutti.com/in/minimalist-leather-flat-slides-l05123093",
  prod_094: "https://www.myntra.com/heels/charles--keith/charles--keith-embellished-metallic-stiletto-pumps/21456094/buy",
  prod_095: "https://www.myntra.com/flats/fabindia/fabindia-women-handcrafted-embroidered-leather-juttis/21456095/buy",
  prod_096: "https://www.myntra.com/casual-shoes/roadster/roadster-men-canvas-low-top-casual-skater-shoes/21456096/buy",
  prod_097: "https://www.myntra.com/sunglasses/mango/mango-women-retro-cat-eye-acetate-sunglasses/21456097/buy",
  prod_098: "https://www.myntra.com/sunglasses/ray-ban/ray-ban-unisex-round-metal-frame-green-lens-sunglasses/21456098/buy",
  prod_099: "https://www.myntra.com/jewellery/aurate/aurate-women-14k-gold-vermeil-chunky-tubular-hoop-earrings/21456099/buy",
  prod_100: "https://www.massimodutti.com/in/reversible-italian-leather-belt-l05123100",
  prod_101: "https://www.zara.com/in/en/printed-mulberry-silk-square-scarf-p08432101.html",
  prod_102: "https://www.myntra.com/watches/fossil/fossil-unisex-minimalist-slim-case-mesh-bracelet-watch/21456102/buy",
  prod_103: "https://www.zara.com/in/en/satin-bias-cut-slip-midi-dress-p08432103.html",
  prod_104: "https://www.massimodutti.com/in/belted-linen-button-down-shirt-dress-l05123104",
  prod_105: "https://www.myntra.com/dresses/mango/mango-women-ribbed-knit-sleeveless-bodycon-maxi-dress/21456105/buy",
};

/**
 * Resolves the exact verified individual product URL from the Pandas catalog.
 * Opens the specific retailer item page in a new browser tab.
 */
export function resolveProductUrl(prod) {
  if (!prod) return "#";
  const explicitUrl = prod.product_url || "";
  if (explicitUrl && (explicitUrl.startsWith("http://") || explicitUrl.startsWith("https://"))) {
    return explicitUrl;
  }
  if (prod.product_id && DEMO_PRODUCT_URLS[prod.product_id]) {
    return DEMO_PRODUCT_URLS[prod.product_id];
  }
  return "#";
}

/**
 * Resolves the product image URL.
 * Automatically serves verified local static images or remote URLs.
 */
export function resolveProductImage(prod) {
  if (!prod) return getFallbackProductImage();
  if (prod.product_id) {
    return `/static/assets/products/${prod.product_id}.jpg`;
  }
  if (prod.image_url) {
    if (prod.image_url.startsWith("http://") || prod.image_url.startsWith("https://") || prod.image_url.startsWith("/")) {
      return prod.image_url;
    }
    return `/static/${prod.image_url}`;
  }
  return getFallbackProductImage(prod.product_name, prod.brand, prod.category);
}

/**
 * Generates an editorial Google Stitch styled fallback SVG data URI.
 */
export function getFallbackProductImage(name = "Fashion Piece", brand = "SnapStyle", category = "") {
  const safeName = (name || "Fashion Piece").replace(/["'<>&]/g, "");
  const safeBrand = (brand || "SnapStyle").replace(/["'<>&]/g, "");
  const safeCat = (category || "").toUpperCase().replace(/["'<>&]/g, "");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="530" viewBox="0 0 400 530" fill="none">
    <rect width="400" height="530" fill="#1f1922"/>
    <rect x="20" y="20" width="360" height="490" rx="16" fill="#241d26" stroke="#39323b" stroke-width="1.5"/>
    <circle cx="200" cy="210" r="48" fill="#2e2830" stroke="#e8b3ff" stroke-width="1.5" stroke-dasharray="4 4"/>
    <path d="M185 210C185 201.716 191.716 195 200 195C208.284 195 215 201.716 215 210C215 218.284 208.284 225 200 225C191.716 225 185 218.284 185 210Z" stroke="#e8b3ff" stroke-width="2"/>
    <path d="M175 235C175 225 186 222 200 222C214 222 225 225 225 235" stroke="#e8b3ff" stroke-width="2" stroke-linecap="round"/>
    <text x="200" y="310" font-family="'Playfair Display', serif" font-size="18" fill="#e8b3ff" text-anchor="middle" font-weight="600">${safeName}</text>
    <text x="200" y="338" font-family="'Hanken Grotesk', sans-serif" font-size="12" fill="#d1c2d3" text-anchor="middle" letter-spacing="2">${safeBrand} &bull; ${safeCat}</text>
    <text x="200" y="370" font-family="'Hanken Grotesk', sans-serif" font-size="10" fill="#7316a0" text-anchor="middle" letter-spacing="1">SNAPSTYLE CURATED</text>
  </svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}
window.getFallbackProductImage = getFallbackProductImage;

/**
 * Resolves the inspiration image URL so it renders reliably across all views.
 */
export function resolveInspirationImageUrl(url) {
  if (!url) return "/uploads/demo_sample.jpg";
  if (url.startsWith("blob:") || url.startsWith("data:") || url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  if (url.startsWith("/")) {
    const base = api.getBaseUrl ? api.getBaseUrl() : "";
    return `${base}${url}`;
  }
  return url;
}

/**
 * Synchronizes the uploaded inspiration image across all 5 prototype screens.
 */
export function updateAllInspirationImages() {
  const currentImg = resolveInspirationImageUrl(state.uploadedImage);
  const elements = [
    document.getElementById("upload-preview-img"),
    document.getElementById("analysis-preview-img"),
    document.getElementById("detected-inspiration-img"),
    document.getElementById("results-inspiration-thumb"),
    document.getElementById("recreate-inspiration-img")
  ];
  elements.forEach(el => {
    if (el) {
      el.src = currentImg;
      el.onerror = function() {
        this.onerror = null;
        this.src = "/uploads/demo_sample.jpg";
      };
    }
  });
}

const VIEW_IDS = ["welcome", "home", "upload", "analysis", "detected", "results", "recreate", "wishlist", "profile"];

function initApp() {
  // Expose global navigation helpers for robust mobile and inline event handling
  window.snapstyleSetView = function(viewName) {
    state.setView(viewName);
  };
  window.snapstyleUseDemo = function() {
    useDemoOutfit();
  };
  window.state = state;

  setupNavigation();
  setupWelcomeView();
  setupHomeView();
  setupUploadView();
  setupAnalysisView();
  setupDetectedView();
  setupResultsView();
  setupFilterModal();
  setupRecreateView();
  setupWishlistView();
  setupProfileView();

  state.subscribe((event) => {
    if (event === "view_changed") {
      renderCurrentView();
      updateNavIndicators();
    } else if (event === "image_updated") {
      updateAllInspirationImages();
    } else if (event === "detected_items_updated") {
      renderDetectedView();
    } else if (event === "hotspot_changed") {
      updateHotspotHighlight();
    } else if (event === "look_updated") {
      renderRecreateView();
    } else if (event === "results_updated") {
      renderResultsView();
    }
  });

  renderCurrentView();
  loadInitialData();
}

function renderCurrentView() {
  VIEW_IDS.forEach(vKey => {
    const el = document.getElementById("view-" + vKey);
    if (el) {
      if (vKey === state.currentView) {
        el.classList.remove("hidden");
        el.classList.add("view-fade-in");
        window.scrollTo({ top: 0, behavior: "smooth" });
      } else {
        el.classList.add("hidden");
        el.classList.remove("view-fade-in");
      }
    }
  });

  const mainHeader = document.getElementById("main-header");
  const bottomNav = document.getElementById("bottom-nav");
  if (state.currentView === "welcome") {
    if (mainHeader) mainHeader.classList.add("hidden");
    if (bottomNav) bottomNav.classList.add("hidden");
  } else {
    if (mainHeader) mainHeader.classList.remove("hidden");
    if (bottomNav) bottomNav.classList.remove("hidden");
  }

  // Ensure active view renders its fresh data and images immediately
  if (state.currentView === "detected") {
    renderDetectedView();
  } else if (state.currentView === "results") {
    renderResultsView();
  } else if (state.currentView === "recreate") {
    renderRecreateView();
  } else if (state.currentView === "wishlist") {
    renderWishlistView();
  }
  updateAllInspirationImages();
}

function updateNavIndicators() {
  document.querySelectorAll("[data-nav-target]").forEach(btn => {
    const target = btn.getAttribute("data-nav-target");
    if (target === state.activeNav) {
      btn.classList.add("text-primary", "font-bold");
      btn.classList.remove("text-on-surface-variant", "opacity-60");
      const icon = btn.querySelector(".material-symbols-outlined");
      if (icon) icon.classList.add("filled");
    } else {
      btn.classList.remove("text-primary", "font-bold");
      btn.classList.add("text-on-surface-variant", "opacity-60");
      const icon = btn.querySelector(".material-symbols-outlined");
      if (icon) icon.classList.remove("filled");
    }
  });
}

function setupNavigation() {
  document.querySelectorAll("[data-nav-target]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const target = btn.getAttribute("data-nav-target");
      state.setView(target);
    });
  });

  document.querySelectorAll("[data-go-back]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      if (state.currentView === "detected") state.setView("upload");
      else if (state.currentView === "results") state.setView("detected");
      else if (state.currentView === "recreate") state.setView("results");
      else state.setView("home");
    });
  });
}

function setupWelcomeView() {
  const btnStart = document.getElementById("btn-welcome-start");
  if (btnStart) {
    const triggerStart = (e) => {
      if (e) e.preventDefault();
      state.setView("home");
    };
    btnStart.addEventListener("click", triggerStart);
    btnStart.addEventListener("touchend", triggerStart);
  }
}

function setupHomeView() {
  const btnUpload = document.getElementById("btn-home-upload");
  if (btnUpload) {
    const triggerUpload = (e) => {
      if (e) e.preventDefault();
      state.setView("upload");
    };
    btnUpload.addEventListener("click", triggerUpload);
    btnUpload.addEventListener("touchend", triggerUpload);
  }

  const btnDemo = document.getElementById("btn-home-demo");
  if (btnDemo) {
    const triggerDemo = (e) => {
      if (e) e.preventDefault();
      useDemoOutfit();
    };
    btnDemo.addEventListener("click", triggerDemo);
    btnDemo.addEventListener("touchend", triggerDemo);
  }
}

function setupUploadView() {
  const dropZone = document.getElementById("upload-dropzone");
  const fileInput = document.getElementById("file-input");
  const btnBrowse = document.getElementById("btn-browse-gallery");
  const btnUseDemo = document.getElementById("btn-use-demo-upload");
  const btnAnalyze = document.getElementById("btn-analyze-look");
  const btnReset = document.getElementById("btn-reset-upload");
  const uploadState1 = document.getElementById("upload-state-initial");
  const uploadState2 = document.getElementById("upload-state-preview");
  const previewImg = document.getElementById("upload-preview-img");

  if (btnBrowse && fileInput) btnBrowse.addEventListener("click", () => fileInput.click());

  if (fileInput) {
    fileInput.addEventListener("change", async (e) => {
      if (e.target.files && e.target.files[0]) handleFileSelected(e.target.files[0]);
    });
  }

  if (dropZone) {
    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("border-primary", "bg-surface-container");
    });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("border-primary", "bg-surface-container"));
    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("border-primary", "bg-surface-container");
      if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFileSelected(e.dataTransfer.files[0]);
    });
  }

  if (btnUseDemo) btnUseDemo.addEventListener("click", () => useDemoOutfit(false));

  if (btnReset) {
    btnReset.addEventListener("click", () => {
      uploadState2.classList.add("hidden");
      uploadState1.classList.remove("hidden");
      state.setImage(null, null);
    });
  }

  if (btnAnalyze) btnAnalyze.addEventListener("click", () => startAiAnalysis());

let pendingImageUploadPromise = null;

  async function handleFileSelected(file) {
    const localUrl = URL.createObjectURL(file);
    previewImg.src = localUrl;
    uploadState1.classList.add("hidden");
    uploadState2.classList.remove("hidden");
    state.setImage(localUrl, null);

    pendingImageUploadPromise = api.uploadImage(file)
      .then(uploadRes => {
        if (uploadRes && uploadRes.upload_id) {
          state.setImage(uploadRes.image_url, uploadRes.upload_id);
        }
        return uploadRes;
      })
      .catch(err => {
        console.log("Local preview active:", err);
        return null;
      });
  }
}

function useDemoOutfit(triggerImmediateAnalysis = false) {
  state.setImage(DEMO_IMAGE_URL, "demo_atelier_look");
  const previewImg = document.getElementById("upload-preview-img");
  const uploadState1 = document.getElementById("upload-state-initial");
  const uploadState2 = document.getElementById("upload-state-preview");
  if (previewImg) previewImg.src = DEMO_IMAGE_URL;
  if (uploadState1) uploadState1.classList.add("hidden");
  if (uploadState2) uploadState2.classList.remove("hidden");

  if (triggerImmediateAnalysis) startAiAnalysis();
  else state.setView("upload");
}

function setupAnalysisView() {
  const btnViewMatches = document.getElementById("btn-view-matches");
  if (btnViewMatches) btnViewMatches.addEventListener("click", () => state.setView("detected"));
}

async function startAiAnalysis() {
  state.setView("analysis");
  const analysisImg = document.getElementById("analysis-preview-img");
  if (analysisImg) analysisImg.src = resolveInspirationImageUrl(state.uploadedImage) || DEMO_IMAGE_URL;

  resetAnalysisSteps();

  setTimeout(() => setStepDone(1), 500);
  setTimeout(() => setStepDone(2), 1400);
  setTimeout(() => setStepDone(3), 2300);

  // Await pending upload if user clicks quickly
  if (pendingImageUploadPromise) {
    try {
      await pendingImageUploadPromise;
    } catch (e) {
      console.warn("Upload resolution note:", e);
    }
    pendingImageUploadPromise = null;
  }

  let detectedItems = [];
  try {
    const res = await api.analyzeLook(state.uploadId, state.uploadedImage);
    if (res && Array.isArray(res.detected_items) && res.detected_items.length > 0) {
      // Use REAL detections directly! Do not append fallback/demo items.
      detectedItems = res.detected_items;
    }
  } catch (err) {
    console.warn("Backend analysis notice, using verified fallback:", err);
  }

  // Only use verified fallback list when detector genuinely returns 0 items
  if (!detectedItems || detectedItems.length === 0) {
    detectedItems = [
      {
        item_id: "det_top_01",
        category: "top",
        label: "White Oversized Shirt",
        attributes: "Cotton, Button-down, Relaxed fit",
        confidence: 0.96,
        hotspot: { top: 35.0, left: 48.0 },
        crop_url: "/static/assets/products/prod_005.jpg",
        is_fallback: true,
        detection_source: "demo_fallback"
      },
      {
        item_id: "det_bottom_02",
        category: "bottom",
        label: "Light Wash Straight Jeans",
        attributes: "Denim, Straight leg, High-rise",
        confidence: 0.94,
        hotspot: { top: 66.0, left: 50.0 },
        crop_url: "/static/assets/products/prod_006.jpg",
        is_fallback: true,
        detection_source: "demo_fallback"
      },
      {
        item_id: "det_bag_03",
        category: "bag",
        label: "Structured Beige Tote",
        attributes: "Leather, Minimalist, Top handle",
        confidence: 0.92,
        hotspot: { top: 54.0, left: 26.0 },
        crop_url: "/static/assets/products/prod_010.jpg",
        is_fallback: true,
        detection_source: "demo_fallback"
      },
      {
        item_id: "det_shoes_04",
        category: "shoes",
        label: "Classic Leather Loafers",
        attributes: "Calfskin leather, Penny loafer, Brown",
        confidence: 0.88,
        hotspot: { top: 92.0, left: 48.0 },
        crop_url: "/static/assets/products/prod_013.jpg",
        is_fallback: true,
        detection_source: "demo_fallback"
      }
    ];
  }

  state.setDetectedItems(detectedItems);

  try {
    const searchRes = await api.searchProducts(detectedItems, state.filters);
    if (searchRes && searchRes.results_by_category) {
      state.setCategoryResults(searchRes.results_by_category);
    }
  } catch (err) {
    loadFallbackCategoryResults();
  }

  setTimeout(() => {
    setStepDone(4);
    revealAnalysisResults(detectedItems);
  }, 2600);
}

function resetAnalysisSteps() {
  for (let i = 1; i <= 4; i++) {
    const step = document.getElementById(`analysis-step-${i}`);
    if (step) {
      const iconContainer = step.querySelector(".step-icon");
      if (iconContainer) {
        iconContainer.className = "step-icon w-8 h-8 rounded-full border-2 border-outline-variant flex items-center justify-center text-outline-variant";
        iconContainer.innerHTML = '<span class="material-symbols-outlined text-[18px]">more_horiz</span>';
      }
    }
  }
  const finalResults = document.getElementById("analysis-final-results");
  if (finalResults) finalResults.classList.add("hidden");
  const scanLine = document.querySelector("#view-analysis .scan-line");
  if (scanLine) scanLine.style.display = "block";
}

function setStepDone(stepNum) {
  const step = document.getElementById(`analysis-step-${stepNum}`);
  if (step) {
    const iconContainer = step.querySelector(".step-icon");
    if (iconContainer) {
      iconContainer.className = "step-icon w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary transition-all duration-300";
      iconContainer.innerHTML = '<span class="material-symbols-outlined text-[18px] filled">check</span>';
    }
    const text = step.querySelector("p");
    if (text) text.classList.remove("text-on-surface-variant", "animate-pulse");
  }
}

function revealAnalysisResults(detectedItems) {
  const finalResults = document.getElementById("analysis-final-results");
  const scanLine = document.querySelector("#view-analysis .scan-line");
  if (scanLine) scanLine.style.display = "none";
  if (finalResults) {
    const countHeader = document.getElementById("analysis-count-header");
    if (countHeader) countHeader.textContent = `${detectedItems.length} item${detectedItems.length === 1 ? '' : 's'} detected ✨`;

    const chipsContainer = document.getElementById("analysis-detected-chips");
    if (chipsContainer) {
      chipsContainer.innerHTML = detectedItems.map(item => `
        <span class="px-4 py-2 bg-[#2e1d38] text-[#f6d9ff] border border-[#7316a0]/80 font-label-md text-sm font-semibold rounded-full shadow-md tracking-wider uppercase">
          ${item.label}
        </span>
      `).join("");
    }
    finalResults.classList.remove("hidden");
    finalResults.classList.add("view-fade-in");
  }
}

function setupDetectedView() {
  const btnProceed = document.getElementById("btn-detected-proceed");
  if (btnProceed) btnProceed.addEventListener("click", () => state.setView("results"));

  const btnUploadNew = document.getElementById("btn-detected-upload-new");
  if (btnUploadNew) btnUploadNew.addEventListener("click", () => state.setView("upload"));
}

function renderDetectedView() {
  const inspirationImg = document.getElementById("detected-inspiration-img");
  if (inspirationImg) {
    inspirationImg.src = resolveInspirationImageUrl(state.uploadedImage);
    inspirationImg.onerror = function() {
      this.onerror = null;
      this.src = "/uploads/demo_sample.jpg";
    };
  }

  const hotspotsOverlay = document.getElementById("detected-hotspots-overlay");
  if (hotspotsOverlay) {
    hotspotsOverlay.innerHTML = state.detectedItems.map(item => `
      <div class="hotspot-point ${state.activeHotspotId === item.item_id ? 'active' : ''}" 
           style="top: ${item.hotspot.top}%; left: ${item.hotspot.left}%;" 
           data-hotspot-id="${item.item_id}">
        <div class="hotspot-pulse-ring"></div>
        <div class="hotspot-core"></div>
        <div class="hotspot-tooltip">${item.label}</div>
      </div>
    `).join("");

    hotspotsOverlay.querySelectorAll(".hotspot-point").forEach(el => {
      el.addEventListener("click", () => state.setActiveHotspot(el.getAttribute("data-hotspot-id")));
    });
  }

  const listContainer = document.getElementById("detected-items-list");
  if (listContainer) {
    listContainer.innerHTML = state.detectedItems.map(item => {
      const cropSrc = item.crop_url ? resolveProductImage({ image_url: item.crop_url }) : resolveInspirationImageUrl(state.uploadedImage);
      const fallbackSrc = resolveInspirationImageUrl(state.uploadedImage);
      const confPct = Math.round((item.confidence || 0.9) * 100);
      return `
      <div class="group relative flex items-center bg-surface-container-lowest hover:bg-surface-container-low transition-all rounded-xl p-4 gap-4 border ${state.activeHotspotId === item.item_id ? 'border-primary' : 'border-surface-container-highest'}"
           id="detected-card-${item.item_id}">
        <div class="w-20 h-24 rounded-lg overflow-hidden bg-surface-container shrink-0">
          <img class="w-full h-full object-cover" src="${cropSrc}" alt="${item.label}" onerror="this.onerror=null; this.src='${fallbackSrc}';" />
        </div>
        <div class="flex-grow">
          <div class="flex items-center gap-2 mb-1.5 flex-wrap">
            <span class="inline-block bg-[#3d2449] text-[#f6d9ff] border border-[#7316a0] font-label-sm text-[11px] px-3 py-1 rounded-full uppercase tracking-wider font-bold">
              ${item.category}
            </span>
            ${item.detection_source === 'deepfashion2_yolo' ? `
              <span class="inline-flex items-center gap-1 bg-[#4d1033] text-[#ffd8e6] border border-[#ffb0d0]/60 font-label-sm text-[10px] px-2.5 py-0.5 rounded-full font-semibold">
                <span class="w-1.5 h-1.5 rounded-full bg-[#ffb0d0] animate-pulse"></span>
                DeepFashion2
              </span>
            ` : item.detection_source === 'coco_yolo' || item.detection_source === 'real_yolo' ? `
              <span class="inline-flex items-center gap-1 bg-[#2a1738] text-[#e8b3ff] border border-[#e8b3ff]/60 font-label-sm text-[10px] px-2.5 py-0.5 rounded-full font-semibold">
                <span class="w-1.5 h-1.5 rounded-full bg-[#e8b3ff] animate-pulse"></span>
                COCO YOLO
              </span>
            ` : `
              <span class="inline-block bg-[#2e2830] text-[#d1c2d3] border border-[#4e4351] font-label-sm text-[10px] px-2.5 py-0.5 rounded-full font-medium">
                Verified Fallback
              </span>
            `}
            <span class="ml-auto px-2.5 py-0.5 rounded-full bg-[#241d26] border border-[#4e4351] text-[#ffffff] font-label-sm text-[11px] font-bold">
              ${confPct}% Conf
            </span>
          </div>
          <h3 class="font-headline text-[#ffffff] text-xl font-bold tracking-wide uppercase mt-1">${item.label}</h3>
          <p class="font-body-md text-on-surface-variant text-sm mt-1">${item.attributes || ''}</p>
        </div>
        <button class="btn-remove-detected w-10 h-10 rounded-full flex items-center justify-center text-on-surface-variant hover:text-error hover:bg-error-container transition-colors shrink-0"
                data-remove-id="${item.item_id}"
                title="Remove item">
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
      </div>
    `;
    }).join("");

    listContainer.querySelectorAll(".btn-remove-detected").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const id = btn.getAttribute("data-remove-id");
        state.detectedItems = state.detectedItems.filter(it => it.item_id !== id);
        renderDetectedView();
      });
    });

    listContainer.querySelectorAll('[id^="detected-card-"]').forEach(card => {
      card.addEventListener("mouseenter", () => state.setActiveHotspot(card.id.replace("detected-card-", "")));
    });
  }

  // Dynamic Item Count Update
  const countText = document.getElementById("detected-count-text");
  if (countText) {
    countText.textContent = `${state.detectedItems.length} Item${state.detectedItems.length === 1 ? '' : 's'} Detected`;
  }
  const countBadge = document.getElementById("detected-count-badge");
  if (countBadge && !countText) {
    countBadge.textContent = `${state.detectedItems.length} Item${state.detectedItems.length === 1 ? '' : 's'} Detected`;
  }

  // Dynamic Average AI Confidence Update
  const confEl = document.getElementById("detected-ai-conf-val");
  if (confEl && state.detectedItems.length > 0) {
    const avgConf = Math.round(state.detectedItems.reduce((acc, it) => acc + (it.confidence || 0.9), 0) / state.detectedItems.length * 100);
    confEl.textContent = `${avgConf}%`;
  }
}

function updateHotspotHighlight() {
  document.querySelectorAll(".hotspot-point").forEach(el => {
    if (el.getAttribute("data-hotspot-id") === state.activeHotspotId) el.classList.add("active");
    else el.classList.remove("active");
  });

  document.querySelectorAll('[id^="detected-card-"]').forEach(card => {
    if (card.id.replace("detected-card-", "") === state.activeHotspotId) {
      card.classList.add("border-primary", "bg-surface-container-low");
      card.classList.remove("border-surface-container-highest");
    } else {
      card.classList.remove("border-primary", "bg-surface-container-low");
      card.classList.add("border-surface-container-highest");
    }
  });
}

function setupResultsView() {
  const btnOpenFilter = document.getElementById("btn-open-filters");
  if (btnOpenFilter) btnOpenFilter.addEventListener("click", () => openFilterModal());

  const btnRecreate = document.getElementById("btn-results-recreate-look");
  if (btnRecreate) btnRecreate.addEventListener("click", () => state.setView("recreate"));
}

function renderResultsView() {
  const thumb = document.getElementById("results-inspiration-thumb");
  if (thumb) thumb.src = state.uploadedImage || DEMO_IMAGE_URL;

  const categoriesContainer = document.getElementById("results-categories-container");
  if (!categoriesContainer) return;

  const categories = Object.keys(state.categoryResults);
  if (categories.length === 0) {
    categoriesContainer.innerHTML = '<div class="text-center py-16 text-on-surface-variant"><p class="font-editorial text-2xl text-primary mb-2">No matches found</p><p class="font-body-md">Try changing your filters.</p></div>';
    return;
  }

  categoriesContainer.innerHTML = categories.map(catKey => {
    const group = state.categoryResults[catKey];
    const itemTitle = group.detected_item || group.category_label || catKey.toUpperCase();
    const catBadge = (group.category || "item").toUpperCase();
    return `
      <section class="mb-14">
        <div class="flex items-center gap-3 mb-5">
          <span class="px-3 py-1 bg-secondary-fixed text-on-secondary-fixed font-label-sm text-[11px] uppercase tracking-wider rounded-full font-semibold">
            ${catBadge}
          </span>
          <h3 class="font-editorial text-2xl md:text-3xl text-primary">${itemTitle}</h3>
        </div>
        <div class="flex overflow-x-auto gap-5 md:gap-gutter pb-4 no-scrollbar">
          ${group.products.map(prod => {
            const imgSrc = resolveProductImage(prod);
            const prodUrl = resolveProductUrl(prod);
            const safeName = (prod.product_name || "").replace(/'/g, "\\'");
            const safeBrand = (prod.brand || "").replace(/'/g, "\\'");
            const safeCat = (prod.category || catKey || "").replace(/'/g, "\\'");

            return `
            <div class="min-w-[220px] md:min-w-[280px] flex-shrink-0 group flex flex-col justify-between bg-surface-container-low/50 p-3 rounded-2xl border border-surface-container-highest/60 hover:border-primary/40 transition-all duration-300" data-product-id="${prod.product_id}">
              <div>
                <div class="relative h-[280px] md:h-[340px] rounded-xl overflow-hidden mb-3 bg-surface-container shadow-sm group-hover:shadow-md transition-all duration-300">
                  <img class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
                       src="${imgSrc}" 
                       alt="${prod.product_name}" 
                       loading="lazy"
                       referrerpolicy="no-referrer"
                       onerror="this.onerror=null; this.src=window.getFallbackProductImage('${safeName}', '${safeBrand}', '${safeCat}');" />
                  <button class="btn-toggle-wishlist absolute top-3 right-3 w-9 h-9 bg-surface/80 hover:bg-surface backdrop-blur-md rounded-full flex items-center justify-center transition-colors z-10"
                          data-product-id="${prod.product_id}"
                          aria-label="Wishlist">
                    <span class="material-symbols-outlined text-[20px] ${prod.is_wishlisted ? 'filled text-tertiary' : 'text-on-surface'}">
                      favorite
                    </span>
                  </button>
                  <div class="absolute bottom-3 left-3 px-2.5 py-1 bg-primary/95 text-on-primary font-label-sm text-[11px] font-semibold tracking-wider rounded-md backdrop-blur-sm">
                    ${prod.match_pct || '92% Match'}
                  </div>
                </div>
                <div class="mb-3">
                  <div class="flex justify-between items-start mb-1">
                    <span class="font-label-sm text-xs text-on-surface-variant uppercase tracking-wider">${prod.brand}</span>
                    <span class="font-body-md text-base font-semibold text-primary">${prod.formatted_price || '₹' + prod.price}</span>
                  </div>
                  <h4 class="font-body-md text-on-surface truncate font-medium">${prod.product_name}</h4>
                </div>
              </div>
              <a href="${prodUrl}" 
                 target="_blank" 
                 rel="noopener noreferrer" 
                 class="btn-view-product flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-full bg-surface-container hover:bg-primary hover:text-on-primary text-on-surface text-xs font-label uppercase tracking-wider font-semibold transition-all duration-300 border border-surface-container-highest hover:border-transparent hover:shadow-[0_4px_16px_rgba(232,179,255,0.25)]">
                <span>View Product</span>
                <span class="material-symbols-outlined text-[16px]">open_in_new</span>
              </a>
            </div>
          `;
          }).join('')}
        </div>
      </section>
    `;
  }).join('');

  categoriesContainer.querySelectorAll(".btn-toggle-wishlist").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const pid = btn.getAttribute("data-product-id");
      const icon = btn.querySelector(".material-symbols-outlined");
      const isFilled = icon.classList.contains("filled");
      if (isFilled) {
        icon.classList.remove("filled", "text-tertiary");
        icon.classList.add("text-on-surface");
        await api.removeFromWishlist(pid);
      } else {
        icon.classList.add("filled", "text-tertiary");
        icon.classList.remove("text-on-surface");
        await api.addToWishlist(pid);
        showToast("Added to Wishlist ❤️");
      }
    });
  });

  categoriesContainer.querySelectorAll("[data-product-id]").forEach(card => {
    card.addEventListener("click", (e) => {
      if (e.target.closest(".btn-toggle-wishlist") || e.target.closest(".btn-view-product")) {
        return;
      }
      const btnView = card.querySelector(".btn-view-product");
      if (btnView && btnView.href) {
        window.open(btnView.href, "_blank");
      }
    });
  });
}

function setupFilterModal() {
  const modal = document.getElementById("filter-modal");
  const btnClose = document.getElementById("btn-close-filter");
  const btnClear = document.getElementById("btn-clear-filter");
  const btnApply = document.getElementById("btn-apply-filter");

  if (btnClose) btnClose.addEventListener("click", closeFilterModal);
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeFilterModal();
    });
  }

  document.querySelectorAll("[data-filter-budget]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-filter-budget]").forEach(b => {
        b.className = "px-5 py-2.5 rounded-full bg-surface-container text-on-surface hover:bg-surface-container-highest transition-colors font-body-md text-sm border border-transparent";
      });
      btn.className = "px-5 py-2.5 rounded-full bg-primary text-on-primary font-body-md text-sm font-medium shadow-sm";
      state.filters.budget = btn.getAttribute("data-filter-budget");
    });
  });

  document.querySelectorAll("[data-filter-category]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-filter-category]").forEach(b => {
        b.className = "px-5 py-2.5 rounded-full bg-surface-container text-on-surface hover:bg-surface-container-highest transition-colors font-body-md text-sm border border-transparent";
      });
      btn.className = "px-5 py-2.5 rounded-full bg-primary text-on-primary font-body-md text-sm font-medium shadow-sm";
      state.filters.category = btn.getAttribute("data-filter-category");
    });
  });

  document.querySelectorAll("input[name='filter-sort']").forEach(radio => {
    radio.addEventListener("change", (e) => state.filters.sort = e.target.value);
  });

  if (btnClear) {
    btnClear.addEventListener("click", () => {
      state.filters = { sort: "match", budget: null, category: "all", brand: null };
      closeFilterModal();
      applyFilters();
    });
  }

  if (btnApply) {
    btnApply.addEventListener("click", () => {
      closeFilterModal();
      applyFilters();
    });
  }
}

function openFilterModal() {
  const modal = document.getElementById("filter-modal");
  if (modal) modal.classList.remove("hidden");
}

function closeFilterModal() {
  const modal = document.getElementById("filter-modal");
  if (modal) modal.classList.add("hidden");
}

async function applyFilters() {
  try {
    const res = await api.searchProducts(state.detectedItems, state.filters);
    if (res && res.results_by_category) state.setCategoryResults(res.results_by_category);
  } catch (err) {
    console.warn("Filter fallback:", err);
  }
}

function setupRecreateView() {
  const btnSaveLook = document.getElementById("btn-save-curated-look");
  if (btnSaveLook) {
    btnSaveLook.addEventListener("click", async () => {
      try {
        await api.saveLook({
          title: "My Curated Outfit",
          inspiration_image: state.uploadedImage || DEMO_IMAGE_URL,
          items: state.curatedLook.items,
          total_price: state.curatedLook.estimatedTotal
        });
        showToast("Complete look saved to your Profile ✨");
      } catch (err) {
        showToast("Curated look saved locally!");
      }
    });
  }

  const btnShopLook = document.getElementById("btn-shop-curated-look");
  if (btnShopLook) {
    btnShopLook.addEventListener("click", () => {
      if (state.curatedLook.items.length > 0) {
        window.open(state.curatedLook.items[0].product_url || "https://www.zara.com", "_blank");
      }
    });
  }
}

function renderRecreateView() {
  const inspImg = document.getElementById("recreate-inspiration-img");
  if (inspImg) inspImg.src = state.uploadedImage || DEMO_IMAGE_URL;

  const totalEl = document.getElementById("recreate-total-price");
  if (totalEl) totalEl.textContent = state.curatedLook.formattedTotal;

  const listContainer = document.getElementById("recreate-items-list");
  if (!listContainer) return;

  listContainer.innerHTML = state.curatedLook.items.map((item, idx) => {
    const imgSrc = resolveProductImage(item);
    const prodUrl = resolveProductUrl(item);
    const safeName = (item.name || "").replace(/'/g, "\\'");
    const safeBrand = (item.brand || "").replace(/'/g, "\\'");
    const safeCat = (item.category || "").replace(/'/g, "\\'");

    return `
    <div class="flex gap-4 p-4 rounded-2xl bg-surface-container-low hover:bg-surface-container transition-colors ambient-shadow group relative overflow-hidden border border-surface-container-highest">
      <div class="w-24 h-32 rounded-xl overflow-hidden shrink-0 bg-surface-container">
        <img class="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500" 
             src="${imgSrc}" 
             alt="${item.name}"
             loading="lazy"
             referrerpolicy="no-referrer"
             onerror="this.onerror=null; this.src=window.getFallbackProductImage('${safeName}', '${safeBrand}', '${safeCat}');" />
      </div>
      <div class="flex flex-col flex-grow justify-between py-1">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-editorial text-lg md:text-xl text-primary font-medium">${item.name}</h3>
            <p class="font-body-md text-sm text-on-surface-variant">${item.brand}</p>
          </div>
          <span class="font-editorial text-lg md:text-xl text-primary font-semibold">₹${item.price.toLocaleString("en-IN")}</span>
        </div>
        <div class="flex justify-between items-end gap-2 flex-wrap pt-2">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full bg-surface border border-outline-variant text-[11px] font-semibold text-on-surface">
              ${item.size}
            </span>
            <button class="btn-edit-size text-on-surface-variant hover:text-primary transition-colors text-xs underline underline-offset-4"
                    data-item-index="${idx}">
              Edit Size
            </button>
          </div>
          <div class="flex items-center gap-3">
            <a href="${prodUrl}" target="_blank" rel="noopener noreferrer" class="text-primary hover:text-secondary-fixed transition-colors flex items-center gap-1 font-label-md text-xs uppercase tracking-wider font-semibold">
              <span>View Product</span>
              <span class="material-symbols-outlined text-[14px]">open_in_new</span>
            </a>
            <button class="btn-swap-item text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 font-label-md text-xs uppercase tracking-wider"
                    data-item-index="${idx}">
              <span class="material-symbols-outlined text-[16px]">swap_horiz</span> Swap
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
  }).join('');

  listContainer.querySelectorAll(".btn-edit-size").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.getAttribute("data-item-index"));
      const current = state.curatedLook.items[idx].size;
      const newSize = prompt("Select size (e.g. S, M, L, XL, 30W, 32W):", current);
      if (newSize) {
        state.curatedLook.items[idx].size = newSize.toUpperCase();
        renderRecreateView();
      }
    });
  });

  listContainer.querySelectorAll(".btn-swap-item").forEach(btn => {
    btn.addEventListener("click", () => {
      showToast("Opening catalog to swap item...");
      state.setView("results");
    });
  });
}

function setupWishlistView() {
  const tabProducts = document.getElementById("tab-wishlist-products");
  const tabLooks = document.getElementById("tab-wishlist-looks");

  if (tabProducts && tabLooks) {
    tabProducts.addEventListener("click", () => {
      state.wishlistTab = "products";
      tabProducts.className = "font-label-md text-sm border-b-2 border-primary text-primary pb-2 px-1 whitespace-nowrap font-semibold";
      tabLooks.className = "font-label-md text-sm border-b-2 border-transparent text-on-surface-variant pb-2 px-1 whitespace-nowrap hover:text-primary transition-colors";
      renderWishlistView();
    });

    tabLooks.addEventListener("click", () => {
      state.wishlistTab = "outfits";
      tabLooks.className = "font-label-md text-sm border-b-2 border-primary text-primary pb-2 px-1 whitespace-nowrap font-semibold";
      tabProducts.className = "font-label-md text-sm border-b-2 border-transparent text-on-surface-variant pb-2 px-1 whitespace-nowrap hover:text-primary transition-colors";
      renderWishlistView();
    });
  }
}

async function renderWishlistView() {
  const productsGrid = document.getElementById("wishlist-products-grid");
  const looksGrid = document.getElementById("wishlist-looks-grid");

  try {
    const wishData = await api.getWishlist();
    if (wishData && wishData.products) state.wishlist = wishData.products;
  } catch (err) {
    console.log("Wishlist load note:", err);
  }

  const tabProducts = document.getElementById("tab-wishlist-products");
  if (tabProducts) tabProducts.textContent = `Products (${state.wishlist.length})`;

  if (state.wishlistTab === "products") {
    if (productsGrid) productsGrid.classList.remove("hidden");
    if (looksGrid) looksGrid.classList.add("hidden");

    if (productsGrid) {
      if (state.wishlist.length === 0) {
        productsGrid.innerHTML = '<div class="col-span-full text-center py-20 text-on-surface-variant"><span class="material-symbols-outlined text-5xl mb-3 text-outline">favorite</span><p class="font-editorial text-2xl text-primary">Your wishlist is empty</p><p class="font-body-md mt-1">Tap the heart on any product to save it here.</p></div>';
      } else {
        productsGrid.innerHTML = state.wishlist.map(item => {
          const imgSrc = resolveProductImage(item);
          const prodUrl = resolveProductUrl(item);
          const safeName = (item.product_name || "").replace(/'/g, "\\'");
          const safeBrand = (item.brand || "").replace(/'/g, "\\'");
          const safeCat = (item.category || "").replace(/'/g, "\\'");

          return `
          <article class="group rounded-2xl bg-surface-container-low overflow-hidden relative border border-surface-container-highest transition-all duration-300 hover:scale-[1.02] shadow-sm flex flex-col justify-between">
            <div>
              <button class="btn-remove-wishlist absolute top-3 right-3 z-10 w-9 h-9 rounded-full bg-surface/80 flex items-center justify-center backdrop-blur-sm shadow-sm hover:bg-surface text-tertiary transition-colors"
                      data-product-id="${item.product_id}"
                      aria-label="Remove from Wishlist">
                <span class="material-symbols-outlined text-[20px] filled">favorite</span>
              </button>
              <div class="aspect-[3/4] w-full overflow-hidden bg-surface-container">
                <img src="${imgSrc}" 
                     alt="${item.product_name}" 
                     class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                     loading="lazy"
                     referrerpolicy="no-referrer"
                     onerror="this.onerror=null; this.src=window.getFallbackProductImage('${safeName}', '${safeBrand}', '${safeCat}');" />
              </div>
              <div class="p-4 bg-surface-container-lowest">
                <div class="flex justify-between items-start mb-1">
                  <span class="font-label-sm text-xs text-on-surface-variant uppercase tracking-wider">${item.brand}</span>
                  <span class="font-body-md text-base font-semibold text-primary">${item.formatted_price || '₹' + item.price}</span>
                </div>
                <h4 class="font-body-md text-sm text-on-surface truncate mb-3 font-medium">${item.product_name}</h4>
                <a href="${prodUrl}" target="_blank" rel="noopener noreferrer" class="flex items-center justify-center gap-1.5 w-full text-center py-2.5 rounded-full bg-secondary-container hover:bg-secondary-container/80 text-on-secondary-container font-label-md text-xs uppercase tracking-wider transition-colors font-semibold">
                  <span>View Product</span>
                  <span class="material-symbols-outlined text-[15px]">open_in_new</span>
                </a>
              </div>
            </div>
          </article>
        `;
        }).join('');

        productsGrid.querySelectorAll(".btn-remove-wishlist").forEach(btn => {
          btn.addEventListener("click", async () => {
            const pid = btn.getAttribute("data-product-id");
            await api.removeFromWishlist(pid);
            state.wishlist = state.wishlist.filter(it => it.product_id !== pid);
            renderWishlistView();
            showToast("Removed from Wishlist");
          });
        });
      }
    }
  } else {
    if (productsGrid) productsGrid.classList.add("hidden");
    if (looksGrid) looksGrid.classList.remove("hidden");

    let saved = [];
    try {
      const res = await api.getSavedLooks();
      saved = res.looks || [];
    } catch (err) {
      saved = state.savedLooks;
    }

    if (looksGrid) {
      looksGrid.innerHTML = saved.map(look => `
        <div class="bg-surface-container-low rounded-2xl p-6 border border-surface-container-highest">
          <div class="flex flex-col md:flex-row gap-6 items-start">
            <div class="w-full md:w-36 aspect-[3/4] rounded-xl overflow-hidden shrink-0">
              <img src="${look.inspiration_image}" alt="Outfit Inspiration" class="w-full h-full object-cover" />
            </div>
            <div class="flex-grow w-full">
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-editorial text-2xl text-primary">${look.title}</h3>
                <span class="font-editorial text-2xl text-primary font-semibold">${look.total_price_formatted || '₹' + look.total_price}</span>
              </div>
              <p class="font-body-md text-xs text-on-surface-variant mb-4">${look.created_at || 'Saved recently'}</p>
              <div class="space-y-2 mb-6">
                ${(look.items || []).map(it => `
                  <div class="flex justify-between text-sm py-1 border-b border-surface-container">
                    <span class="text-on-surface-variant">${it.category || 'Piece'}: <strong class="text-on-surface">${it.name}</strong></span>
                    <span class="text-primary font-medium">₹${(it.price || 0).toLocaleString("en-IN")}</span>
                  </div>
                `).join('')}
              </div>
              <button class="px-6 py-2.5 rounded-full bg-primary text-on-primary font-label-md text-xs uppercase tracking-wider hover:opacity-90 transition-opacity">
                Shop Entire Outfit
              </button>
            </div>
          </div>
        </div>
      `).join('');
    }
  }
}

function setupProfileView() {
  document.querySelectorAll("[data-profile-link]").forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const action = link.getAttribute("data-profile-link");
      if (action === "looks") {
        state.setView("wishlist");
        state.wishlistTab = "outfits";
        renderWishlistView();
      } else if (action === "wishlist") {
        state.setView("wishlist");
        state.wishlistTab = "products";
        renderWishlistView();
      } else {
        showToast("Opening preferences...");
      }
    });
  });
}

function showToast(message) {
  const toast = document.getElementById("snap-toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.remove("opacity-0", "translate-y-4", "pointer-events-none");
  toast.classList.add("opacity-100", "translate-y-0");
  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-y-4", "pointer-events-none");
    toast.classList.remove("opacity-100", "translate-y-0");
  }, 2500);
}

function loadFallbackCategoryResults() {
  state.setCategoryResults({
    top: {
      category_label: "White Top",
      category: "top",
      products: [
        {
          product_id: "prod_001",
          product_name: "Crisp White Blouse",
          brand: "Zara",
          price: 799,
          formatted_price: "₹799",
          match_pct: "94% Match",
          image_url: "https://lh3.googleusercontent.com/aida-public/AB6AXuD_klGO3wsCHqy2cIpbVqKobAyjYbgjLFOJQOXwSs6jdxdtmMJMBz1TmaIoeG9gk9iCzaWgNtpqU0ylYC55escYEKjTTeT0Xz7SU3eGzWqZ_iZsbFQ_4LA3-A4dYFxDGz9kYvZ6z7ykpXQdZCEFIzcGK73k8moV33OSYMeWfECmIRXxJPrD0c9vAmX148B-__wZaEcuVmCWxhC3n8JRuc7GAoBY3MJwuQ_69LGLheOTj2unpChAH7q3LA",
          product_url: "https://www.zara.com"
        },
        {
          product_id: "prod_002",
          product_name: "Cotton Poplin Shirt",
          brand: "H&M",
          price: 1499,
          formatted_price: "₹1,499",
          match_pct: "88% Match",
          image_url: "https://lh3.googleusercontent.com/aida-public/AB6AXuBBErBvaXjNa_BRM647k2k17ZiRjdRcHD2zYF8Y94u-3Bx-i7P8gSdtbqL_iqbo260789tNtoipps-FZbH6MJyuluMfIx26E14ghifUfoEi9zW1glG8TkjLMOClJnMd-ES3OLk_gHVegxbhN0Tg8LO_MZaE4uhRXUuimPCOL4OaTIhQAIVjfTys1DL2wkww_2dNsOuOi1N9Sqh1jqwf5QnU0VZdeqBSfs9WMuJIi_winDEs8BCncyxg1w",
          product_url: "https://www2.hm.com"
        }
      ]
    },
    bottom: {
      category_label: "Blue Jeans",
      category: "bottom",
      products: [
        {
          product_id: "prod_007",
          product_name: "Classic Straight Jeans",
          brand: "Levi's Vintage",
          price: 1299,
          formatted_price: "₹1,299",
          match_pct: "91% Match",
          image_url: "https://lh3.googleusercontent.com/aida-public/AB6AXuCHa8b3RUweUIDNi8AYpmWelULa5je7O6ie31euQpdWuHHfE0AVNkm8J1kTWdqRhqdHvP2LFLWiWUcMPvdFYw0wC8iWNt_7hpCUS9ItnsbfdkxxVjJT3fV290-NjcUK68qzYV4bZcYtvIiTceYhFd0nyMMtLCWzlSpqOUGIntczAnvPDJInjTZndk7wq7xOwWAoQWIkbfcbuN7svWOCZUQkqpzR7wnuW9WhkhLUXOxvvmZAKZBPXcWL1Q",
          product_url: "https://www.levi.in"
        }
      ]
    }
  });
}

async function loadInitialData() {
  try {
    const health = await api.checkHealth();
    console.log("[SnapStyle] Backend status:", health);
    const wish = await api.getWishlist();
    if (wish && wish.products) state.wishlist = wish.products;
  } catch (e) {
    console.log("[SnapStyle] Ready.");
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
