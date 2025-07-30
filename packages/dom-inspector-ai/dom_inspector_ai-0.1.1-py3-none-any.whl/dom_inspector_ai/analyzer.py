### dom_inspector_ai/analyzer.py
import requests
from .extractor import extract_attributes
from .screenshot import get_screenshot_base64

def analyze_url(url: str) -> dict:
    response = requests.get(url)
    html = response.content
    ids, classes = extract_attributes(html)
    screenshot_b64 = get_screenshot_base64(url)

    return {
        "url": url,
        "screenshot_base64": "data:image/png;base64," + screenshot_b64,
        "ids": ids,
        "classes": classes
    }
