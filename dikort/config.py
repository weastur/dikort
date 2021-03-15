import configparser
import logging
import sys

from dikort.print import print_error, print_warning

_FILE_CONFIG_INT_OPTIONS = ("min_length", "max_length")
_FILE_CONFIG_BOOL_OPTIONS = (
    "length",
    "capitalized_summary",
    "trailing_period",
    "singleline_summary",
    "signoff",
    "gpg",
    "regex",
    "author_name_regex",
    "author_email_regex",
)
ERROR_EXIT_CODE = 128
FAILED_EXIT_CODE = 1
DEFAULTS = {
    "main": {
        "config": "./.dikort.cfg",
        "repository": "./",
        "range": "HEAD",
    },
    "rules": {
        "length": True,
        "capitalized_summary": True,
        "trailing_period": True,
        "singleline_summary": True,
        "signoff": False,
        "gpg": False,
        "regex": False,
        "author_name_regex": False,
        "author_email_regex": False,
    },
    "rules.settings": {
        "min_length": 10,
        "max_length": 50,
        "capitalized_summary": True,
        "trailing_period": False,
        "singleline_summary": True,
        "signoff": True,
        "gpg": True,
        "regex": ".*",
        "author_name_regex": ".*",
        "author_email_regex": ".*",
    },
    "logging": {
        "enabled": False,
        "format": "%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "level": "INFO",
    },
}


def _from_cmd_args_to_config(cmd_args):
    args_dict = vars(cmd_args)
    return {
        param: args_dict[param]
        for param in args_dict
        if args_dict[param] is not None
    }


def merge(cmd_args):
    result = DEFAULTS.copy()
    _merge_fileconfig(
        result, cmd_args["main"]["config"] or result["main"]["config"]
    )
    result.update(_from_cmd_args_to_config(cmd_args))
    _validate(result)
    return result


def _merge_fileconfig(config, file_config_path):
    file_config = configparser.ConfigParser(interpolation=None)
    config_filename = file_config_path
    try:
        with open(config_filename) as config_fp:
            file_config.read_file(config_fp)
    except OSError:
        print_error(f"Cannot open file {config_filename}")
        sys.exit(ERROR_EXIT_CODE)
    for section in config:
        if section not in file_config.sections():
            print_warning(f"Unknown config section {section}")
            continue
        for option in config[section]:
            if option not in file_config.options(section):
                print_warning(f"Unknown config option {section}:{option}")
                continue
            value = file_config[section][option]
            try:
                if option in _FILE_CONFIG_INT_OPTIONS:
                    value = file_config[section].getint(option)
                elif option in _FILE_CONFIG_BOOL_OPTIONS:
                    value = file_config[section].getboolean(option)
            except ValueError:
                print_error(f"Cannot parse option {section}:{option}")
                sys.exit(ERROR_EXIT_CODE)
            config[section][option] = value


def configure_logging(section):
    logging_config = {
        "format": section["format"],
        "level": section["level"],
        "datefmt": section["datefmt"],
    }
    if not section.getboolean("enabled"):
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
        "--regex", help="Regex to check commit message summary"
    )
    cmd_args_parser.add_argument(
        "--author-name-regex", help="Regex to check author name"
    )
    cmd_args_parser.add_argument(
        "--author-email-regex", help="Regex to check author email"
    )
    cmd_args_parser.add_argument(
        "--enable-logging",
        help="Enable logs output to stderr (default: False)",
        default=None,
        action="store_true",
    )
    cmd_args_parser.add_argument(
        "--logging-format",
        help="Format string for logging (Python style)",
    )
    cmd_args_parser.add_argument(
        "--logging-datefmt",
        help="Format string for logging datetime (Python style)",
    )
    cmd_args_parser.add_argument(
        "--logging-level",
        help="Logging level (Python style)",
    )
    cmd_args_parser.add_argument(
        "--capitalized-summary",
        default=None,
        action="store_true",
        help="Capitalized summary (default)",
    )
    cmd_args_parser.add_argument(
        "--no-capitalized-summary",
        dest="capitalized_summary",
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
        dest="trailing_period",
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
        dest="singleline_summary",
        action="store_false",
        help="Multiline summary",
    )
    cmd_args_parser.add_argument(
        "--signoff",
        default=None,
        action="store_true",
        help="Presence of signoff (default)",
    )
    cmd_args_parser.add_argument(
        "--no-signoff",
        dest="signoff",
        action="store_false",
        help="No signoff",
    )
    cmd_args_parser.add_argument(
        "--gpg",
        default=None,
        action="store_true",
        help="Presence of GPG sign (default)",
    )
    cmd_args_parser.add_argument(
        "--no-gpg",
        dest="gpg",
        action="store_false",
        help="No GPG sign",
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
        "--enable-gpg-check",
        action="store_true",
        default=None,
        help="Enable checking for GPG sign (default: False)",
    )
    cmd_args_parser.add_argument(
        "--enable-regex-check",
        action="store_true",
        default=None,
        help="Enable check by regex (default: False)",
    )
    cmd_args_parser.add_argument(
        "--enable-author-name-regex-check",
        action="store_true",
        default=None,
        help="Enable author name check by regex (default: False)",
    )
    cmd_args_parser.add_argument(
        "--enable-author-email-regex-check",
        action="store_true",
        default=None,
        help="Enable author email check by regex (default: False)",
    )
    cmd_args_parser.add_argument(
        "range", nargs="?", help="Commit range (default: HEAD)"
    )


def _validate(config):
    if (
        config["rules.settings"]["min_length"]
        > config["rules.settings"]["max_length"]
    ):
        print_error(
            "rules.settings.min_length is greater than rules.settings.max_length"
        )
        sys.exit(ERROR_EXIT_CODE)
