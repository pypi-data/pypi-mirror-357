import getpass
import hashlib
import importlib
import json
import os
from pathlib import Path
from typing import Optional


class MultipleConfJsonFilesError(Exception):
    """Exception raised when multiple 'conf.json' files are found."""

    pass


class AppNameMismatch(Exception):
    """
    Exception raised when a config file is present but app_name passed to the connection
    doesn't match anything in the config file
    """

    pass


class ConnectionConf:
    def __init__(self, db_id, conn_type, default_port) -> None:
        self.db_id = db_id
        self.conf = self._find_conf()
        self.conn_type = conn_type
        self.proxy_host = None
        self.db_host = None
        self.db_user = None
        self.db_name = None
        self.db_password = None
        self.tunnel_user = None
        self.db_port = default_port
        self.tunnel_port = 22
        self.local_port = None
        self._pykeepass = None
        self._set_attributes()

    def _load_keepass(self):
        try:
            self._pykeepass = importlib.import_module("pykeepass")
        except ImportError as e:
            raise ImportError(
                "The pykeepass library is required to load connection details"
                "Either install pykeepass or provide a config.json file"
            ) from e

    def _find_conf(self, base_path: Optional[Path] = None) -> Optional[Path]:
        base_path = base_path or Path.cwd()

        if not base_path.is_dir():
            raise ValueError(f"Provided base path {base_path} is not a directory.")

        conf_files = list(base_path.rglob("conf.json"))

        if len(conf_files) > 1:
            raise MultipleConfJsonFilesError("Found more than one conf.json file")

        return conf_files[0] if conf_files else None

    def _get_keepass_key(self):
        public_key_path = os.path.expanduser("~/.ssh/id_rsa.pub")

        with open(public_key_path, "r", encoding="utf-8") as public_key_file:
            public_key = public_key_file.read()

        return hashlib.sha256(public_key.encode("utf-8")).hexdigest()

    def _read_conf(self):
        try:
            with self.conf.open("r") as conf:
                servers = json.load(conf)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from file {self.conf}: {e}")
        except IOError as e:
            raise ValueError(f"Error reading file {self.conf}: {e}")

        for server in servers:
            if server.get("db_id") == self.db_id:
                settings = server

        # Passed db_id doesn't match any in the config
        if "settings" not in locals():
            raise AppNameMismatch(
                f"db_id {self.db_id} doesn't match anything in the config file"
            )

        return settings

    def _read_keepass(self):
        user = getpass.getuser().replace(".", "_")
        keepass_file_path = os.path.abspath(
            os.path.join("R:", "Connection Manager", user, f"{user}.kdbx ")
        )

        if not os.path.exists(keepass_file_path):
            # Could there be a separate error to point at the VPN as a cause
            raise FileExistsError("Can't find your keepass file. Check connection")

        kp = self._pykeepass.PyKeePass(
            keepass_file_path, password=self._get_keepass_key()
        )

        group = kp.find_groups(name=self.db_id, first=True)

        if not group:
            raise LookupError(f"Could not find server db_id {self.db_id} in keypass")

        return group

    def _set_attribute(self, setting, value):
        if setting == "db_id" and not value:
            raise ValueError("db_id is a required variable")

        if setting in {"tunnel_port", "db_port"}:
            value = int(value)

        setattr(self, setting, value)

    def _set_attributes(self):
        if self.conf:
            settings = self._read_conf()

            if "db_id" not in settings:
                raise ValueError("db_id is a required variable")

            for setting, value in settings.items():
                self._set_attribute(setting, value)

        else:
            self._load_keepass()
            group = self._read_keepass()

            if db_server := next(
                (e for e in group.entries if "db_server" in e.path), None
            ):
                self._set_attribute("db_host", db_server.url)
                self._set_attribute("tunnel_user", db_server.username)

                if db_server.notes:
                    if ports := json.loads(db_server.notes).get("PORTS"):
                        self._set_attribute("db_port", ports.get("DB_PORT"))
                        self._set_attribute("tunnel_port", ports.get("SSH_PORT"))

            if db_user := next((e for e in group.entries if "db_user" in e.path), None):
                self._set_attribute("db_user", db_user.username)
                self._set_attribute("db_password", db_user.password)

                if db_user.notes:
                    if database := json.loads(db_user.notes)["DATABASE"][0]:
                        self._set_attribute("db_name", database)

            if app_server := next(
                (e for e in group.entries if "app_server" in e.path), None
            ):
                self._set_attribute("app_host", app_server.url)

                if (
                    self.conn_type == "proxy"
                    and app_server.notes
                    and "PORTS" in app_server.notes
                ):
                    self._set_attribute("tunnel_user", app_server.username)
                    self.tunnel_port = json.loads(app_server.notes)["PORTS"]["SSH_PORT"]
