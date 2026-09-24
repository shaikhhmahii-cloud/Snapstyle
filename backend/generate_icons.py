"""
Generates high-resolution Android app icons matching Google Stitch aesthetic:
- 192x192 PNG for standard Android launchers and PWA
- 512x512 PNG for high-DPI Android splash/launcher and Google Play/WebAPK
"""

import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def generate_icon(size: int, output_path: str):
    # Dark editorial palette
    bg_color = (23, 17, 25) # #171119
    accent_purple = (232, 179, 255) # #e8b3ff
    accent_glow = (115, 22, 160) # #7316a0
    white = (255, 255, 255)
    soft_pink = (255, 176, 208) # #ffb0d0

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background Rounded Squircle
    corner_radius = int(size * 0.22)
    draw.rounded_rectangle([0, 0, size, size], radius=corner_radius, fill=bg_color)

    # 2. Glowing Accent Border
    border_width = max(2, int(size * 0.02))
    draw.rounded_rectangle(
        [border_width, border_width, size - border_width, size - border_width],
        radius=corner_radius,
        outline=accent_glow,
        width=border_width
    )

    # 3. Stylized Camera / Sparkle Aperture
    center = size // 2
    r_outer = int(size * 0.28)
    draw.ellipse(
        [center - r_outer, center - r_outer, center + r_outer, center + r_outer],
        outline=accent_purple,
        width=max(3, int(size * 0.035))
    )

    r_inner = int(size * 0.16)
    draw.ellipse(
        [center - r_inner, center - r_inner, center + r_inner, center + r_inner],
        fill=accent_glow,
        outline=soft_pink,
        width=max(2, int(size * 0.02))
    )

    # 4. Center Sparkle Star
    sparkle_len = int(size * 0.09)
    sparkle_w = max(2, int(size * 0.025))
    draw.line([center - sparkle_len, center, center + sparkle_len, center], fill=white, width=sparkle_w)
    draw.line([center, center - sparkle_len, center, center + sparkle_len], fill=white, width=sparkle_w)

    # Top-right luxury sparkle
    sprk_x = center + int(size * 0.22)
    sprk_y = center - int(size * 0.22)
    min_len = int(size * 0.05)
    draw.line([sprk_x - min_len, sprk_y, sprk_x + min_len, sprk_y], fill=accent_purple, width=max(1, int(size * 0.015)))
    draw.line([sprk_x, sprk_y - min_len, sprk_x, sprk_y + min_len], fill=accent_purple, width=max(1, int(size * 0.015)))

    img.save(output_path, "PNG")
    print(f"Generated icon: {output_path} ({size}x{size})")

if __name__ == "__main__":
    generate_icon(192, os.path.join(ASSETS_DIR, "icon-192.png"))
    generate_icon(512, os.path.join(ASSETS_DIR, "icon-512.png"))
