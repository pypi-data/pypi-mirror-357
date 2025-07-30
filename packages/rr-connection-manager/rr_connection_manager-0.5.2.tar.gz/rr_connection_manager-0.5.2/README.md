<a name="readme-top"></a>

<br />
<h1 align="center">RR Connection Manager</h1>

  <p align="center">
    A package to help you connect to all Registry databases
    <br />
    <br />
    ·
    <a href="https://github.com/github_username/repo_name/issues">Report Bug</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues">Request Feature</a>
  </p>
<br/>

## About The Project

This package wraps pykeepass and sshtunnel along with various connection tools including SQLAlchemy, to allow an all in one solution for connecting via SSH to our servers without the need to store connection details locally  
<br/>

### Prerequisites

You will need to ensure make sure you meet all the expected requirements for using <strong><a href="https://www.psycopg.org/docs/install.html#psycopg-vs-psycopg-binary">pyscopg2</a></strong>

## Getting Started

```bash
poetry add rr-connection-manager
```
or

```bash
pip install rr-connection-manager
```

### Extras

This package allows for specific dependency setups inline with <strong><a href="https://peps.python.org/pep-0508/#extras">PEP 508</a></strong> so that you can control which database connectors you want to work with.

```
pip install rr-connection-manager[pgsql]
```

Poetry allows for the same behaviour using <strong><a href="https://python-poetry.org/docs/pyproject/#extras">extras</a></strong> but with it's own syntax
```bash
poetry add rr-connection-manager -E pgsql
```

There is a full list of possible options in the pyproject but the general patterns used are

| Extra Name        | Installed           | Notes                                 |
| :---------------- | :-----------------: | :------------------------------------ |
| tunnel            |sshtunnel            | Required if using the tunnel argument |
| keepass           |pykeepass            | Required if using a keepass file      |
| sqlser            |psycopg2             | For only working with cursors         |
| sqlser_sqla       |psycopg2, sqlalchemy | For working with session and engines  |

Most of the database flavours have a standard name for just using cursors and one sufixed with _sqla for working with sqlalchemy

In the case where you wanted to use connection manager to install dependencies that allowed you to work with a postgres database using SQLAlchemy over and SSH connection using the details found in a keepass file you would use the following command

```bash
poetry install rr-connection-manager -E pgsql_sqla -E tunnel -E keepass
```

## Connection Variables

The primary use case is for the connection variables to be taken from a keepass file. This will require some setup which includes running the <strong><a href="https://github.com/renalreg/rr-key-manager">RR Key Manager</a></strong>. Once you have done that connection manager should work out of the box.

Adding a conf.json file at the root of your project will override any attempt to connect to keepass. This is useful if you can't access the keepass file or you want use this on one of the servers. You can add connection details for as many servers as you like but the app_name field in the conf file must match the app_name variable past to the function to create your connection. 

```json
[
  { 
    "db_id": "database_identifier",
    "db_host": "database_host",
    "db_port": "database_port",
    "db_name": "database_name",
    "db_user": "database_username",
    "db_password": "database_user_password",    
    "tunnel_user": "tunnel_user",
    "tunnel_port": "tunnel_port",
    "local_port": "local_port"
  },
]
```
Not all of these are required for each connection. SQL Server connections for example only require DB_HOST and DATABASE.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Using a Tunnel

To connect to a database you need to use one of the predefined connection types. There are four possible connection type enums.

| Enum      | Notes                                                                                              |
| :---------| :--------------------------------------------------------------------------------------------------|
| LOCAL     | Connecting to a local database.                                                                    |
| REMOTE    | Connecting directly to a database on a remote server.                                              |
| TUNNEL    | Uses SSH to connect to a server and then connect locally on the server.                            |
| PROXY     | Uses an SSH tunnel via a proxy server to connect to the DB server and then locally to the database.|


When building the connection object you will need to import the ConnectionTypes. SO if we wanted to build a connection to a postgres database using an ssh tunnel and check to make sure we could connect we would do the following

```python
from rr_connection_manager import PostgresConnection
from rr_connection_manager import ConnectionType


conn = PostgresConnection(db_id="db_identifier", conn_type=ConnectionType.TUNNEL)
conn.connection_check()
```

In cases where you want to tunnel through an app server to the database server you can use the proxy connection type.

```python
from rr_connection_manager import PostgresConnection
from rr_connection_manager import ConnectionType

conn = PostgresConnection(db_id="db_identifier", conn_type=ConnectionType.PROXY)
```

## SQL Server Connection

To create a SQL Server connection object 

``` python
conn = SQLServerConnection(db_id="db_identifier")
```

From this you can choose to open a pyodbc cursor and use that to query the database

``` python
conn = SQLServerConnection(db_id="db_identifier")
cur = conn.cursor()
cur.execute("SELECT @@version")
info = cur.fetchone()
cur.close()
print(info)
```

You can pass in any extra config arguments you like when creating a cursor

