/**
 * SnapStyle API Client
 * Connects frontend to the FastAPI AI Backend.
 */

const API_BASE = window.SNAPSTYLE_API_URL || (window.location.protocol.startsWith("http") ? (window.location.port === "8000" ? "" : window.location.origin) : "http://10.0.2.2:8000");

export const api = {
  getBaseUrl() {
    return API_BASE;
  },

  async checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`, { headers: { "Accept": "application/json" } });
      if (res.ok) return await res.json();
      const resRoot = await fetch(`${API_BASE}/`, { headers: { "Accept": "application/json" } });
      return await resRoot.json();
    } catch (err) {
      console.warn("[SnapStyle API] Backend note:", err);
      return { status: "demo_mode" };
    }
  },

  async uploadImage(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Image upload failed");
    return await res.json();
  },

  async analyzeLook(uploadId, imageUrl) {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ upload_id: uploadId, image_url: imageUrl }),
    });
    if (!res.ok) throw new Error("AI analysis failed");
    return await res.json();
  },

  async searchProducts(detectedItems, filters = {}) {
    const res = await fetch(`${API_BASE}/search-products`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        detected_items: detectedItems,
        category: filters.category,
        budget_tier: filters.budget_tier,
        brand: filters.brand,
        sort_by: filters.sort_by || "match",
      }),
    });
    if (!res.ok) throw new Error("Similarity search failed");
    return await res.json();
  },

  async getProducts(filters = {}) {
    const params = new URLSearchParams();
    if (filters.category) params.append("category", filters.category);
    if (filters.budget) params.append("budget", filters.budget);
    if (filters.brand) params.append("brand", filters.brand);
    if (filters.sort) params.append("sort", filters.sort);
    if (filters.q) params.append("q", filters.q);

    const res = await fetch(`${API_BASE}/products?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch products");
    return await res.json();
  },

  async getWishlist() {
    const res = await fetch(`${API_BASE}/wishlist`);
    if (!res.ok) throw new Error("Failed to fetch wishlist");
    return await res.json();
  },

  async addToWishlist(productId) {
    const res = await fetch(`${API_BASE}/wishlist`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId }),
    });
    if (!res.ok) throw new Error("Failed to add to wishlist");
    return await res.json();
  },

  async removeFromWishlist(productId) {
    const res = await fetch(`${API_BASE}/wishlist/${productId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to remove from wishlist");
    return await res.json();
  },

  async getSavedLooks() {
    const res = await fetch(`${API_BASE}/saved-looks`);
    if (!res.ok) throw new Error("Failed to fetch saved looks");
    return await res.json();
  },

  async saveLook(lookData) {
    const res = await fetch(`${API_BASE}/saved-looks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lookData),
    });
    if (!res.ok) throw new Error("Failed to save look");
    return await res.json();
  }
};
