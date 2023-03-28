"""
Sitelog parser for the specific purpose of extracting the data needed in the
STA-file.

Given

*   Sitelog with sections 1 through 4, extract needed fields to produce station
    history in a STA-file.

"""
import re
import logging
import collections as cs
from typing import Any


log = logging.getLogger(__name__)

# META
SECTION_NUMBER = re.compile(r"[0-9]+\.([1-9]+|x)?")


def is_whitespace(s: str) -> bool:
    return not bool(s.strip())


def is_section(s: str) -> bool:
    return SECTION_NUMBER.match(s) is not None


def parse(sitelog: str) -> None:
    """
    Opinionated sitelog parser in that it taks only the so far needed sections.

    """
    # Remove (so far) unnecessary lines
    sitelog = sitelog[sitelog.find("1.   Site Identification of the GNSS Monument") :]
    sitelog = sitelog[: sitelog.find("5.   Surveyed Local Ties")]

    # Clean up
    sitelog = sitelog.strip()

    # Remove empty lines
    lines = [line.rstrip() for line in sitelog.splitlines() if not is_whitespace(line)]

    # Slice into sections and subsections
    start_indices = [
        index for (index, line) in enumerate(lines) if is_section(line.split()[0])
    ]

    # Combine the start and end indices of each (sub)section
    slices = [
        slice(beg, end) for (beg, end) in zip(start_indices[:-1], start_indices[1:])
    ]
    slices.append(slice(start_indices[-1], -1))

    # Group subsections with sections
    """
    Create the following structure:
    {
        '1': {
            content: <section_lines>,
        },
        '2': {
            content: <section_lines>,
        },
        '3': {
            content: <section_lines>,
            subsections: [
                <subsection_lines>,
                <subsection_lines>,
                ...,
            ]
        },
        '4': {
            content: <section_lines>,
            subsections: [
                <subsection_lines>,
                <subsection_lines>,
                ...,
            ]
        }
    }
    """
    sections = cs.defaultdict(lambda: cs.defaultdict(list))
    for s in slices:
        section_lines = lines[s]
        content = "\n".join(section_lines)

        # '3.1  Receiver Type'              => ['3', '1  Receiver Type']
        # '3.   GNSS Receiver Information'  => ['3', '   GNSS Receiver Information']
        section_number, post_part = section_lines[0].split(".", maxsplit=1)

        # '1  Receiver Type'                => ['1', 'Receiver', 'Type'][0]
        # '   GNSS Receiver Information'    => ['GNSS', 'Receiver', 'Information'][0]
        subsection_number = post_part.split()[0]  # .strip()

        if subsection_number.lower() == "x":
            continue

        if subsection_number.isdigit():
            sections[section_number]["subsections"].append(content)
            continue

        sections[section_number]["content"] = content

    return sections


def main():
    # TODO (JM): Remove this debugging method
    from rich import print
    from ab import pkg

    sections = parse(pkg.demo_sitelog.read_text())
    print(sections)


if __name__ == "__main__":
    main()
