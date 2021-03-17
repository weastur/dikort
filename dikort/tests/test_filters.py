import re
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
        self.config = {}

    def test_singleline(self):
        self.commit.summary = "Singleline summary\n"
        self.config["singleline_summary"] = True
        self.assertFalse(filter_singleline(self.commit, config=self.config))
        self.config["singleline_summary"] = False
        self.assertTrue(filter_singleline(self.commit, config=self.config))

        self.commit.summary = "Multiline summary\nAnother line\n"
        self.config["singleline_summary"] = True
        self.assertTrue(filter_singleline(self.commit, config=self.config))
        self.config["singleline_summary"] = False
        self.assertFalse(filter_singleline(self.commit, config=self.config))

    def test_trailing_period(self):
        self.commit.summary = "No trailing period summary\n"
        self.config["trailing_period"] = False
        self.assertFalse(filter_trailing_period(self.commit, config=self.config))
        self.config["trailing_period"] = True
        self.assertTrue(filter_trailing_period(self.commit, config=self.config))

        self.commit.summary = "Trailing period summary\n"
        self.config["trailing_period"] = False
        self.assertFalse(filter_trailing_period(self.commit, config=self.config))
        self.config["trailing_period"] = True
        self.assertTrue(filter_trailing_period(self.commit, config=self.config))

    def test_capitalized_summary(self):
        self.commit.summary = "Capitalized summary\n"
        self.config["capitalized_summary"] = True
        self.assertFalse(filter_capitalized(self.commit, config=self.config))
        self.config["capitalized_summary"] = False
        self.assertTrue(filter_capitalized(self.commit, config=self.config))

        self.commit.summary = "not capitalized summary\n"
        self.config["capitalized_summary"] = False
        self.assertFalse(filter_capitalized(self.commit, config=self.config))
        self.config["capitalized_summary"] = True
        self.assertTrue(filter_capitalized(self.commit, config=self.config))

        self.commit.summary = "[special case] not capitalized summary\n"
        self.config["capitalized_summary"] = True
        self.assertFalse(filter_capitalized(self.commit, config=self.config))

    def test_lentgh(self):
        self.commit.summary = 5 * "A"
        self.config["max_length"] = 100

        self.config["min_length"] = 10
        self.assertTrue(filter_length(self.commit, config=self.config))
        self.config["min_length"] = 4
        self.assertFalse(filter_length(self.commit, config=self.config))

        self.config["max_length"] = 4
        self.assertTrue(filter_length(self.commit, config=self.config))
        self.config["max_length"] = 5
        self.assertFalse(filter_length(self.commit, config=self.config))

    def test_signoff(self):
        self.commit.message = "My Awesome commit\n" "Fixed all bugs.\n" "Signed-off-by: Neo\n"
        self.config["signoff"] = True
        self.assertFalse(filter_signoff(self.commit, config=self.config))
        self.config["signoff"] = False
        self.assertTrue(filter_signoff(self.commit, config=self.config))

        self.commit.message = "My Awesome commit\n" "Fixed all bugs.\n"
        self.config["signoff"] = False
        self.assertFalse(filter_signoff(self.commit, config=self.config))
        self.config["signoff"] = True
        self.assertTrue(filter_signoff(self.commit, config=self.config))

    def test_gpg(self):
        self.commit.gpgsig = "GPG-SIGNATURE"
        self.config["gpg"] = True
        self.assertFalse(filter_gpg(self.commit, config=self.config))
        self.config["gpg"] = False
        self.assertTrue(filter_gpg(self.commit, config=self.config))

        self.commit.gpgsig = ""
        self.config["gpg"] = False
        self.assertFalse(filter_gpg(self.commit, config=self.config))
        self.config["gpg"] = True
        self.assertTrue(filter_gpg(self.commit, config=self.config))

    def test_regex(self):
        self.config["regex"] = re.compile(r"DEV-\d+: \w+")

        self.commit.summary = "DEV-123: my super fixes"
        self.assertFalse(filter_regex(self.commit, config=self.config))
        self.commit.summary = "OOPS-123: my super fixes"
        self.assertTrue(filter_regex(self.commit, config=self.config))

    def test_author_name_regex(self):
        self.config["author_name_regex"] = re.compile(r"\w+ \w+")

        self.commit.author.name = "Pavel Sapezhko"
        self.assertFalse(filter_author_name_regex(self.commit, config=self.config))
        self.commit.author.name = "Pavel"
        self.assertTrue(filter_author_name_regex(self.commit, config=self.config))

    def test_author_email_regex(self):
        self.config["author_email_regex"] = re.compile(r"\w+@example.com")

        self.commit.author.email = "neo@example.com"
        self.assertFalse(filter_author_email_regex(self.commit, config=self.config))
        self.commit.author.email = "neo@matrix.com"
        self.assertTrue(filter_author_email_regex(self.commit, config=self.config))
