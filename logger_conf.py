import logging

def get_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)

    logger.setLevel("DEBUG")
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("{asctime} - {levelname} - {name} - {funcName} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        

    return logger