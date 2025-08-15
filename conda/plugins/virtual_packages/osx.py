# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Detect whether this is macOS."""

import os

from ...base.context import context
from .. import CondaVirtualPackage, hookimpl


def _detect_rosetta():
    cpu_vendor, cpu_model = "", ""
    try:
        from archspec.cpu.detect import CpuidInfoCollector
        cpu = CpuidInfoCollector()
        cpu_vendor = cpu.vendor
        cpu_model = cpu.brand_string()
    except (ImportError, SystemError):
        cpu_vendor, cpu_model = "", ""

    # Not 100% sure we really _need_ to check the CPU vendor string, but I
    # figure better safe than sorry, since certain AMD CPUs let users modify
    # the model/brand string.
    return (cpu_vendor == "GenuineIntel" and cpu_model == "VirtualApple")


@hookimpl
def conda_virtual_packages():
    if not context.subdir.startswith("osx-"):
        return

    # 1: __osx (always exported if the target subdir is osx-*)
    yield CondaVirtualPackage("unix", None, None)

    # 2: __osx
    dist_version = os.getenv("CONDA_OVERRIDE_OSX")
    if dist_version is None:  # no override found, let's detect it
        dist_name, dist_version = context.os_distribution_name_version
        if dist_name != "OSX":
            # avoid reporting platform.version() of a different OS
            # this happens with CONDA_SUBDIR=osx-* in a non macOS machine
            dist_version = "0"
    if dist_version:  # truthy override found
        yield CondaVirtualPackage("osx", dist_version, None)
    # if a falsey override was found, the __osx virtual package is not exported

    # 3: determine if we're running in Rosetta
    if context.subdir == "osx-64" and _detect_rosetta():
        # Version 2 since Rosetta 1 covered the PPC -> x86 transition
        yield CondaVirtualPackage(f"rosetta", "2", "0")
