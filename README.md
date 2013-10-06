# Unofficial scrapper API for Lloyds bank transactions

Library provides simple API to download couple last transactions for accounts.
Useful for integration with [Ledger](http://www.ledger-cli.org/).

## Sample usage

```python
from lloyds import LloydsBank

bank = LloydsBank()
bank.login('user id', 'password', 'secret')
for account_url in bank.accounts:
    for transaction in bank.get_transactions(account_url):
        print transaction
```

## Similar projects

  - [LBG Statement Downloader](https://github.com/bitplane/tsb-downloader)

## Credits

Written by [Izidor Matušov](http://izidor.io) and licensed under [MIT](LICENSE)
license.
