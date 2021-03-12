import configparser
import logging
import sys

from dikort.print import print_error

NON_CMDLINE_DEFAULTS = {
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
    config.read_dict(NON_CMDLINE_DEFAULTS)
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
        "--min-length", type=int, help="Minimum commit length (default: 10)"
    )
    cmd_args_parser.add_argument(
        "--max-length", type=int, help="Maximum commit length (default: 50)"
    )
    cmd_args_parser.add_argument(
        "--capitalized-summary",
        type=bool,
        help="Is summary message capitalized? (default: True)",
    )
    cmd_args_parser.add_argument(
        "--trailing-period",
        type=bool,
        help="There is trailing period? (default: False)",
    )
    cmd_args_parser.add_argument(
        "--singleline-summary",
        type=bool,
        help="Is summary single-line? (default: True)",
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
        "range", nargs="?", default="HEAD", help="Commit range"
    )
