__copyright__ = "Copyright (C) 2014-2016  Martin Blais"
__license__ = "GNU GPLv2"

# Standard library
import unittest

# Third party
from beancount import loader
from beancount.parser import cmptest

# First party
from beancount_tb_plugins.noduplicates_extended import noduplicates_extended


class TestValidateDuplicatesExtended(cmptest.TestCase):
    def checkDuplicates(self, entries, options_map, config_str):
        _, valid_errors = noduplicates_extended.validate_no_duplicates_extended(entries, options_map, config_str)
        self.assertEqual([noduplicates_extended.CompareError], list(map(type, valid_errors)))
        self.assertRegex(valid_errors[0].message, "Duplicate entry")

    @loader.load_doc()
    def test_validate_no_duplicates__transaction(self, entries, _, options_map):
        """
        2020-12-31 open Assets:UK:Monzo:Joint GBP
            type: "Checking"
            sort_code: "04-00-04"
            account_number: "81345498"

        2007-06-07 open Expenses:Trasporti-e-viaggi:Autobus-Tram-Metropolitana EUR, GBP, SGD, PHP, HUF, JPY

        2025-01-04 * "Lothian Buses" ""
            imported_from: "api"
            location: "Edinburgh"
            country: "GBR"
            timezone: "Europe/London"
            time: "00:04"
            Expenses:Trasporti-e-viaggi:Autobus-Tram-Metropolitana  -0.2 GBP
            Assets:UK:Monzo:Joint

        2025-01-04 * "Lothian Buses" ""
            imported_from: "api"
            location: "Edinburgh"
            country: "GBR"
            timezone: "Europe/London"
            time: "00:04"
            Expenses:Trasporti-e-viaggi:Autobus-Tram-Metropolitana  -0.2 GBP
            Assets:UK:Monzo:Joint
        """
        self.checkDuplicates(entries, options_map, "{'include_meta': ['time']}")


if __name__ == "__main__":
    unittest.main()
