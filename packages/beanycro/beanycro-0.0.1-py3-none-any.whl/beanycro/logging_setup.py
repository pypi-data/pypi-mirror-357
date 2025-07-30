import os
import logging
config_file = "logging.conf"

if not os.path.exists(config_file):
    raise FileNotFoundError(f"Logging config file not found: {config_file}")
logging.config.fileConfig(config_file, disable_existing_loggers=False)