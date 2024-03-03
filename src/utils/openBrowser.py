import time
import webbrowser

import requests

import utils.logger as log

logger = log.setup_logger(name="Browser Opener")

# These are helper functions to open a browser to a specific URL 
# Their is functions that will wait for the URL to be accessible and write the URL to a file.

def open_browser(name, url):
    """
    This function opens a browser to a specific URL.
    """
    try:
        wait_for_url(url, 180, 33)
        logger.info(f"Opened browser to {name}: {url}")
        webbrowser.open(url)
        write_Url_to_file(name, url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        raise e


def wait_for_url(url, amount, sleep):
    """
    This function waits for a URL to be accessible.
    It takes in the URL, amount of time to wait until failed and the sleep time.
    """
    start_time = time.time() # remember when we started
    while True: # loop until we either get a response or time is greater than amount allowed.
        try:
            logger.info(f"Checking URL: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("URL is accessible")
                return True
        except requests.RequestException:
            logger.warning("URL check failed")
            logger.warning("Dont worry, we will try again.")

        if time.time() - start_time >= amount: # When time is greater than amount allowed return Fase meaning URL is not accessible.
            logger.error("Timeout reached. URL is not accessible.")
            raise TimeoutError 
        time.sleep(sleep) 


def write_Url_to_file(name, url):
    """
    This function writes a URL to a file.
    It takes in the name and URL and writes it to a file in data/url.txt.
    """
    try:
        filename = "data/url.txt"
        with open(filename, "a") as file:
            file.write(f"{name} : {url}\n")
            logger.info(f"URL written to file: {filename}")
    except Exception as e:
        logger.error(f"Failed to write URL to file: {e}")
        raise e
