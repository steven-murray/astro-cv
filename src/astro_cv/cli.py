"""CLI entry point for astro-cv."""

import cyclopts
from astro_cv.pub_management import cli as pub_cli
from pathlib import Path
import logging
from rich.logging import RichHandler


handler = RichHandler()
logging.basicConfig(
    level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[handler]
)
logger = logging.getLogger("astro_cv")

app = cyclopts.App(
    name="astro-cv", help="Generate CVs and manage publications for academics."
)


@app.command
def cv(
    profile: cyclopts.types.ExistingDirectory,
    output: cyclopts.types.ExistingDirectory = Path("outputs"),
):
    """Generate CV and publication list from configuration.

    Parameters
    ----------
    profile : ExistingDirectory
        Directory containing the CV configuration files (TOML).

        This directory must hold a `cv-settings.toml` file that specifies which sections
        to include and how to load data for each section. Each section's data should be
        provided in a separate TOML file within this directory, following the naming
        convention `<section-name>.toml` (e.g., `education.toml`,
        `research-interests.toml`).
    output : ExistingDirectory, optional
        Directory where output files will be written, by default "outputs".
    """
    from astro_cv import makecv

    makecv.main(profile, output_dir=output)


# Register pub_management subcommands
app.command(pub_cli.app)
