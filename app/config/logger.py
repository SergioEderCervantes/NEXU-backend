import logging
import logging.config
import os

def setup_logging(config_path = 'app/config/logging.conf', logging_level = logging.INFO) -> logging.Logger:
    if os.path.exists(config_path):
        logging.config.fileConfig(config_path, disable_existing_loggers=False)
    else:
        logging.basicConfig(level=logging_level)
    return logging.getLogger('app')
