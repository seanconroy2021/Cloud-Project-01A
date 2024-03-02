import random
import string

import utils.logger as log

logger = log.setup_logger(name="Random Nam Creator")


def randomName(name):
    randomChars = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
    )
    randomName = f"{randomChars}-{name.lower()}"
    return randomName
