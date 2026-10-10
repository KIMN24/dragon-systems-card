"""Compare the published HTML and assets against the exact build artifact."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen


def verify(base_url, output, attempts=8, delay=15):
    manifest = json.loads((Path(output) / "asset-manifest.json").read_text())
    for attempt in range(attempts):
        try:
            for name, expected in manifest["files"].items():
                request = Request(base_url.rstrip("/") + "/" + name,
                                  headers={"Cache-Control": "no-cache"})
                with urlopen(request, timeout=20) as response:
                    actual = hashlib.sha256(response.read()).hexdigest()
                if actual != expected:
                    raise ValueError(f"Published content differs: {name}")
            print("Published HTML and all resources match the build artifact")
            return
        except (OSError, ValueError) as error:
            if attempt == attempts - 1:
                raise
            print(f"Waiting for Pages propagation: {error}", flush=True)
            time.sleep(delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--output", type=Path, default=Path("_site"))
    args = parser.parse_args()
    verify(args.url, args.output)
