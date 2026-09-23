"""Deterministic extraction of resume sections and explicit technical skills."""

import re


SECTION_HEADERS = {
    "summary": {"summary", "professional summary", "profile", "objective"},
    "skills": {"skills", "technical skills", "technical proficiencies", "skills and tools"},
    "experience": {"experience", "work experience", "professional experience", "employment history"},
    "projects": {"projects", "personal projects", "selected projects", "academic projects"},
    "education": {"education", "academic background"},
    "certifications": {"certifications", "certificates"},
    "activities": {"activities", "leadership", "activities and leadership", "activities leadership"},
}
SKILL_PATTERNS = {
    "Python": r"(?<!\w)python(?!\w)",
    "JavaScript": r"(?<!\w)javascript(?!\w)",
    "TypeScript": r"(?<!\w)typescript(?!\w)",
    "Java": r"(?<!\w)java(?!\w)",
    "C++": r"(?<!\w)c\+\+(?!\w)",
    "C#": r"(?<!\w)c#(?!\w)",
    "Swift": r"(?<!\w)swift(?!\w)",
    "Kotlin": r"(?<!\w)kotlin(?!\w)",
    "Dart": r"(?<!\w)dart(?!\w)",
    "Go": r"(?<!\w)go(?!\w)",
    "Rust": r"(?<!\w)rust(?!\w)",
    "SQL": r"(?<!\w)sql(?!\w)",
    "React": r"(?<!\w)react(?:\.js)?(?!\w)",
    "React Native": r"(?<!\w)react native(?!\w)",
    "Next.js": r"(?<!\w)next(?:\.js)?(?!\w)",
    "Vue": r"(?<!\w)vue(?:\.js)?(?!\w)",
    "Angular": r"(?<!\w)angular(?!\w)",
    "Flutter": r"(?<!\w)flutter(?!\w)",
    "Android": r"(?<!\w)android(?!\w)",
    "iOS": r"(?<!\w)ios(?!\w)",
    "Node.js": r"(?<!\w)node(?:\.js)?(?!\w)",
    "Express": r"(?<!\w)express(?:\.js)?(?!\w)",
    "Django": r"(?<!\w)django(?!\w)",
    "Flask": r"(?<!\w)flask(?!\w)",
    "FastAPI": r"(?<!\w)fastapi(?!\w)",
    "Spring": r"(?<!\w)spring(?: boot)?(?!\w)",
    "PostgreSQL": r"(?<!\w)postgres(?:ql)?(?!\w)",
    "MySQL": r"(?<!\w)mysql(?!\w)",
    "MongoDB": r"(?<!\w)mongodb(?!\w)",
    "Redis": r"(?<!\w)redis(?!\w)",
    "Docker": r"(?<!\w)docker(?!\w)",
    "Kubernetes": r"(?<!\w)kubernetes(?!\w)",
    "AWS": r"(?<!\w)aws(?!\w)|amazon web services",
    "Azure": r"(?<!\w)azure(?!\w)",
    "Git": r"(?<!\w)git(?!\w)",
    "GitHub": r"(?<!\w)github(?!\w)",
    "Linux": r"(?<!\w)linux(?!\w)",
    "REST APIs": r"(?<!\w)rest(?:ful)? apis?(?!\w)",
    "GraphQL": r"(?<!\w)graphql(?!\w)",
    "TensorFlow": r"(?<!\w)tensorflow(?!\w)",
    "PyTorch": r"(?<!\w)pytorch(?!\w)",
    "NumPy": r"(?<!\w)numpy(?!\w)",
    "pandas": r"(?<!\w)pandas(?!\w)",
    "scikit-learn": r"(?<!\w)scikit[ -]learn(?!\w)",
}
BULLET_PREFIX = re.compile(r"^\s*(?:[-*•▪◦]|\d+[.)])\s+")
DATE_RANGE = re.compile(r"\b(?:19|20)\d{2}\s*[-–]\s*(?:(?:19|20)\d{2}|present)\b", re.IGNORECASE)


def _normalized_header(line: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", line.casefold()).strip()


def _section_name(line: str) -> str | None:
    header = _normalized_header(line)
    for section, aliases in SECTION_HEADERS.items():
        if header in aliases:
            return section
    return None


def _entries(section_text: str) -> list[str]:
    """Return paragraph-level entries without treating PDF text lines as entries.

    PDF text extraction is inconsistent about preserving bullet markers. Counting every
    non-bullet line after a bullet can turn one project into dozens of entries, so a
    blank line is the only reliable entry boundary used here.
    """
    entries = []
    for paragraph in re.split(r"\n\s*\n", section_text):
        lines = [
            cleaned
            for line in paragraph.splitlines()
            if (cleaned := BULLET_PREFIX.sub("", line).replace("\x7f", "").strip())
        ]
        if lines:
            entries.append("\n".join(lines))
    return entries


def _clean_lines(section_text: str) -> list[str]:
    return [
        cleaned
        for line in section_text.splitlines()
        if (cleaned := BULLET_PREFIX.sub("", line).replace("\x7f", "").strip())
    ]


def _technology_line(line: str) -> bool:
    """Recognize a project technology stack without inferring technologies."""
    normalized = line.casefold()
    recognized_skills = sum(bool(re.search(pattern, normalized)) for pattern in SKILL_PATTERNS.values())
    return recognized_skills >= 2


def _project_entries(section_text: str) -> list[str]:
    """Split projects at a title followed by a visible technology stack.

    Many PDF extractors remove blank lines between projects. Project titles followed by
    technology stacks are a more reliable boundary than treating every visual line as
    its own entry.
    """
    lines = _clean_lines(section_text)
    starts = [
        index
        for index in range(len(lines) - 1)
        if not _technology_line(lines[index]) and _technology_line(lines[index + 1])
    ]
    if not starts:
        return _entries(section_text)
    return ["\n".join(lines[start:end]).strip() for start, end in zip(starts, [*starts[1:], len(lines)])]


def _experience_entries(section_text: str) -> list[str]:
    """Split roles around visible date ranges when PDF spacing has been removed."""
    lines = _clean_lines(section_text)
    starts = []
    for index, line in enumerate(lines):
        if not DATE_RANGE.search(line):
            continue
        start = index if line.strip() != DATE_RANGE.search(line).group(0) else max(index - 1, 0)
        if start not in starts:
            starts.append(start)
    if len(starts) < 2:
        return _entries(section_text)
    return ["\n".join(lines[start:end]).strip() for start, end in zip(starts, [*starts[1:], len(lines)])]


def parse_resume_text(text: str) -> dict[str, object]:
    """Parse known sections and resume claims from extracted text.

    Skills are only reported when the exact named technology appears in the text;
    this is extraction, not an inference of proficiency.
    """
    sections: dict[str, list[str]] = {name: [] for name in SECTION_HEADERS}
    current_section: str | None = None

    for raw_line in text.splitlines():
        section = _section_name(raw_line)
        if section:
            current_section = section
            continue
        if current_section:
            sections[current_section].append(raw_line.rstrip())

    section_text = {
        section: "\n".join(lines).strip()
        for section, lines in sections.items()
        if "\n".join(lines).strip()
    }
    normalized_text = text.casefold()
    skills = [
        skill for skill, pattern in SKILL_PATTERNS.items() if re.search(pattern, normalized_text)
    ]

    return {
        "sections": section_text,
        "skills": skills,
        "experience": _experience_entries(section_text.get("experience", "")),
        "projects": _project_entries(section_text.get("projects", "")),
    }
