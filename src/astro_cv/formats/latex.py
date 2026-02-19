"""LaTeX formatting utilities."""

import contextlib
import importlib
import os
import subprocess
from pathlib import Path


def custom_format(string, brackets, *args, **kwargs):
    """
    Format strings like str.format(*args, **kwargs), except with brackets instead of {}.

    Copied from https://stackoverflow.com/a/40877821/1467820.
    """
    if len(brackets) != 2:
        raise ValueError(f"Expected two brackets. Got {len(brackets)}.")
    padded = string.replace("{", "{{").replace("}", "}}")
    substituted = padded.replace(brackets[0], "{").replace(brackets[1], "}")
    return substituted.format(*args, **kwargs)


def myformat(string, *args, escape_amp=True, **kwargs):
    """Format function with LaTeX escaping.

    Uses custom brackets '<% %>' instead of '{}' for template substitution.
    Automatically escapes ampersands (&) to LaTeX-safe format (\\&).

    Args:
        string: Template string with '<% %>' placeholders
        *args: Positional arguments for substitution
        escape_amp: Whether to escape ampersands (default: True)
        **kwargs: Keyword arguments for substitution

    Returns:
        Formatted string with LaTeX-safe content
    """
    # Any substitution should be text, and so "&" symbols must be escaped.
    if escape_amp:
        args = list(args)
        for i in range(len(args)):
            with contextlib.suppress(AttributeError):
                args[i] = args[i].replace("&", r"\&")
        for k in kwargs:
            with contextlib.suppress(AttributeError):
                kwargs[k] = kwargs[k].replace("&", r"\&")
    return custom_format(string, ["<% ", " %>"], *args, **kwargs)


def write_section(section_name, data):
    section_key = section_name.replace("-", "_")
    section_module = importlib.import_module(f"astro_cv.sections.{section_key}")

    # Render section to LaTeX
    section_latex = section_module.create(data)

    section_title = section_name.replace("-", " ").title()
    out = r"\section{%s}%%" % section_title
    out += "\n\t"
    out += "\n\t".join(section_latex.split("\n"))
    out += "\n\n"
    return out


def compile_latex(
    tex_file: str | Path, output_dir: str | Path | None = None, quiet: bool = True
) -> int:
    """Compile a LaTeX file to PDF.

    Runs pdflatex twice to ensure references are resolved.

    Args:
        tex_file: Path to the .tex file to compile
        output_dir: Directory containing the tex file (will cd here for compilation)
        quiet: If True, suppress pdflatex output (default: True)

    Returns:
        Exit code from the last pdflatex run
    """
    tex_file = Path(tex_file)

    if output_dir is None:
        output_dir = tex_file.parent
    else:
        output_dir = Path(output_dir)

    # Store original directory
    original_dir = Path.cwd()

    try:
        # Change to output directory
        os.chdir(output_dir)

        # Create log file name
        log_file = tex_file.stem + ".log"

        # Build pdflatex command
        cmd = ["pdflatex", "-synctex=1", "-interaction=nonstopmode", tex_file.name]

        # Run pdflatex twice to resolve references
        exit_code = 0
        for i in range(2):
            if quiet:
                # Redirect output to log file
                with open(log_file, "w" if i == 0 else "a") as logf:
                    result = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT)
                    exit_code = result.returncode
            else:
                result = subprocess.run(cmd)
                exit_code = result.returncode

        return exit_code
    except Exception as e:
        print(f"Error compiling LaTeX: {e}")
        return -1
    finally:
        # Always return to original directory
        os.chdir(original_dir)
