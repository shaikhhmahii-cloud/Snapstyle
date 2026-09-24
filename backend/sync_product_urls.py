"""
Syncs all 105 product URLs from products.csv into backend/main.py and frontend/js/app.js.
Ensures 100% complete coverage for all product URLs across the entire application.
"""

import os
import re
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "products.csv")
MAIN_PY_PATH = os.path.join(PROJECT_ROOT, "backend", "main.py")
APP_JS_PATH = os.path.join(PROJECT_ROOT, "frontend", "js", "app.js")

def sync():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} products from {CSV_PATH}")

    # Build dictionary
    url_dict = {}
    for _, row in df.iterrows():
        url_dict[row["product_id"]] = str(row["product_url"]).strip()

    print(f"Generated URL map for {len(url_dict)} products.")

    # 1. Update backend/main.py
    with open(MAIN_PY_PATH, "r", encoding="utf-8") as f:
        main_content = f.read()

    # Format Python dictionary
    py_lines = ["DEMO_PRODUCT_URLS = {"]
    for pid, url in sorted(url_dict.items()):
        py_lines.append(f'    "{pid}": "{url}",')
    py_lines.append("}")
    py_replacement = "\n".join(py_lines)

    new_main_content = re.sub(
        r"DEMO_PRODUCT_URLS = \{[^}]*\}",
        py_replacement,
        main_content,
        flags=re.DOTALL
    )

    with open(MAIN_PY_PATH, "w", encoding="utf-8") as f:
        f.write(new_main_content)
    print(f"Updated DEMO_PRODUCT_URLS in {MAIN_PY_PATH} with {len(url_dict)} URLs.")

    # 2. Update frontend/js/app.js
    with open(APP_JS_PATH, "r", encoding="utf-8") as f:
        app_content = f.read()

    # Format JS dictionary
    js_lines = ["export const DEMO_PRODUCT_URLS = {"]
    for pid, url in sorted(url_dict.items()):
        js_lines.append(f'  {pid}: "{url}",')
    js_lines.append("};")
    js_replacement = "\n".join(js_lines)

    new_app_content = re.sub(
        r"export const DEMO_PRODUCT_URLS = \{[^}]*\};",
        js_replacement,
        app_content,
        flags=re.DOTALL
    )

    with open(APP_JS_PATH, "w", encoding="utf-8") as f:
        f.write(new_app_content)
    print(f"Updated DEMO_PRODUCT_URLS in {APP_JS_PATH} with {len(url_dict)} URLs.")

if __name__ == "__main__":
    sync()
