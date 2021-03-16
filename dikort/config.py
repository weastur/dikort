import configparser
import re
import sys

from dikort.print import print_error, print_warning

_FILE_CONFIG_INT_OPTIONS = ("min_length", "max_length")
_FILE_CONFIG_BOOL_OPTIONS = (
    "enable_length",
    "enable_capitalized_summary",
    "enable_trailing_period",
    "enable_singleline_summary",
    "enable_signoff",
    "enable_gpg",
    "enable_regex",
    "enable_author_name_regex",
    "enable_author_email_regex",
    "capitalized_summary",
    "trailing_period",
    "singleline_summary",
    "signoff",
    "gpg",
    "enabled",
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
    "merge_rules": {
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
    "merge_rules.settings": {
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
    filtered_dict = {
        param: args_dict[param]
        for param in args_dict
        if args_dict[param] is not None
    }
    result = {}
    for option in filtered_dict:
        section, param = option.split(":")
        result.setdefault(section, {})[param] = filtered_dict[option]
    return result


def merge(cmd_args):
    result = DEFAULTS.copy()
    _merge_fileconfig(result, vars(cmd_args)["main:config"] or result["main"]["config"])
    config_from_cmdline = _from_cmd_args_to_config(cmd_args)
    for section in result:
        if section not in config_from_cmdline:
            continue
        result[section].update(config_from_cmdline[section])
    result.update()
    _validate(result)
    _post_processing(result)
    return result


def _merge_fileconfig(config, file_config_path):
    file_config = configparser.ConfigParser(interpolation=None)
    _read_file_config(file_config, file_config_path)
    for section in config:
        if section not in file_config.sections():
            continue
        for option in config[section]:
            if option not in file_config.options(section):
                continue
            config[section][option] = _parse_value_from_file(
                file_config, option, section
            )


def _parse_value_from_file(file_config, option, section):
    value = file_config[section][option]
    try:
        if option in _FILE_CONFIG_INT_OPTIONS:
            value = file_config[section].getint(option)
        elif option in _FILE_CONFIG_BOOL_OPTIONS:
            value = file_config[section].getboolean(option)
    except ValueError:
        print_error(f"Cannot parse option {section}:{option}")
        sys.exit(ERROR_EXIT_CODE)
    return value


def _read_file_config(file_config, file_config_path):
    config_filename = file_config_path
    try:
        with open(config_filename) as config_fp:
            file_config.read_file(config_fp)
    except FileNotFoundError:
        if file_config_path != DEFAULTS["main"]["config"]:
            print_error(f"Cannot open file {config_filename}")
            sys.exit(ERROR_EXIT_CODE)
    except OSError:
        print_error(f"Cannot open file {config_filename}")
        sys.exit(ERROR_EXIT_CODE)


def _validate(config):
    if (
        config["rules.settings"]["min_length"]
        > config["rules.settings"]["max_length"]
    ):
        print_error(
            "rules.settings.min_length is greater than rules.settings.max_length"
        )
        sys.exit(ERROR_EXIT_CODE)


def _post_processing(config):
    config["rules.settings"]["regex"] = re.compile(
        config["rules.settings"]["regex"]
    )
    config["rules.settings"]["author_name_regex"] = re.compile(
        config["rules.settings"]["author_name_regex"]
    )
    config["rules.settings"]["author_email_regex"] = re.compile(
        config["rules.settings"]["author_email_regex"]
    )


def configure_argparser(cmd_args_parser):
    cmd_args_parser.add_argument(
        "-c",
        "--config",
        dest="main:config",
        help=f"Config file location (default: {DEFAULTS['main']['config']}",
    )
    cmd_args_parser.add_argument(
        "-r",
        "--repository",
        dest="main:repository",
        help=f"Repository location (default: {DEFAULTS['main']['repository']})",
    )
    cmd_args_parser.add_argument(
        "--enable-logging",
        dest="logging:enabled",
        help=f"Enable logs output to stderr (default: {DEFAULTS['logging']['enabled']})",
        default=None,
        action="store_true",
    )
    cmd_args_parser.add_argument(
        "--logging-format",
        dest="logging:format",
        help="Format string for logging (Python style)",
    )
    cmd_args_parser.add_argument(
        "--logging-datefmt",
        dest="logging:datefmt",
        help="Format string for logging datetime (Python style)",
    )
    cmd_args_parser.add_argument(
        "--logging-level",
        dest="logging:level",
        help="Logging level (Python style)",
    )
    cmd_args_parser.add_argument(
        "--min-length",
        dest="rules.settings:min_length",
        type=int,
        help=f"Minimum commit length (default: {DEFAULTS['rules.settings']['min_length']})",
    )
    cmd_args_parser.add_argument(
        "--max-length",
        dest="rules.settings:max_length",
        type=int,
        help=f"Maximum commit length (default: {DEFAULTS['rules.settings']['max_length']})",
    )
    cmd_args_parser.add_argument(
        "--regex",
        help="Regex to check commit message summary",
        dest="rules.settings:regex",
    )
    cmd_args_parser.add_argument(
        "--author-name-regex",
        help="Regex to check author name",
        dest="rules.settings:author_name_regex",
    )
    cmd_args_parser.add_argument(
        "--author-email-regex",
        help="Regex to check author email",
        dest="rules.settings:author_email_regex",
    )
    cmd_args_parser.add_argument(
        "--capitalized-summary",
        default=None,
        dest="rules.settings:capitalized_summary",
        action="store_true",
        help=f"Capitalized summary (default: {DEFAULTS['rules.settings']['capitalized_summary']})",
    )
    cmd_args_parser.add_argument(
        "--no-capitalized-summary",
        dest="rules.settings:capitalized_summary",
        action="store_false",
        help="Not capitalized summary",
    )
    cmd_args_parser.add_argument(
        "--trailing-period",
        default=None,
        dest="rules.settings:trailing_period",
        action="store_true",
        help="Presence of trailing period",
    )
    cmd_args_parser.add_argument(
        "--no-trailing-period",
        dest="rules.settings:trailing_period",
        action="store_false",
        help=f"No trailing period (default: {DEFAULTS['rules.settings']['trailing_period']})",
    )
    cmd_args_parser.add_argument(
        "--singleline-summary",
        default=None,
        dest="rules.settings:singleline_summary",
        action="store_true",
        help=f"Singleline summary (default: {DEFAULTS['rules.settings']['singleline_summary']})",
    )
    cmd_args_parser.add_argument(
        "--no-singleline-summary",
        dest="rules.settings:singleline_summary",
        action="store_false",
        help="Multiline summary",
    )
    cmd_args_parser.add_argument(
        "--signoff",
        default=None,
        dest="rules.settings:signoff",
        action="store_true",
        help=f"Presence of signoff (default: {DEFAULTS['rules.settings']['signoff']})",
    )
    cmd_args_parser.add_argument(
        "--no-signoff",
        dest="rules.settings:signoff",
        action="store_false",
        help="No signoff",
    )
    cmd_args_parser.add_argument(
        "--gpg",
        default=None,
        dest="rules.settings:gpg",
        action="store_true",
        help=f"Presence of GPG sign (default: {DEFAULTS['rules.settings']['gpg']})",
    )
    cmd_args_parser.add_argument(
        "--no-gpg",
        dest="rules.settings:gpg",
        action="store_false",
        help="No GPG sign",
    )
    cmd_args_parser.add_argument(
        "--enable-length-check",
        action="store_true",
        dest="rules:length",
        default=None,
        help=f"Enable length check (default: {DEFAULTS['rules']['length']})",
    )
    cmd_args_parser.add_argument(
        "--enable-capitalized-summary-check",
        action="store_true",
        dest="rules:capitalized_summary",
        default=None,
        help=f"Enable capitalized summary check (default: {DEFAULTS['rules']['capitalized_summary']})",
    )
    cmd_args_parser.add_argument(
        "--enable-trailing-period-check",
        action="store_true",
        dest="rules:trailing_period",
        default=None,
        help=f"Enable trailing period check (default: {DEFAULTS['rules']['trailing_period']})",
    )
    cmd_args_parser.add_argument(
        "--enable-singleline-summary-check",
        action="store_true",
        dest="rules:singleline_summary",
        default=None,
        help=f"Enable single line summary check (default: {DEFAULTS['rules']['singleline_summary']})",
    )
    cmd_args_parser.add_argument(
        "--enable-signoff-check",
        action="store_true",
        dest="rules:signoff",
        default=None,
        help=f"Enable checking for signoff (default: {DEFAULTS['rules']['signoff']})",
    )
    cmd_args_parser.add_argument(
        "--enable-gpg-check",
        action="store_true",
        dest="rules:gpg",
        default=None,
        help=f"Enable checking for GPG sign (default: {DEFAULTS['rules']['gpg']})",
    )
    cmd_args_parser.add_argument(
        "--enable-regex-check",
        action="store_true",
        dest="rules:regex",
        default=None,
        help=f"Enable check by regex (default: {DEFAULTS['rules']['regex']})",
    )
    cmd_args_parser.add_argument(
        "--enable-author-name-regex-check",
        action="store_true",
        dest="rules:author_name_regex",
        default=None,
        help=f"Enable author name check by regex (default: {DEFAULTS['rules']['author_name_regex']})",
    )
    cmd_args_parser.add_argument(
        "--enable-author-email-regex-check",
        action="store_true",
        dest="rules:author_email_regex",
        default=None,
        help=f"Enable author email check by regex (default: {DEFAULTS['rules']['author_email_regex']})",
    )
    cmd_args_parser.add_argument(
        "--merge-min-length",
        type=int,
        dest="merge_rules.settings:min_length",
        help=f"Minimum commit length (default: {DEFAULTS['merge_rules.settings']['min_length']})",
    )
    cmd_args_parser.add_argument(
        "--merge-max-length",
        type=int,
        dest="merge_rules.settings:max_length",
        help=f"Maximum commit length (default: {DEFAULTS['merge_rules.settings']['max_length']})",
    )
    cmd_args_parser.add_argument(
        "--merge-regex",
        help="Regex to check commit message summary",
        dest="merge_rules.settings:regex",
    )
    cmd_args_parser.add_argument(
        "--merge-author-name-regex",
        help="Regex to check author name",
        dest="merge_rules.settings:author_name_regex",
    )
    cmd_args_parser.add_argument(
        "--merge-author-email-regex",
        help="Regex to check author email",
        dest="merge_rules.settings:author_email_regex",
    )
    cmd_args_parser.add_argument(
        "--merge-capitalized-summary",
        default=None,
        action="store_true",
        dest="merge_rules.settings:capitalized_summary",
        help=f"Capitalized summary (default: {DEFAULTS['merge_rules.settings']['capitalized_summary']})",
    )
    cmd_args_parser.add_argument(
        "--no-merge-capitalized-summary",
        dest="merge_rules.settings:capitalized_summary",
        action="store_false",
        help="Not capitalized summary",
    )
    cmd_args_parser.add_argument(
        "--merge-trailing-period",
        default=None,
        dest="merge_rules.settings:trailing_period",
        action="store_true",
        help="Presence of trailing period",
    )
    cmd_args_parser.add_argument(
        "--no-merge-trailing-period",
        dest="merge_rules.settings:trailing_period",
        action="store_false",
        help=f"No trailing period (default: {DEFAULTS['merge_rules.settings']['trailing_period']})",
    )
    cmd_args_parser.add_argument(
        "--merge-singleline-summary",
        default=None,
        action="store_true",
        dest="merge_rules.settings:singleline_summary",
        help=f"Singleline summary (default: {DEFAULTS['merge_rules.settings']['singleline_summary']})",
    )
    cmd_args_parser.add_argument(
        "--no-merge-singleline-summary",
        dest="merge_rules.settings:singleline_summary",
        action="store_false",
        help="Multiline summary",
    )
    cmd_args_parser.add_argument(
        "--merge-signoff",
        default=None,
        dest="merge_rules.settings:signoff",
        action="store_true",
        help=f"Presence of signoff (default: {DEFAULTS['merge_rules.settings']['signoff']})",
    )
    cmd_args_parser.add_argument(
        "--no-merge-signoff",
        dest="merge_rules.settings:signoff",
        action="store_false",
        help="No signoff",
    )
    cmd_args_parser.add_argument(
        "--merge-gpg",
        default=None,
        action="store_true",
        dest="merge_rules.settings:gpg",
        help=f"Presence of GPG sign (default: {DEFAULTS['merge_rules.settings']['gpg']})",
    )
    cmd_args_parser.add_argument(
        "--no-merge-gpg",
        dest="merge_rules.settings:gpg",
        action="store_false",
        help="No GPG sign",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-length-check",
        action="store_true",
        default=None,
        dest="merge_rules:length",
        help=f"Enable length check (default: {DEFAULTS['merge_rules']['length']})",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-capitalized-summary-check",
        action="store_true",
        default=None,
        dest="merge_rules:capitalized_summary",
        help=f"Enable capitalized summary check (default: {DEFAULTS['merge_rules']['capitalized_summary']})",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-trailing-period-check",
        action="store_true",
        default=None,
        dest="merge_rules:trailing_period",
        help=f"Enable trailing period check (default: {DEFAULTS['merge_rules']['trailing_period']})",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-singleline-summary-check",
        action="store_true",
        default=None,
        dest="merge_rules:singleline_summary",
        help=f"Enable single line summary check (default: {DEFAULTS['merge_rules']['singleline_summary']})",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-signoff-check",
        action="store_true",
        default=None,
        dest="merge_rules:signoff",
        help=f"Enable checking for signoff (default: {DEFAULTS['merge_rules']['signoff']})",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-gpg-check",
        action="store_true",
        default=None,
        dest="merge_rules:gpg",
        help=f"Enable checking for GPG sign (default: {DEFAULTS['merge_rules']['gpg']})",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-regex-check",
        action="store_true",
        default=None,
        dest="merge_rules:regex",
        help=f"Enable check by regex (default: {DEFAULTS['merge_rules']['regex']})",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-author-name-regex-check",
        action="store_true",
        default=None,
        dest="merge_rules:author_name_regex",
        help=f"Enable author name check by regex (default: {DEFAULTS['merge_rules']['author_name_regex']})",
    )
    cmd_args_parser.add_argument(
        "--enable-merge-author-email-regex-check",
        action="store_true",
        default=None,
        dest="merge_rules:author_email_regex",
        help=f"Enable author email check by regex (default: {DEFAULTS['merge_rules']['author_email_regex']})",
    )
    cmd_args_parser.add_argument(
        "main:range",
        nargs="?",
        metavar="range",
        help=f"Commit range (default: {DEFAULTS['main']['range']})",
    )
