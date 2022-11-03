cv_generator
------------


This project uses a Google Spreadsheet and a few config options to produce a LaTeX CV.


Setup
-----
Setting up ``gspread``:

Do ``pip install gspread`` and ``pip install oauth2client``.
Go to https://console.developers.google.com/cloud-resource-manager, and make a new project.
Click on that project, go to "Service accounts", create new service account and save the JSON key into the top-level
directory of this package (i.e. alongside this README file).
Go to your spreadsheet, and share the sheet with the email generated as your Service account ID.

Setting up ``ads``: see https://ads.readthedocs.io/en/latest/

