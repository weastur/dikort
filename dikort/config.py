import configparser
import logging


DEFAULTS = {
    "main": {
        "config": "./dikort.cfg",
    },
    "logging": {
        "enabled": False,
        "format": "%%(levelname)s - %%(asctime)s - %%(filename)s:%%(lineno)d - %%(message)s",
        "datefmt": "%%Y-%%m-%%d %%H:%%M:%%S",
        "level": "INFO",
        "another": True,
    },
}


def from_cmdargs_to_config(args):
    args_dict = vars(args)
    return {
        "main": args_dict,
    }


def parse(args):
    args = from_cmdargs_to_config(args)

    config = configparser.ConfigParser()
    config.read_dict(DEFAULTS)
    config.read_dict(args)
    config.read(args["main"]["config"])

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
