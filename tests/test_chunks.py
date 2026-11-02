import unittest

from ai4eo.rag.chunks import build_chunks, chunk_id


def by_blank_line(text):
    return text.split("\n\n")


TEXT = "First paragraph.\n\nSecond paragraph.\n\n\n\nThird paragraph."


class ChunkTests(unittest.TestCase):
    def test_ids_are_deterministic_and_text_sensitive(self):
        self.assertEqual(chunk_id("s", 0, "a"), chunk_id("s", 0, "a"))
        self.assertNotEqual(chunk_id("s", 0, "a"), chunk_id("s", 0, "b"))
        self.assertNotEqual(chunk_id("s", 0, "a"), chunk_id("s", 1, "a"))
        self.assertNotEqual(chunk_id("s", 0, "a"), chunk_id("t", 0, "a"))

    def test_builds_chunks_with_metadata(self):
        chunks = build_chunks(
            TEXT,
            source="CWC bulletin 12",
            split_fn=by_blank_line,
            doc_type="bulletin",
            region="Assam",
            published="2024-07-05",
        )
        texts = ["First paragraph.", "Second paragraph.", "Third paragraph."]
        self.assertEqual([c.text for c in chunks], texts)
        first = chunks[0]
        self.assertEqual(first.metadata["region"], "Assam")
        self.assertEqual(first.metadata["published"], "2024-07-05")
        self.assertEqual(first.metadata["chunk_index"], "0")
        self.assertEqual(first.source, "CWC bulletin 12")
        self.assertEqual(len({c.id for c in chunks}), 3)

    def test_empty_parts_skipped_and_empty_metadata_omitted(self):
        chunks = build_chunks(TEXT, source="s", split_fn=by_blank_line)
        self.assertEqual(len(chunks), 3)
        self.assertNotIn("region", chunks[0].metadata)

    def test_rebuild_is_stable(self):
        a = build_chunks(TEXT, source="s", split_fn=by_blank_line)
        b = build_chunks(TEXT, source="s", split_fn=by_blank_line)
        self.assertEqual([c.id for c in a], [c.id for c in b])

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            build_chunks(TEXT, source="", split_fn=by_blank_line)
        with self.assertRaises(ValueError):
            build_chunks(TEXT, source="s", split_fn=by_blank_line, published="5 July 2024")


if __name__ == "__main__":
    unittest.main()
