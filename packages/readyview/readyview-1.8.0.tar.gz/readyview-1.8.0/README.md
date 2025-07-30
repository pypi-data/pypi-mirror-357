# ReadyView Dashboard Python Library

The ReadyView Dashboard Python library provides all current ReadyView [dashboard API](https://api.readylinks.io/redoc) calls to interface with the ReadyLinks ReadyView cloud-managed platform. ReadyView generates the library based on dashboard API's OpenAPI spec to keep it up to date with the latest API releases, and provides the full source code for the library including the tools used to generate the library. ReadyLinks welcomes constructive pull requests that maintain backwards compatibility with prior versions. The library requires Python 3.10+, receives support from the community, and you can install it via [PyPI](https://pypi.org/project/readyview/):

```
pip install --upgrdade readyview
```

## Usage
1. Export your Organization ID and API Key as an environment variable, for example:
```
export READYVIEW_DASHBOARD_ORG_ID=YOUR_ORG_ID
export READYVIEW_DASHBOARD_API_KEY=YOUR_API_KEY
```
2. Import the library with a single line at the top of your Python script.
```
import readyview
```
3. Instantiate the dashboard client. 
```
dashboard = readyview.Dashboard()
```
4. Start programmatically interacting with your ReadyView dashboard!
```
my_networks = dashboard.network.get_networks()
```