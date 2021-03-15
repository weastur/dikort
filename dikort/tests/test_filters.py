import configparser
from unittest import TestCase
from unittest.mock import Mock

from dikort.filters import (
    filter_author_email_regex,
    filter_author_name_regex,
    filter_capitalized,
    filter_gpg,
    filter_length,
    filter_regex,
    filter_signoff,
    filter_singleline,
    filter_trailing_period,
)


class TestFilters(TestCase):
    def setUp(self):
        self.commit = Mock()
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.add_section("rules.settings")

    def test_singleline(self):
        self.commit.summary = "Singleline summary\n"
        self.config["rules.settings"]["singleline-summary"] = "yes"
        self.assertFalse(filter_singleline(self.commit, config=self.config))
        self.config["rules.settings"]["singleline-summary"] = "no"
        self.assertTrue(filter_singleline(self.commit, config=self.config))

        self.commit.summary = "Multiline summary\nAnother line\n"
        self.config["rules.settings"]["singleline-summary"] = "yes"
        self.assertTrue(filter_singleline(self.commit, config=self.config))
        self.config["rules.settings"]["singleline-summary"] = "no"
        self.assertFalse(filter_singleline(self.commit, config=self.config))

    def test_trailing_period(self):
        self.commit.summary = "No trailing period summary\n"
        self.config["rules.settings"]["trailing-period"] = "no"
        self.assertFalse(
            filter_trailing_period(self.commit, config=self.config)
        )
        self.config["rules.settings"]["trailing-period"] = "yes"
        self.assertTrue(
            filter_trailing_period(self.commit, config=self.config)
        )

        self.commit.summary = "Trailing period summary\n"
        self.config["rules.settings"]["trailing-period"] = "no"
        self.assertFalse(
            filter_trailing_period(self.commit, config=self.config)
        )
        self.config["rules.settings"]["trailing-period"] = "yes"
        self.assertTrue(
            filter_trailing_period(self.commit, config=self.config)
        )

    def test_capitalized_summary(self):
        self.commit.summary = "Capitalized summary\n"
        self.config["rules.settings"]["capitalized-summary"] = "yes"
        self.assertFalse(filter_capitalized(self.commit, config=self.config))
        self.config["rules.settings"]["capitalized-summary"] = "no"
        self.assertTrue(filter_capitalized(self.commit, config=self.config))

        self.commit.summary = "not capitalized summary\n"
        self.config["rules.settings"]["capitalized-summary"] = "no"
        self.assertFalse(filter_capitalized(self.commit, config=self.config))
        self.config["rules.settings"]["capitalized-summary"] = "yes"
        self.assertTrue(filter_capitalized(self.commit, config=self.config))

        self.commit.summary = "[special case] not capitalized summary\n"
        self.config["rules.settings"]["capitalized-summary"] = "yes"
        self.assertFalse(filter_capitalized(self.commit, config=self.config))

    def test_lentgh(self):
        self.commit.summary = 5 * "A"
        self.config["rules.settings"]["max-length"] = "100"

        self.config["rules.settings"]["min-length"] = "10"
        self.assertTrue(filter_length(self.commit, config=self.config))
        self.config["rules.settings"]["min-length"] = "4"
        self.assertFalse(filter_length(self.commit, config=self.config))

        self.config["rules.settings"]["max-length"] = "4"
        self.assertTrue(filter_length(self.commit, config=self.config))
        self.config["rules.settings"]["max-length"] = "5"
        self.assertFalse(filter_length(self.commit, config=self.config))

    def test_signoff(self):
        self.commit.message = (
            "My Awesome commit\n" "Fixed all bugs.\n" "Signed-off-by: Neo\n"
        )
        self.config["rules.settings"]["signoff"] = "yes"
        self.assertFalse(filter_signoff(self.commit, config=self.config))
        self.config["rules.settings"]["signoff"] = "no"
        self.assertTrue(filter_signoff(self.commit, config=self.config))

        self.commit.message = "My Awesome commit\n" "Fixed all bugs.\n"
        self.config["rules.settings"]["signoff"] = "no"
        self.assertFalse(filter_signoff(self.commit, config=self.config))
        self.config["rules.settings"]["signoff"] = "yes"
        self.assertTrue(filter_signoff(self.commit, config=self.config))

    def test_gpg(self):
        self.commit.gpgsig = "GPG-SIGNATURE"
        self.config["rules.settings"]["gpg"] = "yes"
        self.assertFalse(filter_gpg(self.commit, config=self.config))
        self.config["rules.settings"]["gpg"] = "no"
        self.assertTrue(filter_gpg(self.commit, config=self.config))

        self.commit.gpgsig = ""
        self.config["rules.settings"]["gpg"] = "no"
        self.assertFalse(filter_gpg(self.commit, config=self.config))
        self.config["rules.settings"]["gpg"] = "yes"
        self.assertTrue(filter_gpg(self.commit, config=self.config))

    def test_regex(self):
        self.config["rules.settings"]["regex"] = r"DEV-\d+: \w+"

        self.commit.summary = "DEV-123: my super fixes"
        self.assertFalse(filter_regex(self.commit, config=self.config))
        self.commit.summary = "OOPS-123: my super fixes"
        self.assertTrue(filter_regex(self.commit, config=self.config))

    def test_author_name_regex(self):
        self.config["rules.settings"]["author-name-regex"] = r"\w+ \w+"

        self.commit.author.name = "Pavel Sapezhko"
        self.assertFalse(
            filter_author_name_regex(self.commit, config=self.config)
        )
        self.commit.author.name = "Pavel"
        self.assertTrue(
            filter_author_name_regex(self.commit, config=self.config)
        )

    def test_author_email_regex(self):
        self.config["rules.settings"]["author-email-regex"] = r"\w+@example.com"

        self.commit.author.email = "neo@example.com"
        self.assertFalse(
            filter_author_email_regex(self.commit, config=self.config)
        )
        self.commit.author.email = "neo@matrix.com"
        self.assertTrue(
            filter_author_email_regex(self.commit, config=self.config)
        )
