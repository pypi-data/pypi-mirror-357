import logging

def get_logger() -> logging.Logger:
    logger = logging.getLogger("HoundAPI")

    if not logger.hasHandlers():
        # initialize
        output = logging.StreamHandler()
        output.setLevel(logging.INFO)
        output.setFormatter(logging.Formatter(
            "[%(asctime)s][%(endpoint)s] %(message)s"
        ))
        logger.addHandler(output)
        logger.setLevel(logging.INFO)
    
    return logger