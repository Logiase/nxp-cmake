import argparse
import os
import sys
import re
from glob import glob
from typing import List
from xml.etree import ElementTree as ET

driver_regex = r"platform\.(drivers|devices)\.(.*?(?=\.))\.(.*)"


class DriverMeta(object):
    def __init__(self, id, dependencies: List[str], srcs: List[str]):
        self.id = id
        self.dependencies = dependencies
        self.srcs = srcs


class Driver(object):
    def __init__(self, name, dependencies: List[str], srcs: List[str]):
        self.name = name
        self.dependencies = dependencies
        self.srcs = srcs

    @classmethod
    def parse(cls, node: ET.Element) -> "Driver":
        name = node.attrib["name"]
        dependencies = []
        dependencie_nodes = [
            *node.findall("./dependencies/component_dependency"),
            *node.findall("./dependencies/all/component_dependency"),
        ]
        for n in dependencie_nodes:
            matches = re.findall(driver_regex, n.attrib["value"])
            if len(matches) != 1:
                continue
            matches = matches[0]
            if matches[0] != "drivers":
                continue
            dependencies.append(matches[1])
        srcs = []
        src_nodes = node.findall("./source[@type='src']")
        for src_node in src_nodes:
            for file_node in src_node.findall("./files"):
                srcs.append(
                    os.path.join(
                        node.attrib["package_base_path"],
                        src_node.attrib["relative_path"],
                        file_node.attrib["mask"],
                    )
                )

        return cls(name, dependencies, srcs)


class Core(object):
    def __init__(self, name: str, fpu: bool, dsp: bool):
        self.name = name
        self.fpu = fpu
        self.dsp = dsp

    @classmethod
    def parse(cls, node: ET.Element):
        name = node.attrib["name"]
        fpu = True if node.attrib["fpu"] == "true" else False
        dsp = True if node.attrib["dsp"] == "true" else False
        return cls(name, fpu, dsp)


class Device(object):
    def __init__(
        self,
        name: str,
        cores: List[Core],
        packages: List[str],
        defines: List[str],
        drivers: dict[str, Driver],
    ):
        self.name = name
        self.cores = cores
        self.packages = packages
        self.defines = defines
        self.drivers = drivers

    def get_defines(self, package: str, core: str) -> List[str]:
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

    def append_driver(self, driver: Driver):
        self.drivers.append(driver)

    def append_drivers(self, drivers: List[Driver]):
        self.drivers.extend(drivers)


class SDK(object):
    def __init__(self, devices: dict[str, Device]):
        self.devices = devices

    def get_device(self, name):
        if name is None and len(self.devices) == 1:
            return self.devices[list(self.devices.keys())[0]]
        if name not in self.devices:
            raise KeyError(f"device {name} not found")
        return self.devices[name]

    @classmethod
    def parse(cls, dir):
        xmlfile = glob(os.path.join(dir, "*.xml"))
        if len(xmlfile) != 1:
            raise FileNotFoundError(f"SDK meta file not found in {dir}")
        xmlfile = xmlfile[0]

        tree = ET.parse(xmlfile)
        root = tree.getroot()

        # find devices
        devices = {}
        device_nodes = root.findall("./devices/device")
        for device_node in device_nodes:
            name = device_node.attrib["name"]
            packages = []
            defines = []
            cores = []
            drivers = {}

            for package_node in device_node.findall("./package"):
                packages.append(package_node.attrib["name"])
            for define_node in device_node.findall("./defines/define"):
                defines.append(define_node.attrib["name"])
            for core_node in device_node.findall("./core"):
                cores.append(Core.parse(core_node))
            for driver_node in set(
                root.findall("./components/component[@type='driver']")
            ) & set(root.findall(f"./components/component[@devices='{name}']")):
                # drivers.append(Driver.parse(driver_node))
                drivers[driver_node.attrib["name"]] = Driver.parse(driver_node)
            devices[name] = Device(name, cores, packages, defines, drivers)

        return cls(devices)


def get_sources(args):
    sdk = SDK.parse(args.sdk_root)
    if args.device is None:
        if len(sdk.devices) != 1:
            raise ValueError("SDK contains more than 1 devices, please specific one")
        device = sdk.get_device(None)
    else:
        device = sdk.get_device(args.device)

    required = args.drivers
    required = set(required)
    fin = set()

    for c in required:
        if not c in device.drivers:
            raise KeyError(f"driver {c} not found")
        fin.add(c)
    while True:
        last_len = len(fin)
        required.clear()
        for c in fin:
            if not c in device.drivers:
                raise KeyError(f"driver {c} not found")
            for dep in device.drivers[c].dependencies:
                required.add(dep)
        fin = fin.union(required)
        if len(fin) == last_len:
            break

    srcs = set()
    for c in fin:
        driver = device.drivers[c]
        for f in driver.srcs:
            srcs.add(os.path.abspath(os.path.join(args.sdk_root, f)))
    print(*srcs, sep=";")


def get_defines(args):
    print("defines")


def get_includes(args):
    print("includes")


def print_list(args):
    print("list")


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--sdk_root", required=True)
    subparsers = parser.add_subparsers(title="subcommands")

    parser_sources = subparsers.add_parser("sources")
    parser_sources.add_argument("--device")
    parser_sources.add_argument("drivers", nargs="+")
    parser_sources.set_defaults(func=get_sources)

    parser_defines = subparsers.add_parser("defines")
    parser_defines.add_argument("--device")
    parser_defines.set_defaults(func=get_defines)

    parser_includes = subparsers.add_parser("includes")
    parser_includes.add_argument("--device")
    parser_includes.add_argument("--cmsis", action="store_true")
    parser_includes.set_defaults(func=get_includes)

    parser_list_deviec = subparsers.add_parser("list_device")
    parser_list_deviec.set_defaults(func=print_list)
    parser_list_drivers = subparsers.add_parser("list_drivers")
    parser_list_drivers.set_defaults(func=print_list)

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)
    return


if __name__ == "__main__":
    main()
