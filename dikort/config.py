import configparser
import logging


def parse(config_location):
    config = configparser.ConfigParser()
    config.read(config_location)
    print(config.sections())
    configure_logging(config["logging"])


def configure_logging(config):
    logging_config = {
        "format": config["format"],
        "level": config["level"],
        "datefmt": config["datefmt"],
    }
    if not config.getboolean('enabled'):
        logging_config['handlers'] = [logging.NullHandler()]
    logging.basicConfig(**logging_config)
