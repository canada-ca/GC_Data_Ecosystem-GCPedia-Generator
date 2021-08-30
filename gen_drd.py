#!/usr/bin/env python3
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas as pd
import urllib
import functools
import argparse
import sys

Element = namedtuple("Element", ["name", "url"])

CATEGORIES = {
    "Project/Initiative": {"Project/Initiative"},
    "Policy Instrument": {"Policy Instrument"},
    "Learning Resources": {"Data Glossary", "Learning Resource", "Working Document"},
    "Organizations and Teams": {"Organization", "Team"},
    "Communities": {"Working Group", "Committee", "Community"},
}


def df_to_elem(group) -> list[Element]:
    def make_elem(r):
        url = r["URL"] if not pd.isna(r["URL"]) else None
        return Element(r["Entity Name"], url)

    return [make_elem(r) for _, r in group.iterrows()]


def load_data(path) -> dict:
    df = (
        pd.read_csv(path, usecols=["Entity Full Name", "Type", "URL"])
        .dropna(subset=["Entity Full Name", "Type"])
        .reset_index(drop=True)
    )
    df["Entity Name"] = df["Entity Full Name"].str.strip()
    df.drop("Entity Full Name", axis=1, inplace=True)
    df["URL"] = df["URL"].str.strip()
    new_rows = {"Type": [], "URL": [], "Entity Name": []}
    for i, row in df.iterrows():
        types = [t.strip() for t in row["Type"].split(",")]
        for extra_type in types[1:]:
            new_rows["Type"].append(extra_type)
            new_rows["URL"].append(row["URL"])
            new_rows["Entity Name"].append(row["Entity Name"])
        df.iloc[i]["Type"] = types[0]
    df_long = pd.concat((df, pd.DataFrame.from_dict(new_rows))).reset_index(drop=True)
    return {tpl[0]: df_to_elem(tpl[1]) for tpl in df_long.groupby("Type")}


def recategorize(data: dict) -> dict:
    out = {k: [] for k in CATEGORIES.keys()}
    for k, subcats in CATEGORIES.items():
        for subc in subcats:
            if elems := data.get(subc):
                out[k] += elems
    return out


def format_link_text(item) -> str:
    return item.replace("/", f"/{chr(0x200b)}")


def gen_url(item) -> str:
    if "/" in item:
        return f"#{item.replace('/', '.2F')}"
    return f"#{urllib.parse.quote(item.replace(' ', '_'), safe='')}"


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Wikitext source for the Data Resource Directory GCpedia page."
    )
    parser.add_argument(
        "input",
        type=argparse.FileType("r"),
        help="Input file containing entity data.",
    )
    parser.add_argument(
        "-o",
        dest="output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Destination file to write to. Defaults to stdout.",
    )
    return parser


def main():
    args = make_parser().parse_args()
    data = recategorize(load_data(args.input))
    env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
    env.globals.update(format_link_text=format_link_text, gen_url=gen_url, data=data)
    template = env.get_template("drd.j2")
    args.output.write(template.render())


if __name__ == "__main__":
    main()
