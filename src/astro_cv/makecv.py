"""Generate CV from modular sections - generic modular approach."""

import importlib
import os
import tomllib
from pathlib import Path
import logging
from astro_cv.formats.latex import compile_latex, write_section
from astro_cv.structure import document
from astro_cv.data_connectors.toml import DataConnector as LocalTOMLConnector

logger = logging.getLogger(__name__)


def load_cv_settings(config_dir: Path) -> dict:
    """Load general CV settings from TOML file.

    Args:
        config_dir: Directory containing cv-settings.toml

    Returns:
        Dictionary of CV settings
    """
    config_file = config_dir / "cv-settings.toml"
    with open(config_file, "rb") as f:
        return tomllib.load(f)


def initialize_data_connectors(data_connectors_config: dict) -> dict:
    # Setup each integration
    connectors = {"toml": LocalTOMLConnector()}
    for name, dc_config in data_connectors_config.items():
        connector_name = dc_config.pop("data_connector", name)
        logger.info(
            f"Setting up data connector '{name}' with connector '{connector_name}'"
        )

        # Import the connector module
        connector_module = importlib.import_module(
            f"astro_cv.data_connectors.{connector_name}"
        )
        DataConnector = getattr(connector_module, "DataConnector")

        for k, v in dc_config.items():
            if isinstance(v, str) and v.startswith("env:"):
                env_var = v[4:]
                v = os.environ.get(env_var)
                if v is None:
                    raise ValueError(
                        f"Environment variable '{env_var}' not set for connector '{name}'"
                    )

                dc_config[k] = v
                logger.info(
                    f"Loaded environment variable '{env_var}' for connector '{name}'"
                )

        connectors[name] = DataConnector(**dc_config)

    return connectors


def get_section_data(section_name: str, config_dir: Path, connectors: dict):
    logger.info(f"Processing section: {section_name}")

    section_file = config_dir / (section_name + ".toml")

    # Load section config
    with open(section_file, "rb") as f:
        section_config = tomllib.load(f)

    # Determine which connector to use
    connector_name = section_config.get("data_connector", "toml")

    # Import the connector module
    try:
        connector = connectors[connector_name]
    except KeyError:
        logger.error(
            f"Data connector '{connector_name}' not found for section '{section_name}'"
        )
        return

    return connector.get(section_name, section_file)


def main(config_dir: Path, output_dir: Path = Path("outputs")):
    """Main entry point for CV generation.

    Processes each section by:
    1. Loading the section's TOML configuration
    2. Determining the data connector to use
    3. Fetching data via the connector
    4. Rendering the section to LaTeX
    5. Appending to the CV body

    Args:
        config_dir: Directory containing TOML configuration files
        output_dir: Directory where output files will be written
    """
    config_dir = Path(config_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Load general settings
    settings = load_cv_settings(config_dir)
    sections_to_include = settings.get("sections", [])
    data_connectors = settings.get("data_connectors", {})
    connectors = initialize_data_connectors(data_connectors)

    # Load contact information early to get firstname/surname for document
    contact_info = get_section_data("contact-information", config_dir, connectors)

    # Initialize document with name
    doc = document.replace("{%firstname%}", contact_info.personal.firstname)
    doc = doc.replace("{%surname%}", contact_info.personal.surname)

    body = ""
    publist = ""

    # Process sections in order
    for section_name in sections_to_include:
        if section_name == "contact-information":
            data = contact_info
        else:
            data = get_section_data(section_name, config_dir, connectors)
            if data is None:
                continue

        section_latex = write_section(section_name, data)
        # section_key = section_name.replace("-", "_")
        # section_module = importlib.import_module(f"astro_cv.sections.{section_key}")

        # # Render section to LaTeX
        # section_latex = section_module.create(data)

        # Append to body (publications are handled separately)
        # if section_key == "publications":
        #     publist = section_latex

        #     # Write standalone publication list
        #     logger.info("Writing standalone publication list to outputs/publist.pdf")
        #     pubdoc = doc.replace(r"{%body%}", publist)
        #     pubdoc = pubdoc.replace(r"{%doctype%}", "Publication List")

        #     publist_tex = output_dir / "publist.tex"
        #     with open(publist_tex, "w") as f:
        #         f.write(pubdoc)

        #     compile_latex(publist_tex, output_dir=output_dir)
        # else:
        body += section_latex

    # Finalize document
    doc = doc.replace(r"{%doctype%}", "C.V.")

    # Generate CV variants
    for kind in ["nopubs", "full"]:
        if kind == "full":
            final_doc = doc.replace(r"{%body%}", body + publist)
        elif kind == "nopubs":
            final_doc = doc.replace(r"{%body%}", body)

        cvname = f"cv_{kind}.tex"
        cv_path = output_dir / cvname

        logger.info(
            f"""Writing CV with{"out" if kind == "nopubs" else ""} publist at {cv_path}"""
        )

        # Write out a tex file
        with open(cv_path, "w") as f:
            f.write(final_doc)

        # Compile the Document
        compile_latex(cv_path, output_dir=output_dir)
