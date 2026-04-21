from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY_ROOT = ROOT / "data" / "01_raw" / "pdfs" / "library"
DEFAULT_FIRST_PASS_CSV = ROOT / "data" / "01_raw" / "pdfs" / "paper_register_first_pass.csv"
DEFAULT_FIRST_PASS_MD = ROOT / "data" / "01_raw" / "pdfs" / "paper_register_first_pass.md"

CSV_FIELDS = [
    "paper_id",
    "title",
    "doi",
    "family",
    "structure_main_class",
    "structure_subtype_list",
    "status",
    "file_path",
]

CANONICAL_FIELDS = [
    "paper_id",
    "family",
    "structure_main_class",
    "structure_subtype_list",
    "title",
    "authors_raw",
    "year",
    "doi",
    "status",
    "source_path",
    "library_path",
    "notes",
]

DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s<>\]\)]+", re.I)
TITLE_STOP_PREFIXES = (
    "abstract",
    "summary",
    "keywords",
    "index terms",
    "received",
    "available online",
    "article history",
    "highlight",
    "highlights",
    "introduction",
)
TITLE_BLOCK_PREFIXES = (
    "int.",
    "doi:",
    "pii:",
    "printed in",
    "copyright",
    "elsevier",
    "graphical abstract",
)
TITLE_BLOCK_CONTAINS = (
    "vol.",
    "no.",
    "pp.",
    "elsevier",
    "all rights reserved",
    "printed in great britain",
    "department",
    "university",
    "institute",
    "laborator",
    "school",
    "college",
    "corresponding author",
    "email",
)
AUTHOR_LINE_RE = re.compile(r"\b[A-Z]\.\s*[A-Z]\.")


def _normalize_text(value: object | None) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace("\u00ad", "").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _normalize_line(value: object | None) -> str:
    return _normalize_text(value)


def _slugify(value: str) -> str:
    text = re.sub(r"[^0-9a-zA-Z]+", "_", _normalize_text(value).lower())
    return re.sub(r"_+", "_", text).strip("_")


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _match_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _looks_generic_title(title: str) -> bool:
    lowered = title.lower()
    if not lowered:
        return True
    if lowered.startswith(("pii", "doi", "untitled")):
        return True
    if lowered.startswith("s") and re.fullmatch(r"s\d{4}[-\d/x()]+", lowered):
        return True
    if len(title) < 8:
        return True
    return False


def _is_blocked_line(line: str) -> bool:
    lowered = line.lower()
    if not line:
        return True
    if any(lowered.startswith(prefix) for prefix in TITLE_BLOCK_PREFIXES):
        return True
    if any(token in lowered for token in TITLE_BLOCK_CONTAINS):
        return True
    if AUTHOR_LINE_RE.search(line):
        return True
    if "@" in line:
        return True
    if lowered.startswith(("page ", "doi ", "doi/", "article info")):
        return True
    return False


def _title_score(line: str) -> int:
    if _is_blocked_line(line):
        return -1
    words = line.split()
    if len(words) < 3:
        return -1
    if len(words) > 28:
        return -1
    score = len(words) * 3 + len(line)
    if line.isupper():
        score += 18
    if any(char.islower() for char in line):
        score += 6
    if any(char.isdigit() for char in line):
        score -= 2
    if "," in line and len(words) <= 6:
        score -= 2
    return score


def _extract_first_page_text(reader: PdfReader) -> str:
    if not reader.pages:
        return ""
    raw_text = unicodedata.normalize("NFKC", reader.pages[0].extract_text() or "")
    raw_text = raw_text.replace("\u00ad", "").replace("\xa0", " ")
    return raw_text


def _extract_doi_from_text(text: str) -> str:
    match = DOI_RE.search(text)
    if match is None:
        return ""
    doi = match.group(0).rstrip(").,;")
    if doi.lower().startswith("doi:"):
        doi = doi[4:].strip()
    return doi


def _extract_title_from_text(first_page_text: str, metadata_title: str, file_stem: str) -> str:
    if metadata_title and not _looks_generic_title(metadata_title):
        return metadata_title

    lines = [_normalize_line(line) for line in first_page_text.splitlines()]
    title_lines: list[str] = []
    collecting = False

    for line in lines:
        if not line:
            continue
        lowered = line.lower()
        if any(lowered.startswith(prefix) for prefix in TITLE_STOP_PREFIXES):
            break
        score = _title_score(line)
        if not collecting:
            if score >= 12:
                collecting = True
                title_lines.append(line)
            continue
        if score >= 10:
            title_lines.append(line)
            continue
        break

    if title_lines:
        return _collapse_spaces(" ".join(title_lines))

    if metadata_title:
        return metadata_title

    return _collapse_spaces(file_stem.replace("_", " "))


