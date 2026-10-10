import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tools.build import build


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "assets").mkdir()
        (self.source / "assets/logo.png").write_bytes(b"original-logo")
        (self.source / "styles.css").write_text(
            'body{background:url("assets/logo.png")} @import "extra.css";')
        (self.source / "extra.css").write_text("body{color:red}")
        (self.source / "script.js").write_text("console.log('ok')")
        (self.source / "contact.vcf").write_text("BEGIN:VCARD\nEND:VCARD")
        (self.source / "index.html").write_text(
            '<link href="styles.css"><script src="script.js"></script>'
            '<img src="./assets/logo.png"><link href="assets/logo.png">'
            '<a href="contact.vcf" download="contact.vcf">Contact</a>'
            '<a href="tel:+524436155863">Call</a><a href="mailto:a@b.com">Mail</a>'
            '<link href="https://example.com/font.css?a=1&amp;b=2">')

    def run_build(self, name):
        output = self.root / name
        return build(self.source, output), output

    def test_stable_hashes_and_unchanged_sources(self):
        before = {p: p.read_bytes() for p in self.source.rglob("*") if p.is_file()}
        first, output = self.run_build("first")
        second, _ = self.run_build("second")
        self.assertEqual(first, second)
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)
        for name, sha in first["files"].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), sha)
        logo = first["assets"]["assets/logo.png"]
        self.assertEqual((output / logo).read_bytes(), b"original-logo")
        html = (output / "index.html").read_text()
        for path in first["assets"].values():
            if not path.startswith("extra."):
                self.assertIn(path, html)
        self.assertIn('download="contact.vcf"', html)
        self.assertIn("tel:+524436155863", html)
        self.assertIn("mailto:a@b.com", html)
        self.assertIn("https://example.com/font.css?a=1&amp;b=2", html)

    def test_dependency_changes_invalidate_css(self):
        first, _ = self.run_build("first")
        (self.source / "assets/logo.png").write_bytes(b"new-logo")
        second, output = self.run_build("second")
        self.assertNotEqual(first["assets"]["styles.css"], second["assets"]["styles.css"])
        self.assertNotEqual(first["assets"]["assets/logo.png"],
                            second["assets"]["assets/logo.png"])
        self.assertEqual(first["assets"]["script.js"], second["assets"]["script.js"])
        css = (output / second["assets"]["styles.css"]).read_text()
        self.assertIn(second["assets"]["assets/logo.png"], css)
        self.assertIn(second["assets"]["extra.css"], css)

    def test_changed_script_and_contact(self):
        first, _ = self.run_build("first")
        for name in ("script.js", "contact.vcf"):
            with (self.source / name).open("a") as stream:
                stream.write("\nchanged")
        second, _ = self.run_build("second")
        for name in ("script.js", "contact.vcf"):
            self.assertNotEqual(first["assets"][name], second["assets"][name])

    def test_missing_resource_fails(self):
        (self.source / "assets/logo.png").unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.run_build("bad")

    def test_circular_css_fails(self):
        (self.source / "extra.css").write_text('@import "styles.css";')
        with self.assertRaisesRegex(ValueError, "Circular"):
            self.run_build("bad")

    def test_output_cannot_overwrite_sources(self):
        with self.assertRaises(ValueError):
            build(self.source, self.source)
        self.run_build("first")
        with self.assertRaises(ValueError):
            build(self.source, self.root / "first")


if __name__ == "__main__":
    unittest.main()
