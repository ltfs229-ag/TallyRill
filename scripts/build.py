"""Build the self-contained, offline HTML application with Python 3.10+."""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def build():
    html = read("src/layout.html")
    samples = [read(f"examples/catalog-{side}.csv") for side in ("before", "after")]
    substitutions = {
        "__ICON__": "data:image/svg+xml;base64," + base64.b64encode((ROOT/"media/mark.svg").read_bytes()).decode(),
        "__CSS__": read("src/style.css"),
        "__WORKER__": read("src/engine.js") + "\n" + read("src/worker.js"),
        "__SAMPLES__": "const samples = " + json.dumps(samples).replace("<", "\\u003c") + ";",
        "__I18N__": read("src/strings.js"), "__APP__": read("src/app.js")
    }
    for marker, body in substitutions.items():
        html = html.replace(marker, body)
    out = ROOT/"build/TallyRill.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    return out

if __name__ == "__main__":
    print(build().name)

