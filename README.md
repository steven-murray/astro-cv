# astro-cv

**The best way to compile your CV if you're an astro academic.**

## Install

Clone the repo and do ``uv sync`` in the top-level.


## Configuration

To build a CV, you need to create a configuration directory with TOML files containing your CV data.

### Quick Start

The easiest way to get started is to use the minimal example configuration directory:

```bash
cp -r minimal-config-example my-cv-config
```

Then edit the files in `my-cv-config/` with your own information. The minimal example includes:
- `cv-settings.toml` – Main configuration file specifying which sections to include
- `contact-information.toml` – Contact details and personal information
- `research-interests.toml` – Your research interests
- `education.toml` – Educational background

### Configuration Structure

A configuration directory needs:

1. **cv-settings.toml** – Main settings file that specifies:
   - `sections`: ordered list of section names to include in the CV (using kebab-case)
   - `[data_connectors.*]`: configuration for data sources (Google Sheets, NASA ADS, GitHub, or local TOML files)

2. **Section TOML files** – One file per section (e.g., `education.toml`, `publications.toml`). Each section has its own schema defined by the corresponding dataclass in `src/astro_cv/sections/`.

### Available Sections

The following sections can be included in your CV:
- `contact-information`
- `education`
- `research-interests`
- `technical-skills`
- `professional-experience`
- `academic-experience`
- `software`
- `publications`
- `presentations`
- `press-releases`
- `awards-and-scholarships`
- `academic-references`

## Data Connectors

You can populate your CV data from multiple sources:

- **TOML** – Load data directly from local TOML files (no configuration needed)
- **Google Sheets** – Load data from Google Sheets with `gspread` authentication
- **NASA ADS** – Automatically fetch publication data from NASA ADS
- **GitHub** – Load data from GitHub (e.g., for the software section)

Specify which connectors to use (and any setup options) in `cv-settings.toml`, and then
associate each section with a connector in its respective TOML file.

### Setting Up `gsheets`

Setting up `gspread`:

Do `pip install gspread` and `pip install oauth2client`.
Go to https://console.developers.google.com/cloud-resource-manager, and make a new project.
Click on that project, go to "Service accounts", create new service account and save the
JSON key into a file at your standard app config location:
`~/.config/astro-cv/authorization_key.json` (on Linux).
The connector now loads this path automatically via `appdirs`.
If you prefer a custom location, you can still set
`[data_connectors.gsheet] auth_file = "..."` in `cv-settings.toml`.
Go to your spreadsheet, and share the sheet with the email generated as your Service
account ID.

## Setting Up `ads`

See https://ads.readthedocs.io/en/latest/ for setting up your API key (which must
be stored at `~/.ads`).

Once this is done, create an ADS library that contains all of your works, and add the
following to `cv-settings.toml`:

```
[data_connectors.ads]
library_id = "<library_id_from_ads>"
```

There are tools in `astro-cv` for managing your publication list as well (see
section on CLI below).

## Setting Up `github`

To get the `github` data connector to work (for producing the "Software" section), you'll
need to create a [Personal Access Token](https://github.com/settings/tokens) with read
permissions. Then you need to save that token as an environment variable (it shouldn't
be written to the config file in case you store your CV data/config on github!).

For isntance you could add `export GITHUB_TOKEN=<YOUR_GITHUB_TOKEN>` to the end of your
`.bashrc` or `.zshrc` etc.


## Using the CLI

To compile your CV, use:

```
uv run astro-cv cv --profile my-profile-folder --output folder-to-store-tex-and-pdf/
```

The profile folder should have the `cv-settings.toml` file in it.

To manage your publication list on NASA ADS, use

```
uv run astro-cv manage-pubs ads
```

This is configured by a TOML file, of which an example is in
`minimal-config-example/ads/config.toml`. It should define both a "positive" library
that is managed to contain all of your work, and a "negative" library which will
contain false positives --- i.e. papers that are found in a search based on your
search criteria, but aren't yours.

The method is to build a search criteriaon that as closely as possible finds all your
papers and no more (though it's better that it finds all your papers and a few extras
rather than missing some of your papers). This search is defined by other parameters
you'll see in the minimal config example, like your name, year you started publishing,
and the institutions you've published in. The script will perform that search, and then
inform you of any papers found that are not in _either_ the positive or negative library,
and ask you if you'd like to add it to your papers (if you say no, it'll go in the
negative library and you'll never see it again).
