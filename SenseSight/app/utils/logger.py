import logging

logger = logging.getLogger("sensesight")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler("sensesight.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
