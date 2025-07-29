__copyright__ = "Copyright (C) 2014-2016  Martin Blais"
__license__ = "GNU GPLv2"

# Standard library

# Third party
from beancount import loader
from beancount.core import data
from beancount.parser import cmptest

# First party
from beancount_tb_plugins.noduplicates_extended import noduplicates_extended


class TestValidateDuplicatesExtended(cmptest.TestCase):
    def checkDuplicates(self, entries, options_map, config_str):
        _, valid_errors = noduplicates_extended.validate_no_duplicates_extended(entries, options_map, config_str)
        self.assertEqual([noduplicates_extended.CompareError], list(map(type, valid_errors)))
        self.assertRegex(valid_errors[0].message, "Duplicate entry")

    @loader.load_doc()
    def test_validate_no_duplicates__transaction(
        self, entries: data.Directives, _: list[data.BeancountError], options_map: loader.OptionsMap
    ):
        """
        2014-01-01 open Assets:Investments:Stock
        2014-01-01 open Assets:Investments:Cash

        2014-06-24 * "Go negative from zero"
          paid_by: "Angelo"
          Assets:Investments:Stock    1 HOOL {500 USD}
          Assets:Investments:Cash  -500 USD

        2014-06-24 * "Go negative from zero"
          paid_by: "Angelo"
          Assets:Investments:Stock    1 HOOL {500 USD}
          Assets:Investments:Cash  -500 USD
        """
        self.checkDuplicates(entries, options_map, "{'include_meta': ['paid_by']}")
