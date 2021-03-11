import configparser
import logging


def parse(args):
    config = configparser.ConfigParser()
    config.read(args["config"])
    return config


def configure_logging(config):
    logging_config = {
        "format": config["format"],
        "level": config["level"],
        "datefmt": config["datefmt"],
    }
    if not config.getboolean("enabled"):
        logging_config["handlers"] = [logging.NullHandler()]
    logging.basicConfig(**logging_config)
