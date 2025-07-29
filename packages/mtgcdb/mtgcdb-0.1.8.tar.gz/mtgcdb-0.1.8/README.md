# MTGCDB

MTG Card Database

## Usage

```python
from mtgcdb import MTGDBC

mtg = MTGDBC()

card = mtg.get_card_by_name('Goblin Guide')
print(card)

isd = mtg.get_cards_by_set_code('ISD')
print(isd)
```
