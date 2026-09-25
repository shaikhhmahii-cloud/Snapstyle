/**
 * SnapStyle Application State
 * Centralized reactive store for views, uploaded images, detections, matching products, and wishlist.
 */

// Default verified prototype demo image
export const DEMO_IMAGE_URL = "https://lh3.googleusercontent.com/aida-public/AB6AXuDCmSvJyei4rSSZaQgy5nYnFr_nQVtIB6V6XjWb_G2o7NLlsA_WnACLsRdi6WouU3IUhHhtoxrwywGd7AGW5y0hNMSJvMvWChtYnPxBT82PxMM3OuiUuJsqwDSHp8BKQ1naLtZQa6UEW1Z4h8VolyaRtnzZak0B2CZHOIPCavj7jYZ8jt1TrTWsuKGmZ9p1WcxcizqhZejupWWAdRXvQCXPjQr6EcL6BqpANgkyYD-DOptTjrCaMNLr1Q";

export const state = {
  currentView: "home", // home | upload | analysis | detected | results | recreate | wishlist | profile | welcome
  activeNav: "home",
  
  // Upload and AI state
  uploadId: null,
  uploadedImage: null,
  detectedItems: [],
  activeHotspotId: null,
  
  // Products and Matching
  categoryResults: {},
  curatedLook: {
    items: [],
    estimatedTotal: 0,
    formattedTotal: "₹0"
  },
  
  // Filters
  filters: {
    sort: "match",
    budget: null, // "under_1000", "1000_2500", "2500_5000", "5000_plus"
    category: "all",
    brand: null
  },
  
  // User Data
  wishlist: [],
  savedLooks: [],
  wishlistTab: "products", // products | outfits
  
  // Filter Modal
  isFilterModalOpen: false,

  // Change subscribers
  subscribers: [],

  subscribe(fn) {
    this.subscribers.push(fn);
  },

  notify(event) {
    this.subscribers.forEach(fn => fn(event, this));
  },

  setView(viewName) {
    this.currentView = viewName;
    if (["home", "upload", "wishlist", "profile"].includes(viewName)) {
      this.activeNav = viewName;
    } else if (viewName === "results" || viewName === "detected" || viewName === "recreate") {
      this.activeNav = "find";
    }
    this.notify("view_changed");
  },

  setImage(url, uploadId = null) {
    this.uploadedImage = url;
    this.uploadId = uploadId;
    this.notify("image_updated");
  },

  setDetectedItems(items) {
    this.detectedItems = items;
    if (items.length > 0) {
      this.activeHotspotId = items[0].item_id;
    }
    this.notify("detected_items_updated");
  },

  setActiveHotspot(itemId) {
    this.activeHotspotId = itemId;
    this.notify("hotspot_changed");
  },

  setCategoryResults(results) {
    this.categoryResults = results;
    this.updateCuratedLookFromResults();
    this.notify("results_updated");
  },

  updateCuratedLookFromResults() {
    // Pick top matching product from each category for Recreate This Look
    const items = [];
    let total = 0;
    
    Object.keys(this.categoryResults).forEach(catKey => {
      const group = this.categoryResults[catKey];
      if (group.products && group.products.length > 0) {
        const topProd = group.products[0];
        const cat = (group.category || "top").toLowerCase();
        items.push({
          category: group.category_label || group.detected_item || catKey.toUpperCase(),
          product_id: topProd.product_id,
          name: topProd.product_name,
          brand: topProd.brand,
          price: topProd.price,
          image_url: topProd.image_url,
          product_url: topProd.product_url,
          size: cat === "bottom" ? "32W" : cat === "shoes" ? "UK 8" : cat === "top" ? "M" : "One Size"
        });
        total += topProd.price;
      }
    });

    this.curatedLook = {
      items,
      estimatedTotal: total,
      formattedTotal: `₹${total.toLocaleString("en-IN")}`
    };
  },

  swapItemInLook(index, newProduct) {
    if (this.curatedLook.items[index]) {
      this.curatedLook.items[index] = {
        ...this.curatedLook.items[index],
        product_id: newProduct.product_id,
        name: newProduct.product_name,
        brand: newProduct.brand,
        price: newProduct.price,
        image_url: newProduct.image_url,
        product_url: newProduct.product_url
      };
      // Recalculate total
      let total = 0;
      this.curatedLook.items.forEach(it => total += it.price);
      this.curatedLook.estimatedTotal = total;
      this.curatedLook.formattedTotal = `₹${total.toLocaleString("en-IN")}`;
      this.notify("look_updated");
    }
  }
};
