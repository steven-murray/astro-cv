"""Generate LaTeX for technical skills section."""

from .datatype import TechnicalSkill


def create(data: TechnicalSkill) -> str:
    """Generate LaTeX for technical skills section.

    Parameters
    ----------
    data : TechnicalSkill
        Technical skills data.

    Returns
    -------
    str
        LaTeX formatted section content.
    """
    out = []

    def colonlist_to_sentence(text: str) -> str:
        """Convert colon-separated list to sentence."""
        return " and".join(text.replace(";", ",").rsplit(",", 1))

    if data.OSProficient:
        out.append(
            f"Proficiency with {colonlist_to_sentence(data.OSProficient)} operating systems."
        )

    if data.OSUsed:
        oses = colonlist_to_sentence(data.OSUsed)
        out.append(f"Working knowledge of {oses} operating systems")

    if data.LanguageProficient:
        langs = colonlist_to_sentence(data.LanguageProficient)
        msg = f"Intimate knowledge of a variety of programming languages, in particular {langs}"

        if data.LanguageUsed:
            msg += (
                f", and to varying extents {colonlist_to_sentence(data.LanguageUsed)}."
            )
        else:
            msg += "."

        out.append(msg)
    elif data.LanguageUsed:
        out.append(
            f"Basic knowledge of {colonlist_to_sentence(data.LanguageUsed)} programming languages."
        )

    if data.SoftwareProficient:
        msg = f"In-depth experience with {colonlist_to_sentence(data.SoftwareProficient)} programs and frameworks"

        if data.SoftwareUsed:
            msg += (
                f", and to varying extents {colonlist_to_sentence(data.SoftwareUsed)}."
            )
        else:
            msg += "."

        out.append(msg)
    elif data.SoftwareUsed:
        out.append(
            f"Experience with {colonlist_to_sentence(data.SoftwareUsed)} programs and frameworks."
        )

    return "\n\n".join(out)
