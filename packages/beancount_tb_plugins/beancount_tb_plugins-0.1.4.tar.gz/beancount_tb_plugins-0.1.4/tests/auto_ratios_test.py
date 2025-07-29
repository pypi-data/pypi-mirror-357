# Third party

# Standard library
from datetime import datetime

# Third party
import pytest

from beancount import loader
from beancount.core.data import Custom, Entries, Transaction
from beancount.parser import cmptest
from beancount.parser.cmptest import read_string_or_entries

# First party
from auto_ratios import DEFAULT_RATIO_KEY, Config, parse_ratio


def lookup_value_by_date(input_datetime, custom_instances):
    """
    Takes a datetime object and returns the first value from the matching Custom instance.

    Args:
        input_datetime: datetime object to search for
        custom_instances: list of Custom instances

    Returns:
        The first element of the values list from the matching instance, or None if no match
    """
    # Convert datetime to date for comparison
    input_date = input_datetime.date() if isinstance(input_datetime, datetime) else input_datetime

    for instance in custom_instances:
        start_date = instance.date

        # Check if values list has more than one element
        if len(instance.values) > 1:
            # Second element contains the end date as a string
            end_date_str = instance.values[1].value
            # Convert string date (YYYYMMDD) to date object
            end_date = datetime.strptime(end_date_str, "%Y%m%d").date()

            # Check if input date is in range [start_date, end_date]
            if start_date <= input_date <= end_date:
                return instance.values[0].value
        else:
            # Only one element, check if input date is >= start_date
            if input_date >= start_date:
                return instance.values[0].value

    return None


class AutoRatios(cmptest.TestCase):
    @loader.load_doc()
    def test_it_should_store_new_ratios(self, entries, errors, options_map):
        """
        2020-12-31 open Assets:UK:Monzo:Joint GBP
        2020-12-31 open Assets:Partner:Expenses GBP

        2007-06-06 open Expenses:Abitazione GBP
        2007-06-28 open Expenses:Alimentari GBP
        2007-06-28 open Expenses:Trasporti-e-viaggi:Taxi GBP, JPY

        2023-01-01 custom "Ratio" 0.58 "20231231"
        2024-01-01 custom "Ratio" 0.70

        2023-02-28 * "Tesco" ""
          Expenses:Alimentari                           0.30 * 10.00 GBP
          Expenses:Abitazione                           0.30 * 10.00 GBP
          Assets:UK:Monzo:Joint                       -20.00 GBP
          Assets:Partner:Expenses                       0.70 * 20.00 GBP

        2024-01-25 * "Waitrose" ""
          Expenses:Alimentari                           0.30 * 20.00 GBP
          Expenses:Abitazione                            0.30 * 5.00 GBP
          Assets:UK:Monzo:Joint                       -25.00 GBP
          Assets:Partner:Expenses                       0.70 * 25.00 GBP

        2024-09-04 * "Uber" "" #Holiday-JPN-2024
          imported_from: "api"
          id: "tx_0000AleaYRwOr80PGgDQwL"
          country: "NLD"
          paid_by: "Angelo"
          full_amount: "1444 JPY"
          timezone: "Europe/Amsterdam"
          time: "10:09"
          Expenses:Trasporti-e-viaggi:Taxi   1011 JPY @ 0.0052631579 GBP
          Assets:UK:Monzo:Joint             -7.60 GBP
          Assets:Partner:Expenses           2.28 GBP

        plugin "beancount_tatablack_plugins.auto_ratios" "{
            'shared_accounts': ['Assets:UK:Monzo:Joint', 'Assets:UK:Octopus:Cash'],
            'partner_account': 'Assets:Partner:Expenses',
            'ratio_metadata_key': 'ratio'
        }"
        """

        expected_entries: Entries = read_string_or_entries(
            """
            2020-12-31 open Assets:UK:Monzo:Joint GBP
            2020-12-31 open Assets:Partner:Expenses GBP
    
            2007-06-06 open Expenses:Abitazione GBP
            2007-06-28 open Expenses:Alimentari GBP
            2007-06-28 open Expenses:Trasporti-e-viaggi:Taxi GBP, JPY
    
            2023-01-01 custom "Ratio" 0.58 "20231231"
            2024-01-01 custom "Ratio" 0.70
    
            2023-02-28 * "Tesco" ""
              Expenses:Alimentari                           0.30 * 10.00 GBP
                ratio: 0.58
              Expenses:Abitazione                           0.30 * 10.00 GBP
                ratio: 0.58
              Assets:UK:Monzo:Joint                       -20.00 GBP
              Assets:Partner:Expenses                     0.70 * 20.00 GBP
    
            2024-01-25 * "Waitrose" ""
              Expenses:Alimentari                           0.30 * 20.00 GBP
                ratio: 0.70
              Expenses:Abitazione                            0.30 * 5.00 GBP
                ratio: 0.70
              Assets:UK:Monzo:Joint                       -25.00 GBP
              Assets:Partner:Expenses                       0.70 * 25.00 GBP

            2024-09-04 * "Uber" "" #Holiday-JPN-2024
              imported_from: "api"
              id: "tx_0000AleaYRwOr80PGgDQwL"
              country: "NLD"
              paid_by: "Angelo"
              full_amount: "1444 JPY"
              timezone: "Europe/Amsterdam"
              time: "10:09"
              Expenses:Trasporti-e-viaggi:Taxi   1011 JPY @ 0.0052631579 GBP
                ratio: 0.70
              Assets:UK:Monzo:Joint             -7.60 GBP
              Assets:Partner:Expenses           2.28 GBP
        """
        )
        ratio_definitions = list(filter(lambda x: isinstance(x, Custom), entries))
        for expected_entry in expected_entries:
            if isinstance(expected_entry, Transaction):
                for posting in expected_entry.postings:
                    if posting.account.startswith("Expenses"):
                        self.assertEqual(
                            posting.meta["ratio"],
                            lookup_value_by_date(expected_entry.date, ratio_definitions),
                        )


