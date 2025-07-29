from textwrap import dedent


def clean_prompt(prompt: str) -> str:
    """Clean a prompt string.

    Steps performed:
    1. Remove leading/trailing whitespace using ``textwrap.dedent``.
    2. Remove lines that start with ``#`` (treated as comments).
    3. Strip empty lines at the beginning and end of the prompt.
    4. Remove leftover indentation from each remaining line.

    Parameters
    ----------
    prompt:
        The raw prompt string.

    Returns
    -------
    str
        A cleaned prompt string ready for consumption by an LLM.
    """

    # First dedent to normalize overall whitespace and remove common indentation
    cleaned = dedent(prompt)

    # Split into lines and remove lines starting with '#' or empty lines,
    # then remove any remaining indentation from each line.
    lines = cleaned.split("\n")
    cleaned_lines = [
        line.lstrip()
        for line in lines
        if not line.lstrip().startswith("#") and line.strip()
    ]

    # Join the cleaned lines back together and strip leading/trailing whitespace once more
    return "\n".join(cleaned_lines).strip() 