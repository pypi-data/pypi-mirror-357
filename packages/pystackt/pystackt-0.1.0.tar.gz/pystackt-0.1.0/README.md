# PyStack't (`pystackt`)
PyStack't (`pystackt`) is a Python package based on [Stack't](https://github.com/LienBosmans/stack-t) that supports data preparation for object-centric process mining.


## 📦 Installation  
PyStack't is published on [PyPi](https://pypi.org/project/pystackt/) and can be installed using pip.  

```sh
pip install pystackt
```

## [📖 Documentation](https://lienbosmans.github.io/pystackt/)

-   [Extensive documentation](https://lienbosmans.github.io/pystackt/) is available via GitHub pages. 
-   A [demo video on Youtube](https://youtu.be/AS8wI90wRM8) can walk you throught the different functionalities.

## 🔍 Viewing Data  
PyStack't creates **DuckDB database files**. From DuckDB version 1.2.1 onwards, you can explore them using the [**UI extension**](https://duckdb.org/docs/stable/extensions/ui.html). Below code will load the UI by navigating to `http://localhost:4213` in your default browser.

```python
import duckdb

with duckdb.connect("./stackt.duckdb") as quack:
    quack.sql("CALL start_ui()")
    input("Press Enter to close the connection...")
```

Alternatively, you can use a database manager. You can follow this [DuckDB guide](https://duckdb.org/docs/guides/sql_editors/dbeaver.html) to download and install **DBeaver** for easy access.


## 📝 Examples

### ⛏️🐙 Extract object-centric event log from GitHub repo ([`get_github_log`](https://lienbosmans.github.io/pystackt/extract/get_github_log.html))
```python
from pystackt import *

get_github_log(
    GITHUB_ACCESS_TOKEN="insert_your_github_access_token_here",
    repo_owner="LienBosmans",
    repo_name="stack-t",
    max_issues=None, # None returns all issues, can also be set to an integer to extract a limited data set
    quack_db="./stackt.duckdb",
    schema="main"
)
```

### 📈 Interactive data exploration ([`start_visualization_app`](https://lienbosmans.github.io/pystackt/exploration/interactive_data_visualization_app.html))

```python
from pystackt import *

prepare_graph_data( # only needed once
    quack_db="./stackt.duckdb",
    schema_in="main",
    schema_out="graph_data_prep"
)

start_visualization_app(
    quack_db="./stackt.duckdb",
    schema="graph_data_prep"
)
```

### 📤 Export to OCEL 2.0 ([`export_to_ocel2`](https://lienbosmans.github.io/pystackt/export/export_to_ocel2.html))
```python
from pystackt import *

export_to_ocel2(
    quack_db="./stackt.duckdb",
    schema_in="main",
    schema_out="ocel2",
    sqlite_db="./ocel2_stackt.sqlite"
)
```