@pytest.mark.config
def it_should_raise_when_configuration_is_not_valid_json():
    with pytest.raises(ValueError):
        Config("[}")


@pytest.mark.config
def it_should_raise_when_input_is_not_a_dictionary():
    with pytest.raises(TypeError):
        Config("[]")


@pytest.mark.config
def it_should_raise_when_mandatory_attributes_are_missing():
    with pytest.raises(KeyError):
        Config("{}")


@pytest.mark.config
def it_should_raise_when_accounts_provided_are_not_valid():
    with pytest.raises(ValueError):
        Config("{'shared_accounts': [], 'partner_account': ''}")

    with pytest.raises(ValueError):
        Config("{'shared_accounts': [''], 'partner_account': 'test'}")


@pytest.mark.config
def it_should_raise_when_the_ratio_key_provided_is_not_valid():
    with pytest.raises(ValueError):
        Config("{'shared_accounts': ['Assets:Acc-1'], 'partner_account': 'Expenses:Acc-2', 'ratio_metadata_key': ''}")


@pytest.mark.config
def it_should_return_a_working_instance_for_a_valid_configuration():
    shared_accounts = ["Assets:Acc-1"]
    partner_account = "Expenses:Acc-2"
    config_partial = Config(
        "{'shared_accounts': [ "
        + ", ".join(f"'{account}'" for account in shared_accounts)
        + f"], 'partner_account': '{partner_account}'"
        + "}"
    )

    assert config_partial.shared_accounts == shared_accounts
    assert config_partial.partner_account == partner_account
    assert config_partial.ratio_metadata_key == DEFAULT_RATIO_KEY

    ratio_metadata_key = "my_ratio_key"

    config_full = Config(
        "{'shared_accounts': [ "
        + ", ".join(f"'{account}'" for account in shared_accounts)
        + f"], 'partner_account': '{partner_account}',"
        f"'ratio_metadata_key': '{ratio_metadata_key}'" + "}"
    )

    assert config_full.shared_accounts == shared_accounts
    assert config_full.partner_account == partner_account
    assert config_full.ratio_metadata_key == ratio_metadata_key


@pytest.mark.parse_ratio
def it_should_raise_when_parsing_a_directive_with_invalid_ratio():
    broken_directive_str = Custom({}, "2023-01-01", "Ratio", ["1"])

    with pytest.raises(ValueError):
        parse_ratio(broken_directive_str)

    broken_directive_int = Custom({}, "2023-01-01", "Ratio", [1])

    with pytest.raises(ValueError):
        parse_ratio(broken_directive_int)


@pytest.mark.parse_ratio
def it_should_raise_when_parsing_a_directive_with_invalid_arguments():
    broken_directive_too_few_arguments = Custom({}, "2023-01-01", "Ratio", [])

    with pytest.raises(ValueError):
        parse_ratio(broken_directive_too_few_arguments)

    broken_directive_too_many_arguments = Custom({}, "2023-01-01", "Ratio", [1, "2023-12-31", "2023-12-31"])

    with pytest.raises(ValueError):
        parse_ratio(broken_directive_too_many_arguments)
