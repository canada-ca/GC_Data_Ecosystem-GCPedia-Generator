#!/usr/bin/env python3
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader, select_autoescape
import urllib

Element = namedtuple("Element", ["name", "url"])

CATEGORIES = [
    "About the Data Depot",
    "Data Glossary",
    "Community",
    "Learning Resource",
    "Project or Initiative",
    "Working Group",
    "Policy Instrument",
    "Team",
    "Organization",
    "Working Document",
    "Committee",
]


def df_to_elem(group):
    def make_elem(r):
        url = r["URL"] if not pd.isna(r["URL"]) else None
        return Element(r["Entity Name"], url)

    return [make_elem(r) for _, r in group.iterrows()]


def format_link_text(item):
    return item.replace("/", f"/{chr(0x200b)}")


def gen_url(item):
    if item != "About the Data Depot":
        page_name = f"Data depot:{item}".capitalize()
    else:
        page_name = "Data depot"
    return f"https://www.gcpedia.gc.ca/wiki/{urllib.parse.quote(page_name, safe='')}"


def main():
    env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
    env.globals.update(
        format_link_text=format_link_text, gen_url=gen_url, CATEGORIES=CATEGORIES
    )
    template = env.get_template("data_depot.j2")
    with open("data_depot_out.html", "w") as f:
        f.write(template.render())


if __name__ == "__main__":
    main()
