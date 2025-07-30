import importlib

from .connection import Connection, ConnectionType


class SQLiteConnection(Connection):
    def __init__(self, db_id=None, conn_type=ConnectionType.LOCAL) -> None:
        super().__init__(db_id, conn_type)
        self._sqlite = self._load_sqlite()

    def _load_sqlite(self):
        try:
            return importlib.import_module("sqlite3")
        except ImportError as e:
            raise ImportError(
                "The sqlite3 library is required to use SQLiteConnection. "
            ) from e

    def _set_details(self):
        connection_details = {
            "db_name": self.connection_conf.db_name,
            "db_user": self.connection_conf.db_user,
            "db_host": "localhost",
            "db_port": self.connection_conf.db_port,
            "db_password": self.connection_conf.db_password,
        }

        if self.tunnel:
            self.tunnel.start()
            connection_details["db_port"] = self.tunnel.local_bind_port

        if self.connection_conf.conn_type == "proxy" and not self.tunnel:
            connection_details["db_host"] = self.connection_conf.db_host

        return connection_details

    def cursor(self, **kwargs):
        connection = self._sqlite.connect(self.db_id, **kwargs)
        return connection.cursor()

    @Connection.require_sqlalchemy  # type: ignore
    def engine(self, **kwargs):
        return self._sqlalchemy.create_engine(f"sqlite:///{self.db_id}", **kwargs)

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
        cur.execute("SELECT sqlite_version()")
        info = cur.fetchone()
        cur.close()
        print(
            f"\nConnection to {self.db_id} successful. \nDatabase info: \n\t{info[0].split(',')[0]}"
        )
