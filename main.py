import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from urllib.parse import urlparse, urlunparse

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create a timestamped folder
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
SAVE_DIR = os.path.join("E:/ReelGenerator/9gag_downloads", f"run_{timestamp}")
os.makedirs(SAVE_DIR, exist_ok=True)

def setup_browser():
    try:
        options = FirefoxOptions()
        # Browser visible for debugging
        #options.add_argument("--headless")
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_window_size(1400, 1200)

        # Zoom out to 30%
        driver.get("about:blank")
        driver.execute_script("document.body.style.zoom='30%'")
        return driver
    except Exception as e:
        logger.error(f"Failed to set up Firefox browser: {e}")
        return None

def extract_video_urls_live(driver, max_videos=30):
    logger.info("Extracting videos from live DOM...")
    video_urls = set()
    
    posts = driver.find_elements(By.TAG_NAME, "article")
    logger.info(f"Found {len(posts)} posts")

    for post in posts:
        try:
            # Scroll post into view to ensure video loads
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post)
            time.sleep(2.0)  # Let video start loading

            # Find <video> tag inside the post
            video = post.find_element(By.TAG_NAME, "video")
            sources = video.find_elements(By.TAG_NAME, "source")
            for src in sources:
                src_url = src.get_attribute("src")
                if src_url and "9gag" in src_url and src_url.endswith(".mp4"):
                    if src_url not in video_urls:
                        logger.debug(f"Found video: {src_url}")
                        video_urls.add(src_url)

        except Exception as e:
            logger.warning(f"Skipping post due to error: {e}")
            continue

        if len(video_urls) >= max_videos:
            break

    logger.info(f"Extracted {len(video_urls)} video URLs")

    # Save for inspection
    os.makedirs(SAVE_DIR, exist_ok=True)
    with open(os.path.join(SAVE_DIR, "video_urls.txt"), "w") as f:
        f.write("\n".join(video_urls))

    return list(video_urls)

def download_media(url, dest_folder):
    filename = url.split("/")[-1].split("?")[0]
    filepath = os.path.join(dest_folder, filename)

    if os.path.exists(filepath):
        logger.debug(f"File already exists: {filename}")
        return

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        logger.info(f"Downloaded: {filename}")
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")

def clean_url(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query=""))

def filter_video_variants(video_urls):
    """
    Keep only one video per base name, preferring AV1 versions.
    """
    unique = {}
    for url in video_urls:
        filename = os.path.basename(url)
        base_name = filename.split("_")[0]  # e.g., ae94wEB
        if base_name not in unique:
            unique[base_name] = url
        else:
            # Prefer AV1 version
            if "av1" in unique[base_name] and "av1" not in url:
                unique[base_name] = url
    return list(unique.values())

def main():
    logger.info("Starting the 9GAG downloader...")
    driver = setup_browser()

    if driver is None:
        logger.error("Browser setup failed. Exiting.")
        return

    try:
        driver.get("https://9gag.com/")
        time.sleep(10)
        # Set page zoom to 30%
        driver.execute_script("document.body.style.zoom='40%'")
        logger.info("Set zoom to 30%")
        time.sleep(2)


        # Controlled smooth scrolling
        for i in range(35):
            logger.info(f"Scrolling small step ({i + 1}/35)")
            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(5)

        raw_video_urls = extract_video_urls_live(driver, max_videos=50)

        cleaned_urls = [clean_url(url) for url in raw_video_urls]
        video_urls = filter_video_variants(cleaned_urls)

        logger.info(f"Total unique videos to download: {len(video_urls)}")

        for url in video_urls:
            download_media(url, SAVE_DIR)

    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed.")

if __name__ == "__main__":
    main()
