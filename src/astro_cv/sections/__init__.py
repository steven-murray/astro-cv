"""Sections package for CV generation.

This package contains submodules for each CV section, with:
- datatype.py: attrs-based configuration classes with .read_toml() methods
- processing.py: LaTeX generation logic for the section
"""

from . import academic_references, contact_information, education

__all__ = ["academic_references", "contact_information", "education"]
