from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from check_site import ReferenceParser, check_reference


class CheckReferenceTests(unittest.TestCase):
    def test_local_page_fragments_are_checked(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            index = root / "index.html"
            notes = root / "notes.html"
            index.write_text('<main id="top"></main><a name="legacy"></a>', encoding="utf-8")
            notes.write_text('<section id="summary"></section>', encoding="utf-8")
            index_parser = ReferenceParser()
            index_parser.feed(index.read_text(encoding="utf-8"))
            notes_parser = ReferenceParser()
            notes_parser.feed(notes.read_text(encoding="utf-8"))
            page_ids = {
                index.resolve(): index_parser.ids,
                notes.resolve(): notes_parser.ids,
            }

            self.assertIsNone(
                check_reference(index, "#top", site_root=root, page_ids=page_ids)
            )
            self.assertIsNone(
                check_reference(index, "#legacy", site_root=root, page_ids=page_ids)
            )
            self.assertIsNone(
                check_reference(index, "notes.html#summary", site_root=root, page_ids=page_ids)
            )
            self.assertIn(
                "missing fragment",
                check_reference(index, "#missing", site_root=root, page_ids=page_ids) or "",
            )
            self.assertIn(
                "missing fragment",
                check_reference(index, "notes.html#missing", site_root=root, page_ids=page_ids) or "",
            )


if __name__ == "__main__":
    unittest.main()
