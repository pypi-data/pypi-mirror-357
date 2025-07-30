# --------------------------------------------------------------------------------------------------
# Copyright (c) Lukas Vik. All rights reserved.
#
# This file is part of the tsfpga project, a project platform for modern FPGA development.
# https://tsfpga.com
# https://github.com/tsfpga/tsfpga
# --------------------------------------------------------------------------------------------------

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from tsfpga.system_utils import run_command

from .simlib_open_source import VivadoSimlibOpenSource

if TYPE_CHECKING:
    from vunit.sim_if import SimulatorInterface
    from vunit.ui import VUnit


class VivadoSimlibGhdl(VivadoSimlibOpenSource):
    """
    Handle Vivado simlib with GHDL.

    Do not instantiate this class directly.
    Use factory class :class:`.VivadoSimlib` instead.
    """

    # GHDL compilation crashes if its 'workdir' folder does not exist as the analyze command
    # is executed.
    _create_library_folder_before_compile = True

    def __init__(
        self,
        vivado_path: Path | None,
        output_path: Path,
        vunit_proj: VUnit,
        simulator_interface: SimulatorInterface,
    ) -> None:
        """
        See superclass :class:`.VivadoSimlibCommon` constructor for details.
        """
        self.ghdl_binary = Path(simulator_interface.find_prefix()) / "ghdl"

        super().__init__(
            vivado_path=vivado_path,
            output_path=output_path,
            vunit_proj=vunit_proj,
            simulator_interface=simulator_interface,
        )

    def _execute_compile(self, output_path: Path, library_name: str, vhd_files: list[str]) -> None:
        cmd = [
            str(self.ghdl_binary),
            "-a",
            "--ieee=synopsys",
            "--std=08",
            f"--workdir={output_path}",
            f"-P{self.output_path / 'unisim'}",
            "-fexplicit",
            "-frelaxed-rules",
            "--no-vital-checks",
            "--warn-binding",
            "--mb-comments",
            f"--work={library_name}",
            *vhd_files,
        ]

        run_command(cmd, cwd=self.output_path)

    def _get_simulator_tag(self) -> str:
        """
        Return simulator version tag as a string.
        """
        cmd = [str(self.ghdl_binary), "--version"]
        output = run_command(cmd, capture_output=True).stdout

        match_develop = re.search(pattern=r"^GHDL (\S+) \((\S+)\).*", string=output)
        if match_develop is not None:
            return self._format_version(f"ghdl_{match_develop.group(1)}_{match_develop.group(2)}")

        match_release = re.search(pattern=r"^GHDL (\S+).*", string=output)
        if match_release is not None:
            return self._format_version(f"ghdl_{match_release.group(1)}")

        raise ValueError(f"Could not find GHDL version string: {output}")
