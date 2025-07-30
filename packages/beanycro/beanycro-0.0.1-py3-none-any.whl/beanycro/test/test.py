import logging
import logging.config
import os


def ping():
    logging.getLogger(__name__).info("Ping received")
    return "pong"

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.debug("Starting test module")
    import beanycro.test.test2.tmp
    print(ping())
    logger.info("Test module finished")