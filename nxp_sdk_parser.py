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


class Core(object):
    def __init__(self, name: str, fpu: bool, dsp: bool):
        self.name = name
        self.fpu = fpu
        self.dsp = dsp


class Device(object):
    def __init__(
        self, name: str, cores: List[Core], packages: List[str], defines: List[str]
    ):
        self.name = name
        self.cores = cores
        self.packages = packages
        self.defines = defines

    def get_defines(self, package, core) -> List[str]:
        if package not in self.packages:
            raise ValueError()
        cores = [c.name for c in self.cores]
        if core not in cores:
            raise ValueError()

        defines = []
        for d in self.defines:
            defines.append(
                d.replace("$|package|", package).replace("$|core_name|", core)
            )
        return defines


class SDK(object):
    def __init__(self):
        pass

    @classmethod
    def parse(cls, dir):
        xmlfile = glob(os.path.join(dir, "a.xml"))
        if len(xmlfile) != 1:
            print(f"SDK meta file not found in {dir}", file=sys.stderr)
            raise FileNotFoundError()
        xmlfile = xmlfile[0]

        tree = ET.parse(xmlfile)
        root = tree.getroot()

        # find devices
        devices = []
        devices_meta = root.findall("./devices/device")
        for meta in devices_meta:
            packages = []
            defines = []
            cores = []
            mems = []
            for one in meta.findall("./package"):
                packages.append(one.attrib["name"])
            for one in meta.findall("./defines/define"):
                defines.append(one.attrib["name"])
            for one in meta.findall("./core"):
                name = one.attrib["name"]
                fpu = True if one.attrib["fpu"] == "true" else False
                dsp = True if one.attrib["dsp"] == "true" else False
                cores.append(Core(name, fpu, dsp))
            for one in meta.findall("./memory/memoryBlock"):
                pass
            devices.append(Device(meta.attrib["name"], cores, packages, defines))

        # find drivers
        drivers = {}
        for device in devices:
            drivers[device.name] = {}
        comps = root.findall("./components/component")
        # for comp in comps:
        #     id = comp.attrib["id"]
        #     if (not id.startswith("platform.drivers.")) or (
        #         not id.startswith("platform.devices.")
        #     ):
        #         pass
        for comp in comps:
            id = comp.attrib["id"]
            process = False

            if id.startswith("platform.drivers."):
                process = True
                id = id.removeprefix("platform.drivers.")

            if id.startswith("platform.devices."):
                process = True
                id = id.removesuffix("platform.devices.")

            if not process:
                continue

        return cls()


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
    xmlfile = xmlfile[0]

    tree = ET.parse(xmlfile)
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

    required = args.drivers
    required = set(required)
    fin = set()

    for c in required:
        if not c in map:
            print(f"{c} not found, ignore it", file=sys.stderr)
            continue
        fin.add(c)

    while True:
        last_len = len(fin)
        required.clear()
        for c in fin:
            if not c in map:
                print(f"{c} not found, ignore it", file=sys.stderr)
                continue
            for dep in map[c].dependencies:
                required.add(dep)
        fin = fin.union(required)
        if len(fin) == last_len:
            break

    srcs = set()
    driver_path = os.path.join(args.sdk_root, f"devices/{device}/drivers")
    for c in fin:
        d = map[c]
        for f in d.srcs:
            srcs.add(os.path.abspath(os.path.join(driver_path, f)))
    print(*srcs, sep=";")


if __name__ == "__main__":
    main()
