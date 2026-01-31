"""CLI entry point for astro-cv."""

import cyclopts
from astro_cv.pub_management import cli as pub_cli

app = cyclopts.App(
    name="astro-cv", help="Generate CVs and manage publications for academics."
)


@app.command
def cv():
    """Generate CV and publication list from configuration."""
    from astro_cv import makecv

    makecv.main()


# Register pub_management subcommands
app.command(pub_cli.app)

