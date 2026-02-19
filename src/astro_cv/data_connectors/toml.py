"""Local TOML file data connector for CV sections.

This connector loads data directly from TOML files, using the section's
read_toml() method to instantiate the appropriate dataclass.
"""

import importlib
from pathlib import Path
from typing import Any


class DataConnector:
    """Load data from local TOML files.

    This connector uses the section module's read_toml() method to load
    and parse TOML configuration files into the appropriate dataclass.
    """

    def get(self, section_name: str, config_path: Path | str) -> Any:
        """Load section data from local TOML file.

        Parameters
        ----------
        section_name : str
            Name of the section (e.g., 'education', 'research_interests').
        config_path : Path or str
            Path to the TOML configuration file.

        Returns
        -------
        Any
            The dataclass instance loaded from the TOML file.
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # Convert section name to class name (e.g., education -> Education)
        class_name = "".join(
            word.capitalize() for word in section_name.replace("-", "_").split("_")
        )

        # Get the dataclass from the module
        section_key = section_name.replace("-", "_")
        section_module = importlib.import_module(f"astro_cv.sections.{section_key}")

        if hasattr(section_module, class_name):
            DataClass = getattr(section_module, class_name)
        else:
            # Try common alternatives if the conversion didn't work
            raise AttributeError(
                f"Could not find class {class_name} in module {section_module.__name__}"
            )

        # Use the dataclass's read_toml method
        return DataClass.read_toml(config_path)
