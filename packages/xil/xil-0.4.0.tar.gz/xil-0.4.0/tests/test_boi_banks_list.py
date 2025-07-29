"""
Test the known list of banks against the Bank of Israel (BOI) online list
"""

import pandas as pd
import pytest

from xil.boi import get_boi_url_response

BOI_XML_URL = "\
https://www.boi.org.il/boi_files/Pikuah/banking_corporations_en.xml"

KNOWN_BANKS = {
    "Bank Hapoalim B.M",
    "Bank Leumi Le-Israel B.M",
    "Bank Massad Ltd",
    "Bank of Jerusalem Ltd",
    "Israel Discount Bank Ltd",
    "Mercantile Discount Bank ltd",
    "Mizrahi Tefahot Bank Ltd",
    "The First International Bank of Israel Ltd",
    "Bank Yahav  for Government Employees Ltd",  # Not supported - no public data
    "One Zero Digital Bank LTD",  # Not supported - no public data
    "Bank Esh Israel Ltd",  # Not supported - not commercially active yet
}


@pytest.fixture(name="boi_banks")
def fixture_boi_banks() -> set[str]:
    """Get the set on Israeli banks with bank code from BOI online XML"""
    with get_boi_url_response(BOI_XML_URL) as response:
        df = pd.read_xml(response)
    return set(
        df[(df["Category"] == "COMMERCIAL BANKS") & df["Bank_Code"].notna()]["Name"]
    )


@pytest.mark.live
def test_boi_banks(boi_banks: set[str]) -> None:
    """Test the online set vs. the hard-coded one"""
    assert boi_banks == KNOWN_BANKS, (
        "Mismatch between the updated banks list data from BOI and the saved data"
    )
