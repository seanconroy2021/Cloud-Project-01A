import utils.logger as log
import webbrowser
import requests
import time

logger = log.setup_logger(name="Browser Opener")

def open_browser(name,url):
    try:
        wait_for_url(url, 120, 60)
        logger.info(f"Opened browser to {name}: {url}")
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        return None
    
def wait_for_url(url, amount, sleep):
    start_time = time.time()
    while True:
        try:
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