def _extract_abstract_from_text(first_page_text: str) -> str:
    lines = [_normalize_line(line) for line in first_page_text.splitlines()]
    start_index = None
    inline_prefix = ""

    for index, line in enumerate(lines):
        lowered = line.lower()
        if lowered.startswith("summary"):
            start_index = index
            inline_prefix = line[len("summary") :].strip(" :-")
            break
        if lowered.startswith("abstract"):
            start_index = index
            inline_prefix = line[len("abstract") :].strip(" :-")
            break

    if start_index is None:
        return ""

    collected: list[str] = []
    if inline_prefix and "article info" not in inline_prefix.lower():
        collected.append(inline_prefix)

    for line in lines[start_index + 1 :]:
        lowered = line.lower()
        if not line:
            continue
        if lowered.startswith(
            (
                "1. introduction",
                "introduction",
                "keywords",
                "key words",
                "index terms",
                "references",
                "acknowledgments",
                "acknowledgements",
            )
        ):
            break
        if lowered.startswith(("article history", "received", "available online", "highlights", "graphical abstract")):
            continue
        if line.startswith("•"):
            continue
        if _is_blocked_line(line):
            continue
        collected.append(line)

    return _collapse_spaces(" ".join(collected))


def _classify_structure_main_class(family: str, title: str, text: str) -> str:
    if family == "honeycomb":
        return "honeycomb_2d"

    combined = f"{title}\n{text}".lower()

    if any(
        token in combined
        for token in (
            "hybrid plate-rod",
            "plate-rod",
            "sopl",
            "hybrid tpms",
            "hybrid lattice",
            "combining a hollow rhombic dodecahedron and six cylindrical tubes",
            "combining",
        )
    ) and any(token in combined for token in ("tube", "rod", "plate", "strut", "shell", "dodecahedron", "octet-plate")):
        return "hybrid_lattice"

    if any(
        token in combined
        for token in (
            "triply periodic minimal surface",
            "tpms",
            "gyroid",
            "diamond",
            "primitive",
            "frd",
            "iwp",
            "sheet-based 3d periodic",
        )
    ):
        return "tpms"

    if "voronoi" in combined:
        return "voronoi"

    if any(
        token in combined
        for token in (
            "bio-inspired",
            "bio inspired",
            "bioinspired",
            "biomimetic",
            "bionic honeycomb",
            "bionic lattice",
            "biomimetic honeycomb",
            "biomimetic lattice",
        )
    ):
        return "bioinspired"

    if any(token in combined for token in ("plate lattice", "plate-based", "shell lattice")):
        return "plate_lattice"

    if any(token in combined for token in ("tube lattice", "tubular lattice", "cylindrical tube", "tubes")):
        return "tube_lattice"

    if any(
        token in combined
        for token in (
            "truss-lattice",
            "truss lattice",
            "bcc",
            "octet",
            "octagonal unit cell",
            "octagonal",
            "unit cell topology",
            "cell topology",
            "bending-dominated",
            "stretch-dominated",
            "buckling-dominated",
            "strut",
            "struts",
            "beam lattice",
            "rod-based",
            "fcc",
        )
    ):
        return "truss_lattice"

    if "spatial lattice" in combined:
        return "unknown"

    return "unknown"


