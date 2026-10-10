import functools
import http.server
import tempfile
import threading
import unittest
from pathlib import Path
from tools.build import build
from tools.verify_deploy import verify


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class DeployVerificationTests(unittest.TestCase):
    def test_served_content_and_detected_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "index.html").write_text('<link href="styles.css">')
            (source / "styles.css").write_text("body{color:red}")
            # Serve below a project prefix, as GitHub Pages does.
            output = root / "public" / "dragon-systems-card"
            manifest = build(source, output)
            handler = functools.partial(QuietHandler, directory=str(output.parent))
            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_port}/dragon-systems-card/"
                verify(url, output, attempts=1)
                (output / manifest["assets"]["styles.css"]).write_text("stale content")
                with self.assertRaisesRegex(ValueError, "differs"):
                    verify(url, output, attempts=1)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
