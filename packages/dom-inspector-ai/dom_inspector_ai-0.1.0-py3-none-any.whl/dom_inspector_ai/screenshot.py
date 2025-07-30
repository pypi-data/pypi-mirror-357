### dom_inspector_ai/screenshot.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64

def get_screenshot_base64(url: str) -> str:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 720)
    driver.get(url)

    png = driver.get_screenshot_as_png()
    driver.quit()

    return base64.b64encode(png).decode('utf-8')