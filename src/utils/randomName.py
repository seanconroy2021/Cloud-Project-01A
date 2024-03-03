import random
import string

import utils.logger as log

logger = log.setup_logger(name="Random Name Creator")


def randomName(name):
    """
    This function is helper function to create a random name it take in name
    and adds a random 6 character string to the start of the name.eg. "a34f343-Name"
    """
    randomChars = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
    )
    randomName = f"{randomChars}-{name.lower()}"
    return randomName
