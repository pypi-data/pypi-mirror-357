from __future__ import annotations
import importlib
from typing import Any, Optional, cast, TYPE_CHECKING
from types import ModuleType

from .connection import Connection
from .connection import ConnectionType

if TYPE_CHECKING:
    import pyodbc
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class SQLServerConnection(Connection):
    """
    A class for managing connections to a Microsoft SQL Server database.

    This class provides functions for creating a cursor, SQLAlchemy engine, and sessions
    while supporting both trusted (Windows Authentication) and non-trusted (username/password)
    connection modes.

    Args:
        db_id (str): Custom identifier that links a connection to a config entry
        trusted (bool, optional): Whether to use a trusted connection.
            Defaults to True.
    """

    default_port = 1433

    def __init__(
        self, db_id: str, conn_type=ConnectionType.LOCAL, trusted: bool = True
    ) -> None:
        super().__init__(db_id, conn_type, self.default_port)
        self.trusted: bool = trusted
        self._pyodbc = self._load_pyodbc()

    def _load_pyodbc(self) -> ModuleType:
        """
        Dynamically imports the `pyodbc` module.

        This method attempts to import the `pyodbc` library dynamically. If the library
        is not installed in the current environment, it raises an `ImportError`.

        Returns:
            ModuleType: The dynamically imported `pyodbc` module.

        Raises:
            ImportError: If the `pyodbc` library is not installed.
        """
        try:
            return importlib.import_module("pyodbc")
        except ImportError as e:
            raise ImportError(
                "The pyodbc library is required to use SQLServerConnection. "
            ) from e

    def cursor(self, **kwargs: Any) -> pyodbc.Cursor:
        """
        Establishes a connection to the SQL Server and returns a cursor.

        This function constructs a connection string based on whether a trusted authentication
        or a non-trusted connection is required. It then creates a connection
        using pyodbc and returns a cursor.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            pyodbc.Cursor: Cursor object.
        """
        config: dict[str, Optional[str]] = {
            "driver": "SQL Server",
            "server": f"{self.connection_conf.db_host},{self.connection_conf.db_port}",
            "database": self.connection_conf.db_name,
        }

        if self.trusted:
            config["trusted_connection"] = "Yes"
        else:
            config["uid"] = self.connection_conf.db_user
            config["pwd"] = self.connection_conf.db_password

        connection = self._pyodbc.connect(
            **config,
            **kwargs,
        )

        return connection.cursor()

    @Connection.require_sqlalchemy  # type: ignore
    def engine(self, **kwargs: Any) -> Engine:
        """
        Creates and returns an SQLAlchemy engine for connecting to a SQL Server database.

        This function constructs a connection string based on whether a trusted authentication
        or a non-trusted connection is required. It then uses the connection
        string to create and return an SQLAlchemy engine.

        Args:
            **kwargs: Additional keyword arguments passed to create_engine.

        Returns:
            Engine: An SQLAlchemy engine.
        """
        driver: str = "SQL+Server+Native+Client+11.0"

        db_auth: str = (
            f"{self.connection_conf.db_user}:" f"{self.connection_conf.db_password}@"
            if not self.trusted
            else ""
        )

        connection_string: str = (
            f"mssql+pyodbc://{db_auth}"
            f"{self.connection_conf.db_host}/"
            f"{self.connection_conf.db_name}?driver={driver}"
        )

        return cast(
            Engine,
            cast(ModuleType, self._sqlalchemy).create_engine(
                connection_string, **kwargs
            ),
        )

    @Connection.require_sqlalchemy  # type: ignore
    def session_maker(
        self, engine: Optional[Engine] = None, **kwargs: Any
    ) -> sessionmaker:
        """
        Creates and returns a session maker for SQLAlchemy.

        If an engine is provided, it will be used to create the session maker otherwise
        the function will use the engine created by `self.engine`.

        Args:
            engine (Optional[Engine], optional): The SQLAlchemy engine to be used for creating sessions.
                If not provided, the engine created by the `self.engine` function will be used.
            **kwargs: Additional keyword arguments passed to the session maker.

        Returns:
            sessionmaker: A session maker.
        """
        return cast(
            sessionmaker,
            cast(ModuleType, self._sqlaorm).sessionmaker(
                engine or self.engine(), **kwargs
            ),
        )

    @Connection.require_sqlalchemy  # type: ignore
    def session(self, engine: Optional[Engine] = None, **kwargs: Any) -> Session:
        """
        Creates and returns an SQLAlchemy session.

        This function creates a session using the provided SQLAlchemy engine. If no engine is provided,
        the engine created by the `self.engine` function will be used.

        Args:
            engine (Optional[Engine], optional): The SQLAlchemy engine to be used for the session.
                If not provided, the engine created by the `self.engine` function will be used.
            **kwargs: Additional keyword arguments passed to the Session constructor.

        Returns:
            Session: An SQLAlchemy session that can be used for querying the database.
        """
        return cast(
            Session,
            cast(ModuleType, self._sqlaorm).Session(engine or self.engine(), **kwargs),
        )

    def connection_check(self) -> None:
        """
        Checks the connection to the SQL Server database.

        This function attempts to execute a query to verify that the connection
        to the database is successful. Prints basic database info.
        """
        with self.cursor() as cur:
            cur.execute("SELECT @@version")
            info: tuple[str] = cur.fetchone()
        print(
            f"\nConnection to {self.db_id} successful.\nDatabase info:\n\t{info[0].split(',')[0]}"
        )