``` python
conn = SQLServerConnection(db_id="db_identifier")
cur = conn.cursor(timeout=30, autocommit=True)
```

You can also create an untrusted connection to an SQL Server database whihc just means it will use a user name and password instead of using your windows credintials to authenticate.

``` python
conn = SQLServerConnection(db_id="db_identifier", trusted=False)
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Postgres Connection

To create a Postgres connection object 

``` python
conn = PostgresConnection(db_id="db_identifier")
```

From this you can choose to open a pyscopg2 cursor and use that to query the database

``` python
conn = PostgresConnection(db_id="db_identifier")
cur = conn.cursor()
cur.execute("SELECT version()")
info = cur.fetchone()
cur.close()
print(info)
```

You can pass in any extra config arguments you like when creating a cursor

``` python
conn = PostgresConnection(db_id="db_identifier")
cur = conn.cursor(connect_timeout=30, autocommit=True)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## SQLite Connection

To create a SQLite connection object 

``` python
conn = conn = SQLiteConnection(db_id="db_identifier")
```

From this you can choose to open a sqlite cursor and use that to query the database

``` python
conn = SQLiteConnection(db_id="db_identifier")
cur = conn.cursor()
cur.execute("SELECT sqlite_version()")
info = cur.fetchone()
cur.close()
print(info)
```

## Redis Connection

To create a Redis connection object 

``` python
conn = RedisConnection(db_id="db_identifier")
```

From this you can choose to open a redis cursor and use that to query the database

``` python
conn = RedisConnection(db_id="db_identifier")
cur = conn.cursor()
info = cur.ping()
cur.close()
print(info)
```

You can pass any extra options you wish to the cursor as you would when using the Redis package normally.

```python
conn = RedisConnection(db_id="db_identifier")
cur = conn.cursor( charset="utf-8", decode_responses=True)
```

## SQL Alchemy

All connection types also wrap sqlalchemy so you are able to access a session. This uses the standard set of arguments when creating the engine.

``` python
conn = PostgresConnection(db_id="db_identifier")
session = conn.session()
```

You can build the engine yourself which you allows you to pass arguments

``` python
conn = PostgresConnection(db_id="db_identifier")
eng = conn.engine(echo=True)
session = conn.session(eng)
```

A session maker is also accessible and allows you to pass arguments

``` python
conn = PostgresConnection(db_id="db_identifier")
Session = conn.session_maker(expire_on_commit=True)
session = Session()
```

You can combine both

``` python
conn = PostgresConnection(db_id="db_identifier")
eng = conn.engine(echo=True)
Session = conn.session_maker(eng, expire_on_commit=True)
session = Session()
check_message = session.execute(text("""select version()""")).first()
session.close()
conn.close()
print(check_message)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Connection check

To make testing the connection simple each class has a `connection_check` function that checks the version of the database it is connecting to. This uses the base packages not SQLAlchemy but it is assumed if they work so should SQLAlchemy.

```python
from rr_connection_manager import PostgresConnection
from rr_connection_manager import SQLServerConnection

conn = PostgresConnection(db_id="db_identifier")
conn.connection_check()

conn = SQLServerConnection(db_id="db_identifier")
conn.connection_check()
```

## Config Warning

To make it simple to create sanity checks before running the APi exposes a function named `config_warning` which prints out some information about the connection you have created. This works with any connection type Redis is used for demonstration purposes only.

```python
conn = RedisConnection(db_id="db_identifier")
conn.config_warning()
```

Output

```
Warning: You are connecting using the following settings

Config Location: C:\Path\to\the\conf.json or keepass
Database ID: db_identifier
Host Address: some.host.somewhere.uk
Database Name: your_db
Database User: you
```

## Using a Specific Local Port

> ⚠️ **Warning:** This is probably broken

To use a specific local port with your connection you can pass the local_port argument.

```python
conn = PostgresConnection(db_id="db_identifier", tunnel=True, local_port=6100)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.


# Contact

Renal Registry - [@UKKidney](https://twitter.com/@UKKidney) - rrsystems@renalregistry.nhs.uk

Project Link: [https://github.com/renalreg/rr-connection-manager](https://github.com/renalreg/rr-connection-manager)

<br />


# Acknowledgments

- [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
- [Psycopg2](https://www.psycopg.org/)
- [Pyodbc](https://github.com/mkleehammer/pyodbc/wiki)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pykeepass](https://github.com/libkeepass/pykeepass)
- [sshtunnel](https://github.com/pahaz/sshtunnel)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


[issues-shield]: https://img.shields.io/github/issues/renalreg/rr-connection-manager.svg?style=for-the-badge
[issues-url]: https://github.com/renalreg/rr-connection-manager/issues
[license-shield]: https://img.shields.io/github/license/renalreg/rr-connection-manager.svg?style=for-the-badge
[license-url]: https://github.com/renalreg/rr-connection-manager/blob/main/LICENSE

