import configparser
import logging
import sys

from dikort.print import print_error

DEFAULTS = {
    "main": {
        "config": "./dikort.cfg",
        "repository": "./",
        "range": "HEAD",
    },
    "rules": {
        "min-length": 10,
        "max-length": 50,
        "capitalized-summary": True,
        "trailing-period": False,
        "singleline-summary": True,
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
        sys.exit(128)
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


def configure_argparser(cmd_args_parser):
    cmd_args_parser.add_argument(
        "-c", "--config", default="./.dikort.cfg", help="Config file location"
    )
    cmd_args_parser.add_argument(
        "-r", "--repository", default="./", help="Repository location"
    )
    cmd_args_parser.add_argument(
        "--min-length", default=10, type=int, help="Minimum commit length"
    )
    cmd_args_parser.add_argument(
        "--max-length", default=50, type=int, help="Maximum commit length"
    )
    cmd_args_parser.add_argument(
        "--capitalized-summary",
        default=True,
        type=bool,
        help="Check is summary message capitalized",
    )
    cmd_args_parser.add_argument(
        "--trailing-period",
        default=False,
        type=bool,
        help="Check for trailing period",
    )
    cmd_args_parser.add_argument(
        "--singleline-summary",
        default=True,
        type=bool,
        help="Check if summary is single-line",
    )
    cmd_args_parser.add_argument(
        "range", nargs="?", default="HEAD", help="Commit range"
    )
