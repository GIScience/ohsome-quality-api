import os

from jinja2 import Environment, FileSystemLoader


def get_template(name):
    env = get_env()
    if name == "indicator":
        return env.get_template("indicator_template.html")
    elif name == "report":
        return env.get_template("report_template.html")
    else:
        raise ValueError("Template name has to be 'indicator' or 'report'.")


def get_env():
    path = os.path.dirname(os.path.abspath(__file__))
    return Environment(loader=FileSystemLoader(path))


def get_traffic_light(label, red="#bbb", yellow="#bbb", green="#bbb"):
    dot_css = (
        "style='height: 25px; width: 25px; background-color: {0};"
        "border-radius: 50%; display: inline-block;'"
    )
    return (
        "<span {0} class='dot'></span>\n<span {1} class='dot'>"
        "</span>\n<span {2} class='dot'></span>\n {3}".format(
            dot_css.format(red),
            dot_css.format(yellow),
            dot_css.format(green),
            label,
        )
    )
