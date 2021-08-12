#!/usr/bin/env python3
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas as pd

Element = namedtuple("Element", ["name", "url"])


def df_to_elem(group):
    def make_elem(r):
        url = r["URL"] if not pd.isna(r["URL"]) else None
        return Element(r["Entity Name"], url)

    return [make_elem(r) for _, r in group.iterrows()]


# TODO: Split URL
def load_data() -> dict:
    df = (
        pd.read_csv("entities_master.csv", usecols=["Entity Full Name", "Type", "URL"])
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


def main():
    env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
    template = env.get_template("data_depot.j2")
    with open("data_depot_out.html", "w") as f:
        f.write(template.render(data=load_data()))


if __name__ == "__main__":
    main()
