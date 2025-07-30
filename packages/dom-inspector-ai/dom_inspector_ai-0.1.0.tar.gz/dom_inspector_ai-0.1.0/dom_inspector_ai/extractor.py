### dom_inspector_ai/extractor.py
from bs4 import BeautifulSoup

def extract_attributes(html):
    soup = BeautifulSoup(html, 'html.parser')
    ids = {}
    classes = {}

    for tag in soup.find_all(True):
        tag_name = tag.name
        tag_id = tag.get('id')
        tag_classes = tag.get('class')

        if tag_id:
            hierarchy, selector = get_path_info(tag)
            ids[tag_id] = {
                "tag": tag_name,
                "hierarchy": hierarchy,
                "selector_path": selector
            }

        if tag_classes:
            hierarchy, selector = get_path_info(tag)
            for cls in tag_classes:
                if cls not in classes:
                    classes[cls] = {
                        "count": 0,
                        "example_paths": []
                    }
                classes[cls]["count"] += 1
                if len(classes[cls]["example_paths"]) < 3:
                    classes[cls]["example_paths"].append(selector)

    return ids, classes

def get_path_info(tag):
    hierarchy = []
    current = tag
    while current.parent and current.name:
        name = current.name
        if current.get("id"):
            name += f"#{current.get('id')}"
        elif current.get("class"):
            name += "." + ".".join(current.get("class"))
        hierarchy.insert(0, name)
        current = current.parent
    selector_path = " > ".join(hierarchy)
    return hierarchy, selector_path