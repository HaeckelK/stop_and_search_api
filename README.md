# stop_and_search_api

stop_and_search_api is a Python module for making API calls to https://data.police.uk/docs/method/stops-force/ to download UK Stop and Search data.

## Installation

stop_and_search_api is not yet a package and cannot be installed via pip. Instead the repository may be cloned.

```bash
git clone https://github.com/HaeckelK/stop_and_search_api.git
```

## Usage

```python
from police_stop_and_search_api.police_api import PoliceAPI

police = PoliceAPI(savefolder='downloads')
police.add_job(dates=['2019-10'],
               forces=['cambridgeshire', 'cheshire'])
police.download()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](LICENSE.md)