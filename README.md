# ZTMParser

## Description

Parser for the [ZTM](https://www.ztm.waw.pl/pliki-do-pobrania/dane-rozkladowe/) public dataset.

- [ztm.py](./ztm.py) this file contains ZTMTagReader that will return all return raw text (without leading and trailing spaces) for given tag.
- [parsers.py](./parsers.py) this file contains parsers for each tag. At this moment the following parsers are implemented:
  - ZTMParserWK
  - ZTMParserPR
  - ZTMParserZP

To add new parsers you must follow this naming convention: ZTMParser\<TAG\>

## Installation

To use this parser you can clone this repository:

```bash
git clone <repository-link>
cd <repository-name>
```

If you are working with this parser from different path make sure to add the following line to your code

```py
import os
import sys

sys.path.append(os.path.abspath("<abs/relative path to ZTMParser>"))
# e.g. sys.path.append(os.path.abspath("../ZTMParser/"))
```

## Usage

Example of usage is provided in [`example.ipynb`](example.ipynb).