def _classify_structure_subtypes(family: str, structure_main_class: str, title: str, text: str) -> list[str]:
    combined = f"{title}\n{text}".lower()
    subtypes: list[str] = []

    general_rules: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("bioinspired", (r"\bbio[- ]?inspired\b", r"\bbiomimetic\b")),
        ("bionic_honeycomb", (r"\bbionic honeycomb\b", r"\bbiomimetic honeycomb\b")),
    )
    honeycomb_rules: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("hierarchical", (r"\bhierarchical\b",)),
        ("auxetic", (r"\bauxetic\b",)),
        ("circular_celled", (r"circular[- ]celled", r"circular[- ]cell(?:ed)?")),
        ("star", (r"\bstar[- ]auxetic\b", r"\bstar[- ]shaped\b", r"\bstar honeycomb\b")),
        ("petal_shaped", (r"petal[- ]shaped",)),
        ("vertex_based", (r"vertex[- ]based",)),
        ("triangular_substructures", (r"triangular substructures?",)),
        ("nested", (r"\bnested\b",)),
    )
    tpms_rules: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("sheet_based", (r"sheet[- ]based",)),
        ("hybrid_tpms", (r"hybrid tpms", r"hybrid triply periodic minimal surface")),
        ("primitive", (r"\bprimitive\b",)),
        ("gyroid", (r"\bgyroid\b",)),
        ("diamond", (r"\bdiamond\b",)),
    )
    truss_rules: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("bcc", (r"\bbccz?\b",)),
        ("octet", (r"\boctet\b",)),
        ("kagome", (r"\bkagome\b",)),
        ("tetrahedral", (r"\btetrahedral\b",)),
        ("octahedral", (r"\boctahedral\b",)),
        ("auxiliary_struts", (r"auxiliary struts?",)),
    )
    plate_rules: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("plate_rod", (r"plate[- ]rod",)),
        ("plate_based", (r"plate[- ]based",)),
    )
    tube_rules: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("tube", (r"\btube\b",)),
        ("tubular", (r"\btubular\b",)),
        ("cylindrical_tube", (r"cylindrical tube",)),
    )
    voronoi_rules: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("voronoi", (r"\bvoronoi\b",)),
    )

    for subtype, patterns in general_rules:
        if _match_any(combined, patterns):
            subtypes.append(subtype)

    if family == "honeycomb":
        for subtype, patterns in honeycomb_rules:
            if _match_any(combined, patterns):
                subtypes.append(subtype)

    if structure_main_class == "tpms":
        for subtype, patterns in tpms_rules:
            if _match_any(combined, patterns):
                subtypes.append(subtype)

    if structure_main_class == "truss_lattice":
        for subtype, patterns in truss_rules:
            if _match_any(combined, patterns):
                subtypes.append(subtype)

    if structure_main_class == "plate_lattice":
        for subtype, patterns in plate_rules:
            if _match_any(combined, patterns):
                subtypes.append(subtype)

    if structure_main_class == "tube_lattice":
        for subtype, patterns in tube_rules:
            if _match_any(combined, patterns):
                subtypes.append(subtype)

    if structure_main_class == "voronoi":
        for subtype, patterns in voronoi_rules:
            if _match_any(combined, patterns):
                subtypes.append(subtype)

    if structure_main_class == "hybrid_lattice":
        for subtype, patterns in tpms_rules + plate_rules + tube_rules + truss_rules:
            if _match_any(combined, patterns):
                subtypes.append(subtype)

    return _unique_preserve_order(subtypes)


def _find_paper_dirs(library_root: Path) -> Iterable[Path]:
    if not library_root.exists():
        raise FileNotFoundError(f"library root not found: {library_root}")
    for family_dir in sorted(path for path in library_root.iterdir() if path.is_dir()):
        for paper_dir in sorted(path for path in family_dir.iterdir() if path.is_dir()):
            pdf_path = paper_dir / "original.pdf"
            if pdf_path.exists():
                yield pdf_path


