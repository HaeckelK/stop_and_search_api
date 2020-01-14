# stop_and_search_api

stop_and_search_api is a Python module for making API calls to https://data.police.uk/docs/method/stops-force/ to download UK Stop and Search data.

## Installation

stop_and_search_api is not yet a package and cannot be installed via pip. Instead the repository may be cloned.

```bash
git clone https://github.com/HaeckelK/stop_and_search_api.git
```

## Usage

```python
from police_api import PoliceAPI

police = PoliceAPI()

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](LICENSE.md)