"""Deterministic extraction of resume sections and explicit technical skills."""

import re


SECTION_HEADERS = {
    "summary": {"summary", "professional summary", "profile", "objective"},
    "skills": {"skills", "technical skills", "technical proficiencies", "skills and tools"},
    "experience": {"experience", "work experience", "professional experience", "employment history"},
    "projects": {"projects", "personal projects", "selected projects", "academic projects"},
    "education": {"education", "academic background"},
    "certifications": {"certifications", "certificates"},
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


def _normalized_header(line: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", line.casefold()).strip()


def _section_name(line: str) -> str | None:
    header = _normalized_header(line)
    for section, aliases in SECTION_HEADERS.items():
        if header in aliases:
            return section
    return None


def _entries(section_text: str) -> list[str]:
    lines = [line.strip() for line in section_text.splitlines() if line.strip()]
    if any(BULLET_PREFIX.match(line) for line in lines):
        entries = []
        current_entry = []
        for line in lines:
            if BULLET_PREFIX.match(line):
                current_entry.append(BULLET_PREFIX.sub("", line).strip())
            else:
                if current_entry:
                    entries.append("\n".join(current_entry))
                current_entry = [line]
        if current_entry:
            entries.append("\n".join(current_entry))
        return entries
    return [entry.strip() for entry in re.split(r"\n\s*\n", section_text) if entry.strip()]


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
        "experience": _entries(section_text.get("experience", "")),
        "projects": _entries(section_text.get("projects", "")),
    }
