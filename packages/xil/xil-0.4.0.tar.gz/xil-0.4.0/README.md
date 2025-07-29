[![Tests](https://github.com/jond01/xil/actions/workflows/tests.yml/badge.svg)](https://github.com/jond01/xil/actions/workflows/tests.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Python Versions](https://img.shields.io/pypi/pyversions/xil)](https://pypi.org/project/xil/)
[![PyPI](https://img.shields.io/pypi/v/xil)](https://pypi.org/project/xil/#history)

# XIL

Gather and compare foreign currency exchange buy and sell rates offered by Israeli
banks.

## Banks data

The XIL project supports the following banks:

| Bank and data source                                                                                                                                       | XIL module        | Tests              | Bank name (Hebrew)           |
|------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|--------------------|------------------------------|
| [Bank Leumi Le-Israel](https://www.leumi.co.il/Lobby/currency_rates/40806/)                                                                                | `leumi`           | :white_check_mark: | בנק לאומי לישראל             |
| [Bank Hapoalim](https://www.bankhapoalim.co.il/he/foreign-currency/exchange-rates)                                                                         | `poalim`          | :white_check_mark: | בנק הפועלים                  |
| [Mizrahi Tefahot Bank](https://www.mizrahi-tefahot.co.il/brokerage/currancyexchange/)                                                                      | `mizrahi_tefahot` | :x:                | בנק מזרחי טפחות              |
| [Israel Discount Bank](https://www.discountbank.co.il/private/general-information/foreign-currency-transfers/exchange-rates/)                              | `discount`        | :white_check_mark: | בנק דיסקונט לישראל           |
| [First International Bank of Israel](https://www.fibi.co.il/wps/portal/FibiMenu/Marketing/Private/ForeignCurrency/Trade/Rates)                             | `fibi`            | :x:                | הבנק הבינלאומי הראשון לישראל |
| [Bank of Jerusalem](https://www.bankjerusalem.co.il/capital-market/rates)                                                                                  | `jerusalem`       | :x:                | בנק ירושלים                  |
| [Mercantile Discount Bank](https://www.mercantile.co.il/en/private/foregin-currency/exchange-rates/)                                                       | `mercantile`      | :white_check_mark: | בנק מרכנתיל דיסקונט          |
| [Bank Massad](https://www.bankmassad.co.il/wps/portal/FibiMenu/Marketing/Private/ForeignCurrency/ForexOnline/Rates)                                        | `massad`          | :x:                | בנק מסד                      |
| [One Zero Digital Bank](https://www.onezerobank.com/currencies/)                                                                                           | `onezero`         | :white_check_mark: | וואן זירו הבנק הדיגיטלי      |
| [Bank of Israel](https://www.boi.org.il/roles/markets/%D7%A9%D7%A2%D7%A8%D7%99-%D7%97%D7%9C%D7%99%D7%A4%D7%99%D7%9F-%D7%99%D7%A6%D7%99%D7%92%D7%99%D7%9D/) | `boi`             | :x:                | בנק ישראל                    |

For the data sources (websites and URLs) for each bank, see the docstring of the
corresponding XIL module.

Banks that are not supported yet:

- Bank Yahav (בנק יהב): no public information available.
  https://www.bank-yahav.co.il/investments/foreing-currency/
- Bank Esh Israel (בנק אש ישראל): a new bank - not commercially active yet.
  https://www.esh.com/

## Installation

The project requires Python 3.12 or above. To install the project, run:

```shell
pip install xil
```

## Contributing to the XIL project

Please read the [Contribution Guide](https://github.com/jond01/xil/blob/main/CONTRIBUTING.md).

## Similar projects

* https://github.com/eshaham/israeli-bank-scrapers
