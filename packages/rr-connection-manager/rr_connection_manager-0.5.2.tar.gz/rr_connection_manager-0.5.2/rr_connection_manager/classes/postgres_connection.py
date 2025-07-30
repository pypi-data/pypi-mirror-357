import importlib
from typing import Optional

from .connection import Connection, ConnectionType


class PostgresConnection(Connection):
    default_port = 5432

    def __init__(self, db_id=None, conn_type=ConnectionType.LOCAL) -> None:
        super().__init__(db_id, conn_type, self.default_port)
        self._psycopg = self._load_psycopg()

    def _load_psycopg(self):
        try:
            return importlib.import_module("psycopg")
        except ImportError as e:
            raise ImportError(
                "The psycopg library is required to use PostgresConnection."
            ) from e

    def cursor(self, **kwargs):
        config: dict[str, Optional[str]] = {
            "dbname": self.connection_conf.db_name,
            "user": self.connection_conf.db_user,
            "host": self.connection_conf.db_host,
            "port": self.connection_conf.db_port,
            "password": self.connection_conf.db_password,
        }

        if self.connection_conf.conn_type != "remote":
            config["host"] = "localhost"

        if self.tunnel:
            self.tunnel.start()
            config["port"] = self.tunnel.local_bind_port

        connection = self._psycopg.connect(
            **config,
            **kwargs,
        )

        return connection.cursor()

    @Connection.require_sqlalchemy  # type: ignore
    def engine(self, **kwargs):
        return self._sqlalchemy.create_engine(
            (
                f"postgresql://{self.connection_conf.db_user}:"
                f"{self.connection_conf.db_password}@"
                f"{self.connection_conf.db_host or 'localhost'}:"
                f"{self.connection_conf.db_port}/"
                f"{self.connection_conf.db_name}"
            ),
            **kwargs,
        )

    @Connection.require_sqlalchemy  # type: ignore
    def session_maker(self, engine=None, **kwargs):
        if engine:
            return self._sqlaorm.sessionmaker(engine, **kwargs)
        else:
            return self._sqlaorm.sessionmaker(self.engine(), **kwargs)

    @Connection.require_sqlalchemy  # type: ignore
    def session(self, engine=None, **kwargs):
        if engine:
            return self._sqlaorm.Session(engine, **kwargs)
        else:
            return self._sqlaorm.Session(self.engine())

    def connection_check(self):
        cur = self.cursor()
        cur.execute("SELECT version()")
        info = cur.fetchone()
        cur.close()
        print(
            f"\nConnection to {self.db_id} successful. \nDatabase info: \n\t{info[0].split(',')[0]}"
            ""
        )
