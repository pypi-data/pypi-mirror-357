# helix-py
[Helix-DB](https://github.com/HelixDB/helix-db) | [Homepage](https://www.helix-db.com/) | [Documentation](https://docs.helix-db.com/introduction/overview) | [PyPi](https://pypi.org/project/helix-py/)

Helix-py is a python library for interacting with [helix-db](https://github.com/HelixDB/helix-db) a
graph-vector database written in rust.
This library will make it easy to quickly setup a rag agent with your documents and favorite model.

## Features

### Queries
helix-py using a pytorch like front-end to creating queries. Like you would define a neural network
forward pass, you can do the same thing for a helix-db query. We provide some default queries in
`helix/client.py` to get started with inserting and search vectors, but you can also define you're
own queries if you plan on doing more complex things. For example, for this hql query
```sql
QUERY addUser(name: String, age: I64) =>
  usr <- AddV<User>({name: name, nge: age})
  RETURN usr
```
you would write
```python
class addUser(Query):
    def __init__(self, user: Tuple[str, int]):
        super().__init__()
        self.user = user

    def query(self) -> List[Any]:
        return [{ "name": self.user[0], "age": self.user[1] }]

    def response(self, response):
        return response
```
for your python script. Make sure that the Query.query method returns a list of objects.

### Loader
The loader (`helix/loader.py`) currently supports `.parquet`, `.fvecs`, and `.csv` data. Simply pass in the path to your
file or files and the columns you want to process and the loader does the rest for you and is easy to integrate with
your queries

## Installation
### Install helix-py
```bash
pip install helix-py
```
See [getting started](https://github.com/HelixDB/helix-db?tab=readme-ov-file#getting-started) for more
information on installing helix-db

### Install the Helix CLI
```bash
curl -sSL "https://install.helix-db.com" | bash
helix install
helix init
helix deploy
```

## Documentation
Proper docs are coming soon. See `examples/tutorial.py` for now.
```python
import helix
from helix.client import hnswload, hnswsearch

db = helix.Client(local=True)
data = helix.Loader("path/to/data", cols=["vecs"])
ids = db.query(hnswload(data)) # build hnsw index

my_query = [0.32, ..., -1.321]
nearest = db.query(hnswsearch(my_query)) # query hnsw index
```

#### LLM Install for Demo
For the demo in `examples/rag_demo/` you can also install [Ollama here](https://ollama.com/download)
to get up and running with a local model.

Just run this after installing ollama. (We used llama3.1:8b, but you can just use whatever you want
ofcourse.)
```bash
ollama serve
ollama pull llama3.1:8b
```

Now you're good to go! See `examples/` for how to use helix-py. See
`helixdb-queries/queries.hx` for the queries installed with `helix deploy --local`. You can add your own here
and write corresponding `Query` classes in your python script.

## Getting Started With MCP With Helix
Helix's custom mcp server backend is built into the db and the `mcp_server.py` server can be used
to interface with that. To get started with this, you can for example use uv:

```bash
uv init project
cp mcp_server.py project
cd project
uv venv && source .venv/bin/activate
uv add helix-py "mcp[cli]"
```
then for claude-desktop for example add this to
`~/Library/Application Support/Claude/claude_desktop_config.json` adjusting paths of course
```json
{
  "mcpServers": {
    "helix-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/user/helix-py/proect",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

## License
helix-py is licensed under the GNU General Public License v3.0 (GPL-3.0).