def extract_register_row(pdf_path: Path) -> dict[str, str]:
    family = pdf_path.parent.parent.name
    paper_id = pdf_path.parent.name
    reader = PdfReader(str(pdf_path))
    metadata = reader.metadata
    first_page_text = _extract_first_page_text(reader)
    abstract_text = _extract_abstract_from_text(first_page_text)
    metadata_title = ""
    metadata_doi = ""
    if metadata is not None:
        metadata_title = _normalize_text(getattr(metadata, "title", "") or metadata.get("/Title", ""))
        metadata_doi = _normalize_text(getattr(metadata, "doi", "") or metadata.get("/doi", "") or metadata.get("/DOI", ""))

    title = _extract_title_from_text(first_page_text, metadata_title, pdf_path.stem)
    doi = _extract_doi_from_text(metadata_doi or first_page_text)
    classification_text = abstract_text or first_page_text
    structure_main_class = _classify_structure_main_class(family, title, classification_text)
    structure_subtype_list = _classify_structure_subtypes(family, structure_main_class, title, classification_text)
    status = "needs_review" if structure_main_class == "unknown" else "identified"

    return {
        "paper_id": paper_id,
        "title": title,
        "doi": doi,
        "family": family,
        "structure_main_class": structure_main_class,
        "structure_subtype_list": ";".join(structure_subtype_list),
        "status": status,
        "file_path": str(pdf_path),
    }


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "| " + " | ".join(CSV_FIELDS) + " |"
    divider = "|" + "|".join(["---"] * len(CSV_FIELDS)) + "|"
    lines = ["# First Pass Paper Register", "", header, divider]
    for row in rows:
        cells = [row[field].replace("|", r"\|") for field in CSV_FIELDS]
        lines.append("| " + " | ".join(cells) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _canonical_rows_from_first_pass(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    canonical_rows: list[dict[str, str]] = []
    for row in rows:
        canonical_rows.append(
            {
                "paper_id": row["paper_id"],
                "family": row["family"],
                "structure_main_class": row["structure_main_class"],
                "structure_subtype_list": row["structure_subtype_list"],
                "title": row["title"],
                "authors_raw": "",
                "year": "",
                "doi": row["doi"],
                "status": row["status"],
                "source_path": row["file_path"],
                "library_path": row["file_path"],
                "notes": "manual review required" if row["status"] == "needs_review" else "",
            }
        )
    return canonical_rows


def _write_canonical_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_canonical_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "| " + " | ".join(CANONICAL_FIELDS) + " |"
    divider = "|" + "|".join(["---"] * len(CANONICAL_FIELDS)) + "|"
    lines = ["# Paper Register", "", header, divider]
    for row in rows:
        cells = [row[field].replace("|", r"\|") for field in CANONICAL_FIELDS]
        lines.append("| " + " | ".join(cells) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_first_pass_register(
    library_root: Path | str = DEFAULT_LIBRARY_ROOT,
    csv_path: Path | str = DEFAULT_FIRST_PASS_CSV,
    md_path: Path | str = DEFAULT_FIRST_PASS_MD,
) -> list[dict[str, str]]:
    library_root = Path(library_root)
    csv_path = Path(csv_path)
    md_path = Path(md_path)
    rows = [extract_register_row(pdf_path) for pdf_path in _find_paper_dirs(library_root)]
    rows.sort(key=lambda row: (row["family"], row["paper_id"]))
    _write_csv(csv_path, rows)
    _write_markdown(md_path, rows)
    return rows


def build_canonical_register(
    first_pass_rows: list[dict[str, str]],
    csv_path: Path | str = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.csv",
    md_path: Path | str = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.md",
) -> list[dict[str, str]]:
    csv_path = Path(csv_path)
    md_path = Path(md_path)
    canonical_rows = _canonical_rows_from_first_pass(first_pass_rows)
    _write_canonical_csv(csv_path, canonical_rows)
    _write_canonical_markdown(md_path, canonical_rows)
    return canonical_rows


def build_pdf_register_bundle(
    library_root: Path | str = DEFAULT_LIBRARY_ROOT,
    first_pass_csv: Path | str = DEFAULT_FIRST_PASS_CSV,
    first_pass_md: Path | str = DEFAULT_FIRST_PASS_MD,
    canonical_csv: Path | str = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.csv",
    canonical_md: Path | str = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.md",
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    first_pass_rows = build_first_pass_register(library_root, first_pass_csv, first_pass_md)
    canonical_rows = build_canonical_register(first_pass_rows, canonical_csv, canonical_md)
    return first_pass_rows, canonical_rows


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the first-pass PDF paper register")
    parser.add_argument("--library-root", type=Path, default=DEFAULT_LIBRARY_ROOT)
    parser.add_argument("--csv", type=Path, default=DEFAULT_FIRST_PASS_CSV)
    parser.add_argument("--md", type=Path, default=DEFAULT_FIRST_PASS_MD)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    first_pass_rows, canonical_rows = build_pdf_register_bundle(args.library_root, args.csv, args.md)
    print(f"first-pass rows written: {len(first_pass_rows)}")
    print(f"canonical rows written: {len(canonical_rows)}")
    print(f"csv written: {args.csv}")
    print(f"markdown written: {args.md}")
    print(f"canonical csv written: {ROOT / 'data' / '01_raw' / 'pdfs' / 'paper_register.csv'}")
    print(f"canonical markdown written: {ROOT / 'data' / '01_raw' / 'pdfs' / 'paper_register.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
