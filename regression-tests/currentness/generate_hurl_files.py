import json
from pathlib import Path
from string import Template

dir = Path(__file__).parent
with open(dir / "template.hurl", "r") as file:
    hurl_file_template = Template(file.read())
for topic in ("building-count", "roads"):
    for region in ("heidelberg", "frankfurt", "rhineland-palatinate"):
        for ohsomedb in ("true", "false"):
            with open(Path(dir / region).with_suffix(".geojson"), "r") as f:
                bpolys = json.load(f)
            hurl_file = hurl_file_template.substitute(
                base_url="https://api.quality.ohsome.org/v1-test",
                indicator="currentness",
                topic=topic,
                bpolys=json.dumps(bpolys),
                ohsomedb=ohsomedb,
            )
            if ohsomedb == "true":
                ohsomedb_text = "-ohsomedb"
            else:
                ohsomedb_text = ""
            path = Path(dir) / f"indicator-{topic}-{region}{ohsomedb_text}.hurl"
            with open(path, "w") as f:
                f.write(hurl_file)
