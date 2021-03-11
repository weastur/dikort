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


def from_cmd_args_to_config(cmd_args):
    args_dict = vars(cmd_args)
    return {
        "main": args_dict,
    }


def parse(cmd_args):
    cmd_args = from_cmd_args_to_config(cmd_args)

    config = configparser.ConfigParser()
    config.read_dict(DEFAULTS)
    config.read(cmd_args["main"]["config"])
    config.read_dict(cmd_args)

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
