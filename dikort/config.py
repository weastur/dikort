import configparser
import logging
import sys

from dikort.print import print_error

DEFAULTS = {
    "main": {
        "config": "./dikort.cfg",
        "repository": "./",
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
    config_filename = cmd_args["main"]["config"]
    try:
        with open(config_filename) as config_fp:
            config.read_file(config_fp)
    except OSError:
        print_error(f"Cannot open file {config_filename}")
        sys.exit(1)
    config.read_dict(cmd_args)
    print(config["main"]["config"])

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
