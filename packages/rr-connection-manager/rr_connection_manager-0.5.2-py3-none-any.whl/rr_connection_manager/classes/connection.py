import importlib
import inspect
from functools import wraps
from enum import Enum
from typing import Optional
from types import ModuleType

from .connection_conf import ConnectionConf


class ConnectionType(Enum):
    PROXY = "proxy"
    TUNNEL = "tunnel"
    REMOTE = "remote"
    LOCAL = "local"


class Connection:
    def __init__(
        self,
        db_id=None,
        conn_type: ConnectionType = ConnectionType.LOCAL,
        default_port=None,
    ) -> None:
        self.db_id = db_id
        self.connection_conf = ConnectionConf(db_id, conn_type.value, default_port)
        self.tunnel = self._create_tunnel()
        self._sqlalchemy: Optional[ModuleType] = None
        self._sqlaorm: Optional[ModuleType] = None
        self._sshtunnel: Optional[ModuleType] = None

    def _load_sshtunnel(self):
        try:
            self._sshtunnel = importlib.import_module("sshtunnel")
        except ImportError as e:
            raise ImportError(
                "The sshtunnel library is required to use the tunnel option."
            ) from e

    def _create_tunnel(self):
        if self.connection_conf.conn_type in {"remote", "local"}:
            return None

        self._load_sshtunnel()

        # If going via a proxy server then DB is remote so bind using DB address
        # If not going via a proxy tunnel is direct to DB so DB is local
        ssh_address_or_host = (
            (self.connection_conf.proxy_host, self.connection_conf.tunnel_port)
            if self.connection_conf.conn_type == "proxy"
            else (self.connection_conf.db_host, self.connection_conf.tunnel_port)
        )

        remote_bind_address = (
            (self.connection_conf.db_host, self.connection_conf.db_port)
            if self.connection_conf.conn_type == "proxy"
            else ("localhost", self.connection_conf.db_port)
        )

        local_bind_address = (
            ("", int(self.connection_conf.local_port))
            if self.connection_conf.local_port
            else ("",)
        )

        config = {
            "ssh_address_or_host": ssh_address_or_host,
            "ssh_username": self.connection_conf.tunnel_user,
            "ssh_pkey": "~/.ssh/id_rsa",
            "remote_bind_address": remote_bind_address,
            "local_bind_address": local_bind_address,
        }

        return self._sshtunnel.open_tunnel(**config)

    def close(self):
        if self.tunnel:
            self.tunnel.stop()

    def _load_sqlalchemy(self):
        if not self._sqlalchemy:
            try:
                self._sqlalchemy = importlib.import_module("sqlalchemy")
                self._sqlaorm = importlib.import_module("sqlalchemy.orm")
            except ImportError as e:
                calling_function = inspect.stack()[2].function
                raise ImportError(
                    f"The sqlalchemy library is required to use the '{calling_function}' function."
                ) from e

    def require_sqlalchemy(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            self._load_sqlalchemy()
            return function(self, *args, **kwargs)

        return wrapper

    def config_warning(self):
        print(
            f"""
            Warning: You are connecting using the following settings

            Config Location: {self.connection_conf.conf or 'Keepass'}
            Database ID: {self.db_id}
            Host Address: {self.connection_conf.db_host}
            Database Name: {self.connection_conf.db_name}
            Database User: {self.connection_conf.db_user}
            """
        )
