import argparse
import os
import sys
import re
from glob import glob
from typing import List
from xml.etree import ElementTree as ET

driver_regex = r"platform\.(drivers|devices)\.(.*?(?=\.))\.(.*)"


class ReturnReason:
    ArgsError = 1
    NotImplemented = 2


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

    def __repr__(self) -> str:
        return f"{self.name} dep {self.dependencies}"


class Core(object):
    def __init__(self, name: str, type: str, fpu: bool, dsp: bool):
        self.name = name
        self.type = type
        self.fpu = fpu
        self.dsp = dsp

    @classmethod
    def parse(cls, node: ET.Element):
        name = node.attrib["name"]
        type = node.attrib["type"]
        fpu = True if node.attrib["fpu"] == "true" else False
        dsp = True if node.attrib["dsp"] == "true" else False
        return cls(name, type, fpu, dsp)

    def __repr__(self) -> str:
        type_regex = r""
        s = f"{self.name}: {self.type}"


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

    def get_defines(self, package: str | None, core: str | None) -> List[str]:
        if not self.package_exists(package):
            raise ValueError(
                f"{package} not found, avaliable packages: ${self.packages}"
            )
        if package is None:
            package = self.packages[0]
        core = self.get_core(core)

        defines = []
        for d in self.defines:
            defines.append(
                d.replace("$|package|", package)
                .replace("$|core_name|", core.name)
                .replace("$|core|", core.type)
            )
        return defines

    def package_exists(self, package: str | None) -> bool:
        if package is None and len(self.packages) == 1:
            return True
        if package in self.packages:
            return True
        return False

    def get_core(self, core: str | None) -> Core:
        if core is None and len(self.cores) == 1:
            return self.cores[0]
        cores = [c.name for c in self.cores]
        if not core in cores:
            raise KeyError(f"{core} not found, avaliable cores: {cores}")
        return self.cores[cores.index(core)]

    def append_driver(self, driver: Driver):
        self.drivers.append(driver)

    def append_drivers(self, drivers: List[Driver]):
        self.drivers.extend(drivers)


class SDK(object):
    def __init__(self, devices: dict[str, Device]):
        self.devices = devices

    def get_device(self, name: str | None):
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
    device = sdk.get_device(args.device)
    srcs = set()

    if args.cmsis:
        core = device.get_core(args.core)
        srcs.add(
            os.path.abspath(
                os.path.join(
                    args.sdk_root,
                    "devices",
                    device.name,
                    f"system_{device.name}_{core.name}.c",
                )
            )
        )

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

    for c in fin:
        driver = device.drivers[c]
        for f in driver.srcs:
            srcs.add(os.path.abspath(os.path.join(args.sdk_root, f)))
    print(*srcs, sep=";")


def get_defines(args):
    sdk = SDK.parse(args.sdk_root)
    device = sdk.get_device(args.device)
    defines = device.get_defines(args.package, args.core)
    print(*defines, sep=";")


def get_includes(args):
    sdk = SDK.parse(args.sdk_root)
    device = sdk.get_device(args.device)

    includes = [
        os.path.abspath(os.path.join(args.sdk_root, "devices", device.name)),
        os.path.abspath(os.path.join(args.sdk_root, "devices", device.name, "drivers")),
    ]
    if args.cmsis:
        includes.append(
            os.path.abspath(os.path.join(args.sdk_root, "CMSIS", "Core", "Include"))
        )

    print(*includes, sep=";")


def print_list(args):
    sdk = SDK.parse(args.sdk_root)
    avaliable_targets = ["drivers", "devices", "packages", "cores"]
    if not args.target in avaliable_targets:
        print("targets should in `drivers`, `devices`, `packages`, `cores`")
        exit(ReturnReason.ArgsError)


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--sdk_root", required=True, help="SDK root dir")
    parser.add_argument(
        "--device",
        required=False,
        help="selected device, print all avaliable values with `list devices`",
    )
    parser.add_argument(
        "--package",
        required=False,
        help="selected package, print all avaliable values with `list packages`",
    )
    parser.add_argument(
        "--core",
        required=False,
        help="selected core, print all avaliable values with `list cores`",
    )
    subparsers = parser.add_subparsers(title="subcommands", help="all subcommands")

    parser_sources = subparsers.add_parser(
        "sources", help="print selected sources with `;` seperated"
    )
    parser_sources.add_argument(
        "--cmsis", action="store_true", help="add CMSIS system source"
    )
    parser_sources.add_argument("drivers", nargs="+", help="selected drivers")
    parser_sources.set_defaults(func=get_sources)

    parser_defines = subparsers.add_parser(
        "defines", help="print defines with selected device and package"
    )
    parser_defines.set_defaults(func=get_defines)

    parser_includes = subparsers.add_parser(
        "includes", help="print include directories for SDK"
    )
    parser_includes.add_argument(
        "--cmsis", action="store_true", help="include SDK's CMSIS"
    )
    parser_includes.set_defaults(func=get_includes)

    parser_list = subparsers.add_parser("list", help="print avaliable informations")
    parser_list.add_argument(
        "target", help="avaliable values: drivers, devices, packages, cores"
    )
    parser_list.set_defaults(func=print_list)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    if not "func" in args:
        print("sdk_root not defined")
        parser.print_help()
        exit(ReturnReason.ArgsError)
    args.func(args)


if __name__ == "__main__":
    main()
