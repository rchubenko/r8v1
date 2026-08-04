"""Small deterministic checks for the repository foundation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md",
    "README.md",
    "docs/architecture.md",
    "docs/isa.md",
    "docs/microarchitecture.md",
    "docs/control-word.md",
    "docs/memory.md",
    "docs/repository-structure.md",
    "docs/adr/README.md",
    "docs/plans/milestone-0-repository-foundation.md",
    "docs/reports/architecture-inception.md",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ADR_FILE_RE = re.compile(r"^([0-9]{4})-.*\.md$")
ADR_HEADING_RE = re.compile(r"^# ADR-([0-9]{4}):")


def check_required() -> list[str]:
    return [path for path in REQUIRED if not (ROOT / path).is_file()]


def check_links() -> list[str]:
    errors: list[str] = []
    for document in sorted(ROOT.rglob("*.md")):
        for target in LINK_RE.findall(document.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (document.parent / target_path).resolve()
            if not resolved.is_file():
                errors.append(f"{document.relative_to(ROOT)} -> {target}")
    return errors


def check_adrs() -> list[str]:
    errors: list[str] = []
    adr_dir = ROOT / "docs" / "adr"
    files: dict[str, list[Path]] = {}
    headings: dict[str, list[Path]] = {}
    for path in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
        match = ADR_FILE_RE.match(path.name)
        if match:
            files.setdefault(match.group(1), []).append(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            heading = ADR_HEADING_RE.match(line)
            if heading:
                headings.setdefault(heading.group(1), []).append(path)
    for number, paths in files.items():
        if len(paths) != 1:
            errors.append(f"ADR-{number}: expected one file, found {len(paths)}")
    for number, paths in headings.items():
        if len(paths) != 1:
            errors.append(f"ADR-{number}: expected one heading, found {len(paths)}")
    index = (adr_dir / "README.md").read_text(encoding="utf-8")
    indexed = re.findall(r"ADR-([0-9]{4})\]\(([^)]+)\)", index)
    indexed_numbers = [number for number, _ in indexed]
    if len(indexed_numbers) != len(set(indexed_numbers)):
        errors.append("ADR index contains duplicate numbers")
    if set(indexed_numbers) != set(files):
        errors.append("ADR index does not match ADR files")
    if indexed_numbers.count("0005") != 1:
        errors.append("ADR-0005 must occur exactly once in the active index")
    if "0010" not in indexed_numbers:
        errors.append("ADR-0010 is missing from the active index")
    return errors


def check_architecture_constants() -> list[str]:
    errors: list[str] = []
    control_word = (ROOT / "docs" / "control-word.md").read_text(encoding="utf-8")
    memory = (ROOT / "docs" / "memory.md").read_text(encoding="utf-8")
    isa = (ROOT / "docs" / "isa.md").read_text(encoding="utf-8")
    if "Width:** 16 bit" not in control_word:
        errors.append("control-word width is not 16 bit")
    if "4096" not in memory or "0xFFF" not in memory:
        errors.append("memory contract does not contain 4096 and 0xFFF")
    if "0xB`–`0xE" not in isa and "0xB..0xE" not in isa:
        errors.append("reserved opcode range is missing")
    active_sources = (
        ROOT / "docs" / "architecture.md",
        ROOT / "docs" / "isa.md",
        ROOT / "docs" / "microarchitecture.md",
        ROOT / "docs" / "control-word.md",
        ROOT / "docs" / "memory.md",
        ROOT / "docs" / "adr" / "0005-flags-update-on-a-write.md",
    )
    for document in active_sources:
        for line in document.read_text(encoding="utf-8").splitlines():
            lower = line.lower()
            allowed_negative = (
                "no independent" in lower
                or "нет independent" in lower
                or "отсутствует independent" in lower
                or "отсутствует" in lower
                or "would" in lower
                or "дал бы" in lower
            )
            if "FLAGS_LOAD" in line and "FLAGS_LOAD_INTERNAL" not in line and not allowed_negative:
                errors.append(f"possible independent FLAGS_LOAD in {document.relative_to(ROOT)}")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(f"missing required document: {path}" for path in check_required())
    errors.extend(f"broken Markdown link: {error}" for error in check_links())
    errors.extend(check_adrs())
    errors.extend(check_architecture_constants())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Documentation and architecture checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
