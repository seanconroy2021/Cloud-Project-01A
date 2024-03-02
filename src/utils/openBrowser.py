import time
import webbrowser

import requests

import utils.logger as log

logger = log.setup_logger(name="Browser Opener")


def open_browser(name, url):
    try:
        wait_for_url(url, 120, 40)
        logger.info(f"Opened browser to {name}: {url}")
        webbrowser.open(url)
        write_Url_to_file(name, url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        return None


def wait_for_url(url, amount, sleep):
    start_time = time.time()
    while True:
        try:
            logger.info(f"Checking URL: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("URL is accessible")
                return True
        except requests.RequestException as e:
            logger.warning(f"URL check failed")

        if time.time() - start_time >= amount:
            logger.error("Timeout reached. URL is not accessible.")
            return False
        time.sleep(sleep)


def write_Url_to_file(name, url):
    try:
        filename = "data/url.txt"
        with open(filename, "a") as file:
            file.write(f"{name} : {url}\n")
            logger.info(f"URL written to file: {filename}")
    except Exception as e:
        logger.error(f"Failed to write URL to file: {e}")
        return None
