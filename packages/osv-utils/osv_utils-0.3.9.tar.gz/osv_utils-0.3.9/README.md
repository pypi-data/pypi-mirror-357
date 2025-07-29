# osv-utils

`osv-utils` is a Python package designed for collecting and loading OSV (Open Source Vulnerability) records from 
various ecosystems. It provides an easy-to-use interface to interact with OSV data.

## Installation

To install the `osv-utils` package, you can use pip:

```sh
pip install osv-utils
```

## Setup
Before using `osv-utils`, you may want to configure the data path where OSV records will be stored. By default, the data 
will be saved in the `~/.osvutils/gs` directory.

You can customize the `data_path` by providing it during the initialization of `OSVDataCollector` or `OSVDataLoader`.

## Usage

### Collecting OSV Records
To collect OSV records from specific ecosystems, use the `OSVDataCollector` class. Below is an example of how to collect 
records from the `GIT` ecosystem:

```python
from osvutils.core.collector import OSVDataCollector

collector = OSVDataCollector(verbose=True)
count = collector(['GIT'])

print(f"Total records collected: {count}")
```

### Loading OSV Records

To load the collected OSV records, use the `OSVDataLoader` class. Below is an example of how to load records from 
the `GIT` ecosystem:
    
```python
from osvutils.core.loader import OSVDataLoader

loader = OSVDataLoader(verbose=True)
loader(['GIT'])
print(len(loader))
```

### Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any improvements, bug fixes, 
or feature requests.
