# pygrid
Simple Python based client for the GRID esports API with a collection of data pipeline functions to support processing of game data.

## Features / TODO
- [x] Rate limited access to GRID GraphQL endpoints
- [x] Simple client class to access commonly used queries.
- [x] Automatic pagination for queries that require multiple API calls
- [x] Minimal external dependencies; only httpx, pendulum, pydantic and orjson for the client and ariadne-codegen for GraphQL API code generation.
- [ ] Release my scripts that parse returned data files ideally in a database agnositic format. As I don't expect this library to become that popular, my main focus will be on compatability with my own [ATG](https://github.com/Allan-Cao/ATG) database format.
- [ ] Complete unit testing coverage of all parsing functions.
- [ ] Release on PyPi for easier installation

## Installation

```bash
pip install git+https://github.com/Allan-Cao/pygrid
```

## Example Usage

Client API key setup

```python
import os
from pygrid.client import GridClient

client = GridClient(os.environ["GRID_API_KEY"])
```

Lookup series information with filtering
```python
from pygrid import OrderDirection, SeriesType
gte = "2025-01-01T00:00:00.000Z"
tournaments = ["825437", "825439", "825438", "825440", "825441"]
available_series = client.get_all_matches(
    order=OrderDirection.DESC,
    title_ids = [3], # LoL
    gte = gte, # Earliest series time
    tournaments = tournaments,
)
```
Example Series:

> GetSeriesAllSeriesEdges(node=GetSeriesAllSeriesEdgesNode(id='2780287', type=<SeriesType.ESPORTS: 'ESPORTS'>, format=GetSeriesAllSeriesEdgesNodeFormat(id='4', name='best-of-5', name_shortened='Bo5'), external_links=[GetSeriesAllSeriesEdgesNodeExternalLinks(data_provider=GetSeriesAllSeriesEdgesNodeExternalLinksDataProvider(description='Riot Esports API', name='LOL'), external_entity=GetSeriesAllSeriesEdgesNodeExternalLinksExternalEntity(id='114058320676724257'))], tournament=GetSeriesAllSeriesEdgesNodeTournament(id='825441', end_date=None, logo_url='https://cdn.grid.gg/assets/tournament-logos/generic', name='NACL - Spring 2025 (Playoffs: Playoffs)', name_shortened='Playoffs', start_date=None), teams=[GetSeriesAllSeriesEdgesNodeTeams(base_info=GetSeriesAllSeriesEdgesNodeTeamsBaseInfo(id='48610', color_primary='#5b6f7e', color_secondary='#ffffff', external_links=[], logo_url='https://cdn.grid.gg/assets/team-logos/389822452c3763a1fca49f66bbab781c', name_shortened=None, name='TBD-1')), GetSeriesAllSeriesEdgesNodeTeams(base_info=GetSeriesAllSeriesEdgesNodeTeamsBaseInfo(id='48611', color_primary='#5b6f7e', color_secondary='#ffffff', external_links=[], logo_url='https://cdn.grid.gg/assets/team-logos/5dd850a9a2c427406c4e68b4c458ec33', name_shortened=None, name='TBD-2'))], start_time_scheduled='2025-06-06T21:00:00Z'))

## Generating API code with Ariadne Codegen
Ariadne Codegen lets us translate raw GraphQL queries into a Python library as well as bringing GraphQL's type safety to Python

You'll need to set your GRID API key to be able to access the central data GraphQL API
```bash
export GRID_API_KEY=YOUR_KEY_HERE
```

To regenerate the GraphQL Client code use the following commands
```bash
ariadne-codegen client --config central-data.toml
ariadne-codegen client --config series-state.toml
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
