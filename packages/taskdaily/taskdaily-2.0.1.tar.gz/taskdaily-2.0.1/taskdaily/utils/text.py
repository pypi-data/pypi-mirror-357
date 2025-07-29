"""Text utilities for TaskDaily."""

import re
from typing import Dict, List, Tuple


def is_emoji(char: str) -> bool:
    """Check if a character is an emoji.

    Args:
        char: Character to check

    Returns:
        True if character is an emoji
    """
    # Emoji ranges in Unicode
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+"
    )
    return bool(emoji_pattern.match(char))


def clean_section_header(header: str) -> tuple[str, str]:
    """Clean section header to extract emoji and name.

    Args:
        header: Raw section header string

    Returns:
        Tuple of (emoji, name)
    """
    parts = header.strip().split(" ", 1)
    emoji = parts[0].strip()
    name = parts[1].strip() if len(parts) > 1 else ""
    return emoji, name


def split_into_sections(content: str) -> dict[str, list[str]]:
    """Split content into sections.

    Args:
        content: Raw markdown content

    Returns:
        Dictionary mapping section headers to lists of task lines
    """
    if not content.strip():
        return {}

    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    current_tasks: list[str] = []

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        # Check if line is a section header (starts with emoji)
        if line and is_emoji(line[0]):
            if current_section:
                sections[current_section] = current_tasks
            current_section = line
            current_tasks = []
        elif current_section and line.startswith("- "):
            current_tasks.append(line)

    # Add last section
    if current_section:
        sections[current_section] = current_tasks

    return sections
