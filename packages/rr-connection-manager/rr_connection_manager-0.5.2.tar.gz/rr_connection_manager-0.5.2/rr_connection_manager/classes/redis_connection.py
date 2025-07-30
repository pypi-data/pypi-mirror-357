import importlib
from .connection import Connection, ConnectionType


class RedisConnection(Connection):
    default_port = 6379

    def __init__(self, db_id=None, conn_type=ConnectionType.LOCAL) -> None:
        super().__init__(db_id, conn_type, self.default_port)
        self._connection_details = self._set_details()
        self._redis = self._load_redis()

    def _load_redis(self):
        try:
            return importlib.import_module("redis")
        except ImportError as e:
            raise ImportError(
                "The redis library is required to use RedisConnection. "
            ) from e

    def _set_details(self):
        connection_details = {
            "db_host": "localhost",
            "db_port": self.connection_conf.db_port,
            "db_name": self.connection_conf.db_name,
        }

        if self.tunnel:
            self.tunnel.start()
            connection_details["db_port"] = self.tunnel.local_bind_port

        # Connecting remotely to the DB not using SSH
        # Not sure about this logic any more
        if self.connection_conf.conn_type == "proxy" and not self.tunnel:
            connection_details["db_host"] = self.connection_conf.db_host

        return connection_details

    def cursor(self, **kwargs):
        return self._redis.Redis(
            host=self._connection_details["db_host"],
            port=self._connection_details["db_port"],
            db=self._connection_details["db_name"],
            **kwargs,
        )

    def connection_check(self):
        try:
            cursor = self.cursor()
            response = cursor.ping()
            print(
                f"\nConnection to {self.db_id} successful. \nPing response: {response}"
            )
        except self._redis.ConnectionError as e:
            print(f"Error connecting to Redis: {e}")
