## Data Extraction Tool

1. Independently extracts all balance-affecting data within a specified date range from the
following exchanges for multiple accounts (ie solution must be flexible to add more accounts
per exchange using additional API keys):
a. gate.io
b. AscendEx.com
c. FTX.com
d. Bit Global (formerly Bithumb)

2. All exports must be standardised / formatted using Koinly.io’s Universal format (including
blockchain transaction hash, origin / destination wallet addresses for deposits / withdrawals,
note if present/relevant, and transaction type ie Deposit/Reward/Fee) in CSV file format using
UTC date / times.

### How to run app locally
- clone app
- create a virtualenv with python3
- Activate virtualenv and run `pip install > requirements.txt`
- Run command `python run.py`
