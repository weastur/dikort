import argparse
import configparser
import logging
import sys

from dikort.print import print_error

DEFAULTS = {
    "main": {
        "config": "./.dikort.cfg",
        "repository": "./",
        "range": "HEAD",
    },
    "rules": {
        "length": True,
        "capitalized-summary": True,
        "trailing-period": True,
        "singleline-summary": True,
        "signoff": False,
    },
    "rules.settings": {
        "min-length": 10,
        "max-length": 50,
        "capitalized-summary": True,
        "trailing-period": False,
        "singleline-summary": True,
        "signoff": True,
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
    cmd_args_parsed = {
        "rules": {
            "length": args_dict["enable_length_check"],
            "capitalized-summary": args_dict[
                "enable_capitalized_summary_check"
            ],
            "trailing-period": args_dict["enable_trailing_period_check"],
            "singleline-summary": args_dict["enable_singleline_summary_check"],
        },
        "rules.settings": {
            "min-length": args_dict["min_length"],
            "max-length": args_dict["max_length"],
            "capitalized-summary": args_dict["capitalized_summary"],
            "trailing-period": args_dict["trailing_period"],
            "singleline-summary": args_dict["singleline_summary"],
        },
        "main": {
            "config": args_dict["config"],
            "repository": args_dict["repository"],
            "range": args_dict["range"],
        },
    }
    cmd_args = {}
    for section in cmd_args_parsed:
        cmd_args[section] = {}
        for param in cmd_args_parsed[section]:
            if cmd_args_parsed[section][param] is not None:
                cmd_args[section][param] = cmd_args_parsed[section][param]
    return cmd_args


def parse(cmd_args):
    cmd_args = from_cmd_args_to_config(cmd_args)

    config = configparser.ConfigParser()
    config.read_dict(DEFAULTS)
    config_filename = config["main"]["config"]
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
        "-c", "--config", help="Config file location (default: ./.dikort.cfg"
    )
    cmd_args_parser.add_argument(
        "-r", "--repository", help="Repository location (default: ./)"
    )
    cmd_args_parser.add_argument(
        "--min-length", type=int, help="Minimum commit length (default: 10)"
    )
    cmd_args_parser.add_argument(
        "--max-length", type=int, help="Maximum commit length (default: 50)"
    )
    cmd_args_parser.add_argument(
        "--capitalized-summary",
        default=None,
        action="store_true",
        help="Capitalized summary (default)",
    )
    cmd_args_parser.add_argument(
        "--no-capitalized-summary",
        dest="capitalized-summary",
        action="store_false",
        help="Not capitalized summary",
    )
    cmd_args_parser.add_argument(
        "--trailing-period",
        default=None,
        action="store_true",
        help="Presence of trailing period",
    )
    cmd_args_parser.add_argument(
        "--no-trailing-period",
        dest="trailing-period",
        action="store_false",
        help="No trailing period (default)",
    )
    cmd_args_parser.add_argument(
        "--singleline-summary",
        default=None,
        action="store_true",
        help="Singleline summary (default)",
    )
    cmd_args_parser.add_argument(
        "--no-singleline-summary",
        dest="singleline-summary",
        action="store_false",
        help="Multiline summary",
    )
    cmd_args_parser.add_argument(
        "--signoff",
        default=None,
        action="store_true",
        help="Presence of signoff",
    )
    cmd_args_parser.add_argument(
        "--no-signoff",
        dest="signoff",
        action="store_false",
        help="No signoff (default)",
    )
    cmd_args_parser.add_argument(
        "--enable-length-check",
        action="store_true",
        default=None,
        help="Enable length check (default: True)",
    )
    cmd_args_parser.add_argument(
        "--enable-capitalized-summary-check",
        action="store_true",
        default=None,
        help="Enable capitalized summary check (default: True)",
    )
    cmd_args_parser.add_argument(
        "--enable-trailing-period-check",
        action="store_true",
        default=None,
        help="Enable trailing period check (default: True)",
    )
    cmd_args_parser.add_argument(
        "--enable-singleline-summary-check",
        action="store_true",
        default=None,
        help="Enable single line summary check (default: True)",
    )
    cmd_args_parser.add_argument(
        "--enable-signoff-check",
        action="store_true",
        default=None,
        help="Enable checking for signoff (default: False)",
    )
    cmd_args_parser.add_argument(
        "range", nargs="?", help="Commit range (default: HEAD)"
    )
