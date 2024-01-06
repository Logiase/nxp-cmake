import argparse
import os
import sys
from glob import glob
from typing import List
from xml.etree import ElementTree as ET


class DriverMeta(object):
    def __init__(self, id, dependencies: List[str], srcs: List[str]):
        self.id = id
        self.dependencies = dependencies
        self.srcs = srcs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk_root", required=True)
    parser.add_argument("drivers", nargs="+")
    return parser.parse_args()


def main():
    args = parse_args()

    xmlfile = glob(os.path.join(args.sdk_root, "*.xml"))
    if not len(xmlfile) == 1:
        print(f"SDK meta file not found in {args.sdk_root}", file=sys.stderr)
        exit(1)

    required = args.drivers
    required = set(required)


if __name__ == "__main__":
    main()


required = ["flexio_mculcd_smartdma"]
required = set(required)
fin = set(required)

tree = ET.parse("./test.xml")
root = tree.getroot()
device = root.attrib["name"]

map = {}

comps = root.findall("./components/")
for comp in comps:
    id = comp.attrib["id"]
    if not id.startswith("platform.drivers."):
        continue
    id = id.removeprefix("platform.drivers.").removesuffix("." + device)

    dependencies = []
    deps = comp.findall("./dependencies/all/component_dependency")
    for dep in deps:
        dep_id = dep.attrib["value"]
        if not dep_id.startswith("platform.drivers."):
            continue
        dependencies.append(
            dep_id.removeprefix("platform.drivers.").removesuffix("." + device)
        )
    deps = comp.findall("./dependencies/component_dependency")
    for dep in deps:
        dep_id = dep.attrib["value"]
        if not dep_id.startswith("platform.drivers."):
            continue
        dependencies.append(
            dep_id.removeprefix("platform.drivers.").removesuffix("." + device)
        )

    sources = []
    srcs = comp.findall("./source/")
    for src in srcs:
        fname = src.attrib["mask"]
        if not fname.endswith(".c"):
            continue
        sources.append(fname)

    map[id] = DriverMeta(id, dependencies, sources)


while True:
    last_len = len(fin)
    required.clear()

    for c in fin:
        for dep in map[c].dependencies:
            required.add(dep)
    fin = fin.union(required)
    print(f"required: {required}\n\rfin: {fin}")

    if len(fin) == last_len:
        break


print(fin)
