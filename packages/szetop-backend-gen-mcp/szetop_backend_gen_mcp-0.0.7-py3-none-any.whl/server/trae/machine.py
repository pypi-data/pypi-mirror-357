import logging
import os
import platform
from pathlib import Path

import json5

logger = logging.getLogger(__name__)


class Machine:
    @staticmethod
    def __get_code_storage_path() -> Path:
        """
        获取存储路径
        :return:
        """
        system = platform.system()
        if system == "Windows":
            base_path = Path(os.getenv("APPDATA"))
        elif system == "Darwin":  # macOS
            base_path = Path.home() / "Library" / "Application Support"
        elif system == "Linux":
            base_path = Path.home() / ".config"
        else:
            raise OSError("Unsupported OS")
        return Path(base_path) / "Trae CN" / "User" / "globalStorage" / "storage.json"

    @staticmethod
    def get_machine_id() -> str | None:
        """
        获取机器ID
        :return: 机器Id
        """
        storage_path = Machine.__get_code_storage_path()
        if not storage_path.exists():
            return None

        with open(storage_path, "r", encoding="utf-8") as f:
            try:
                storage = json5.load(f)
                return storage.get("telemetry.machineId")
            except Exception as e:
                logger.error(f"Failed to parse storage file {storage_path}: {e}")
