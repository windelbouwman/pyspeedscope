
# Speedscope for python

[Speedscope](https://www.speedscope.app/) is a nice web-app to view a flame graph of your application.

This project contains a python recorder for speedscope.

## Installation

    $ pip install speedscope

## Usage

```python

import speedscope
from my_code import slow_function

with speedscope.track('speedscope.json'):
    slow_function()

````

Next, upload the file `speedscope.json` into the [webapp](https://www.speedscope.app/).
