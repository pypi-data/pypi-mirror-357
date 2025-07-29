import json
import os
from typing import Any, Optional


class SaveKit:
    """
    SaveKit: A lightweight JSON-based key-value storage toolkit.

    This class allows storing, retrieving, updating, deleting, exporting, and importing
    data persistently using a local JSON file.

    Data is stored in a flat (non-nested) structure, where each entry is a key-value pair.
    Lazy loading is used: the file is not read until the data is accessed.

    Suitable for storing simple configuration values, user preferences, state flags, or cached data.

    Attributes:
        filename (str): Path to the JSON file used for storage.
        _data (dict): In-memory data store, loaded from the file on first access.

    Example:
        kit = SaveKit()
        kit.put("dark_mode", True)
        theme = kit.get("theme", "light")
        kit.export("backup.json")
    """

    def __init__(self, filename: str = 'savekit.json'):
        """
        Initializes the SaveKit instance with the specified JSON file path.

        Args:
            filename (str): Name or path of the JSON file to use for storage. Defaults to 'savekit.json'.
        """
        self.filename = filename
        self._data = None  # Data will be loaded lazily

    @property
    def data(self) -> dict:
        """
        Lazily loads and returns the in-memory data dictionary.

        Returns:
            dict: The loaded key-value data from the file.
        """
        if self._data is None:
            self._data = self._load_data()
        return self._data

    def _load_data(self) -> dict:
        """
        Reads the JSON file from disk and loads its contents into memory.

        Returns:
            dict: Parsed key-value data from the file.

        If the file doesn't exist or is corrupted, a new empty file is created.
        """
        if not os.path.exists(self.filename):
            self._create_empty_file()
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._create_empty_file()
            return {}

    def _create_empty_file(self):
        """Creates an empty JSON file with an empty dictionary structure."""
        with open(self.filename, 'w') as f:
            json.dump({}, f, indent=4)

    def _save(self):
        """Writes the current in-memory data to the JSON file on disk."""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def put(self, key: str, value: Any):
        """
        Inserts or updates a key-value pair in the data store.

        Args:
            key (str): The key name.
            value (Any): The value to store (must be JSON-serializable).
        """
        self.data[key] = value
        self._save()

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves the value associated with a given key.

        Args:
            key (str): The key to retrieve.
            default (Any, optional): The value to return if the key is not found. Defaults to None.

        Returns:
            Any: The stored value or the default.
        """
        return self.data.get(key, default)

    def remove(self, key: str):
        """
        Deletes a key-value pair from the data store, if it exists.

        Args:
            key (str): The key to remove.
        """
        if key in self.data:
            del self.data[key]
            self._save()

    def get_all(self) -> dict:
        """
        Returns all stored key-value pairs.

        Returns:
            dict: The entire data dictionary.
        """
        return self.data

    def reset(self):
        """
        Clears all stored data and resets the file to an empty state.
        """
        self._data = {}
        self._save()

    def export(self, export_path: str):
        """
        Saves the current data to another file (backup or external copy).

        Args:
            export_path (str): Destination file path for exporting the data.
        """
        with open(export_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def import_data(self, import_path: str):
        """
        Imports data from another JSON file, overwriting the current data.

        Args:
            import_path (str): Source file path to import data from.
        """
        with open(import_path, 'r') as f:
            self._data = json.load(f)
        self._save()

    def reload(self):
        """
        Reloads the data from the file, discarding any unsaved in-memory changes.
        """
        self._data = self._load_data()
