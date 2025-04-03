from algo1_bot.bot import MyBot
from algo1_bot.config import load_config
import logging


def setup_logging(log_level: str | int) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main():
    config = load_config()
    setup_logging(config.log_level)
    bot = MyBot()
    bot.run(config.token)
