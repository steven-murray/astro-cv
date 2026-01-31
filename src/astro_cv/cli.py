"""CLI entry point for astro-cv."""

import cyclopts

app = cyclopts.App(name="astro-cv", help="Generate CVs and manage publications for academics.")


@app.command
def cv():
    """Generate CV and publication list from configuration."""
    from astro_cv import makecv
    
    makecv.main()


# Register pub_management subcommands
from astro_cv.pub_management import cli as pub_cli
app.command(pub_cli.app)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
