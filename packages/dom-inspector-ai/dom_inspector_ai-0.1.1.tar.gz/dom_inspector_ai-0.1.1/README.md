# DOM Inspector AI

This package extracts all `id` and `class` attributes from a web page, along with their DOM paths and a base64 screenshot.

## Installation

```bash
pip install git+https://github.com/yut0takagi/dom-inspector-ai.git
```

## CLI Usage

```bash
python cli.py https://example.com > output.json
```

## Python Usage

```python
from dom_inspector_ai.analyzer import analyze_url

result = analyze_url("https://example.com")
print(result["ids"])
```

## Output

- `ids`: Dictionary of id attributes with tag, hierarchy, and CSS selector path
- `classes`: Dictionary of class attributes with count and example paths
- `screenshot_base64`: PNG screenshot of the page in base64
