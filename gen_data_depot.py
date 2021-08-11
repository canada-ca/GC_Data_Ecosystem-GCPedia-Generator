#!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader, select_autoescape

SECTIONS = [
    "About the Data Depot",
    "Data Glossary",
    "Annotation",
    "Committee",
    "Community",
    "Data Sources",
    "Learning Resources",
    "Organization",
    "Other",
    "Policy Instruments",
    "Projects/Initiatives",
    "Team",
    "Working Document",
    "Working Group",
]


def main():
    env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
    template = env.get_template("data_depot.j2")
    with open("build/data_depot_out.html", "w") as f:
        f.write(template.render(sections=SECTIONS))



if __name__ == "__main__":
    main()
