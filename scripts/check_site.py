"""Small, dependency-free checks for the static GitHub Pages site."""

from html.parser import HTMLParser
from pathlib import Path
from typing import Collection
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class ReferenceParser(HTMLParser):
    """Collect local resource references and element ids from one HTML file."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.ids.add(element_id)
        anchor_name = attributes.get("name") if tag == "a" else None
        if anchor_name:
            self.ids.add(anchor_name)
        for name in ("href", "src"):
            value = attributes.get(name)
            if value:
                self.references.append(value)


def check_reference(
    source: Path,
    reference: str,
    *,
    site_root: Path = ROOT,
    page_ids: dict[Path, Collection[str]] | None = None,
) -> str | None:
    """Return an error for a broken local reference, otherwise ``None``."""

    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc:
        return None

    if not parsed.path:
        target = source
    elif parsed.path.startswith("/"):
        target = site_root / unquote(parsed.path).lstrip("/")
    else:
        target = source.parent / unquote(parsed.path)

    try:
        target = target.resolve()
        target.relative_to(site_root.resolve())
    except ValueError:
        return f"{source.relative_to(site_root)} points outside the site: {reference}"

    if not target.exists():
        return f"{source.relative_to(site_root)} points to missing file: {reference}"
    if parsed.fragment and target.suffix.lower() == ".html" and page_ids is not None:
        ids = page_ids.get(target)
        if ids is not None and unquote(parsed.fragment) not in ids:
            return f"{source.relative_to(site_root)} points to missing fragment: {reference}"
    return None


def main() -> int:
    html_files = sorted(ROOT.rglob("*.html"))
    errors: list[str] = []
    pages: dict[Path, ReferenceParser] = {}

    for html_file in html_files:
        parser = ReferenceParser()
        try:
            parser.feed(html_file.read_text(encoding="utf-8-sig"))
            parser.close()
        except (OSError, UnicodeError) as error:
            errors.append(f"{html_file.relative_to(ROOT)} cannot be read: {error}")
            continue

        pages[html_file] = parser

        if html_file == ROOT / "index.html":
            required_ids = {"main-content", "now", "notes", "work", "about"}
            missing_ids = required_ids - parser.ids
            if missing_ids:
                errors.append(
                    "index.html is missing required sections: "
                    + ", ".join(sorted(missing_ids))
                )

    homepage_parser = pages.get(ROOT / "index.html")
    if homepage_parser is None:
        errors.append("index.html is missing")
    else:
        homepage_references = set(homepage_parser.references)
        for note in sorted((ROOT / "notes").glob("*.html")):
            reference = f"notes/{note.name}"
            if reference not in homepage_references:
                errors.append(f"index.html does not list note: {reference}")

    page_ids = {path.resolve(): parser.ids for path, parser in pages.items()}
    reference_count = 0
    for html_file, parser in pages.items():
        for reference in parser.references:
            reference_count += 1
            error = check_reference(html_file, reference, page_ids=page_ids)
            if error:
                errors.append(error)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        f"Checked {len(html_files)} HTML files and "
        f"{reference_count} references; local references are valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
