import json
from pathlib import Path
from string import Template

dir_ = Path(__file__).parent
with open(dir_ / "template.hurl", "r") as file:
    hurl_file_template = Template(file.read())
for topic in ("building-count", "roads"):
    for region in ("heidelberg", "frankfurt", "rhineland-palatinate"):
        for ohsomedb in ("true", "false"):
            with open(Path(dir_ / region).with_suffix(".geojson"), "r") as f:
                bpolys = json.load(f)
            hurl_file = hurl_file_template.substitute(
                base_url="https://api.quality.ohsome.org/v1-test",
                indicator="currentness",
                topic=topic,
                bpolys=json.dumps(bpolys),
                ohsomedb=ohsomedb,
            )
            ohsomedb_text = "-ohsomedb" if ohsomedb == "true" else ""
            path = Path(dir_) / f"indicator-{topic}-{region}{ohsomedb_text}.hurl"
            with open(path, "w") as f:
                f.write(hurl_file)
