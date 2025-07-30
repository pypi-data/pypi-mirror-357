import importlib

from .connection import Connection, ConnectionType


class MySQLConnection(Connection):
    default_port = 3306

    def __init__(self, db_id=None, conn_type=ConnectionType.LOCAL) -> None:
        super().__init__(db_id, conn_type, self.default_port)
        self._connection_details = self._set_details()
        self._mysql = self._load_mysql()

    def _load_mysql(self):
        try:
            return importlib.import_module("mysql.connector")
        except ImportError as e:
            raise ImportError(
                "The mysql library is required to use MySQLConnection. "
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
        self.connection = self._mysql.connect(
            database=self._connection_details["db_name"],
            user=self._connection_details["db_user"],
            host=self._connection_details["db_host"],
            port=self._connection_details["db_port"],
            password=self._connection_details["db_password"],
            **kwargs,
        )

        return self.connection.cursor()

    @Connection.require_sqlalchemy  # type: ignore
    def engine(self, **kwargs):
        return self._sqlalchemy.create_engine(
            (
                f"mysql+mysqlconnector://{self._connection_details['db_user']}:"
                f"{self._connection_details['db_password']}@"
                f"{self._connection_details['db_host']}:"
                f"{self._connection_details['db_port']}/"
                f"{self._connection_details['db_name']}"
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
        cur.execute("SELECT VERSION()")
        info = cur.fetchone()
        cur.close()
        print(
            f"\nConnection to {self.db_id} successful. \nDatabase info: \n\tMySQL version: {info[0]}"
        )
