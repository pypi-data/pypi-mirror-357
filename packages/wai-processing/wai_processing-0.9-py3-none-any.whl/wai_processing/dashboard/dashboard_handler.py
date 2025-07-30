import logging
import os
from pathlib import Path

import aiosqlite
from argconf import argconf_parse
from fastapi import WebSocket
from wai_processing import WAI_PROC_CONFIG_PATH

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dashboard")


class DashboardConnectionHandler(object):
    """
    Singleton class to manage the connection to SQLite db and websocket connections for the dashboard.
    This class ensures that only one instance of db is created and used throughout the application.
    """

    _instance = None

    def __new__(cls):
        """
        Override the __new__ method to implement the singleton pattern.
        Ensures that only one instance of the class is created.
        """
        if cls._instance is None:
            cls._instance = super(DashboardConnectionHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "dashboard" / "default.yaml")
        self.db_path = Path(self.cfg.db_log_root) / f"process_logs_{os.getlogin()}.db"
        self.columns = [
            "dataset",
            "scene",
            "stage",
            "state",
            "date",
            "message",
            "file_mtime",
        ]
        self.first_start = True
        self.datasets = self.filter_datasets_from_cfg()
        self.active_connections: list[WebSocket] = []

    def filter_datasets_from_cfg(self):
        """
        Filters datasets based on the configuration.
        This method iterates over all directories in the root path specified in the configuration,
        excluding any that are not directories or are explicitly excluded. If an 'include' list is
        provided in the configuration, only directories with names in this list are included.
        Returns:
            A list of Path objects representing the filtered datasets.
        """
        datasets = sorted(Path(self.cfg.root).iterdir())
        filtered_datasets = []
        for wai_path in datasets:
            dataset_name = wai_path.stem
            if not wai_path.is_dir() or dataset_name in self.cfg.exclude:
                continue
            if (self.cfg.get("include") is not None) and (
                dataset_name not in self.cfg.include
            ):
                continue
            filtered_datasets.append(wai_path)
        return filtered_datasets

    async def init_db_connection(self):
        """
        Initialize the connection to the SQLite database.
        Logs the connection attempt and establishes an asynchronous connection to the database.
        """
        logger.info(f"Connecting db: {self.db_path}")
        self.db = await aiosqlite.connect(self.db_path)

    async def close_db_connection(self):
        """
        Close the connection to the SQLite database.
        Logs the closure attempt and closes the asynchronous connection to the database.
        """
        logger.info(f"Closing db connection: {self.db_path}")
        await self.db.close()

    async def ws_connect(self, websocket: WebSocket):
        """
        Establishes a new WebSocket connection.
        Args:
            websocket (WebSocket): The WebSocket object representing the incoming connection.
        Notes:
            This method accepts the incoming connection and adds it to the list of active connections
            during start lifespan of application
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def ws_disconnect(self, websocket: WebSocket):
        """
        Closes an existing WebSocket connection.
        Args:
            websocket (WebSocket): The WebSocket object representing the connection to be closed.
        Notes:
            This method removes the connection from the list of active connections during end lifespan of application.
        """
        self.active_connections.remove(websocket)
